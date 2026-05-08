"""Evaluator for electron_g_minus_2_precision.

Measurement (Fan et al. 2023, Northwestern Penning trap):
    a_e = 1.15965218059(13) x 10^-3
i.e. central value 1.15965218059e-3, sigma 1.3e-13.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import within_measurement


MEASURED = 1.15965218059e-3
SIGMA = 1.3e-13


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return within_measurement(
        prediction,
        measured=MEASURED,
        sigma_exp=SIGMA,
        units="dimensionless",
        what="a_e",
    )
