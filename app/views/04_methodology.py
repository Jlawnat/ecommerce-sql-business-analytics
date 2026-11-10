"""Data contracts, lineage, limitations, and reproduction instructions."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from dashboard.data import ASSETS, DashboardRepository, REPO_URL
from dashboard.ui import boundary_note, page_header

repo = DashboardRepository()
availability = repo.availability()

page_header(
    "Methodology & reproducibility",
    "Can every visible figure be traced to a tested analytical source?",
    "Each dashboard asset has an explicit grain, observation window, required schema, and SQL or Python lineage; no customer-level records are exposed for download.",
    "Phase 1–2.5 definitions preserved · aggregate presentation layer",
)
boundary_note("The checked-in aggregates support portfolio reproducibility without distributing raw Olist files, SQLite databases, credentials, or customer-level extracts.")
st.caption("Validation status: 39/39 automated tests passed on 2026-11-10, including all historical tests and new dashboard contracts, figures, privacy checks, and route smoke tests.")

st.subheader("Data contracts and lineage")
rows = []
for key, contract in ASSETS.items():
    rows.append({
        "Asset": key,
        "Status": "available" if availability[key] else "missing",
        "Grain": contract.grain,
        "Observation": contract.observation,
        "Source": f"{REPO_URL}/blob/main/{contract.source}",
    })
st.dataframe(
    pd.DataFrame(rows), hide_index=True, width="stretch", height=430,
    column_config={"Source": st.column_config.LinkColumn("SQL / code evidence", display_text="Open source")},
)

st.subheader("Authoritative definitions")
definitions = {
    "Delivered order": "orders.order_status = 'delivered'; the same population used in Phases 1–2.5.",
    "Merchandise value": "SUM(order_items.price) at delivered-order grain; freight excluded. It is not profit or accounting revenue.",
    "Late delivery": "Full timestamp: order_delivered_customer_date > order_estimated_delivery_date.",
    "Customer": "customer_unique_id, not order-scoped customer_id.",
    "Low review": "Aggregated order-level review score ≤ 2 after resolving multiple review rows.",
    "RFM snapshot": "Features use only delivered purchases strictly before the reproducible cutoff 2018-09-01.",
}
for name, definition in definitions.items():
    st.markdown(f"**{name}**  \n{definition}")

left, right = st.columns(2, gap="large")
with left:
    st.subheader("Quality controls")
    st.markdown("- Mart grains are asserted unique and reconciled to Phase 1 anchors.\n- Payment and review rows are aggregated before order joins.\n- Censored cohort cells remain null.\n- Dashboard downloads are restricted to aggregate allowlisted assets.\n- Existing statistical outputs are displayed, not refit in the app.")
with right:
    st.subheader("Interpretation limits")
    st.markdown("- Historical 2016–2018 marketplace data are not current market estimates.\n- Observational delivery models do not identify causal effects.\n- Review missingness can create selection bias.\n- RFM labels vary with snapshot date.\n- Product-category attribution is order-level and may simplify mixed baskets.")

st.subheader("Local reproduction")
st.code("""python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/streamlit run app/streamlit_app.py""", language="bash")
db = repo.sqlite_status()
st.caption(f"Optional local source database: {'available' if db['source_database'] else 'not downloaded'} · analytics mart: {'available' if db['analytics_mart'] else 'not built'}. The dashboard itself reads checked-in aggregates.")

st.subheader("Research documentation")
st.markdown(
    f"[Phase 2.5 audit]({REPO_URL}/blob/main/docs/PHASE25_AUDIT.md) · "
    f"[Statistical methods]({REPO_URL}/blob/main/docs/PHASE25_STATISTICAL_METHODS.md) · "
    f"[Research results]({REPO_URL}/blob/main/reports/PHASE25_RESEARCH_RESULTS.md) · "
    f"[Metric definitions]({REPO_URL}/blob/main/docs/METRIC_DEFINITIONS.md)"
)
st.caption("Dataset: Brazilian E-Commerce Public Dataset by Olist · CC BY-NC-SA 4.0 · anonymized historical marketplace records; raw data are not redistributed here.")
