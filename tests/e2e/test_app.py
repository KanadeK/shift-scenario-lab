from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path("src/shift_scenario_lab/app.py")


def test_default_dashboard_path_runs_and_saves_a_scenario() -> None:
    app = AppTest.from_file(str(APP)).run(timeout=15)
    assert not app.exception
    assert len(app.metric) == 4
    assert "Association simulation" in app.warning[0].value
    app.button[0].click().run(timeout=15)
    assert app.success[0].value == "Saved Candidate policy."
    assert len(app.dataframe) == 2
