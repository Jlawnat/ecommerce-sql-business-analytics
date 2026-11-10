"""Censored cohort, RFM, and repeat-purchase research."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from dashboard.charts import cohort_heatmap, km_curve, rfm_distribution
from dashboard.data import DashboardRepository, DataContractError, DataUnavailable
from dashboard.ui import boundary_note, format_int, format_pct, metric_strip, page_header, render_data_error, source_caption

repo = DashboardRepository()
try:
    retention = repo.csv("cohort_retention")
    summary = repo.csv("cohort_summary")
    segments = repo.csv("rfm_segments")
    km = repo.csv("repeat_km")
    research = repo.json("research_results")
except (DataUnavailable, DataContractError) as error:
    render_data_error(error)
    st.stop()

repeat = research["repeat_purchase"]
km90 = km.loc[km["horizon_days"] == 90].iloc[0]
km365 = km.loc[km["horizon_days"] == 365].iloc[0]
stability = repeat["rfm_stability"]

page_header(
    "Customer intelligence",
    "How quickly do customers make a second observed delivered purchase?",
    "Estimated cumulative repeat incidence is 2.13% by day 90 and 3.81% by day 365; later cohorts require explicit right-censoring.",
    "Customer identity: customer_unique_id · Primary cutoff: 2018-09-01",
)
metric_strip([
    ("Observed customers", "93,358", "At least one delivered order"),
    ("Repeat by day 90", format_pct(km90["repeat_cumulative_incidence"] * 100), f"95% CI {km90['repeat_ci_95_low']*100:.2f}–{km90['repeat_ci_95_high']*100:.2f}%"),
    ("Repeat by day 365", format_pct(km365["repeat_cumulative_incidence"] * 100), f"95% CI {km365['repeat_ci_95_low']*100:.2f}–{km365['repeat_ci_95_high']*100:.2f}%"),
    ("RFM stability", format_pct(stability["exact_segment_agreement"] * 100, 1), f"κ = {stability['cohen_kappa']:.3f}"),
])
boundary_note("Grey heatmap cells are unobserved, not zero retention. Kaplan–Meier estimates treat customers without a second observed purchase as right-censored; they are not labelled as confirmed churn.")

max_month = st.slider("Retention horizon shown", 3, 18, 12, help="The display never converts immature cohort cells into zero.")
st.plotly_chart(cohort_heatmap(retention, max_month), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Monthly cohort retention heatmap with unobserved right-censored cells left blank.")
c = repo.contract("cohort_retention")
source_caption(c.grain, c.observation, c.source, repo.source_url("cohort_retention"))

left, right = st.columns(2, gap="large")
with left:
    st.plotly_chart(rfm_distribution(segments), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Horizontal bars showing the number of customers in each RFM segment at the September 2018 snapshot.")
    c = repo.contract("rfm_segments")
    source_caption(c.grain, c.observation, c.source, repo.source_url("rfm_segments"))
with right:
    st.plotly_chart(km_curve(km), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Kaplan Meier cumulative incidence curve for a second observed delivered purchase with a 95 percent confidence band.")
    c = repo.contract("repeat_km")
    source_caption(c.grain, c.observation, c.source, repo.source_url("repeat_km"))

st.subheader("Maturity and stability audit")
col1, col2 = st.columns([1.3, 1], gap="large")
with col1:
    maturity = summary[["cohort_month", "acquired_customers", "repeat_purchase_rate_pct", "last_observed_month"]].copy()
    maturity["months_observable"] = (
        (pd.to_datetime(maturity["last_observed_month"]).dt.year - pd.to_datetime(maturity["cohort_month"]).dt.year) * 12
        + pd.to_datetime(maturity["last_observed_month"]).dt.month - pd.to_datetime(maturity["cohort_month"]).dt.month
    )
    st.dataframe(maturity.sort_values("cohort_month", ascending=False), hide_index=True, width="stretch", height=310)
with col2:
    st.markdown(f"**Cutoff sensitivity**  \nRFM labels were compared for {format_int(stability['common_customers'])} customers present at both 2018-06-01 and 2018-09-01 snapshots.")
    st.markdown(f"**Exact agreement**  \n{stability['exact_segment_agreement']*100:.2f}%")
    st.markdown(f"**Cohen’s κ**  \n{stability['cohen_kappa']:.3f}")
    st.warning("Segment labels are snapshot-dependent. They should guide prioritisation, not be interpreted as permanent customer traits.", icon=None)

st.download_button("Download cohort maturity aggregate", repo.export_csv("cohort_summary"), "cohort_maturity_aggregate.csv", "text/csv")

