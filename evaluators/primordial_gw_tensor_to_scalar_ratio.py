"""Evaluator for primordial_gw_tensor_to_scalar_ratio.

Bound: r_{0.05} < 0.036 at 95% CL.
Source: BICEP/Keck Collaboration, 'Improved Constraints on Primordial
Gravitational Waves using Planck, WMAP, and BICEP/Keck Observations
through the 2018 Observing Season', PRL 127, 151301 (2021),
arXiv:2110.00483. The constraint is on the tensor-to-scalar ratio at
pivot scale k = 0.05 Mpc^-1.

A 95%-CL upper bound is the standard convention for the tensor-to-
scalar ratio; the benchmark is treated as |r| < 0.036 (r is non-
negative by definition).
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import upper_limit_on_abs


LIMIT = 0.036  # tensor-to-scalar ratio, 95% CL upper limit at k = 0.05 Mpc^-1


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return upper_limit_on_abs(
        prediction,
        limit=LIMIT,
        units="dimensionless",
        what="r (tensor-to-scalar ratio at k = 0.05 Mpc^-1)",
    )
