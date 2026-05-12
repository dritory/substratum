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


def derive_puzzle_verdicts(
    frameworks: list[dict],
    mechanisms_by_id: dict[str, dict],
    puzzle_ids: list[str],
) -> tuple[list[dict], dict[str, dict[str, int]]]:
    """For each (framework, puzzle), derive the L1 verdict from composed
    mechanisms' addresses_puzzles edges.

    The verdict ladder (strongest role wins):
        any 'solves' or 'explains_pattern'  -> 'closed'
        else any 'ameliorates'              -> 'partial'
        else any 'requires'                 -> 'requires_external'
        no edges                            -> 'untouched'

    Returns (verdicts_list, tallies_by_framework_id) where:
        verdicts_list = [{framework_id, puzzle_id, verdict, contributing_mechanisms}, ...]
        tallies_by_framework_id = {framework_id: {closed, partial, requires_external, untouched}}
    """
    ROLE_TO_VERDICT = {
        "solves": "closed",
        "explains_pattern": "closed",
        "ameliorates": "partial",
        "requires": "requires_external",
    }
    VERDICT_RANK = {
        "closed": 3,
        "partial": 2,
        "requires_external": 1,
        "untouched": 0,
    }

    verdicts: list[dict] = []
    tallies: dict[str, dict[str, int]] = {}

    for fw in frameworks:
        fw_id = fw["id"]
        composed = fw.get("composes_mechanisms") or []
        tally = {"closed": 0, "partial": 0, "requires_external": 0, "untouched": 0}
        for pid in puzzle_ids:
            best_verdict = "untouched"
            contributors: list[tuple[str, str]] = []  # (mech_id, role)
            for mid in composed:
                m = mechanisms_by_id.get(mid)
                if m is None:
                    continue
                for e in m.get("addresses_puzzles", []):
                    if e["puzzle_id"] != pid:
                        continue
                    v = ROLE_TO_VERDICT.get(e["role"], "untouched")
                    if VERDICT_RANK[v] > VERDICT_RANK[best_verdict]:
                        best_verdict = v
                    contributors.append((mid, e["role"]))
            tally[best_verdict] += 1
            verdicts.append({
                "framework_id": fw_id,
                "puzzle_id": pid,
                "verdict": best_verdict,
                "contributing_mechanisms": [
                    {"mechanism_id": m, "role": r} for m, r in contributors
                ],
            })
        tallies[fw_id] = tally

    return verdicts, tallies


def compute_verdicts(
    frameworks: list[dict],
    benchmarks: dict[str, dict],
    mechanisms_by_id: dict[str, dict] | None = None,
    puzzle_ids: list[str] | None = None,
) -> dict:
    """Score every (framework, benchmark) pair and return a structured payload.

    Shape:
      {
        "frameworks": [{"id", "name", "summary", "lineage", "tags", "tally", "puzzle_tally"}, ...],
        "verdicts":   [{"framework_id", "benchmark_id", "status", "score", "note", "reference", "kind"}, ...],
        "puzzle_verdicts": [{"framework_id", "puzzle_id", "verdict", "contributing_mechanisms"}, ...]
      }

    The L1 puzzle verdicts are derived from each framework's composes_mechanisms
    using the addresses_puzzles edges of those mechanisms. Only included if
    mechanisms_by_id and puzzle_ids are supplied; otherwise omitted for
    backward compatibility.
    """
    fw_records: list[dict] = []
    verdicts: list[dict] = []

    for fw in frameworks:
        tally: dict[str, int] = {}
        for bench_id, bench in benchmarks.items():
            v = score_one(bench, fw)
            tally[v.status] = tally.get(v.status, 0) + 1
            pred = (fw.get("predictions") or {}).get(bench_id) or {}
            verdicts.append(
                {
                    "framework_id": fw["id"],
                    "benchmark_id": bench_id,
                    "status": v.status,
                    "score": v.score,
                    "note": v.note,
                    "kind": pred.get("kind"),
                    "value": pred.get("value"),
                    "uncertainty": pred.get("uncertainty"),
                    "units": pred.get("units"),
                    "reference": pred.get("reference"),
                }
            )
        fw_records.append(
            {
                "id": fw["id"],
                "name": fw["name"],
                "summary": fw.get("summary", ""),
                "lineage": fw.get("lineage", []),
                "tags": fw.get("tags", []),
                "tally": tally,
                "composes_mechanisms": fw.get("composes_mechanisms") or [],
            }
        )

    payload: dict = {"frameworks": fw_records, "verdicts": verdicts}

    if mechanisms_by_id is not None and puzzle_ids is not None:
        puzzle_verdicts, puzzle_tallies = derive_puzzle_verdicts(
            frameworks, mechanisms_by_id, puzzle_ids
        )
        payload["puzzle_verdicts"] = puzzle_verdicts
        for rec in fw_records:
            rec["puzzle_tally"] = puzzle_tallies.get(rec["id"], {})

    return payload


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
            note = v.note.replace("|", "\\|")
            lines.append(
                f"| `{bench_id}` | {STATUS_GLYPH[v.status]} | {score} | {note} |"
            )
        summary = ", ".join(f"{STATUS_GLYPH[k]} {v}" for k, v in sorted(tally.items()))
        lines.append(f"\n**Tally:** {summary}\n")

    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frameworks", nargs="*", help="framework ids to score (default: all)")
    parser.add_argument("--output", "-o", type=Path, help="write markdown report to file instead of stdout")
    parser.add_argument("--json", type=Path, help="write structured JSON report to this path")
    args = parser.parse_args(argv[1:])

    frameworks = collect_frameworks(args.frameworks)
    if not frameworks:
        print("no frameworks found", file=sys.stderr)
        return 1
    benchmarks = collect_benchmarks()

    if args.json:
        payload = compute_verdicts(frameworks, benchmarks)
        args.json.write_text(json.dumps(payload, indent=2))
        print(f"wrote {args.json}", file=sys.stderr)

    report = render(frameworks, benchmarks)
    if args.output:
        args.output.write_text(report)
        print(f"wrote {args.output}", file=sys.stderr)
    elif not args.json:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
