"""Shared helpers for trivial-arithmetic evaluators.

Two common bound shapes cover most of the 'trivial' tier:

  - upper_limit_on_abs:  |framework_value| <= experimental_limit
  - within_measurement:  framework_value agrees with experimental measurement
                         to within combined N-sigma uncertainty

Both return a Verdict; both handle the prediction.kind dispatch
('by_construction', 'not_applicable', 'open', 'value') uniformly.
"""
from __future__ import annotations

from typing import Any

from . import Verdict


def _dispatch_non_value(prediction: dict[str, Any], by_construction_passes: bool) -> Verdict | None:
    kind = prediction.get("kind")
    if kind == "by_construction":
        return Verdict(
            status="pass" if by_construction_passes else "fail",
            score=None,
            note=prediction.get("note", "framework reproduces standard result by structural identity"),
        )
    if kind == "not_applicable":
        return Verdict(
            status="inapplicable",
            score=None,
            note=prediction.get("note", "framework declares this benchmark out of scope"),
        )
    if kind == "open":
        return Verdict(
            status="open",
            score=None,
            note="framework has not yet supplied a prediction",
        )
    if kind != "value":
        return Verdict(
            status="open",
            score=None,
            note=f"unrecognized prediction kind {kind!r}",
        )
    return None


def _numeric(prediction: dict[str, Any], key: str) -> tuple[float | None, str]:
    raw = prediction.get(key)
    if raw is None:
        return None, f"prediction is missing required field {key!r}"
    if not isinstance(raw, (int, float)):
        return None, f"prediction.{key} must be numeric, got {type(raw).__name__}"
    return float(raw), ""


def upper_limit_on_abs(
    prediction: dict[str, Any],
    *,
    limit: float,
    units: str,
    what: str,
) -> Verdict:
    """Pass if |prediction.value| (+ uncertainty) <= limit."""
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    value, err = _numeric(prediction, "value")
    if value is None:
        return Verdict(status="open", score=None, note=err)
    sigma_raw = prediction.get("uncertainty")
    sigma = float(sigma_raw) if isinstance(sigma_raw, (int, float)) else 0.0

    effective = abs(value) + sigma
    score = (limit - effective) / limit if limit else None

    if effective > limit:
        return Verdict(
            status="fail",
            score=score,
            note=(
                f"|{what}| = {abs(value):.3g}{f' + {sigma:.3g}' if sigma else ''} {units}"
                f" exceeds limit {limit:.3g} {units}"
            ),
        )
    return Verdict(
        status="pass",
        score=score,
        note=(
            f"|{what}| = {abs(value):.3g}{f' + {sigma:.3g}' if sigma else ''} {units}"
            f" within limit {limit:.3g} {units}"
        ),
    )


def within_measurement(
    prediction: dict[str, Any],
    *,
    measured: float,
    sigma_exp: float,
    sigma_threshold: float = 3.0,
    units: str,
    what: str,
) -> Verdict:
    """Pass if predicted value matches measurement within N-sigma combined."""
    nv = _dispatch_non_value(prediction, by_construction_passes=True)
    if nv is not None:
        return nv

    value, err = _numeric(prediction, "value")
    if value is None:
        return Verdict(status="open", score=None, note=err)
    sigma_th_raw = prediction.get("uncertainty")
    sigma_th = float(sigma_th_raw) if isinstance(sigma_th_raw, (int, float)) else 0.0

    sigma_total = (sigma_exp ** 2 + sigma_th ** 2) ** 0.5
    if sigma_total == 0:
        return Verdict(
            status="open",
            score=None,
            note="cannot evaluate: combined uncertainty is zero",
        )
    pull = (value - measured) / sigma_total
    score = max(0.0, 1.0 - abs(pull) / sigma_threshold)

    detail = (
        f"{what} = {value:.6g}{f' +/- {sigma_th:.2g}' if sigma_th else ''} {units}"
        f" vs measured {measured:.6g} +/- {sigma_exp:.2g}; pull = {pull:+.2f}"
    )
    if abs(pull) > sigma_threshold:
        return Verdict(status="fail", score=score, note=f"{detail} > {sigma_threshold} sigma")
    return Verdict(status="pass", score=score, note=f"{detail} (within {sigma_threshold} sigma)")
