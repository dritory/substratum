#!/usr/bin/env python3
"""Surface structural patterns in the puzzle/mechanism graph.

Emits a single markdown report with:
  1. Gap puzzles (no `solves` edge, or no `solves`/`explains_pattern` at all)
  2. Pareto frontier of compositions in (puzzles closed, parameter cost) space
  3. Shared field-tag clusters (mechanisms grouped by field content)
  4. Never-composed-but-compatible mechanism pairs that share field tags or puzzles

Usage:
    python scripts/search.py                  # write to docs/search_report.md
    python scripts/search.py --output X.md    # custom path
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_all() -> tuple[dict, dict, dict, dict]:
    mechs = {p.stem: json.loads(p.read_text())
             for p in sorted((ROOT / "mechanisms").glob("*.json"))}
    puzzles = {p.stem: json.loads(p.read_text())
               for p in sorted((ROOT / "puzzles").glob("*.json"))}
    frameworks = {p.stem: json.loads(p.read_text())
                  for p in sorted((ROOT / "frameworks").glob("*.json"))}
    benchmarks = {p.stem: json.loads(p.read_text())
                  for p in sorted((ROOT / "benchmarks").glob("*.json"))}
    return mechs, puzzles, frameworks, benchmarks


def role_index(mechs: dict) -> tuple[dict, dict, dict]:
    """Return {puzzle: [(mech, role, confidence)]}, plus reverse, plus solvers-of."""
    by_puzzle: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    by_mech: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for mid, m in mechs.items():
        for e in m.get("addresses_puzzles", []):
            t = (mid, e["role"], e.get("confidence", "proposed"))
            by_puzzle[e["puzzle_id"]].append(t)
            by_mech[mid].append((e["puzzle_id"], e["role"], e.get("confidence", "proposed")))
    return dict(by_puzzle), dict(by_mech)


# ---------- 1. Gap puzzles ----------

def find_gaps(puzzles: dict, by_puzzle: dict) -> list[dict]:
    """Each puzzle gets a record of its strongest available role across mechanisms."""
    out = []
    for pid, p in puzzles.items():
        edges = by_puzzle.get(pid, [])
        roles = {e[1] for e in edges}
        confidences = {e[2] for e in edges}
        if not edges:
            tier = "untouched"
        elif "solves" in roles:
            tier = "has_solver"
        elif "explains_pattern" in roles:
            tier = "has_pattern_explainer"
        elif "ameliorates" in roles:
            tier = "only_ameliorates"
        elif "requires" in roles:
            tier = "only_requires"
        else:
            tier = "other"
        out.append({
            "puzzle_id": pid,
            "name": p.get("name", pid),
            "tier": tier,
            "n_edges": len(edges),
            "n_solves": sum(1 for e in edges if e[1] == "solves"),
            "n_explains": sum(1 for e in edges if e[1] == "explains_pattern"),
            "n_ameliorates": sum(1 for e in edges if e[1] == "ameliorates"),
            "n_requires": sum(1 for e in edges if e[1] == "requires"),
            "established": "established" in confidences,
        })
    return out


# ---------- 2. Pareto frontier of compositions ----------

def composition_metrics(comp: tuple[str, ...], mechs: dict) -> dict:
    closed: set[str] = set()
    partial: set[str] = set()
    requires: set[str] = set()
    cost = 0
    fields: set[str] = set()
    for mid in comp:
        m = mechs[mid]
        cost += m.get("introduces", {}).get("new_parameters_count", 0)
        fields.update(m.get("field_tags", []))
        for e in m.get("addresses_puzzles", []):
            r, pid = e["role"], e["puzzle_id"]
            if r in ("solves", "explains_pattern"):
                closed.add(pid)
            elif r == "ameliorates":
                partial.add(pid)
            elif r == "requires":
                requires.add(pid)
    partial -= closed
    requires -= closed
    requires -= partial
    return {
        "comp": tuple(sorted(comp)),
        "closed": closed,
        "partial": partial,
        "requires_external": requires,
        "cost": cost,
        "field_tags": fields,
    }


def is_feasible(comp: tuple[str, ...], mechs: dict) -> bool:
    s = set(comp)
    for mid in comp:
        ex = set(mechs[mid].get("excludes", []))
        if ex & s:
            return False
    return True


def beam_search_pareto(mechs: dict, max_size: int = 6,
                       beam: int = 80) -> list[dict]:
    """Beam search for compositions that close many puzzles cheaply.

    Multiple scoring criteria sweep different lambdas to span the Pareto front.
    Returns the Pareto-optimal set in (puzzles_closed, parameter_cost) space.
    """
    # Seed with high-impact mechanisms — those that solve or explain_pattern
    # at least one puzzle.
    strong = [mid for mid, m in mechs.items()
              if any(e["role"] in ("solves", "explains_pattern")
                     for e in m.get("addresses_puzzles", []))]
    seeds = [composition_metrics((mid,), mechs) for mid in strong]
    seeds = [s for s in seeds if is_feasible(s["comp"], mechs)]

    all_evaluated: dict[tuple[str, ...], dict] = {s["comp"]: s for s in seeds}
    current = seeds

    for size in range(2, max_size + 1):
        scored: list[tuple[float, dict]] = []
        # For each current composition, try adding any mechanism
        for c in current:
            comp_set = set(c["comp"])
            for mid in mechs:
                if mid in comp_set:
                    continue
                new_comp = tuple(sorted(comp_set | {mid}))
                if new_comp in all_evaluated:
                    continue
                # cheap excludes check
                ex = set(mechs[mid].get("excludes", []))
                if ex & comp_set:
                    continue
                if any(mid in set(mechs[m].get("excludes", [])) for m in comp_set):
                    continue
                metrics = composition_metrics(new_comp, mechs)
                all_evaluated[new_comp] = metrics
                # Score: balance coverage and cost. We'll sweep two extremes.
                cov = len(metrics["closed"])
                cost = max(metrics["cost"], 1)
                scored.append((cov - 0.5 * cost, metrics))
                scored.append((cov, metrics))
                scored.append((cov / cost, metrics))
        # Trim to beam by best score; dedupe by comp
        seen = set()
        next_beam: list[dict] = []
        for _, m in sorted(scored, key=lambda x: -x[0]):
            if m["comp"] in seen:
                continue
            seen.add(m["comp"])
            next_beam.append(m)
            if len(next_beam) >= beam:
                break
        current = next_beam

    # Pareto filter on all evaluated compositions
    candidates = list(all_evaluated.values())
    pareto: list[dict] = []
    for c in candidates:
        cov, cost = len(c["closed"]), c["cost"]
        dominated = False
        for d in candidates:
            if d["comp"] == c["comp"]:
                continue
            dcov, dcost = len(d["closed"]), d["cost"]
            if dcov >= cov and dcost <= cost and (dcov > cov or dcost < cost):
                dominated = True
                break
        if not dominated:
            pareto.append(c)
    pareto.sort(key=lambda c: (-len(c["closed"]), c["cost"]))
    return pareto


# ---------- 3. Field-tag clusters ----------

def field_tag_clusters(mechs: dict) -> dict[str, list[str]]:
    by_tag: dict[str, list[str]] = defaultdict(list)
    for mid, m in mechs.items():
        for t in m.get("field_tags", []):
            by_tag[t].append(mid)
    return {t: sorted(ms) for t, ms in sorted(by_tag.items(), key=lambda x: -len(x[1]))}


# ---------- 4. Never-composed-but-compatible pairs ----------

def never_composed_compatible(mechs: dict, frameworks: dict) -> list[dict]:
    """Pairs that:
      - are not pairwise-excluded
      - share at least one field_tag OR at least one puzzle
      - never co-occur in any framework's composes_mechanisms
    """
    co_occur: set[tuple[str, str]] = set()
    for fw in frameworks.values():
        comp = fw.get("composes_mechanisms") or []
        for a, b in combinations(sorted(comp), 2):
            co_occur.add((a, b))

    mech_puzzles: dict[str, set[str]] = {
        mid: {e["puzzle_id"] for e in m.get("addresses_puzzles", [])}
        for mid, m in mechs.items()
    }
    mech_tags: dict[str, set[str]] = {
        mid: set(m.get("field_tags", [])) for mid, m in mechs.items()
    }
    mech_ex: dict[str, set[str]] = {
        mid: set(m.get("excludes", [])) for mid, m in mechs.items()
    }
    mech_status: dict[str, str] = {
        mid: m.get("status", "") for mid, m in mechs.items()
    }

    pairs: list[dict] = []
    ids = sorted(mechs)
    for a, b in combinations(ids, 2):
        if b in mech_ex[a] or a in mech_ex[b]:
            continue
        if (a, b) in co_occur:
            continue
        # Restrict to "real" mechanisms (skip disfavored/historical) to cut noise
        if mech_status[a] in ("disfavored", "historical"):
            continue
        if mech_status[b] in ("disfavored", "historical"):
            continue
        shared_tags = mech_tags[a] & mech_tags[b]
        shared_puzzles = mech_puzzles[a] & mech_puzzles[b]
        if not shared_tags and not shared_puzzles:
            continue
        # Score by overlap strength
        score = 2 * len(shared_tags) + len(shared_puzzles)
        pairs.append({
            "a": a, "b": b,
            "shared_tags": sorted(shared_tags),
            "shared_puzzles": sorted(shared_puzzles),
            "score": score,
        })
    pairs.sort(key=lambda p: -p["score"])
    return pairs


# ---------- Render ----------

def render(mechs, puzzles, frameworks, benchmarks) -> str:
    by_puzzle, _ = role_index(mechs)
    gaps = find_gaps(puzzles, by_puzzle)
    pareto = beam_search_pareto(mechs, max_size=6, beam=80)
    clusters = field_tag_clusters(mechs)
    pairs = never_composed_compatible(mechs, frameworks)

    L: list[str] = []
    L.append("# Structural search over the catalog\n")
    L.append(f"Inputs: {len(mechs)} mechanisms, {len(puzzles)} puzzles, "
             f"{len(frameworks)} frameworks, {len(benchmarks)} benchmarks.\n")
    L.append("Report sections: gaps · Pareto frontier · field-tag clusters · "
             "never-composed-compatible pairs.\n")

    # --- Section 1: gaps ---
    L.append("## 1. Gap puzzles\n")
    L.append("Puzzles ranked by how weakly current mechanisms address them. "
             "`untouched` = no mechanism edges at all. `only_requires` = some "
             "mechanism declares it must be closed by something else, but "
             "nothing claims to close it.\n")
    tier_order = ["untouched", "only_requires", "only_ameliorates",
                  "has_pattern_explainer", "has_solver"]
    gaps.sort(key=lambda g: (tier_order.index(g["tier"]), -g["n_edges"]))
    L.append("| puzzle | tier | edges | solves | explains | ameliorates | requires |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for g in gaps:
        L.append(f"| `{g['puzzle_id']}` | {g['tier']} | {g['n_edges']} | "
                 f"{g['n_solves']} | {g['n_explains']} | "
                 f"{g['n_ameliorates']} | {g['n_requires']} |")
    L.append("")

    weak = [g for g in gaps if g["tier"] in ("untouched", "only_requires", "only_ameliorates")]
    L.append(f"**{len(weak)} weakly-addressed puzzles** — these are the "
             "places where existing mechanism design leaves the most room.\n")

    # --- Section 2: Pareto frontier ---
    L.append("## 2. Pareto frontier of compositions\n")
    L.append("Compositions of 1-6 mechanisms with no pairwise `excludes` "
             "conflicts, ranked by puzzles closed (`solves` ∪ `explains_pattern`) "
             "vs total new parameters introduced (sum across mechanisms). "
             "A composition is on the frontier if no other composition has at "
             "least as many closures AND no greater cost.\n")
    L.append("| closed | partial | req. ext. | cost | size | mechanisms |")
    L.append("|---:|---:|---:|---:|---:|---|")
    for c in pareto[:40]:
        comp_str = ", ".join(f"`{m}`" for m in c["comp"])
        L.append(f"| {len(c['closed'])} | {len(c['partial'])} | "
                 f"{len(c['requires_external'])} | {c['cost']} | "
                 f"{len(c['comp'])} | {comp_str} |")
    L.append(f"\n*({len(pareto)} compositions on the frontier; "
             f"showing top 40 by coverage.)*\n")

    # --- Section 3: clusters ---
    L.append("## 3. Field-tag clusters\n")
    L.append("Mechanisms grouped by shared field content. Compositions drawn "
             "from a dense cluster compose 'for free' — they share the same "
             "physical degree of freedom doing different jobs. (Note: shared "
             "tag is *necessary* but not *sufficient* for shared content — "
             "mass scale and role aren't captured.)\n")
    for tag, ms in clusters.items():
        if len(ms) < 3:
            continue
        L.append(f"### `{tag}` ({len(ms)} mechanisms)")
        L.append(", ".join(f"`{m}`" for m in ms))
        L.append("")

    # --- Section 4: never-composed-compatible pairs ---
    L.append("## 4. Never-composed-but-compatible pairs\n")
    L.append("Pairs of mechanisms that (a) don't pairwise-exclude each other, "
             "(b) share at least one field tag or puzzle, (c) do not co-occur "
             "in any framework currently in the catalog. These are candidate "
             "compositions nobody has explicitly tried, or that the catalog "
             "hasn't recorded yet. Top 30 by overlap score "
             "(`2 * shared_tags + shared_puzzles`).\n")
    L.append("| score | mech A | mech B | shared tags | shared puzzles |")
    L.append("|---:|---|---|---|---|")
    for p in pairs[:30]:
        tags = ", ".join(f"`{t}`" for t in p["shared_tags"]) or "—"
        pzs = ", ".join(f"`{q}`" for q in p["shared_puzzles"]) or "—"
        L.append(f"| {p['score']} | `{p['a']}` | `{p['b']}` | {tags} | {pzs} |")
    L.append(f"\n*({len(pairs)} compatible pairs total; showing top 30.)*\n")

    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", "-o", type=Path,
                    default=ROOT / "docs" / "search_report.md")
    args = ap.parse_args(argv[1:])
    mechs, puzzles, frameworks, benchmarks = load_all()
    report = render(mechs, puzzles, frameworks, benchmarks)
    args.output.write_text(report)
    print(f"wrote {args.output} ({len(report)} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
