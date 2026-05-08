"""Evaluator for equivalence_principle_microscope.

Bound (MICROSCOPE final analysis 2022, Touboul et al.):
    |eta| < 1.5e-15 at 1 sigma; |eta| < 4.7e-15 at 95% CL.
We use the 95% CL combined bound 4.7e-15 as the pass/fail threshold to
match the benchmark's stated current_bound.confidence_level.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 4.7e-15  # Eotvos parameter, 95% CL


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="dimensionless",
        what="eta (Eotvos parameter)",
    )
