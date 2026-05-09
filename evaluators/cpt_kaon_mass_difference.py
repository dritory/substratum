"""Evaluator for cpt_kaon_mass_difference.

Bound: |m_{K^0} - m_{K^0_bar}| < 4.8 x 10^-19 GeV at 95% CL.
Source: Particle Data Group, 'Review of Particle Physics', Prog.
Theor. Exp. Phys. 2024, 083C01 (2024), derived from CPLEAR + KLOE
semileptonic-asymmetry analyses assuming CPT violation enters via the
mass matrix only. CPLEAR Collaboration, Angelopoulos et al., 'T-
violation and CPT-tests in neutral-kaon decays', PLB 444, 52 (1998).

A framework that respects CPT symmetry predicts |Delta m| = 0 exactly.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT_GEV = 4.8e-19  # GeV, 95% CL upper limit on |m_K0 - m_K0bar|


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT_GEV,
        units="GeV",
        what="m_K0 - m_K0bar",
    )
