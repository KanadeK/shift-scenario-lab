from __future__ import annotations

import argparse
from pathlib import Path

from .adapters.csv_input import load_cost_matrix, load_predictions
from .domain.models import CostMatrix, Scenario
from .services.simulator import SimulationService


def _project_file(name: str) -> Path:
    return Path(__file__).resolve().parents[2] / name


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local deployment sensitivity scenario.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("demo", "run"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--input", type=Path)
        command_parser.add_argument("--costs", type=Path)
        command_parser.add_argument("--output", type=Path, required=True)
        command_parser.add_argument("--threshold", type=float, default=0.5)
        command_parser.add_argument("--score-shift", type=float, default=0.0)
        command_parser.add_argument("--target-positive-rate", type=float)
    args = parser.parse_args()
    input_path = args.input or _project_file("examples/synthetic_credit.csv")
    costs_path = args.costs or _project_file("examples/cost_matrix.json")
    rows = load_predictions(input_path)
    costs = load_cost_matrix(costs_path) if costs_path else CostMatrix()
    scenario = Scenario(
        name="demo" if args.command == "demo" else "cli-run",
        threshold=args.threshold,
        score_shift=args.score_shift,
        target_positive_rate=args.target_positive_rate,
    )
    result = SimulationService(rows, costs).run(scenario)
    SimulationService(rows, costs).export_report(result, args.output)
    print(f"Wrote {args.output} with net value {result.overall.net_value:.2f}")


if __name__ == "__main__":
    main()

