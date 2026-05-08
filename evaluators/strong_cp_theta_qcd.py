"""Evaluator for strong_cp_theta_qcd.

Bound: |theta_QCD| < 1e-10 (95% CL upper limit, derived from the neutron
EDM bound |d_n| < 1.8e-26 e cm).

A framework that has no mechanism to dynamically suppress theta_QCD
must still predict an effective value below this bound; 'by_construction'
passes only if the framework has such a mechanism (Peccei-Quinn,
massless quark, anthropic argument, etc.). The SM by itself does NOT
explain theta_QCD = 0; it merely accommodates whatever the data say.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 1e-10  # dimensionless


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="dimensionless",
        what="theta_QCD",
    )
