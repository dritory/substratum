"""Evaluator for axion_haloscope_admx.

Bound: g_a_gamma_gamma (axion-photon coupling, GeV^-1) is excluded above
- ADMX:  g_a_gamma_gamma < ~3e-16 GeV^-1 for m_a in [2.66, 4.2] microeV
- CAST:  g_a_gamma_gamma < 6.6e-11 GeV^-1 for m_a < 0.02 eV
We encode a coarse two-region bound. Outside both ranges we report
'open' (the haloscope-vs-helioscope coverage gap).

Framework prediction shape:
    {"value": {"mass_ev": ..., "g_a_gamma_gamma_inv_gev": ...}, ...}
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _dispatch_non_value


ADMX_RANGE_EV = (2.66e-6, 4.2e-6)
ADMX_LIMIT = 3e-16        # GeV^-1
CAST_UPPER_EV = 0.02
CAST_LIMIT = 6.6e-11      # GeV^-1


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    raw = prediction.get("value")
    if not isinstance(raw, dict):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must be {mass_ev, g_a_gamma_gamma_inv_gev}",
        )
    m = raw.get("mass_ev")
    g = raw.get("g_a_gamma_gamma_inv_gev")
    if not isinstance(m, (int, float)) or not isinstance(g, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric mass_ev and g_a_gamma_gamma_inv_gev",
        )

    m = float(m)
    g = float(g)
    if m <= 0 or g < 0:
        return Verdict(status="open", score=None, note="mass_ev must be > 0, coupling >= 0")

    if ADMX_RANGE_EV[0] <= m <= ADMX_RANGE_EV[1]:
        if g > ADMX_LIMIT:
            return Verdict(
                status="fail",
                score=None,
                note=f"g = {g:.2g} GeV^-1 above ADMX limit {ADMX_LIMIT:.2g} GeV^-1 at m = {m:.2g} eV",
            )
        return Verdict(
            status="pass",
            score=None,
            note=f"g = {g:.2g} GeV^-1 below ADMX limit at m = {m:.2g} eV",
        )

    if m <= CAST_UPPER_EV:
        if g > CAST_LIMIT:
            return Verdict(
                status="fail",
                score=None,
                note=f"g = {g:.2g} GeV^-1 above CAST limit {CAST_LIMIT:.2g} GeV^-1 at m = {m:.2g} eV",
            )
        return Verdict(
            status="pass",
            score=None,
            note=f"g = {g:.2g} GeV^-1 below CAST limit at m = {m:.2g} eV",
        )

    return Verdict(
        status="open",
        score=None,
        note=f"m = {m:.2g} eV outside encoded coverage (ADMX or CAST range)",
    )
