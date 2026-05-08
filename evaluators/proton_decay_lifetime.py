"""Evaluator for proton_decay_lifetime.

Bound (Super-Kamiokande, 90% CL): the strongest single-channel limit
is tau/B(p -> e+ pi^0) > 2.4e34 years. We treat this as the threshold
the framework's *minimum* predicted partial lifetime across channels
must exceed. (Frameworks with no proton decay should declare
'by_construction'; they pass automatically.)

Framework prediction shape (kind == 'value'):
    "value": <minimum partial lifetime in years across all channels>
    "uncertainty": <years, optional>
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import lower_limit_on_value


LIMIT_YEARS = 2.4e34  # tau/B(p -> e+ pi^0), strongest single-channel bound


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return lower_limit_on_value(
        prediction,
        limit=LIMIT_YEARS,
        units="years",
        what="proton partial lifetime (minimum across channels)",
    )
