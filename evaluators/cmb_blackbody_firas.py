"""Evaluator for cmb_blackbody_firas.

Bounds (COBE/FIRAS, Fixsen et al. 1996, ApJ 473, 576, arXiv:astro-
ph/9605054):
    |mu| < 9e-5  (95% CL)  - chemical-potential distortion
    |y|  < 1.5e-5 (95% CL) - Comptonization (Sunyaev-Zel'dovich)
                              distortion
Both must be satisfied simultaneously; failing either is a fail.

Framework prediction shape:
    {"value": {"mu": ..., "y": ...}, ...}
or by_construction (any framework that reproduces a thermal CMB with
SM/LambdaCDM matter and radiation passes both at the FIRAS level: the
expected SM y ~ 10^-6 and mu ~ 10^-8 are below the bounds, with the
SM expectation marginal for y at PIXIE-class future sensitivities).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _dispatch_non_value


MU_LIMIT = 9e-5
Y_LIMIT = 1.5e-5


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    raw = prediction.get("value")
    if not isinstance(raw, dict):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must be {mu, y} for this evaluator",
        )
    mu = raw.get("mu")
    y = raw.get("y")
    if not isinstance(mu, (int, float)) or not isinstance(y, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric mu and y",
        )

    mu = float(mu)
    y = float(y)

    if abs(mu) > MU_LIMIT and abs(y) > Y_LIMIT:
        return Verdict(
            status="fail",
            score=-1.0,
            note=(
                f"|mu| = {abs(mu):.2g} > {MU_LIMIT:.2g} AND "
                f"|y| = {abs(y):.2g} > {Y_LIMIT:.2g}"
            ),
        )
    if abs(mu) > MU_LIMIT:
        return Verdict(
            status="fail",
            score=-1.0,
            note=f"|mu| = {abs(mu):.2g} exceeds limit {MU_LIMIT:.2g}",
        )
    if abs(y) > Y_LIMIT:
        return Verdict(
            status="fail",
            score=-1.0,
            note=f"|y| = {abs(y):.2g} exceeds limit {Y_LIMIT:.2g}",
        )

    mu_margin = (MU_LIMIT - abs(mu)) / MU_LIMIT
    y_margin = (Y_LIMIT - abs(y)) / Y_LIMIT
    score = min(mu_margin, y_margin)
    return Verdict(
        status="pass",
        score=score,
        note=(
            f"|mu| = {abs(mu):.2g} < {MU_LIMIT:.2g}, "
            f"|y| = {abs(y):.2g} < {Y_LIMIT:.2g}"
        ),
    )
