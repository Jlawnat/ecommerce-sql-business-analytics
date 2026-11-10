"""Executive evidence summary built only from checked-in aggregate outputs."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from dashboard.charts import category_pareto, monthly_trend
from dashboard.data import DashboardRepository, DataContractError, DataUnavailable, REPO_URL
from dashboard.ui import (
    boundary_note, evidence_note, format_brl, format_int, format_pct,
    metric_strip, page_header, render_data_error, source_caption,
)

repo = DashboardRepository()

try:
    monthly = repo.csv("monthly_sales")
    categories = repo.csv("category_pareto")
    anchor = repo.anchor_metrics()
except (DataUnavailable, DataContractError) as error:
    render_data_error(error)
    st.stop()

page_header(
    "Executive overview",
    "Where is the historical business volume concentrated, and what deserves action?",
    "The delivered-order population contains 96,478 orders and BRL 13.22M of merchandise value; category concentration is meaningful but not dominated by one category.",
    "Verified historical aggregates · Olist public dataset · 2016–2018",
)
metric_strip([
    ("Delivered orders", format_int(anchor["delivered_orders"]), "Delivered-order definition"),
    ("Merchandise value", format_brl(anchor["merchandise_value"]), "Excludes freight; not profit"),
    ("Average / order", format_brl(anchor["average_order_value"]), "Delivered orders"),
    ("Largest category", format_pct(anchor["top_category_share_pct"]), str(anchor["top_category"])),
])
boundary_note("Historical evidence only: the observation window ends in August 2018 and does not describe current ecommerce conditions. Sparse boundary months are marked and excluded from interpreted growth claims.")

st.plotly_chart(monthly_trend(monthly), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Monthly delivered merchandise value from September 2016 through August 2018; sparse boundary months are marked.")
c = repo.contract("monthly_sales")
source_caption(c.grain, c.observation, c.source, repo.source_url("monthly_sales"))

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.plotly_chart(category_pareto(categories), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Category merchandise value bars and cumulative share line for the top twenty categories.")
    c = repo.contract("category_pareto")
    source_caption(c.grain, c.observation, c.source, repo.source_url("category_pareto"))
with right:
    st.subheader("Decision ledger")
    evidence_note("Concentration", f"{anchor['top_category']} contributes {anchor['top_category_share_pct']:.2f}% of delivered merchandise value. Monitor a portfolio of leading categories rather than treating one category as the business.")
    evidence_note("Customer return", "Only 2,801 of 93,358 observed delivered customers made more than one delivered order. Use time-to-second-purchase analysis; non-return is not proven churn.")
    evidence_note("Fulfilment signal", "Late delivery is strongly associated with low reviews after measured adjustment. Operational pilots need prospective validation because this historical analysis is observational.")

st.subheader("Proposed actions and evidence")
for title, body, link in [
    ("Prioritise second-purchase measurement", "Track 90- and 365-day cumulative repeat incidence with cohort maturity controls.", "reports/PHASE25_RESEARCH_RESULTS.md"),
    ("Target fulfilment diagnostics", "Investigate high-lateness state and category cells while guarding review rate and cancellation outcomes.", "sql/analysis/10_delivery_satisfaction_research.sql"),
    ("Protect category mix visibility", "Review Pareto contribution and month mix without interpreting sparse boundary-month changes.", "sql/analysis/07_sales_category_trends.sql"),
]:
    st.markdown(f"**{title}** — {body} [Evidence]({REPO_URL}/blob/main/{link})")

st.download_button("Download monthly aggregate", repo.export_csv("monthly_sales"), "monthly_sales_aggregate.csv", "text/csv", help="Aggregate month-level data only; no customer records.")

