"""Evaluator for sidm_self_interaction_clusters.

Bound: sigma/m < 0.47 cm^2/g at 95% CL, derived from the dark-matter /
stellar offset in 72 stacked galaxy-cluster mergers at v ~ 1000 km/s.
Source: Harvey, Massey, Kitching, Taylor, Tittley, 'The non-
gravitational interactions of dark matter in colliding galaxy
clusters', Science 347, 1462 (2015), arXiv:1503.07675. Abstract:
"sigma_DM / m < 0.47 cm^2/g (95% CL)".

Note: SIDM cross sections are velocity-dependent in many models;
this benchmark constrains the cluster-velocity regime (v ~ 1000 km/s).
Frameworks with strongly velocity-dependent cross sections may also
need to address dwarf-galaxy bounds (v ~ 30 km/s) where the limit is
weaker but the inferred cross section can be larger.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 0.47  # cm^2/g, 95% CL upper limit at v ~ 1000 km/s


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="cm^2/g",
        what="sigma/m (DM self-interaction at cluster scale)",
    )
