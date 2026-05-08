"""Evaluator for sum_neutrino_masses_cosmology.

Bound: Sum m_nu < 0.072 eV at 95% CL (DESI BAO Y1 + Planck + Pantheon+).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 0.072  # eV


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="eV",
        what="Sum m_nu",
    )
