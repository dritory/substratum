"""Evaluator modules: one per benchmark id (or per benchmark family).

Each module defines `evaluate(benchmark, prediction)` returning a Verdict.
The contract is intentionally minimal so adding a new evaluator means
writing one short Python file plus an entry in EVALUATORS below.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Optional


@dataclass
class Verdict:
    status: str
    score: Optional[float]
    note: str

    VALID_STATUSES = ("pass", "fail", "contested", "inapplicable", "open", "no_evaluator")


EvaluatorFn = Callable[[dict[str, Any], dict[str, Any]], Verdict]


EVALUATORS: dict[str, str] = {
    "alpha_variation_atomic_clocks": "evaluators.alpha_variation_atomic_clocks",
    "antihydrogen_gravity_alpha_g": "evaluators.antihydrogen_gravity_alpha_g",
    "axion_haloscope_admx": "evaluators.axion_haloscope_admx",
    "dark_photon_kinetic_mixing": "evaluators.dark_photon_kinetic_mixing",
    "electron_g_minus_2_precision": "evaluators.electron_g_minus_2_precision",
    "graviton_mass_gw_dispersion": "evaluators.graviton_mass_gw_dispersion",
    "graviton_speed_gw170817": "evaluators.graviton_speed_gw170817",
    "inverse_square_law_short_distance": "evaluators.inverse_square_law_short_distance",
    "katrin_neutrino_mass": "evaluators.katrin_neutrino_mass",
}


def get_evaluator(benchmark_id: str) -> Optional[EvaluatorFn]:
    module_path = EVALUATORS.get(benchmark_id)
    if module_path is None:
        return None
    return import_module(module_path).evaluate


def no_evaluator_verdict(benchmark_id: str) -> Verdict:
    return Verdict(
        status="no_evaluator",
        score=None,
        note=f"no evaluator registered for benchmark {benchmark_id!r}",
    )
