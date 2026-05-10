"""Evaluator for electroweak_oblique_s_t_u.

Measurements (Particle Data Group 2024 Electroweak Review constrained
fit, with U fixed-vs-floating treatment standard):
    S = -0.05 +/- 0.07
    T =  0.00 +/- 0.06
    U =  0.00 +/- 0.05

Source: Particle Data Group, 'Review of Particle Physics' 2024,
Electroweak Review section.

The SM (with reference Higgs and top masses) gives (S, T, U) = (0, 0, 0)
by construction. A framework predicting BSM oblique corrections must
supply all three; the evaluator computes pulls and requires the worst
to be within sigma_threshold.

Framework prediction shape:
    "value": {"S": ..., "T": ..., "U": ...}
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _clip, _dispatch_non_value


S_MEASURED, S_SIGMA = -0.05, 0.07
T_MEASURED, T_SIGMA = 0.00, 0.06
U_MEASURED, U_SIGMA = 0.00, 0.05
SIGMA_THRESHOLD = 3.0


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    raw = prediction.get("value")
    if not isinstance(raw, dict):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must be {S, T, U}",
        )
    S = raw.get("S")
    T = raw.get("T")
    U = raw.get("U")
    if not all(isinstance(x, (int, float)) for x in (S, T, U)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric S, T, U",
        )

    pulls = {
        "S": (float(S) - S_MEASURED) / S_SIGMA,
        "T": (float(T) - T_MEASURED) / T_SIGMA,
        "U": (float(U) - U_MEASURED) / U_SIGMA,
    }
    pull_max = max(abs(p) for p in pulls.values())
    score = _clip(1.0 - pull_max / SIGMA_THRESHOLD)
    detail = "; ".join(f"{k} pull = {v:+.2f}" for k, v in pulls.items())
    if pull_max > SIGMA_THRESHOLD:
        return Verdict(status="fail", score=score, note=f"{detail} > {SIGMA_THRESHOLD} sigma")
    return Verdict(status="pass", score=score, note=f"{detail} (within {SIGMA_THRESHOLD} sigma)")
