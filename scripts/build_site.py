#!/usr/bin/env python3
"""Bundle data/ and benchmarks/ JSON into docs/data.json for the static site.

Produces a single combined JSON with light derived fields (numeric sigma where
parseable, normalized scale entries) so the front-end stays simple. The source
of truth remains the per-entry JSON files; this script is a build step.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
BENCH_DIR = ROOT / "benchmarks"
OUT_DIR = ROOT / "docs"
OUT_FILE = OUT_DIR / "data.json"

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


def derive_benchmark(entry: dict) -> dict:
    regime = entry.get("regime") or {}
    entry["_length_m"] = regime.get("length_m")
    entry["_energy_ev"] = regime.get("energy_ev")
    entry["_evaluator_status"] = (entry.get("procedural") or {}).get("evaluator_status")
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


def main() -> int:
    tensions = [derive_tension(e) for e in load_dir(DATA_DIR)]
    benchmarks = [derive_benchmark(e) for e in load_dir(BENCH_DIR)]

    domains_tension = sorted({e.get("domain") for e in tensions if e.get("domain")})
    domains_bench_kinds = sorted({e.get("kind") for e in benchmarks if e.get("kind")})
    evaluator_statuses = sorted(
        {e["_evaluator_status"] for e in benchmarks if e.get("_evaluator_status")}
    )
    statuses = sorted({e.get("status") for e in tensions if e.get("status")})

    bundle = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {
            "tensions": len(tensions),
            "benchmarks": len(benchmarks),
        },
        "facets": {
            "tension_domains": domains_tension,
            "tension_statuses": statuses,
            "benchmark_kinds": domains_bench_kinds,
            "benchmark_evaluator_statuses": evaluator_statuses,
        },
        "tensions": tensions,
        "benchmarks": benchmarks,
    }

    OUT_DIR.mkdir(exist_ok=True)
    with OUT_FILE.open("w") as f:
        json.dump(bundle, f, indent=2, sort_keys=False)
    print(
        f"wrote {OUT_FILE.relative_to(ROOT)}: "
        f"{len(tensions)} tensions, {len(benchmarks)} benchmarks"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
