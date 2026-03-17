"""Runtime lifecycle helpers for safe process management."""

from __future__ import annotations

import atexit
import logging
import shutil
import socket
import sys
import tempfile
import time
from contextlib import AbstractContextManager
from pathlib import Path

import psutil

LOGGER = logging.getLogger(__name__)


class ManagedRuntime(AbstractContextManager["ManagedRuntime"]):
    """Manage PID files, temporary directories, and periodic heartbeats."""

    def __init__(
        self,
        *,
        app_name: str,
        pid_dir: Path,
        mode: str,
        command: str,
        dry_run: bool,
        port: int | None = None,
        heartbeat_seconds: int = 30,
    ) -> None:
        self.app_name = app_name
        self.pid_dir = pid_dir
        self.mode = mode
        self.command = command
        self.dry_run = dry_run
        self.port = port
        self.heartbeat_seconds = heartbeat_seconds
        self.pid = psutil.Process().pid
        self.pid_file = self.pid_dir / f"{self.app_name}.pid"
        self.temp_dir: Path | None = None
        self._last_heartbeat = 0.0
        self._cleaned = False

    def __enter__(self) -> ManagedRuntime:
        """Create runtime state and register cleanup hooks."""

        self.pid_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"{self.app_name}-", dir=str(self.pid_dir)))
        self._check_pid_conflict()
        if self.port is not None:
            self._check_port_conflict(self.port)
        self.pid_file.write_text(f"{self.pid}\n{self.command}\n", encoding="utf-8")
        atexit.register(self.cleanup)
        LOGGER.info(
            "Runtime started.",
            extra={
                "event": "runtime_start",
                "pid": self.pid,
                "command": self.command,
                "mode": self.mode,
                "port": self.port,
                "dry_run": self.dry_run,
                "details": {
                    "pid_file": str(self.pid_file),
                    "temp_dir": str(self.temp_dir),
                },
            },
        )
        self.print_cleanup_hint()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """Clean runtime resources on exit."""

        self.cleanup()
        return None

    def heartbeat(self) -> None:
        """Emit a periodic liveness message for long-running jobs."""

        now = time.monotonic()
        if now - self._last_heartbeat < self.heartbeat_seconds:
            return
        self._last_heartbeat = now
        LOGGER.info(
            "Heartbeat.",
            extra={"event": "heartbeat", "pid": self.pid, "mode": self.mode},
        )

    def cleanup(self) -> None:
        """Remove runtime artifacts and log exit details."""

        if self._cleaned:
            return
        self._cleaned = True
        if self.pid_file.exists():
            self.pid_file.unlink(missing_ok=True)
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        LOGGER.info(
            "Runtime stopped.",
            extra={
                "event": "runtime_stop",
                "pid": self.pid,
                "details": {"cleanup_command_windows": f"taskkill /PID {self.pid} /F"},
            },
        )

    def print_cleanup_hint(self) -> None:
        """Print OS-specific cleanup hints to stdout for quick recovery."""

        if sys.platform.startswith("win"):
            cleanup_hint = f"taskkill /PID {self.pid} /F"
        else:
            cleanup_hint = f"kill -9 {self.pid}"
        print(f"PID={self.pid} COMMAND={self.command}")
        print(f"Cleanup hint: {cleanup_hint}")

    def _check_pid_conflict(self) -> None:
        """Detect stale or active PID files before startup."""

        if not self.pid_file.exists():
            return
        content = self.pid_file.read_text(encoding="utf-8").splitlines()
        if not content:
            return
        existing_pid = int(content[0])
        if psutil.pid_exists(existing_pid):
            raise RuntimeError(
                "An existing process is already registered. "
                f"PID={existing_pid}. Suggested cleanup: taskkill /PID {existing_pid} /F"
            )
        self.pid_file.unlink(missing_ok=True)

    def _check_port_conflict(self, port: int) -> None:
        """Detect listeners already bound to the requested port."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(
                    f"Port {port} is already in use. Inspect with `netstat -ano | findstr :{port}` "
                    f"then clean up using `taskkill /PID <PID> /F`."
                )
