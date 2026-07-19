from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import polars as pl
from pydantic import ValidationError

from ..domain.models import CostMatrix, PredictionRow

REQUIRED_COLUMNS = {"prediction", "actual", "group"}


def load_predictions(path: Path) -> list[PredictionRow]:
    """Load a local CSV and return validated prediction events."""
    if not path.is_file():
        raise FileNotFoundError(f"prediction file not found: {path}")
    try:
        frame = pl.read_csv(path)
    except pl.exceptions.PolarsError as exc:
        raise ValueError(f"could not parse CSV: {exc}") from exc
    return _validate_prediction_frame(frame)


def load_predictions_bytes(content: bytes) -> list[PredictionRow]:
    try:
        frame = pl.read_csv(BytesIO(content))
    except pl.exceptions.PolarsError as exc:
        raise ValueError(f"could not parse CSV: {exc}") from exc
    return _validate_prediction_frame(frame)


def _validate_prediction_frame(frame: pl.DataFrame) -> list[PredictionRow]:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")
    try:
        selected = frame.select(sorted(REQUIRED_COLUMNS))
        selected = selected.filter(
            ~pl.all_horizontal([pl.col(column).is_null() for column in selected.columns])
        )
        return [PredictionRow.model_validate(row) for row in selected.to_dicts()]
    except ValidationError as exc:
        raise ValueError(f"invalid prediction row: {exc}") from exc


def load_cost_matrix(path: Path) -> CostMatrix:
    if not path.is_file():
        raise FileNotFoundError(f"cost matrix file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"cost matrix is not valid JSON: {exc}") from exc
    try:
        return CostMatrix.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"invalid cost matrix: {exc}") from exc


def load_cost_matrix_bytes(content: bytes) -> CostMatrix:
    try:
        raw = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cost matrix is not valid UTF-8 JSON: {exc}") from exc
    try:
        return CostMatrix.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"invalid cost matrix: {exc}") from exc
