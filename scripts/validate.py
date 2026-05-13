#!/usr/bin/env python3
"""Validate every JSON file under data/ against schema/anomaly.schema.json.

Usage:
    python scripts/validate.py
    python scripts/validate.py data/muon_g_minus_2.json   # specific files
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.stderr.write(
        "jsonschema is required. Install with: pip install jsonschema\n"
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent

DATASETS = [
    {
        "name": "data",
        "dir": ROOT / "data",
        "schema": ROOT / "schema" / "anomaly.schema.json",
    },
    {
        "name": "benchmarks",
        "dir": ROOT / "benchmarks",
        "schema": ROOT / "schema" / "benchmark.schema.json",
    },
    {
        "name": "frameworks",
        "dir": ROOT / "frameworks",
        "schema": ROOT / "schema" / "framework.schema.json",
    },
    {
        "name": "puzzles",
        "dir": ROOT / "puzzles",
        "schema": ROOT / "schema" / "puzzle.schema.json",
    },
    {
        "name": "mechanisms",
        "dir": ROOT / "mechanisms",
        "schema": ROOT / "schema" / "mechanism.schema.json",
    },
    {
        "name": "search_spaces",
        "dir": ROOT / "search_spaces",
        "schema": ROOT / "schema" / "search_space.schema.json",
    },
]


def load_validator(schema_path: Path) -> Draft202012Validator:
    with schema_path.open() as f:
        schema = json.load(f)
    return Draft202012Validator(schema)


def validate_file(validator: Draft202012Validator, path: Path) -> list[str]:
    try:
        with path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]

    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    msgs = []
    for err in errors:
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        msgs.append(f"{loc}: {err.message}")

    if data.get("id") != path.stem:
        msgs.append(
            f"id mismatch: file is {path.name} but id field is {data.get('id')!r}"
        )

    return msgs


def cross_check_tension_links() -> list[str]:
    """Verify every tension_links id in benchmarks/ resolves to a data/ entry."""
    data_ids = {p.stem for p in (ROOT / "data").glob("*.json")}
    msgs = []
    for path in (ROOT / "benchmarks").glob("*.json"):
        try:
            with path.open() as f:
                entry = json.load(f)
        except json.JSONDecodeError:
            continue
        for ref in entry.get("tension_links", []):
            if ref not in data_ids:
                msgs.append(
                    f"{path.relative_to(ROOT)}: tension_links references "
                    f"unknown data entry {ref!r}"
                )
    return msgs


def cross_check_framework_predictions() -> list[str]:
    """Verify framework prediction keys resolve to benchmarks and composes_mechanisms resolve to mechanisms."""
    fw_dir = ROOT / "frameworks"
    if not fw_dir.exists():
        return []
    bench_ids = {p.stem for p in (ROOT / "benchmarks").glob("*.json")}
    mech_dir = ROOT / "mechanisms"
    mech_ids = {p.stem for p in mech_dir.glob("*.json")} if mech_dir.exists() else set()
    msgs = []
    for path in fw_dir.glob("*.json"):
        try:
            with path.open() as f:
                entry = json.load(f)
        except json.JSONDecodeError:
            continue
        rel = path.relative_to(ROOT)
        for ref in entry.get("predictions", {}):
            if ref not in bench_ids:
                msgs.append(f"{rel}: predictions references unknown benchmark {ref!r}")
        for ref in entry.get("composes_mechanisms", []):
            if ref not in mech_ids:
                msgs.append(f"{rel}: composes_mechanisms references unknown mechanism {ref!r}")
    return msgs


def _ids_in(dir_name: str) -> set[str]:
    return {p.stem for p in (ROOT / dir_name).glob("*.json")}


def cross_check_puzzle_links() -> list[str]:
    """Verify puzzle.data_links/benchmark_links resolve."""
    puz_dir = ROOT / "puzzles"
    if not puz_dir.exists():
        return []
    data_ids = _ids_in("data")
    bench_ids = _ids_in("benchmarks")
    msgs = []
    for path in puz_dir.glob("*.json"):
        try:
            with path.open() as f:
                entry = json.load(f)
        except json.JSONDecodeError:
            continue
        rel = path.relative_to(ROOT)
        for ref in entry.get("data_links", []):
            if ref not in data_ids:
                msgs.append(f"{rel}: data_links references unknown data entry {ref!r}")
        for ref in entry.get("benchmark_links", []):
            if ref not in bench_ids:
                msgs.append(f"{rel}: benchmark_links references unknown benchmark {ref!r}")
    return msgs


def cross_check_mechanism_links() -> list[str]:
    """Verify mechanism edges resolve."""
    mech_dir = ROOT / "mechanisms"
    if not mech_dir.exists():
        return []
    puzzle_ids = _ids_in("puzzles")
    bench_ids = _ids_in("benchmarks")
    mech_ids = _ids_in("mechanisms")
    msgs = []
    for path in mech_dir.glob("*.json"):
        try:
            with path.open() as f:
                entry = json.load(f)
        except json.JSONDecodeError:
            continue
        rel = path.relative_to(ROOT)
        for edge in entry.get("addresses_puzzles", []):
            ref = edge.get("puzzle_id")
            if ref and ref not in puzzle_ids:
                msgs.append(f"{rel}: addresses_puzzles references unknown puzzle {ref!r}")
        for edge in entry.get("touches_benchmarks", []):
            ref = edge.get("benchmark_id")
            if ref and ref not in bench_ids:
                msgs.append(f"{rel}: touches_benchmarks references unknown benchmark {ref!r}")
        for ref in entry.get("composes_with", []):
            if ref not in mech_ids:
                msgs.append(f"{rel}: composes_with references unknown mechanism {ref!r}")
        for ref in entry.get("excludes", []):
            if ref not in mech_ids:
                msgs.append(f"{rel}: excludes references unknown mechanism {ref!r}")
    return msgs


def cross_check_data_mechanism_links() -> list[str]:
    """Verify data.mechanism_links/puzzle_links resolve."""
    data_dir = ROOT / "data"
    if not data_dir.exists():
        return []
    mech_ids = _ids_in("mechanisms")
    puzzle_ids = _ids_in("puzzles")
    msgs = []
    for path in data_dir.glob("*.json"):
        try:
            with path.open() as f:
                entry = json.load(f)
        except json.JSONDecodeError:
            continue
        rel = path.relative_to(ROOT)
        for ref in entry.get("mechanism_links", []):
            if ref not in mech_ids:
                msgs.append(f"{rel}: mechanism_links references unknown mechanism {ref!r}")
        for ref in entry.get("puzzle_links", []):
            if ref not in puzzle_ids:
                msgs.append(f"{rel}: puzzle_links references unknown puzzle {ref!r}")
    return msgs


def main(argv: list[str]) -> int:
    explicit_targets = [Path(p) for p in argv[1:]]
    fail = 0
    total = 0

    for ds in DATASETS:
        validator = load_validator(ds["schema"])
        if explicit_targets:
            targets = [
                p for p in explicit_targets if p.resolve().is_relative_to(ds["dir"])
            ]
        else:
            targets = sorted(ds["dir"].glob("*.json"))

        if not targets:
            continue

        print(f"== {ds['name']} ==")
        for path in targets:
            errs = validate_file(validator, path)
            total += 1
            if errs:
                fail += 1
                print(f"FAIL {path.relative_to(ROOT)}")
                for e in errs:
                    print(f"  - {e}")
            else:
                print(f"ok   {path.relative_to(ROOT)}")
        print()

    cross_errs = (
        cross_check_tension_links()
        + cross_check_framework_predictions()
        + cross_check_puzzle_links()
        + cross_check_mechanism_links()
        + cross_check_data_mechanism_links()
    )
    if cross_errs:
        print("== cross-references ==")
        for e in cross_errs:
            print(f"FAIL {e}")
        fail += len(cross_errs)
        print()

    if fail:
        print(f"{fail} problem(s) across {total} file(s)")
        return 1
    print(f"all {total} file(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
