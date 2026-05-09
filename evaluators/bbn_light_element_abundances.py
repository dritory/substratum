"""Evaluator for bbn_light_element_abundances.

Measurements (Fields, Olive, Yeh, Young, JCAP 03, 010 (2020),
arXiv:1912.01132 'Big-Bang Nucleosynthesis after Planck'):
    D/H = (2.527 +/- 0.030) x 10^-5
    Y_p = 0.245 +/- 0.003

A framework that runs SM BBN with the Planck-determined baryon-to-
photon ratio and N_eff = 3.044 reproduces both abundances within
~1 sigma; the well-known lithium-7 problem is captured separately in
the lithium_problem_bbn benchmark and is NOT folded into this check.

Framework prediction shape:
    "value": {"D_H": ..., "Y_p": ...}
where D_H is the deuterium-to-hydrogen ratio (e.g. 2.527e-5).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _clip, _dispatch_non_value


D_H_MEASURED = 2.527e-5
D_H_SIGMA = 0.030e-5
YP_MEASURED = 0.245
YP_SIGMA = 0.003
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
            note="prediction.value must be {D_H, Y_p}",
        )
    d_h = raw.get("D_H")
    y_p = raw.get("Y_p")
    if not isinstance(d_h, (int, float)) or not isinstance(y_p, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric D_H and Y_p",
        )

    pull_d = (float(d_h) - D_H_MEASURED) / D_H_SIGMA
    pull_y = (float(y_p) - YP_MEASURED) / YP_SIGMA
    pull_max = max(abs(pull_d), abs(pull_y))
    score = _clip(1.0 - pull_max / SIGMA_THRESHOLD)
    detail = (
        f"D/H pull = {pull_d:+.2f}; Y_p pull = {pull_y:+.2f} (vs Fields 2020)"
    )
    if pull_max > SIGMA_THRESHOLD:
        return Verdict(status="fail", score=score, note=f"{detail} > {SIGMA_THRESHOLD} sigma")
    return Verdict(status="pass", score=score, note=f"{detail} (within {SIGMA_THRESHOLD} sigma)")
