"""Evaluator for muon_to_electron_gamma_meg.

Bound: Br(mu+ -> e+ gamma) < 4.2e-13 at 90% CL.
Source: Baldini et al. (MEG Collaboration at PSI), 'Search for the
lepton flavour violating decay mu+ -> e+ gamma with the full dataset
of the MEG experiment', EPJC 76, 434 (2016), arXiv:1605.05081.
The abstract states: "BR(mu+ -> e+ gamma) < 4.2 x 10^-13
(90% confidence level)".

This is a forbidden-phenomenon benchmark: the SM predicts BR ~ 10^-54
via neutrino-mediated penguin diagrams, far below any conceivable
experimental sensitivity. Any framework predicting BR above 4.2e-13
is excluded.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 4.2e-13  # branching ratio, 90% CL upper limit


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="branching ratio",
        what="Br(mu+ -> e+ gamma)",
    )
