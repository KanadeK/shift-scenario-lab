from __future__ import annotations

import pytest
from pydantic import ValidationError

from shift_scenario_lab.domain.models import PredictionRow, Scenario


@pytest.mark.parametrize("actual", [-1, 2, 9])
def test_only_binary_labels_allowed(actual: int) -> None:
    with pytest.raises(ValidationError, match="actual must be 0 or 1"):
        PredictionRow(prediction=0.5, actual=actual, group="risk")


def test_invalid_threshold_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Scenario(name="invalid", threshold=1.1)

