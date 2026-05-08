"""Evaluator for hydrogen_1s_2s_transition.

Measurement (Parthey et al. 2011, MPQ Garching):
    f_1S2S = 2 466 061 413 187 035 Hz +/- 10 Hz (4.2e-15 fractional)
Source: Parthey, Matveev, Alnis, Bernhardt, Beyer, Holzwarth, Maistrou,
Pohl, Predehl, Udem, Wilken, Kolachevsky, Abgrall, Rovera, Salomon,
Laurent, Hansch, 'Improved Measurement of the Hydrogen 1S-2S
Transition Frequency', PRL 107, 203001 (2011), arXiv:1107.3101.

A framework that reproduces SM QED for atomic hydrogen passes
by_construction. A framework predicting deviations must supply the
predicted frequency in Hz with a theoretical uncertainty.
"""
from __future__ import annotations

from typing import Any

from . import Verdict
from ._helpers import within_measurement


MEASURED_HZ = 2466061413187035.0
SIGMA_HZ = 10.0


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    return within_measurement(
        prediction,
        measured=MEASURED_HZ,
        sigma_exp=SIGMA_HZ,
        units="Hz",
        what="f_1S2S",
    )
