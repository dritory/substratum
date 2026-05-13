"""Shared evaluator for `kind: pattern_compression` benchmarks.

A pattern_compression benchmark provides:
- procedural.target_data: array of {label, value, ...} observables
- procedural.compression_ansatz: human-readable functional form
- procedural.free_parameters: list of fit parameters

A framework's prediction supplies, in the `value` field, a map
{label: predicted_value} keyed by the labels in target_data. The
evaluator compares each label's predicted value against the target on a
log10 scale; pass if every observable agrees within `factor` orders of
magnitude (default 0.5, i.e. within a factor of ~3).

This is order-of-magnitude scoring on purpose: pattern compressions
predict the structure rather than precise values. Frameworks that
overpredict precision will pass; frameworks that miss the structure by
many orders of magnitude will fail loudly.
"""
from __future__ import annotations

import math
from typing import Any

from . import Verdict
from ._helpers import _dispatch_non_value


DEFAULT_LOG_TOLERANCE = 0.5


def _coerce_float(raw: Any) -> float | None:
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def evaluate(benchmark: dict[str, Any], prediction: dict[str, Any]) -> Verdict:
    nv = _dispatch_non_value(prediction, by_construction_passes=False)
    if nv is not None:
        return nv

    procedural = benchmark.get("procedural", {})
    targets = procedural.get("target_data", [])
    if not targets:
        return Verdict(
            status="open",
            score=None,
            note="benchmark has no target_data; cannot score pattern compression",
        )

    predicted_map = prediction.get("value")
    if not isinstance(predicted_map, dict):
        return Verdict(
            status="open",
            score=None,
            note=(
                "pattern_compression prediction.value must be a "
                "{label: predicted_value} mapping keyed by target_data labels"
            ),
        )

    log_tol = float(prediction.get("log_tolerance", DEFAULT_LOG_TOLERANCE))

    worst_residual = 0.0
    failures: list[str] = []
    n_compared = 0
    for entry in targets:
        label = entry.get("label")
        target_value = _coerce_float(entry.get("value"))
        if label is None or target_value is None or target_value <= 0:
            continue
        if label not in predicted_map:
            continue
        predicted = _coerce_float(predicted_map[label])
        if predicted is None or predicted <= 0:
            failures.append(f"{label}: prediction missing or non-positive")
            continue
        residual = abs(math.log10(predicted / target_value))
        worst_residual = max(worst_residual, residual)
        n_compared += 1
        if residual > log_tol:
            failures.append(
                f"{label}: predicted {predicted:.3g}, target {target_value:.3g} "
                f"(|log10| = {residual:.2f} > {log_tol:.2f})"
            )

    if n_compared == 0:
        return Verdict(
            status="open",
            score=None,
            note=(
                "framework supplied no predictions for this benchmark's "
                "target_data labels"
            ),
        )

    score = max(-1.0, min(1.0, 1.0 - worst_residual / log_tol)) if log_tol else None
    detail = (
        f"compared {n_compared} of {len(targets)} target observables; "
        f"worst |log10 ratio| = {worst_residual:.2f} (tol {log_tol:.2f})"
    )
    if failures:
        return Verdict(
            status="fail",
            score=score,
            note=detail + "; failures: " + "; ".join(failures[:3])
            + ("; ..." if len(failures) > 3 else ""),
        )
    return Verdict(status="pass", score=score, note=detail)
