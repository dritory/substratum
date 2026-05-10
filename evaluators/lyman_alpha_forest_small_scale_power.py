"""Evaluator for lyman_alpha_forest_small_scale_power.

Bound: thermal-relic-equivalent warm dark matter mass m_WDM > 5.3 keV
at 95% CL.
Source: Irsic et al., 'New Constraints on the free-streaming of warm
dark matter from intermediate and small scale Lyman-alpha forest data',
PRD 96, 023522 (2017), arXiv:1702.01764.

A framework that produces fully cold dark matter (no free-streaming
suppression of small-scale power) passes by_construction. A framework
predicting WDM with a finite thermal-relic-equivalent mass must report
that mass; the bound is one-sided (lower limit on the WDM mass).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import lower_limit_on_value


LIMIT_KEV = 5.3  # keV, 95% CL lower limit on thermal-relic-equivalent m_WDM


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return lower_limit_on_value(
        prediction,
        limit=LIMIT_KEV,
        units="keV",
        what="m_WDM (thermal-relic-equivalent warm DM mass)",
    )
