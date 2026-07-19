from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class PredictionRow(BaseModel):
    """One scored event. Scores must be calibrated probabilities in [0, 1]."""

    prediction: float = Field(ge=0, le=1)
    actual: int
    group: str = Field(min_length=1, max_length=80)

    @model_validator(mode="after")
    def actual_is_binary(self) -> PredictionRow:
        if self.actual not in (0, 1):
            raise ValueError("actual must be 0 or 1")
        return self


class CostMatrix(BaseModel):
    """Business value assigned to each weighted confusion-matrix outcome."""

    true_positive_value: float = 150.0
    false_positive_cost: float = 80.0
    false_negative_cost: float = 200.0
    true_negative_value: float = 0.0


class Scenario(BaseModel):
    """A deterministic, explicitly non-causal simulation assumption set."""

    name: str = Field(min_length=1, max_length=80)
    threshold: float = Field(default=0.5, ge=0, le=1)
    score_shift: float = Field(default=0.0, ge=-1, le=1)
    target_positive_rate: float | None = Field(default=None, gt=0, lt=1)
    note: str = Field(default="", max_length=500)


class ConfusionMatrix(BaseModel):
    true_positive: float = 0.0
    false_positive: float = 0.0
    false_negative: float = 0.0
    true_negative: float = 0.0

    @property
    def total(self) -> float:
        return self.true_positive + self.false_positive + self.false_negative + self.true_negative


class Metrics(BaseModel):
    precision: float
    recall: float
    approval_rate: float
    total_cost: float
    net_value: float
    confusion: ConfusionMatrix


class SimulationResult(BaseModel):
    scenario: Scenario
    overall: Metrics
    by_group: dict[str, Metrics]
    assumptions: list[str]
