from __future__ import annotations

import pytest

from shift_scenario_lab.domain.calculation import evaluate
from shift_scenario_lab.domain.models import CostMatrix, PredictionRow, Scenario

ROWS = [
    PredictionRow(prediction=0.9, actual=1, group="A"),
    PredictionRow(prediction=0.8, actual=0, group="A"),
    PredictionRow(prediction=0.4, actual=1, group="B"),
    PredictionRow(prediction=0.1, actual=0, group="B"),
]


def test_threshold_recomputes_weighted_confusion_and_cost() -> None:
    costs = CostMatrix(true_positive_value=100, false_positive_cost=10, false_negative_cost=50)
    result = evaluate(ROWS, Scenario(name="strict", threshold=0.85), costs)
    assert result.overall.confusion.model_dump() == {
        "true_positive": 1.0,
        "false_positive": 0.0,
        "false_negative": 1.0,
        "true_negative": 2.0,
    }
    assert result.overall.precision == 1.0
    assert result.overall.recall == 0.5
    assert result.overall.total_cost == 50.0
    assert result.overall.net_value == 50.0


def test_score_shift_changes_the_decision_boundary() -> None:
    base = evaluate(ROWS, Scenario(name="base", threshold=0.5), CostMatrix())
    shifted = evaluate(ROWS, Scenario(name="shift", threshold=0.5, score_shift=0.2), CostMatrix())
    assert base.overall.confusion.true_positive == 1
    assert shifted.overall.confusion.true_positive == 2
    assert shifted.by_group["B"].approval_rate > base.by_group["B"].approval_rate


def test_class_mix_reweights_observed_outcomes() -> None:
    result = evaluate(
        ROWS,
        Scenario(name="mix", threshold=0.5, target_positive_rate=0.75),
        CostMatrix(),
    )
    assert result.overall.confusion.true_positive == 1.5
    assert result.overall.confusion.false_positive == 0.5
    assert result.overall.confusion.false_negative == 1.5
    assert "not causal" in result.assumptions[-1]


def test_empty_data_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        evaluate([], Scenario(name="empty"), CostMatrix())


def test_single_class_cannot_simulate_class_mix() -> None:
    rows = [PredictionRow(prediction=0.7, actual=1, group="A")]
    with pytest.raises(ValueError, match="both positive"):
        evaluate(rows, Scenario(name="bad", target_positive_rate=0.4), CostMatrix())
