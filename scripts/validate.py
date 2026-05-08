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
SCHEMA_PATH = ROOT / "schema" / "anomaly.schema.json"
DATA_DIR = ROOT / "data"


def load_schema() -> Draft202012Validator:
    with SCHEMA_PATH.open() as f:
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


def main(argv: list[str]) -> int:
    validator = load_schema()
    if len(argv) > 1:
        targets = [Path(p) for p in argv[1:]]
    else:
        targets = sorted(DATA_DIR.glob("*.json"))

    if not targets:
        print("no data files found")
        return 0

    fail = 0
    for path in targets:
        errs = validate_file(validator, path)
        if errs:
            fail += 1
            print(f"FAIL {path.relative_to(ROOT)}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"ok   {path.relative_to(ROOT)}")

    if fail:
        print(f"\n{fail} file(s) failed validation")
        return 1
    print(f"\nall {len(targets)} file(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
