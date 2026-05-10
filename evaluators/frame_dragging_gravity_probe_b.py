"""Evaluator for frame_dragging_gravity_probe_b.

Measurements (Everitt et al. 2011, Gravity Probe B):
    Geodetic precession:   -6601.8 +/- 18.3 mas/yr  (GR predicts -6606.1)
    Frame-dragging (LT):     -37.2 +/-  7.2 mas/yr  (GR predicts  -39.2)

Source: Everitt et al., 'Gravity Probe B: Final Results of a Space
Experiment to Test General Relativity', PRL 106, 221101 (2011),
arXiv:1105.3456.

A framework predicts both precession rates (in mas/yr) and the
evaluator computes a pull for each, requiring both to be within
sigma_threshold sigma of the measured values. The framework should
supply
    "value": {"geodetic_mas_yr": ..., "lense_thirring_mas_yr": ...}
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _clip, _dispatch_non_value


GEODETIC_MEASURED = -6601.8
GEODETIC_SIGMA = 18.3
LT_MEASURED = -37.2
LT_SIGMA = 7.2
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
            note="prediction.value must be {geodetic_mas_yr, lense_thirring_mas_yr}",
        )
    geo = raw.get("geodetic_mas_yr")
    lt = raw.get("lense_thirring_mas_yr")
    if not isinstance(geo, (int, float)) or not isinstance(lt, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric geodetic_mas_yr and lense_thirring_mas_yr",
        )

    pull_geo = (float(geo) - GEODETIC_MEASURED) / GEODETIC_SIGMA
    pull_lt = (float(lt) - LT_MEASURED) / LT_SIGMA
    pull_max = max(abs(pull_geo), abs(pull_lt))
    score = _clip(1.0 - pull_max / SIGMA_THRESHOLD)

    detail = (
        f"geodetic = {geo:.1f} (pull {pull_geo:+.2f}); "
        f"LT = {lt:.1f} (pull {pull_lt:+.2f}); both vs Everitt 2011"
    )
    if pull_max > SIGMA_THRESHOLD:
        return Verdict(status="fail", score=score, note=f"{detail} > {SIGMA_THRESHOLD} sigma")
    return Verdict(status="pass", score=score, note=f"{detail} (within {SIGMA_THRESHOLD} sigma)")
