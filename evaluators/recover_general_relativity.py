"""Evaluator for recover_general_relativity.

This benchmark covers multiple sub-tests of GR (PPN gamma and beta,
post-Keplerian timing, GW waveform). For the trivial-tier evaluator we
check the most quotable single-number test:

    PPN parameter gamma - 1 = (2.1 +/- 2.3) x 10^-5

Source: Bertotti, Iess, Tortora, 'A test of general relativity using
radio links with the Cassini spacecraft', Nature 425, 374-376 (2003).

GR predicts gamma = 1 exactly, so a framework with kind=value should
supply ppn_gamma directly. Other sub-tests (PPN beta, PPK, GW waveform
deviations) are NOT covered by this evaluator and would each warrant
their own evaluator if more granular distinction is wanted.

Framework prediction shape (kind == 'value'):
    "value": {"ppn_gamma": <float>}, "uncertainty": <float, optional>
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _dispatch_non_value, within_measurement


GAMMA_MEASURED = 1.0 + 2.1e-5  # Cassini central value
GAMMA_SIGMA = 2.3e-5


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    raw = prediction.get("value")
    if isinstance(raw, dict):
        gamma = raw.get("ppn_gamma")
    elif isinstance(raw, (int, float)):
        # Permit a bare float meaning "ppn_gamma".
        gamma = raw
    else:
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must be {ppn_gamma: ...} or a numeric ppn_gamma",
        )

    if not isinstance(gamma, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction must supply numeric ppn_gamma",
        )

    sub = dict(prediction)
    sub["value"] = float(gamma)
    return within_measurement(
        sub,
        measured=GAMMA_MEASURED,
        sigma_exp=GAMMA_SIGMA,
        units="dimensionless",
        what="PPN gamma (Cassini Shapiro delay)",
    )
