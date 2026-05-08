"""Evaluator for katrin_neutrino_mass.

Bound: m_nu_e <= 0.45 eV/c^2 (KATRIN 2024, 90% CL).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 0.45  # eV


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="eV",
        what="m_nu_e (effective electron-neutrino mass)",
    )
