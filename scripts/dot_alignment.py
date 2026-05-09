#!/usr/bin/env python3
"""Render the puzzle-mechanism bipartite graph as a markdown report.

For each mechanism, compute the compression score (puzzles_closed /
parameters_introduced) and surface mechanisms that touch many puzzles. For each
puzzle, surface mechanisms that compete to address it. Flag mechanisms whose
encoded effects violate established benchmarks while still claiming
mainstream/niche status (encoding error or genuinely dead proposal).

Usage:
    python scripts/dot_alignment.py                  # stdout
    python scripts/dot_alignment.py -o report.md     # write to file
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ROLE_GLYPH = {
    "solves": "SOLVES",
    "ameliorates": "amelior.",
    "explains_pattern": "pattern",
    "requires": "requires",
}

EFFECT_GLYPH = {
    "respects": "ok",
    "near_bound": "near",
    "violates": "VIOLATES",
    "predicts_signal": "signal",
}

CLOSING_ROLES = {"solves", "explains_pattern"}


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def load_dir(name: str) -> dict[str, dict]:
    d = ROOT / name
    if not d.exists():
        return {}
    return {p.stem: load_json(p) for p in sorted(d.glob("*.json"))}


def compression_score(mech: dict) -> float:
    closed = sum(
        1 for e in mech.get("addresses_puzzles", [])
        if e.get("role") in CLOSING_ROLES
    )
    params = max(int(mech.get("introduces", {}).get("new_parameters_count", 1)), 1)
    return closed / params


def benchmarks_violated(mech: dict) -> list[str]:
    return [
        e["benchmark_id"]
        for e in mech.get("touches_benchmarks", [])
        if e.get("effect") == "violates"
    ]


def render_bipartite_table(puzzles: dict, mechanisms: dict) -> list[str]:
    lines = ["## Bipartite graph: mechanisms x puzzles\n"]
    pids = sorted(puzzles)
    header = "| mechanism \\\\ puzzle | " + " | ".join(f"`{p}`" for p in pids) + " |"
    sep = "|" + "---|" * (len(pids) + 1)
    lines += [header, sep]
    for mid in sorted(mechanisms):
        m = mechanisms[mid]
        cells: list[str] = []
        edges = {e["puzzle_id"]: e for e in m.get("addresses_puzzles", [])}
        for pid in pids:
            e = edges.get(pid)
            if e is None:
                cells.append("")
            else:
                role = ROLE_GLYPH.get(e["role"], e["role"])
                conf = e.get("confidence", "?")
                cells.append(f"{role} ({conf})")
        lines.append(f"| `{mid}` ({m.get('status', '?')}) | " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def render_compression(mechanisms: dict) -> list[str]:
    lines = ["## Compression scores\n"]
    lines.append(
        "Compression = (puzzles closed via 'solves' or 'explains_pattern') / "
        "(new free parameters introduced). Higher is better. Mechanisms that "
        "address many puzzles with few parameters surface here.\n"
    )
    lines.append("| mechanism | type | status | puzzles closed | params | compression |")
    lines.append("|---|---|---|---|---|---|")
    rows = []
    for mid, m in mechanisms.items():
        closed = sum(
            1 for e in m.get("addresses_puzzles", []) if e.get("role") in CLOSING_ROLES
        )
        params = int(m.get("introduces", {}).get("new_parameters_count", 0))
        rows.append((compression_score(m), mid, m, closed, params))
    rows.sort(key=lambda r: -r[0])
    for score, mid, m, closed, params in rows:
        lines.append(
            f"| `{mid}` | {m['type']} | {m.get('status', '?')} | {closed} | "
            f"{params} | {score:.3f} |"
        )
    lines.append("")
    return lines


def render_high_degree(mechanisms: dict, threshold: int = 3) -> list[str]:
    lines = [f"## High-degree mechanisms (>= {threshold} puzzles closed or addressed)\n"]
    lines.append(
        "These mechanisms touch many puzzles at once - the historical signature "
        "of theoretical proposals worth taking seriously (GIM, SUSY's appeal, "
        "inflation). High-degree does not mean correct; it means worth "
        "comprehensive cross-domain accountability.\n"
    )
    rows = []
    for mid, m in mechanisms.items():
        edges = m.get("addresses_puzzles", [])
        addressed = [e["puzzle_id"] for e in edges if e.get("role") != "requires"]
        if len(addressed) >= threshold:
            rows.append((len(addressed), mid, m, addressed, edges))
    rows.sort(key=lambda r: -r[0])
    if not rows:
        lines.append("_(none in current seed.)_\n")
        return lines
    for degree, mid, m, addressed, edges in rows:
        roles = ", ".join(
            f"`{e['puzzle_id']}` ({ROLE_GLYPH[e['role']]})"
            for e in edges if e.get("role") != "requires"
        )
        lines.append(f"- **`{mid}`** (degree {degree}, status {m.get('status', '?')}): {roles}")
    lines.append("")
    return lines


def render_convergent(puzzles: dict, mechanisms: dict, threshold: int = 3) -> list[str]:
    lines = [f"## Convergent puzzles (>= {threshold} mechanisms address them)\n"]
    lines.append(
        "Puzzles that have attracted multiple distinct mechanism proposals. "
        "These are the active battlegrounds of theoretical physics; a "
        "compression-superior mechanism here would carry strong evidential "
        "weight.\n"
    )
    incoming: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for mid, m in mechanisms.items():
        for e in m.get("addresses_puzzles", []):
            if e.get("role") == "requires":
                continue
            incoming[e["puzzle_id"]].append(
                (mid, e.get("role", "?"), e.get("confidence", "?"))
            )
    rows = sorted(
        ((p, ms) for p, ms in incoming.items() if len(ms) >= threshold),
        key=lambda r: -len(r[1]),
    )
    if not rows:
        lines.append("_(none in current seed.)_\n")
        return lines
    for pid, ms in rows:
        contenders = ", ".join(
            f"`{mid}` ({ROLE_GLYPH[role]}/{conf})" for mid, role, conf in ms
        )
        lines.append(f"- **`{pid}`** ({len(ms)} mechanisms): {contenders}")
    lines.append("")
    return lines


def render_violations(mechanisms: dict) -> list[str]:
    lines = ["## Encoded violations\n"]
    lines.append(
        "Mechanisms whose declared effect on a benchmark is `violates`. A "
        "mainstream/niche entry that violates a benchmark is either an encoding "
        "error or a genuinely dead proposal that has not yet been retired.\n"
    )
    bad = []
    for mid, m in mechanisms.items():
        violated = benchmarks_violated(m)
        if violated:
            bad.append((mid, m, violated))
    if not bad:
        lines.append("_(none.)_\n")
        return lines
    for mid, m, violated in bad:
        flag = "WARN" if m.get("status") in {"mainstream", "niche"} else "(historical)"
        lines.append(
            f"- {flag} **`{mid}`** (status {m.get('status', '?')}): violates "
            + ", ".join(f"`{b}`" for b in violated)
        )
    lines.append("")
    return lines


def render_structural_clusters(mechanisms: dict) -> list[str]:
    lines = ["## Structural-feature clustering\n"]
    lines.append(
        "Tags shared across mechanisms suggest latent families. This is a "
        "naive co-occurrence count; UMAP / graph clustering is a follow-up.\n"
    )
    feature_counts: dict[str, list[str]] = defaultdict(list)
    for mid, m in mechanisms.items():
        for f in m.get("structural_features", []):
            feature_counts[f].append(mid)
    rows = sorted(feature_counts.items(), key=lambda r: -len(r[1]))
    lines.append("| feature | mechanisms |")
    lines.append("|---|---|")
    for feat, mids in rows:
        if len(mids) < 2:
            continue
        lines.append(f"| `{feat}` | " + ", ".join(f"`{m}`" for m in mids) + " |")
    lines.append("")
    return lines


def render_dependencies(mechanisms: dict) -> list[str]:
    lines = ["## Dependency edges (`requires`)\n"]
    edges = []
    for mid, m in mechanisms.items():
        for e in m.get("addresses_puzzles", []):
            if e.get("role") == "requires":
                edges.append((mid, e["puzzle_id"]))
    if not edges:
        lines.append("_(none.)_\n")
        return lines
    for mid, pid in edges:
        lines.append(f"- `{mid}` requires `{pid}` to be addressed by another mechanism")
    lines.append("")
    return lines


def render(puzzles: dict, mechanisms: dict, benchmarks: dict) -> str:
    lines = ["# Dot-alignment report\n"]
    lines.append(
        f"**Puzzles**: {len(puzzles)} | **Mechanisms**: {len(mechanisms)} | "
        f"**Benchmarks linked from mechanisms**: "
        f"{sum(len(m.get('touches_benchmarks', [])) for m in mechanisms.values())}\n"
    )
    lines.append(
        "Operational principle: make it expensive to ignore evidence and cheap "
        "to compress it. A mechanism scores well when it addresses many puzzles "
        "with few new parameters and respects every benchmark.\n"
    )
    lines += render_bipartite_table(puzzles, mechanisms)
    lines += render_compression(mechanisms)
    lines += render_high_degree(mechanisms)
    lines += render_convergent(puzzles, mechanisms)
    lines += render_dependencies(mechanisms)
    lines += render_violations(mechanisms)
    lines += render_structural_clusters(mechanisms)
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args(argv[1:])

    puzzles = load_dir("puzzles")
    mechanisms = load_dir("mechanisms")
    benchmarks = load_dir("benchmarks")
    if not puzzles or not mechanisms:
        print("puzzles/ or mechanisms/ is empty; nothing to align.", file=sys.stderr)
        return 1
    report = render(puzzles, mechanisms, benchmarks)
    if args.output:
        args.output.write_text(report)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
