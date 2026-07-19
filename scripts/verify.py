"""Cross-platform verification entry point."""
from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    [sys.executable, "-m", "ruff", "check", "."],
    [sys.executable, "-m", "mypy", "src"],
    [sys.executable, "-m", "pytest", "-q", "--cov=src", "--cov-fail-under=80"],
    [sys.executable, "-m", "build"],
]

for command in COMMANDS:
    subprocess.run(command, check=True)

