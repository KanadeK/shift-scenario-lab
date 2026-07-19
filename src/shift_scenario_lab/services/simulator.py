from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ..domain.calculation import evaluate
from ..domain.models import CostMatrix, PredictionRow, Scenario, SimulationResult


class SimulationService:
    def __init__(self, rows: list[PredictionRow], costs: CostMatrix) -> None:
        self.rows = rows
        self.costs = costs
        self._saved: dict[str, SimulationResult] = {}

    def run(self, scenario: Scenario) -> SimulationResult:
        return evaluate(self.rows, scenario, self.costs)

    def save(self, scenario: Scenario) -> SimulationResult:
        result = self.run(scenario)
        self._saved[scenario.name] = result
        return result

    def compare(self) -> list[SimulationResult]:
        return list(self._saved.values())

    def export_report(self, result: SimulationResult, destination: Path) -> None:
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "input_rows": len(self.rows),
            "cost_matrix": self.costs.model_dump(),
            "result": result.model_dump(),
            "disclaimer": "This report is a sensitivity simulation, not a causal claim or deployment decision.",
        }
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")

