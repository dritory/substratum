"""Evaluator for electron_edm_jila.

Bound: |d_e| < 4.1e-30 e cm at 90% CL.
Source: Roussy et al. (JILA HfF+ ion trap), 'An improved bound on the
electron's electric dipole moment', Science 381, 6653 (2023),
arXiv:2212.11841. The benchmark's current_bound.value field reports
4.1e-30 e cm, which matches the abstract directly.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 4.1e-30  # e cm, 90% CL upper limit


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="e cm",
        what="d_e (electron EDM)",
    )
