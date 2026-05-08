"""Evaluator for cabibbo_angle_anomaly.

Measurement (Cirigliano et al. 2022 + PDG 2024 averages):
    |V_ud|^2 + |V_us|^2 + |V_ub|^2 = 0.9985 +/- 0.0005
SM predicts the sum equals 1 exactly by CKM unitarity; the data sit
~3 sigma below. Frameworks that predict CKM unitarity will sit right
at the within_measurement threshold.

Source: Cirigliano, Crivellin, Hoferichter, Moulson, 'Scrutinizing CKM
unitarity with a new measurement of the K_mu3 / K_mu2 branching
fraction', PLB 838, 137748 (2023), arXiv:2208.11707.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import within_measurement


MEASURED = 0.9985
SIGMA = 0.0005


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return within_measurement(
        prediction,
        measured=MEASURED,
        sigma_exp=SIGMA,
        units="dimensionless",
        what="|V_ud|^2 + |V_us|^2 + |V_ub|^2 (first-row CKM unitarity)",
    )
