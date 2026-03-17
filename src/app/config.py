"""Configuration loading utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration loaded from environment variables."""

    env: str
    log_level: str
    log_dir: Path
    pid_dir: Path
    heartbeat_seconds: int
    default_timeout_seconds: int
    host: str
    port: int


def load_config(project_root: Path) -> AppConfig:
    """Load application configuration from the local `.env` file and process env."""

    load_dotenv(project_root / ".env", override=False)
    return AppConfig(
        env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("APP_LOG_LEVEL", "INFO"),
        log_dir=project_root / os.getenv("APP_LOG_DIR", "logs"),
        pid_dir=project_root / os.getenv("APP_PID_DIR", "tmp"),
        heartbeat_seconds=int(os.getenv("APP_HEARTBEAT_SECONDS", "30")),
        default_timeout_seconds=int(os.getenv("APP_DEFAULT_TIMEOUT_SECONDS", "300")),
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
    )
