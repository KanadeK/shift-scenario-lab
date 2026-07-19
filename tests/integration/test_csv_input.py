from __future__ import annotations

from pathlib import Path

import pytest

from shift_scenario_lab.adapters.csv_input import load_cost_matrix, load_predictions


def test_loads_real_csv_fixture() -> None:
    rows = load_predictions(Path("examples/synthetic_credit.csv"))
    assert len(rows) == 36
    assert {row.group for row in rows} == {"urban", "rural", "small_business"}


def test_rejects_missing_columns(tmp_path: Path) -> None:
    path = tmp_path / "missing.csv"
    path.write_text("prediction,actual\n0.5,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="group"):
        load_predictions(path)


def test_rejects_non_binary_csv_values(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("prediction,actual,group\n0.5,4,a\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid prediction row"):
        load_predictions(path)


def test_rejects_missing_cost_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_cost_matrix(tmp_path / "nope.json")

