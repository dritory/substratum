"""Evaluator for dark_photon_kinetic_mixing.

Bound: epsilon (kinetic-mixing parameter) is excluded at varying levels
across (m_A', epsilon) space. We encode a coarse piecewise lower
envelope of the visible + invisible search bounds (BaBar, NA64,
Belle II, beam dumps; sub-MeV cosmological floors not encoded here).

Framework prediction shape:
    {"value": {"mass_ev": ..., "epsilon": ...}, ...}
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import _dispatch_non_value


# Coarse upper-envelope bound on epsilon as a function of m_A' (in eV).
# Each entry is (m_A' eV, max allowed epsilon) defining a piecewise-linear
# (in log-log) bound. Numbers chosen to bracket the published exclusion
# region; serious evaluation should consult DarkCast.
ENVELOPE = [
    (1e-3, 1e-9),    # sub-MeV: cosmology / stellar cooling regimes
    (1e3, 1e-9),     # ~keV: invisible-decay / cooling
    (1e6, 1e-3),     # ~MeV: visible-decay searches loosen
    (1e9, 1e-3),     # ~GeV: BaBar / Belle II / NA64 ~ 1e-3 to 1e-7 depending on channel
]


def _bound_at(mass_ev: float) -> float:
    import math
    if mass_ev <= ENVELOPE[0][0]:
        return ENVELOPE[0][1]
    if mass_ev >= ENVELOPE[-1][0]:
        return ENVELOPE[-1][1]
    for (m_lo, e_lo), (m_hi, e_hi) in zip(ENVELOPE, ENVELOPE[1:]):
        if m_lo <= mass_ev <= m_hi:
            t = (math.log10(mass_ev) - math.log10(m_lo)) / (math.log10(m_hi) - math.log10(m_lo))
            return 10 ** (math.log10(e_lo) + t * (math.log10(e_hi) - math.log10(e_lo)))
    return ENVELOPE[-1][1]


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    raw = prediction.get("value")
    if not isinstance(raw, dict):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must be {mass_ev, epsilon} for this evaluator",
        )
    m = raw.get("mass_ev")
    eps = raw.get("epsilon")
    if not isinstance(m, (int, float)) or not isinstance(eps, (int, float)):
        return Verdict(
            status="open",
            score=None,
            note="prediction.value must supply numeric mass_ev and epsilon",
        )

    m = float(m)
    eps = float(eps)
    if m <= 0 or eps < 0:
        return Verdict(status="open", score=None, note="mass_ev must be > 0, epsilon >= 0")

    bound = _bound_at(m)
    if eps > bound:
        return Verdict(
            status="fail",
            score=None,
            note=(
                f"epsilon = {eps:.2g} above coarse bound {bound:.2g} at "
                f"m_A' = {m:.2g} eV; consult DarkCast for precise exclusion"
            ),
        )
    return Verdict(
        status="pass",
        score=None,
        note=(
            f"epsilon = {eps:.2g} below coarse bound {bound:.2g} at "
            f"m_A' = {m:.2g} eV (note: bound is a coarse envelope)"
        ),
    )
