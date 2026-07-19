from __future__ import annotations

import json
from pathlib import Path

from shift_scenario_lab.domain.models import CostMatrix, PredictionRow, Scenario
from shift_scenario_lab.services.simulator import SimulationService


def test_service_saves_compares_and_exports_report(tmp_path: Path) -> None:
    service = SimulationService(
        [
            PredictionRow(prediction=0.9, actual=1, group="a"),
            PredictionRow(prediction=0.2, actual=0, group="b"),
        ],
        CostMatrix(),
    )
    result = service.save(Scenario(name="candidate"))
    service.save(Scenario(name="strict", threshold=0.9))
    output = tmp_path / "nested" / "report.json"
    service.export_report(result, output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert [item.scenario.name for item in service.compare()] == ["candidate", "strict"]
    assert payload["input_rows"] == 2
    assert "not a causal claim" in payload["disclaimer"]
