"""Evaluator for nordtvedt_parameter_strong_ep.

Bound: |eta_N| < ~2 x 10^-5 at 95% CL (strong-field, dominant), derived
from the PSR J0337+1715 fractional-acceleration measurement Delta_acc
= (+0.5 +/- 1.8) x 10^-6 (Voisin et al. 2020, A&A 638, A24,
arXiv:2005.01388) and the difference in gravitational binding-energy
fraction (E_grav/Mc^2) ~ 0.15 between the neutron star and the inner
white dwarf.

The weak-field LLR bound is |eta_N| < 4.4 x 10^-4 (Williams, Turyshev,
Boggs, CQG 29, 184004 (2012), arXiv:1203.2150). The PSR result is
~20x tighter and dominates here.

A framework that satisfies the strong equivalence principle predicts
eta_N = 0 by construction.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 2e-5  # |eta_N|, 95% CL upper limit (PSR J0337+1715 strong-field)


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="dimensionless",
        what="eta_N (Nordtvedt parameter)",
    )
