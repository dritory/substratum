"""Evaluator for binary_pulsar_psr_b1913_16.

Measurement (Weisberg-Huang 2016):
    P_b_dot_obs / P_b_dot_GR = 0.9983 +/- 0.0016
i.e. the observed orbital decay rate of the Hulse-Taylor binary pulsar
PSR B1913+16 (corrected for kinematic Galactic acceleration) divided
by the GR quadrupole-formula prediction.

Source: Weisberg and Huang, 'Relativistic Measurements from Timing the
Binary Pulsar PSR B1913+16', ApJ 829, 55 (2016), arXiv:1606.02744.

GR predicts the ratio = 1 by construction. A framework that modifies
gravitational radiation by introducing extra polarizations or scalar
charges generically perturbs this ratio.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import within_measurement


MEASURED = 0.9983
SIGMA = 0.0016


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return within_measurement(
        prediction,
        measured=MEASURED,
        sigma_exp=SIGMA,
        units="dimensionless",
        what="P_b_dot_obs / P_b_dot_GR",
    )
