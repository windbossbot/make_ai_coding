"""Example CLI showing the safety defaults for local automation projects."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.config import load_config
from app.logging_utils import configure_logging
from app.runtime import ManagedRuntime
from app.tasks import run_oneshot, run_service_loop


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(description="Run the safe automation example.")
    parser.add_argument("--mode", choices=("oneshot", "service"), default="oneshot")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=True)
    parser.add_argument(
        "--execute",
        dest="dry_run",
        action="store_false",
        help="Perform real actions.",
    )
    parser.add_argument("--force", action="store_true", help="Skip the confirmation prompt.")
    parser.add_argument("--port", type=int, help="Port to reserve for long-running services.")
    parser.add_argument("--timeout-seconds", type=int, help="Maximum runtime for service mode.")
    return parser


def main() -> int:
    """Run the example application."""

    project_root = Path(__file__).resolve().parents[1]
    config = load_config(project_root)
    parser = build_parser()
    args = parser.parse_args()

    timeout_seconds = args.timeout_seconds or config.default_timeout_seconds
    port = (
        args.port if args.port is not None else config.port if args.mode == "service" else None
    )
    log_path = configure_logging(config.log_dir, config.log_level)
    print(f"Log file: {log_path}")

    command = " ".join(sys.argv)
    with ManagedRuntime(
        app_name="safe_automation_template",
        pid_dir=config.pid_dir,
        mode=args.mode,
        command=command,
        dry_run=args.dry_run,
        port=port,
        heartbeat_seconds=config.heartbeat_seconds,
    ) as runtime:
        if args.mode == "oneshot":
            run_oneshot(dry_run=args.dry_run, force=args.force)
            return 0
        run_service_loop(timeout_seconds=timeout_seconds, heartbeat=runtime.heartbeat)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
