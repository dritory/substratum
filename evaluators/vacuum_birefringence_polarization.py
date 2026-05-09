"""Evaluator for vacuum_birefringence_polarization.

Bound: |k_AF^kappa| < ~10^-42 GeV (canonical Carroll-Field-Jackiw 1990
bound from radio-galaxy polarization). Individual sky-direction-
projected components in the Kostelecky-Russell SME data tables reach
10^-43 GeV; we take the more conservative norm-bound here.

Sources:
- Carroll, Field, Jackiw, 'Limits on a Lorentz and parity violating
  modification of electrodynamics', PRD 41, 1231 (1990).
- Kostelecky and Mewes, 'Sensitive Polarimetric Search for Relativity
  Violations in Gamma-Ray Bursts', PRL 97, 140401 (2006),
  arXiv:hep-ph/0607084.
- Kostelecky and Russell, 'Data Tables for Lorentz and CPT Violation',
  RMP 83, 11 (2011), updated annually at arXiv:0801.0287.

A framework that respects Lorentz invariance in the photon sector
predicts k_AF = 0 by construction. Frameworks predicting CPT-odd
photon couplings must report the magnitude of the dominant component
to be checked against this bound.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT_GEV = 1e-42  # GeV, conservative norm-bound on |k_AF^kappa|


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT_GEV,
        units="GeV",
        what="k_AF (SME photon CPT-odd coefficient)",
    )
