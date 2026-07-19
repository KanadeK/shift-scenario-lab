from __future__ import annotations

import json
from pathlib import Path

import plotly.express as px
import streamlit as st

from shift_scenario_lab.adapters.csv_input import (
    load_cost_matrix,
    load_cost_matrix_bytes,
    load_predictions,
    load_predictions_bytes,
)
from shift_scenario_lab.domain.models import CostMatrix, Scenario, SimulationResult
from shift_scenario_lab.services.simulator import SimulationService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_data() -> tuple[list, CostMatrix]:
    prediction_upload = st.sidebar.file_uploader("Predictions CSV", type="csv")
    cost_upload = st.sidebar.file_uploader("Cost matrix JSON", type="json")
    rows = (
        load_predictions_bytes(prediction_upload.getvalue())
        if prediction_upload is not None
        else load_predictions(PROJECT_ROOT / "examples/synthetic_credit.csv")
    )
    costs = (
        load_cost_matrix_bytes(cost_upload.getvalue())
        if cost_upload is not None
        else load_cost_matrix(PROJECT_ROOT / "examples/cost_matrix.json")
    )
    return rows, costs


def _group_chart(result: SimulationResult) -> None:
    records = [
        {"group": group, "metric": metric, "value": value}
        for group, metrics in result.by_group.items()
        for metric, value in (("Precision", metrics.precision), ("Recall", metrics.recall))
    ]
    figure = px.bar(records, x="group", y="value", color="metric", barmode="group", range_y=[0, 1])
    figure.update_layout(yaxis_tickformat=".0%", legend_title_text="")
    st.plotly_chart(figure, width="stretch")


def _comparison_table(results: list[SimulationResult]) -> None:
    if not results:
        st.info("Save a scenario to compare it with later runs.")
        return
    rows = [
        {
            "Scenario": item.scenario.name,
            "Threshold": item.scenario.threshold,
            "Score shift": item.scenario.score_shift,
            "Target positive rate": item.scenario.target_positive_rate,
            "Precision": item.overall.precision,
            "Recall": item.overall.recall,
            "Net value": item.overall.net_value,
        }
        for item in results
    ]
    st.dataframe(rows, width="stretch", hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Shift Scenario Lab", page_icon="📊", layout="wide")
    st.title("Shift Scenario Lab")
    st.caption("Pre-deployment sensitivity simulations for thresholds, score shifts, and class mix.")
    st.warning("Association simulation only. These outputs are not causal conclusions or deployment advice.")
    if "saved" not in st.session_state:
        st.session_state.saved = []

    try:
        rows, costs = _load_data()
    except (FileNotFoundError, ValueError) as exc:
        st.error(str(exc))
        st.stop()

    st.sidebar.header("Scenario assumptions")
    name = st.sidebar.text_input("Scenario name", value="Candidate policy")
    threshold = st.sidebar.slider("Decision threshold", 0.0, 1.0, 0.50, 0.01)
    score_shift = st.sidebar.slider("Feature-driven score shift", -0.50, 0.50, 0.00, 0.01)
    change_mix = st.sidebar.checkbox("Simulate class-mix change")
    target_rate = (
        st.sidebar.slider("Target positive rate", 0.01, 0.99, 0.50, 0.01) if change_mix else None
    )
    scenario = Scenario(
        name=name,
        threshold=threshold,
        score_shift=score_shift,
        target_positive_rate=target_rate,
    )
    service = SimulationService(rows, costs)
    try:
        result = service.run(scenario)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    metrics = result.overall
    first, second, third, fourth = st.columns(4)
    first.metric("Precision", f"{metrics.precision:.1%}")
    second.metric("Recall", f"{metrics.recall:.1%}")
    third.metric("Total cost", f"{metrics.total_cost:,.0f}")
    fourth.metric("Net value", f"{metrics.net_value:,.0f}")

    st.subheader("Group slice changes")
    _group_chart(result)
    st.subheader("Confusion matrix")
    st.dataframe([metrics.confusion.model_dump()], width="stretch", hide_index=True)

    save, report = st.columns(2)
    if save.button("Save scenario", width="stretch"):
        st.session_state.saved = [
            saved for saved in st.session_state.saved if saved.scenario.name != scenario.name
        ] + [result]
        st.success(f"Saved {scenario.name}.")
    payload = json.dumps(
        {
            "input_rows": len(rows),
            "cost_matrix": costs.model_dump(),
            "result": result.model_dump(),
            "disclaimer": "Sensitivity simulation, not a causal claim or deployment decision.",
        },
        indent=2,
    )
    report.download_button(
        "Download scenario report", payload, file_name="scenario-report.json", mime="application/json", width="stretch"
    )
    st.subheader("Saved scenario comparison")
    _comparison_table(st.session_state.saved)
    st.caption("Assumptions: " + " ".join(result.assumptions))


if __name__ == "__main__":
    main()
