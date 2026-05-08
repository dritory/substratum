"""Evaluator for inverse_square_law_short_distance.

Bound (Eot-Wash 2020 + Casimir-regime composite, see also
casimir_force_precision): for the Yukawa parameterization
    V(r) = -G m1 m2 / r [1 + alpha * exp(-r/lambda)]
the (alpha, lambda) plane has alpha < 1 for lambda > 52 micrometers.

Framework prediction shape (kind == 'value'):
    {"value": {"alpha": ..., "lambda_m": ...}, ...}
where alpha is the Yukawa amplitude (dimensionless) and lambda_m
is the range in metres.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _dispatch_non_value


LAMBDA_THRESHOLD_M = 52e-6
ALPHA_LIMIT_AT_THRESHOLD = 1.0


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    raw = prediction.get("value")
    if not isinstance(raw, dict):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must be {alpha, lambda_m} for this evaluator",
        )
    alpha = raw.get("alpha")
    lam = raw.get("lambda_m")
    if not isinstance(alpha, (int, float)) or not isinstance(lam, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric alpha and lambda_m",
        )

    alpha = float(alpha)
    lam = float(lam)

    if lam < LAMBDA_THRESHOLD_M:
        return Verdict(
            status="open",
            score=None,
            note=(
                f"lambda = {lam:.2g} m below 52 micrometer Eot-Wash threshold; "
                f"casimir_force_precision benchmark covers this range"
            ),
        )
    if alpha > ALPHA_LIMIT_AT_THRESHOLD:
        return Verdict(
            status="fail",
            score=None,
            note=f"alpha = {alpha:.3g} exceeds 1.0 at lambda = {lam:.2g} m",
        )
    return Verdict(
        status="pass",
        score=ALPHA_LIMIT_AT_THRESHOLD - alpha,
        note=f"alpha = {alpha:.3g} <= 1.0 at lambda = {lam:.2g} m",
    )
