from __future__ import annotations

from collections import defaultdict

from .models import ConfusionMatrix, CostMatrix, Metrics, PredictionRow, Scenario, SimulationResult


def _safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _weight_for_prevalence(row: PredictionRow, baseline: float, target: float | None) -> float:
    if target is None:
        return 1.0
    if row.actual == 1:
        return target / baseline
    return (1 - target) / (1 - baseline)


def _metrics(confusion: ConfusionMatrix, costs: CostMatrix) -> Metrics:
    precision = _safe_divide(
        confusion.true_positive, confusion.true_positive + confusion.false_positive
    )
    recall = _safe_divide(
        confusion.true_positive, confusion.true_positive + confusion.false_negative
    )
    approval_rate = _safe_divide(
        confusion.true_positive + confusion.false_positive, confusion.total
    )
    total_cost = (
        confusion.false_positive * costs.false_positive_cost
        + confusion.false_negative * costs.false_negative_cost
    )
    net_value = (
        confusion.true_positive * costs.true_positive_value
        + confusion.true_negative * costs.true_negative_value
        - total_cost
    )
    return Metrics(
        precision=precision,
        recall=recall,
        approval_rate=approval_rate,
        total_cost=total_cost,
        net_value=net_value,
        confusion=confusion,
    )


def evaluate(rows: list[PredictionRow], scenario: Scenario, costs: CostMatrix) -> SimulationResult:
    """Evaluate a scenario using score displacement and deterministic prevalence reweighting.

    `score_shift` is a sensitivity assumption, not a causal model of a feature change.
    `target_positive_rate` reweights observed labels to the declared expected prevalence.
    """
    if not rows:
        raise ValueError("at least one prediction row is required")
    baseline = sum(row.actual for row in rows) / len(rows)
    if scenario.target_positive_rate is not None and baseline in (0.0, 1.0):
        raise ValueError("class-mix simulation needs both positive and negative observations")

    matrices: dict[str, ConfusionMatrix] = defaultdict(ConfusionMatrix)
    overall = ConfusionMatrix()
    for row in rows:
        score = min(1.0, max(0.0, row.prediction + scenario.score_shift))
        approved = score >= scenario.threshold
        weight = _weight_for_prevalence(row, baseline, scenario.target_positive_rate)
        matrix = matrices[row.group]
        if approved and row.actual:
            matrix.true_positive += weight
            overall.true_positive += weight
        elif approved:
            matrix.false_positive += weight
            overall.false_positive += weight
        elif row.actual:
            matrix.false_negative += weight
            overall.false_negative += weight
        else:
            matrix.true_negative += weight
            overall.true_negative += weight

    assumptions = [
        "Scores are shifted additively and clamped to [0, 1].",
        "Class-mix changes reweight observed labels; they do not synthesize individuals.",
        "Results show simulated association under stated assumptions, not causal effects.",
    ]
    return SimulationResult(
        scenario=scenario,
        overall=_metrics(overall, costs),
        by_group={group: _metrics(matrix, costs) for group, matrix in sorted(matrices.items())},
        assumptions=assumptions,
    )
