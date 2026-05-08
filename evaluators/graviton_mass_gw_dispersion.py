"""Evaluator for graviton_mass_gw_dispersion.

Bound: m_g <= 1.27e-23 eV/c^2 (LIGO-Virgo-KAGRA GWTC-3 dispersion fit, 90% CL).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 1.27e-23  # eV


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="eV",
        what="m_g (graviton mass)",
    )
