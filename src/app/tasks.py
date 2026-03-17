"""Example task implementations that follow safe runtime defaults."""

from __future__ import annotations

import logging
import time

from .guards import (
    NumericBounds,
    confirm_destructive_action,
    detect_price_anomaly,
    validate_numeric,
)

LOGGER = logging.getLogger(__name__)


def run_oneshot(dry_run: bool, force: bool) -> None:
    """Execute a bounded example task and exit immediately."""

    validate_numeric("balance", 1000, NumericBounds(minimum=0, maximum=1e12))
    detect_price_anomaly(price=101.0, moving_average=100.0, sigma=2.0)
    should_write = confirm_destructive_action(
        force=force,
        dry_run=dry_run,
        description="Write results to downstream system.",
    )
    if should_write:
        LOGGER.info("Performed write operation.", extra={"event": "write_performed"})
    LOGGER.info("Completed one-shot task.", extra={"event": "oneshot_complete"})


def run_service_loop(timeout_seconds: int, heartbeat) -> None:
    """Run a bounded service loop with timeout and heartbeat support."""

    started = time.monotonic()
    while True:
        heartbeat()
        time.sleep(1)
        if time.monotonic() - started >= timeout_seconds:
            LOGGER.info(
                "Service timeout reached, exiting cleanly.",
                extra={"event": "service_timeout", "details": {"timeout_seconds": timeout_seconds}},
            )
            break
