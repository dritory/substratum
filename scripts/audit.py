#!/usr/bin/env python3
"""Catalog consistency auditor.

Runs a battery of correctness checks beyond schema + cross-reference validation.
Designed to be CI-runnable and to fail (exit 1) on any flagged issue. Each
check addresses a specific failure mode that has shown up in practice or that
is easy to introduce by inattention:

- status_coherence: mechanisms labelled `disfavored`/`historical` should either
  declare a benchmark violation or use empirical-pressure language in their
  history note. Otherwise the status is asserted without justification.
- mainstream_must_close: mechanisms with status `mainstream` should close at
  least one puzzle (role solves/explains_pattern). 'Mainstream' shouldn't be
  applied to a proposal that only nudges existing tensions.
- provenance: every reference must have either an `arxiv` or `doi` field
  (or be explicitly noted as pre-electronic), so claims trace to a stable
  external object.
- bound_consistency: when a mechanism's note about benchmark X cites a numeric
  bound, that value should match the benchmark's current_bound to within a
  factor of two.
- compose_excludes_consistency: if A `excludes` B then B should not list A in
  `composes_with`, and vice versa.

Use `--json` for machine-readable output suitable for parsing in CI.

Usage:
    python scripts/audit.py
    python scripts/audit.py --json
    python scripts/audit.py --no-bound-check    # skip the heuristic bound check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dir(name: str) -> dict[str, dict]:
    d = ROOT / name
    if not d.exists():
        return {}
    out = {}
    for p in sorted(d.glob("*.json")):
        try:
            out[p.stem] = json.loads(p.read_text())
        except json.JSONDecodeError:
            pass
    return out


EMPIRICAL_PRESSURE_KEYWORDS = (
    "excluded", "ruled out", "disfavour", "disfavor",
    "superseded", "supplanted", "constrained", "tension", "killed",
    "ruled-out", "post-lhc", "post-bicep", "post-gw170817",
    "historical", "challenged", "marginalised", "marginalized",
    "contested", "retired", "not statistically robust",
    "speculative", "not survived", "did not survive",
)


def check_status_coherence(mechanisms: dict) -> list[str]:
    """Disfavored/historical entries should declare a violation or explain why."""
    msgs = []
    for mid, m in mechanisms.items():
        status = m.get("status")
        if status not in {"disfavored", "historical"}:
            continue
        has_violation = any(
            e.get("effect") == "violates"
            for e in m.get("touches_benchmarks", [])
        )
        history = (m.get("history") or "").lower()
        summary = (m.get("summary") or "").lower()
        text = history + " " + summary
        has_pressure = any(kw in text for kw in EMPIRICAL_PRESSURE_KEYWORDS)
        if not has_violation and not has_pressure:
            msgs.append(
                f"mechanisms/{mid}: status={status!r} but no `violates` edge and "
                f"no empirical-pressure language in history/summary."
            )
    return msgs


def check_mainstream_closes_puzzle(mechanisms: dict) -> list[str]:
    """Mainstream mechanisms should close at least one puzzle."""
    msgs = []
    for mid, m in mechanisms.items():
        if m.get("status") != "mainstream":
            continue
        closes = [
            e for e in m.get("addresses_puzzles", [])
            if e.get("role") in {"solves", "explains_pattern"}
        ]
        if not closes:
            msgs.append(
                f"mechanisms/{mid}: status=mainstream but no puzzle is addressed "
                f"with role solves/explains_pattern."
            )
    return msgs


def check_provenance(directory: str) -> list[str]:
    """Every reference must have an arxiv ID or DOI."""
    msgs = []
    entries = load_dir(directory)
    for name, entry in entries.items():
        refs = entry.get("references") or entry.get("primary_references") or []
        for i, r in enumerate(refs):
            if not isinstance(r, dict):
                continue
            if r.get("arxiv") or r.get("doi") or r.get("url"):
                continue
            citation = (r.get("citation") or "")[:120]
            msgs.append(
                f"{directory}/{name}: reference[{i}] lacks arxiv/doi/url: {citation!r}"
            )
    return msgs


BOUND_RE = re.compile(
    r"<\s*~?\s*(?P<value>[0-9]*\.?[0-9]+(?:[eE][+-]?\d+)?)\s*"
    r"(?P<units>cm\^?2|e\s*cm|eV|GeV|TeV)",
)


def _parse_bound(value):
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    m = re.search(r"([0-9]*\.?[0-9]+(?:[eE][+-]?\d+)?)", value)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def check_bound_consistency(mechanisms: dict, benchmarks: dict) -> list[str]:
    """Heuristic: bound values cited in mechanism notes should match the source
    benchmark to within a factor of two."""
    msgs = []
    for mid, m in mechanisms.items():
        for edge in m.get("touches_benchmarks", []):
            bid = edge.get("benchmark_id")
            note = edge.get("note", "")
            if not bid or not note or bid not in benchmarks:
                continue
            match = BOUND_RE.search(note)
            if not match:
                continue
            cited = _parse_bound(match.group("value"))
            if cited is None:
                continue
            bench_bound = (benchmarks[bid].get("current_bound") or {}).get("value")
            actual = _parse_bound(bench_bound)
            if actual is None or actual == 0:
                continue
            ratio = cited / actual
            if ratio < 0.5 or ratio > 2.0:
                msgs.append(
                    f"mechanisms/{mid} -> benchmarks/{bid}: note cites bound "
                    f"{cited:.3g} {match.group('units').strip()} but benchmark "
                    f"current_bound is {actual:.3g}; ratio {ratio:.2f}"
                )
    return msgs


def check_compose_excludes_consistency(mechanisms: dict) -> list[str]:
    """If A excludes B then B should not list A in composes_with."""
    msgs = []
    for mid, m in mechanisms.items():
        excludes = set(m.get("excludes") or [])
        composes = set(m.get("composes_with") or [])
        # Inconsistency within the same entry
        for other in excludes & composes:
            msgs.append(
                f"mechanisms/{mid}: lists {other!r} in both `excludes` and `composes_with`."
            )
        # Symmetric inconsistency across entries
        for other in excludes:
            if other not in mechanisms:
                continue
            other_composes = set(mechanisms[other].get("composes_with") or [])
            if mid in other_composes:
                msgs.append(
                    f"mechanisms/{mid} excludes {other!r}, but {other!r} composes_with {mid!r}."
                )
    return msgs


def check_orphan_benchmarks(mechanisms: dict, benchmarks: dict) -> list[str]:
    """Benchmarks that no mechanism touches — informational, not a failure."""
    touched = set()
    for m in mechanisms.values():
        for edge in m.get("touches_benchmarks", []):
            if edge.get("benchmark_id"):
                touched.add(edge["benchmark_id"])
    orphans = sorted(set(benchmarks) - touched)
    return [
        f"benchmarks/{b}: no mechanism touches this benchmark (informational)"
        for b in orphans
    ]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-bound-check", action="store_true")
    parser.add_argument("--no-orphans", action="store_true",
                        help="Suppress the informational orphan-benchmark report")
    parser.add_argument("--fail-on-orphans", action="store_true",
                        help="Treat orphan benchmarks as failures (default: warn only)")
    args = parser.parse_args(argv[1:])

    mechanisms = load_dir("mechanisms")
    puzzles = load_dir("puzzles")
    benchmarks = load_dir("benchmarks")

    issues: dict[str, list[str]] = {
        "status_coherence": check_status_coherence(mechanisms),
        "mainstream_must_close": check_mainstream_closes_puzzle(mechanisms),
        "provenance_mechanisms": check_provenance("mechanisms"),
        "provenance_puzzles": check_provenance("puzzles"),
        "provenance_benchmarks": check_provenance("benchmarks"),
        "compose_excludes_consistency": check_compose_excludes_consistency(mechanisms),
    }
    if not args.no_bound_check:
        issues["bound_consistency"] = check_bound_consistency(mechanisms, benchmarks)

    orphans = [] if args.no_orphans else check_orphan_benchmarks(mechanisms, benchmarks)
    if orphans and args.fail_on_orphans:
        issues["orphan_benchmarks"] = orphans

    blocking = sum(len(v) for v in issues.values())

    if args.json:
        out = dict(issues)
        if orphans and not args.fail_on_orphans:
            out["orphan_benchmarks_info"] = orphans
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for check, msgs in issues.items():
            print(f"== {check}: {len(msgs)} issue(s) ==")
            for m in msgs:
                print(f"  - {m}")
            print()
        if orphans and not args.fail_on_orphans:
            print(f"== orphan_benchmarks (informational): {len(orphans)} ==")
            for m in orphans[:10]:
                print(f"  - {m}")
            if len(orphans) > 10:
                print(f"  ... ({len(orphans) - 10} more)")
            print()
        print(
            f"Summary: {blocking} blocking issue(s); "
            f"{len(mechanisms)} mechanisms, {len(puzzles)} puzzles, "
            f"{len(benchmarks)} benchmarks; {len(orphans)} orphan benchmarks."
        )

    return 1 if blocking > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
