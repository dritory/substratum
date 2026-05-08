"""Evaluator for antihydrogen_gravity_alpha_g.

Measurement (ALPHA-g 2023, Anderson et al., Nature 621, 716):
    a_gbar / g = 0.75 +/- 0.21 (stat + syst combined in quadrature)
i.e. central 0.75, sigma 0.21. Equivalence principle / CPT predicts +1.
Antigravity (-1) is excluded at >5 sigma.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import within_measurement


MEASURED = 0.75
SIGMA = 0.21


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return within_measurement(
        prediction,
        measured=MEASURED,
        sigma_exp=SIGMA,
        units="local g",
        what="a_gbar / g",
    )
