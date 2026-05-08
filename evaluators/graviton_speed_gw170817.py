"""Evaluator for graviton_speed_gw170817.

Bound (LVC + Fermi-GBM + INTEGRAL, 2017): -3e-15 < (c_gw - c)/c < 7e-16.
A framework passes if its predicted fractional speed deviation lies
inside that interval (allowing one sigma of theoretical uncertainty).
"""
from __future__ import annotations

from typing import Any

from . import Verdict


LOWER = -3e-15
UPPER = 7e-16


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    kind = prediction.get("kind")

    if kind == "by_construction":
        return Verdict(
            status="pass",
            score=None,
            note="framework predicts c_gw = c by structural identity",
        )
    if kind == "not_applicable":
        return Verdict(
            status="inapplicable",
            score=None,
            note=prediction.get("note", "framework declares this benchmark out of scope"),
        )
    if kind == "open":
        return Verdict(
            status="open",
            score=None,
            note="framework has not yet supplied a prediction",
        )
    if kind != "value":
        return Verdict(
            status="open",
            score=None,
            note=f"unrecognized prediction kind {kind!r}",
        )

    raw = prediction.get("value")
    if not isinstance(raw, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note=f"prediction value must be numeric for this evaluator, got {type(raw).__name__}",
        )

    delta = float(raw)
    sigma = prediction.get("uncertainty")
    sigma = float(sigma) if isinstance(sigma, (int, float)) else 0.0

    margin = max(UPPER - delta, delta - LOWER)
    width = UPPER - LOWER
    score = margin / width if width else None

    if (delta - sigma) < LOWER or (delta + sigma) > UPPER:
        return Verdict(
            status="fail",
            score=score,
            note=(
                f"predicted (c_gw - c)/c = {delta:+.2e}"
                f"{f' +/- {sigma:.2e}' if sigma else ''}"
                f" outside bound [{LOWER:+.2e}, {UPPER:+.2e}]"
            ),
        )
    return Verdict(
        status="pass",
        score=score,
        note=(
            f"predicted (c_gw - c)/c = {delta:+.2e}"
            f"{f' +/- {sigma:.2e}' if sigma else ''}"
            f" inside bound [{LOWER:+.2e}, {UPPER:+.2e}]"
        ),
    )
