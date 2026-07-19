from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from shift_scenario_lab import cli


def test_demo_user_path_creates_a_real_report(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    completed = subprocess.run(
        [sys.executable, "-m", "shift_scenario_lab.cli", "demo", "--output", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "net value" in completed.stdout
    assert payload["input_rows"] == 36
    assert payload["result"]["overall"]["confusion"]["true_positive"] > 0


def test_cli_user_path_rejects_bad_input(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    output = tmp_path / "report.json"
    bad.write_text("prediction,actual\n0.5,1\n", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "shift_scenario_lab.cli",
            "run",
            "--input",
            str(bad),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "missing required columns" in completed.stderr


def test_cli_main_runs_in_process_with_user_options(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "in-process.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "shift-scenario",
            "demo",
            "--output",
            str(output),
            "--threshold",
            "0.7",
            "--score-shift",
            "0.1",
            "--target-positive-rate",
            "0.6",
        ],
    )
    cli.main()
    assert json.loads(output.read_text(encoding="utf-8"))["result"]["scenario"]["threshold"] == 0.7
