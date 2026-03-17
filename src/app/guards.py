"""Safety and data integrity guards."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from math import isfinite

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class NumericBounds:
    """Numeric boundaries used to validate external values."""

    minimum: float | None = None
    maximum: float | None = None
    allow_zero: bool = True


def validate_numeric(name: str, value: float | int | None, bounds: NumericBounds) -> float:
    """Validate numeric inputs from external systems and raise helpful errors on anomalies."""

    if value is None:
        raise ValueError(f"{name} is missing.")
    numeric_value = float(value)
    if not isfinite(numeric_value):
        raise ValueError(f"{name} must be a finite number.")
    if not bounds.allow_zero and numeric_value == 0:
        raise ValueError(f"{name} cannot be zero.")
    if bounds.minimum is not None and numeric_value < bounds.minimum:
        raise ValueError(f"{name} must be >= {bounds.minimum}.")
    if bounds.maximum is not None and numeric_value > bounds.maximum:
        raise ValueError(f"{name} must be <= {bounds.maximum}.")
    return numeric_value


def detect_price_anomaly(
    price: float,
    moving_average: float,
    sigma: float,
    sigma_limit: float = 4.0,
) -> None:
    """Stop execution when a price is far outside the expected range."""

    validated_price = validate_numeric(
        "price",
        price,
        NumericBounds(minimum=0.0000001, maximum=1e10, allow_zero=False),
    )
    validated_average = validate_numeric(
        "moving_average",
        moving_average,
        NumericBounds(minimum=0.0000001, maximum=1e10, allow_zero=False),
    )
    validated_sigma = validate_numeric(
        "sigma",
        sigma,
        NumericBounds(minimum=0.0000001, maximum=1e9, allow_zero=False),
    )
    z_score = abs(validated_price - validated_average) / validated_sigma
    if z_score > sigma_limit:
        LOGGER.error(
            "Detected anomalous input; stopping execution.",
            extra={"event": "input_anomaly", "details": {"price": price, "z_score": z_score}},
        )
        raise ValueError(f"Price anomaly detected with z-score {z_score:.2f}.")


def confirm_destructive_action(force: bool, dry_run: bool, description: str) -> bool:
    """Require explicit approval before destructive operations."""

    if dry_run:
        LOGGER.info(
            "Would have performed destructive action.",
            extra={"event": "dry_run_skip", "details": {"description": description}},
        )
        return False
    if force:
        return True
    answer = input(f"{description} Really proceed? y/N: ").strip().lower()
    return answer == "y"
