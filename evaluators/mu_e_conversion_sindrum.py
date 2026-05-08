"""Evaluator for mu_e_conversion_sindrum.

Bound: R(mu Au -> e Au) < 7e-13 at 90% CL.
Source: Bertl et al. (SINDRUM II Collaboration at PSI), 'A search for
muon to electron conversion in muonic gold', EPJC 47, 337 (2006),
DOI 10.1140/epjc/s2006-02582-x. The conversion ratio is defined as
    R = Gamma(mu^- Au -> e^- Au_g.s.) / Gamma_capture(mu^- Au).

This is a forbidden-phenomenon benchmark: the SM predicts R ~ 10^-54.
Any framework predicting R above 7e-13 in muonic gold is excluded.
Mu2e (Fermilab) and COMET (J-PARC) target ~10^-17 sensitivity in
aluminum, so this bound will tighten by ~4-5 orders of magnitude
within the next decade; frameworks that predict R just below the
current SINDRUM bound are within Mu2e/COMET reach.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 7e-13  # conversion ratio R(mu Au -> e Au), 90% CL upper limit


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="conversion ratio",
        what="R(mu^- Au -> e^- Au)",
    )
