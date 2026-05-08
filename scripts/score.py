#!/usr/bin/env python3
"""Score every framework against every benchmark and emit a markdown table.

Usage:
    python scripts/score.py                      # all frameworks
    python scripts/score.py lambda_cdm_gr        # named framework(s)
    python scripts/score.py --output report.md   # write instead of stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluators import (  # noqa: E402  (path-mangling above is intentional)
    Verdict,
    get_evaluator,
    no_evaluator_verdict,
)


STATUS_GLYPH = {
    "pass": "PASS",
    "fail": "FAIL",
    "contested": "CONT",
    "inapplicable": "N/A",
    "open": "open",
    "no_evaluator": "-",
}


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def collect_frameworks(names: list[str]) -> list[dict]:
    fw_dir = ROOT / "frameworks"
    if not fw_dir.exists():
        return []
    if names:
        paths = [fw_dir / f"{n}.json" for n in names]
    else:
        paths = sorted(fw_dir.glob("*.json"))
    return [load_json(p) for p in paths if p.exists()]


def collect_benchmarks() -> dict[str, dict]:
    return {
        p.stem: load_json(p)
        for p in sorted((ROOT / "benchmarks").glob("*.json"))
    }


def score_one(benchmark: dict, framework: dict) -> Verdict:
    bench_id = benchmark["id"]
    prediction = framework.get("predictions", {}).get(bench_id)
    if prediction is None:
        return Verdict(
            status="open",
            score=None,
            note="framework supplies no prediction for this benchmark",
        )
    evaluator = get_evaluator(bench_id)
    if evaluator is None:
        return no_evaluator_verdict(bench_id)
    return evaluator(benchmark, prediction)


def render(frameworks: list[dict], benchmarks: dict[str, dict]) -> str:
    lines: list[str] = []
    lines.append("# Framework scoring report\n")
    lines.append(
        f"Frameworks: {len(frameworks)} | Benchmarks: {len(benchmarks)} | "
        f"Evaluators registered: {sum(1 for b in benchmarks if get_evaluator(b))}\n"
    )

    for fw in frameworks:
        lines.append(f"## {fw['name']} (`{fw['id']}`)\n")
        lines.append(f"{fw['summary']}\n")
        lines.append("| Benchmark | Status | Score | Note |")
        lines.append("|---|---|---|---|")
        tally: dict[str, int] = {}
        for bench_id, bench in benchmarks.items():
            v = score_one(bench, fw)
            tally[v.status] = tally.get(v.status, 0) + 1
            score = "" if v.score is None else f"{v.score:.3f}"
            lines.append(
                f"| `{bench_id}` | {STATUS_GLYPH[v.status]} | {score} | "
                f"{v.note.replace('|', '\\|')} |"
            )
        summary = ", ".join(f"{STATUS_GLYPH[k]} {v}" for k, v in sorted(tally.items()))
        lines.append(f"\n**Tally:** {summary}\n")

    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frameworks", nargs="*", help="framework ids to score (default: all)")
    parser.add_argument("--output", "-o", type=Path, help="write report to file instead of stdout")
    args = parser.parse_args(argv[1:])

    frameworks = collect_frameworks(args.frameworks)
    if not frameworks:
        print("no frameworks found", file=sys.stderr)
        return 1
    benchmarks = collect_benchmarks()
    report = render(frameworks, benchmarks)

    if args.output:
        args.output.write_text(report)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
