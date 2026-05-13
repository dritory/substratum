#!/usr/bin/env python3
"""Bundle data/ and benchmarks/ JSON into docs/data.json for the static site.

Produces a single combined JSON with light derived fields (numeric sigma where
parseable, normalized scale entries) so the front-end stays simple. The source
of truth remains the per-entry JSON files; this script is a build step.
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
BENCH_DIR = ROOT / "benchmarks"
FW_DIR = ROOT / "frameworks"
PUZZLE_DIR = ROOT / "puzzles"
MECH_DIR = ROOT / "mechanisms"
OUT_DIR = ROOT / "docs"
OUT_FILE = OUT_DIR / "data.json"

CLOSING_ROLES = {"solves", "explains_pattern"}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:sigma|σ)?")


def parse_sigma(value):
    """Return a best-effort numeric sigma plus the original text.

    sigma fields can be numbers ("4.2"), ranges ("1-2 (lattice)"), or
    descriptive strings ("naturalness, not statistical"). Numbers and ranges
    are reduced to a midpoint; narrative-only strings return None.
    """
    if isinstance(value, (int, float)):
        return float(value), str(value)
    if not isinstance(value, str):
        return None, ""
    text = value.strip()
    if not text:
        return None, text
    if re.match(r"^\s*naturalness\b", text, re.IGNORECASE):
        return None, text
    rng = RANGE_RE.search(text)
    if rng:
        a, b = float(rng.group(1)), float(rng.group(2))
        return (a + b) / 2.0, text
    nums = [float(x) for x in NUM_RE.findall(text)]
    if not nums:
        return None, text
    return nums[0], text


def derive_tension(entry: dict) -> dict:
    history = entry.get("tension_history") or []
    parsed = []
    for h in history:
        sigma_num, sigma_text = parse_sigma(h.get("sigma"))
        parsed.append(
            {
                "year": h.get("year"),
                "sigma_numeric": sigma_num,
                "sigma_text": sigma_text,
                "comparison": h.get("comparison", ""),
                "note": h.get("note", ""),
            }
        )
    numeric = [p for p in parsed if p["sigma_numeric"] is not None and p["year"] is not None]
    latest = max(numeric, key=lambda p: p["year"]) if numeric else None
    entry["_history_parsed"] = parsed
    entry["_latest_sigma"] = latest["sigma_numeric"] if latest else None
    entry["_latest_year"] = latest["year"] if latest else None

    measurements = entry.get("measurements") or []
    measurement_years = [m.get("year") for m in measurements if isinstance(m.get("year"), int)]
    entry["_measurement_year_range"] = (
        [min(measurement_years), max(measurement_years)] if measurement_years else None
    )

    scale = entry.get("characteristic_scale") or {}
    entry["_length_m"] = scale.get("length_m")
    entry["_energy_ev"] = scale.get("energy_ev")
    entry["_layer"] = "tension"
    return entry


# Tag-to-category map. Order matters: the first matching category wins,
# so place more-specific buckets above more-general ones (e.g. "neutrino"
# before "flavor_cp" so a flavor-conserving neutrino oscillation entry
# lands as 'neutrino' rather than 'flavor_cp').
CATEGORY_RULES = [
    ("meta", {"meta", "constraint_set", "tensions", "tension"}),
    ("lorentz_cpt", {"lorentz", "sme", "cpt"}),
    ("gravity", {
        "gravity", "gravitational_waves", "ppn", "ppk",
        "equivalence_principle", "frame_dragging", "fifth_force",
        "shapiro_delay", "strong_field", "strong_field_gravity",
        "massive_gravity", "primordial_gw", "dispersion",
        "dipolar_radiation", "gyroscope", "extra_dimensions", "yukawa",
        "short_range_force", "casimir", "polarization",
    }),
    ("qcd_hadronic", {
        "qcd", "lattice_qcd", "lattice", "hadron_spectrum", "nucleon",
        "strong_cp", "nuclear_eos", "nuclear",
    }),
    ("cosmology", {
        "cosmology", "cmb", "bbn", "lambda_cdm", "n_eff", "early_universe",
        "inflation", "lyman_alpha", "lss", "structure_growth",
        "redshift_distortions", "spectral_distortion", "dark_energy",
        "energy_injection", "light_relics", "cmb_damping_tail", "bao",
        "statistical_isotropy", "cosmic_strings", "small_scale", "lithium",
        "b_mode",
    }),
    ("neutrino", {
        "neutrino", "neutrinos", "pmns", "oscillation", "msw",
        "double_beta_decay", "majorana", "lepton_number_violation",
        "tritium", "sno", "borexino", "matter_effect",
        "flavor_conversion",
    }),
    ("flavor_cp", {
        "flavor", "cp_violation", "b_meson", "kaon", "fcnc", "lfu",
        "lepton_universality", "ckm", "v_ud", "kaon_mixing",
        "d_meson_mixing", "epsilon_k", "weak_decay", "weak_effective_theory",
        "rare_decay", "radiative_decay", "leptoquark", "mixing",
        "edm", "clfv", "lfv", "lepton_flavor",
        "comagnetometer",
    }),
    ("electroweak_higgs", {
        "electroweak", "oblique", "higgs", "smeft", "lhc", "z_prime",
        "charged_higgs", "susy", "gut", "wilson_coefficient",
        "baryon_number", "parity_violation", "super_kamiokande",
    }),
    ("qed_atomic", {
        "qed", "anomalous_moment", "lamb_shift", "atomic_physics",
        "spectroscopy", "hvp", "bound_state", "qed_vacuum", "muonic_atom",
        "proton_radius", "atomic_clocks", "alpha_variation", "dilaton",
        "alpha_determination",
    }),
    # dark_sector is intentionally below the physics-discipline buckets:
    # an EP test or a strong-CP entry is more naturally 'gravity' or 'qcd'
    # even when its dark-sector tag is present. Axion is omitted from
    # dark_sector keys for the same reason — it slots into qcd_hadronic
    # (strong CP) or flavor_cp (axion-mediated EDM) when those signals
    # are present, and still hits dark_sector here when only dark-matter
    # keys remain (e.g. axion_haloscope_admx via dark_matter+haloscope).
    ("dark_sector", {
        "dark_matter", "dark_photon", "dark_sector", "hidden_sector",
        "haloscope", "helioscope", "ultralight_dark_matter",
        "warm_dark_matter", "kinetic_mixing", "wimp", "xenon",
        "indirect_detection", "direct_detection", "sidm", "self_interaction",
        "primordial_black_holes", "microlensing", "mond", "fermi_lat",
        "modified_gravity",
    }),
    ("astrophysics", {
        "astrophysics", "neutron_stars", "helioseismology", "sun", "solar",
        "gzk", "uhecr", "auger", "telescope_array", "smbh", "pulsar",
        "pulsar_timing", "grb", "stellar_physics", "neutron",
    }),
]

CATEGORY_LABEL = {
    "gravity":           "gravity & GW",
    "cosmology":         "cosmology",
    "dark_sector":       "dark sector",
    "flavor_cp":         "flavor & CP",
    "neutrino":          "neutrinos",
    "electroweak_higgs": "EW / Higgs",
    "qcd_hadronic":      "QCD / hadronic",
    "qed_atomic":        "QED / atomic / clocks",
    "lorentz_cpt":       "Lorentz / CPT",
    "astrophysics":      "astrophysics",
    "meta":              "meta",
    "uncategorized":     "uncategorized",
}

CATEGORY_ORDER = [
    "gravity", "cosmology", "dark_sector", "flavor_cp", "neutrino",
    "electroweak_higgs", "qcd_hadronic", "qed_atomic", "lorentz_cpt",
    "astrophysics", "meta", "uncategorized",
]


def categorize(entry: dict) -> str:
    tags = set(entry.get("tags") or [])
    if not tags:
        return "uncategorized"
    for cat, keys in CATEGORY_RULES:
        if tags & keys:
            return cat
    return "uncategorized"


def derive_benchmark(entry: dict) -> dict:
    regime = entry.get("regime") or {}
    entry["_length_m"] = regime.get("length_m")
    entry["_energy_ev"] = regime.get("energy_ev")
    entry["_evaluator_status"] = (entry.get("procedural") or {}).get("evaluator_status")
    entry["_category"] = categorize(entry)
    entry["_category_label"] = CATEGORY_LABEL.get(entry["_category"], entry["_category"])
    entry["_layer"] = "benchmark"
    return entry


def load_dir(path: Path) -> list[dict]:
    out = []
    for p in sorted(path.glob("*.json")):
        with p.open() as f:
            try:
                out.append(json.load(f))
            except json.JSONDecodeError as e:
                print(f"FAIL: {p}: {e}", file=sys.stderr)
                raise
    return out


def compute_evaluation(
    benchmarks: list[dict],
    mechanisms: list[dict] | None = None,
    puzzles: list[dict] | None = None,
) -> dict | None:
    """Run scripts.score.compute_verdicts if frameworks/ has any entries.

    Tolerates evaluator import errors so the site still builds when an
    evaluator module is broken. When mechanisms and puzzles are supplied,
    the returned payload also carries L1 puzzle verdicts derived from each
    framework's composes_mechanisms.
    """
    if not FW_DIR.exists():
        return None
    fw_paths = sorted(FW_DIR.glob("*.json"))
    if not fw_paths:
        return None
    try:
        from scripts.score import compute_verdicts
    except Exception as e:  # pragma: no cover
        print(f"warning: could not import score.compute_verdicts: {e}", file=sys.stderr)
        return None

    frameworks = []
    for p in fw_paths:
        with p.open() as f:
            frameworks.append(json.load(f))
    bench_map = {b["id"]: b for b in benchmarks}
    mech_map = {m["id"]: m for m in (mechanisms or [])} or None
    puzzle_ids = [p["id"] for p in (puzzles or [])] or None
    try:
        return compute_verdicts(frameworks, bench_map, mech_map, puzzle_ids)
    except Exception as e:  # pragma: no cover
        print(f"warning: scoring raised: {e}", file=sys.stderr)
        return None


def fruchterman_reingold(
    nodes: list[str],
    edges: list[tuple[str, str]],
    *,
    iterations: int = 200,
    seed: int = 1729,
    width: float = 2.0,
) -> dict[str, list[float]]:
    """Compute a Fruchterman-Reingold spring layout for a small graph.

    Pure Python, no deps. ~200 nodes converges in <1s. Returns
    {node_id: [x, y]} with coordinates roughly in [-width/2, width/2].
    """
    rng = random.Random(seed)
    n = len(nodes)
    if n == 0:
        return {}
    pos = {v: [rng.uniform(-width / 2, width / 2),
               rng.uniform(-width / 2, width / 2)] for v in nodes}
    if not edges:
        return pos

    area = width * width
    k = math.sqrt(area / n)  # natural edge length
    t = width / 4.0          # initial temperature (max displacement)
    cooling = t / iterations

    for _ in range(iterations):
        disp = {v: [0.0, 0.0] for v in nodes}

        # repulsive forces — O(n^2). For n <= 200 this is fine.
        keys = nodes
        for i in range(n):
            vi = keys[i]
            pxi, pyi = pos[vi]
            for j in range(i + 1, n):
                vj = keys[j]
                dx = pxi - pos[vj][0]
                dy = pyi - pos[vj][1]
                d2 = dx * dx + dy * dy
                if d2 < 1e-6:
                    dx, dy = rng.uniform(-0.01, 0.01), rng.uniform(-0.01, 0.01)
                    d2 = dx * dx + dy * dy + 1e-6
                d = math.sqrt(d2)
                f = (k * k) / d
                ux, uy = dx / d, dy / d
                disp[vi][0] += ux * f
                disp[vi][1] += uy * f
                disp[vj][0] -= ux * f
                disp[vj][1] -= uy * f

        # attractive forces along edges
        for u, v in edges:
            if u not in pos or v not in pos:
                continue
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            d = math.sqrt(dx * dx + dy * dy) + 1e-9
            f = (d * d) / k
            ux, uy = dx / d, dy / d
            disp[u][0] -= ux * f
            disp[u][1] -= uy * f
            disp[v][0] += ux * f
            disp[v][1] += uy * f

        # apply, cooled and clamped to the frame
        for v in nodes:
            dx, dy = disp[v]
            d = math.sqrt(dx * dx + dy * dy) + 1e-9
            step = min(d, t)
            pos[v][0] += (dx / d) * step
            pos[v][1] += (dy / d) * step
            half = width / 2
            pos[v][0] = max(-half, min(half, pos[v][0]))
            pos[v][1] = max(-half, min(half, pos[v][1]))

        t = max(t - cooling, cooling)

    return pos


def derive_alignment(puzzles: list[dict], mechanisms: list[dict]) -> dict:
    """Build the bipartite-graph payload consumed by the alignment view."""
    puzzle_index = {p["id"]: i for i, p in enumerate(puzzles)}
    edges = []
    closing_per_puzzle: dict[str, int] = {pid: 0 for pid in puzzle_index}
    for mech in mechanisms:
        closed = 0
        for edge in mech.get("addresses_puzzles", []) or []:
            pid = edge.get("puzzle_id")
            role = edge.get("role")
            if pid in puzzle_index:
                edges.append({
                    "mechanism_id": mech["id"],
                    "puzzle_id": pid,
                    "role": role,
                    "confidence": edge.get("confidence"),
                    "note": edge.get("note", ""),
                })
                if role in CLOSING_ROLES:
                    closing_per_puzzle[pid] += 1
            if role in CLOSING_ROLES:
                closed += 1
        params = int((mech.get("introduces") or {}).get("new_parameters_count", 1) or 1)
        mech["_puzzles_closed"] = closed
        mech["_puzzles_addressed"] = len(mech.get("addresses_puzzles", []) or [])
        mech["_params"] = params
        mech["_compression"] = closed / max(params, 1)

    # per-puzzle convergence count and closure fraction
    convergence = {pid: 0 for pid in puzzle_index}
    for e in edges:
        convergence[e["puzzle_id"]] += 1
    for p in puzzles:
        total = convergence.get(p["id"], 0)
        closing = closing_per_puzzle.get(p["id"], 0)
        p["_mechanisms_addressing"] = total
        p["_mechanisms_closing"] = closing
        p["_closure_fraction"] = (closing / total) if total > 0 else 0.0

    # Spring layout for the bipartite network. Node keys are namespaced so
    # the JS can tell puzzle nodes from mechanism nodes by prefix.
    node_ids = [f"puzzle:{p['id']}" for p in puzzles] + \
               [f"mechanism:{m['id']}" for m in mechanisms]
    layout_edges = [
        (f"mechanism:{e['mechanism_id']}", f"puzzle:{e['puzzle_id']}")
        for e in edges
    ]
    layout_iters = 200
    layout_seed = 1729
    positions = fruchterman_reingold(
        node_ids, layout_edges, iterations=layout_iters, seed=layout_seed
    )

    return {
        "edges": edges,
        "positions": positions,
        "layout_meta": {
            "algorithm": "fruchterman_reingold",
            "iterations": layout_iters,
            "seed": layout_seed,
        },
    }


def main() -> int:
    tensions = [derive_tension(e) for e in load_dir(DATA_DIR)]
    benchmarks = [derive_benchmark(e) for e in load_dir(BENCH_DIR)]
    puzzles = load_dir(PUZZLE_DIR) if PUZZLE_DIR.exists() else []
    mechanisms = load_dir(MECH_DIR) if MECH_DIR.exists() else []
    alignment = derive_alignment(puzzles, mechanisms)

    domains_tension = sorted({e.get("domain") for e in tensions if e.get("domain")})
    domains_bench_kinds = sorted({e.get("kind") for e in benchmarks if e.get("kind")})
    evaluator_statuses = sorted(
        {e["_evaluator_status"] for e in benchmarks if e.get("_evaluator_status")}
    )
    statuses = sorted({e.get("status") for e in tensions if e.get("status")})

    evaluation = compute_evaluation(benchmarks, mechanisms, puzzles)
    verdict_statuses = sorted(
        {v["status"] for v in (evaluation or {}).get("verdicts", [])}
    )

    used_categories = sorted(
        {b["_category"] for b in benchmarks if b.get("_category")},
        key=lambda c: (CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else 999, c),
    )

    bundle = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {
            "tensions": len(tensions),
            "benchmarks": len(benchmarks),
            "frameworks": len((evaluation or {}).get("frameworks", [])),
            "puzzles": len(puzzles),
            "mechanisms": len(mechanisms),
        },
        "facets": {
            "tension_domains": domains_tension,
            "tension_statuses": statuses,
            "benchmark_kinds": domains_bench_kinds,
            "benchmark_evaluator_statuses": evaluator_statuses,
            "verdict_statuses": verdict_statuses,
            "benchmark_categories": used_categories,
            "category_labels": {c: CATEGORY_LABEL[c] for c in used_categories},
        },
        "tensions": tensions,
        "benchmarks": benchmarks,
        "evaluation": evaluation,
        "puzzles": puzzles,
        "mechanisms": mechanisms,
        "alignment": alignment,
    }

    OUT_DIR.mkdir(exist_ok=True)
    with OUT_FILE.open("w") as f:
        json.dump(bundle, f, indent=2, sort_keys=False)
    n_fw = bundle["counts"]["frameworks"]
    n_verdicts = len((evaluation or {}).get("verdicts", []))
    print(
        f"wrote {OUT_FILE.relative_to(ROOT)}: "
        f"{len(tensions)} tensions, {len(benchmarks)} benchmarks, "
        f"{n_fw} frameworks ({n_verdicts} verdicts), "
        f"{len(puzzles)} puzzles, {len(mechanisms)} mechanisms, "
        f"{len(alignment['edges'])} alignment edges"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
