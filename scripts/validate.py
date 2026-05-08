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
    """Verify every prediction key in frameworks/ resolves to a benchmark."""
    fw_dir = ROOT / "frameworks"
    if not fw_dir.exists():
        return []
    bench_ids = {p.stem for p in (ROOT / "benchmarks").glob("*.json")}
    msgs = []
    for path in fw_dir.glob("*.json"):
        try:
            with path.open() as f:
                entry = json.load(f)
        except json.JSONDecodeError:
            continue
        for ref in entry.get("predictions", {}):
            if ref not in bench_ids:
                msgs.append(
                    f"{path.relative_to(ROOT)}: predictions references "
                    f"unknown benchmark {ref!r}"
                )
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

    cross_errs = cross_check_tension_links() + cross_check_framework_predictions()
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
