"""Evaluator for neutron_electric_dipole_moment.

Bound: |d_n| < 1.8e-26 e cm at 90% CL.
Source: Abel et al. (nEDM Collaboration at PSI), 'Measurement of the
Permanent Electric Dipole Moment of the Neutron', PRL 124, 081803
(2020), arXiv:2001.11966. The paper measures
    d_n = (0.0 +/- 1.1_stat +/- 0.2_sys) x 10^-26 e cm,
from which the quoted 90% CL upper limit |d_n| < 1.8e-26 e cm follows.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 1.8e-26  # e cm, 90% CL upper limit


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="e cm",
        what="d_n (neutron EDM)",
    )
