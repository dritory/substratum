"""Evaluator for alpha_variation_atomic_clocks.

Bound: |alpha_dot / alpha| <= 2e-18 / yr (Lange et al. 2021, Yb+ E3/E2).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 2e-18  # 1/yr


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="1/yr",
        what="alpha_dot / alpha",
    )
