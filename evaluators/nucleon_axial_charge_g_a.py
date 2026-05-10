"""Evaluator for nucleon_axial_charge_g_a.

Measurement (PERKEO III, Markisch et al. 2019):
    lambda = g_A / g_V = -1.27641(45)_stat(33)_sys
i.e. |g_A| = 1.27641 with combined uncertainty
sqrt(0.45^2 + 0.33^2) x 10^-3 = 0.00056.
Source: Markisch et al. (PERKEO III), 'Measurement of the Weak Axial-
Vector Coupling Constant in the Decay of Free Neutrons Using a Pulsed
Cold Neutron Beam', PRL 122, 242501 (2019), arXiv:1812.04666.

The benchmark JSON quotes the slightly looser PDG-average uncertainty
(0.0013) reflecting the world average across PERKEO, UCNA, and other
measurements. We use the PDG-quoted value here for consistency with
the benchmark; PERKEO III tightens this further.

A framework that derives g_A from QCD lattice (CalLat 2018: 1.271 +/-
0.013) supplies value=1.271, uncertainty=0.013; pull is ~0.4 sigma.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import within_measurement


MEASURED = 1.2756
SIGMA = 0.0013


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return within_measurement(
        prediction,
        measured=MEASURED,
        sigma_exp=SIGMA,
        units="dimensionless",
        what="g_A (nucleon axial coupling)",
    )
