"""Generate a deterministic report from the committed sample data."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(
    [
        sys.executable,
        "-m",
        "shift_scenario_lab.cli",
        "demo",
        "--output",
        "examples/demo-report.json",
    ],
    check=True,
    cwd=ROOT,
)

