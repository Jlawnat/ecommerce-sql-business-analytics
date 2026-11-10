"""Olist Evidence Lab multipage entrypoint."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from dashboard.ui import apply_global_style, render_brand

st.set_page_config(
    page_title="Olist Evidence Lab",
    page_icon="OE",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": "Historical Olist analytics research. Metrics are verified SQL outputs; associations are not causal effects."},
)
apply_global_style()
render_brand()

page_dir = Path(__file__).parent / "views"
navigation = st.navigation([
    st.Page(page_dir / "01_executive_overview.py", title="Executive overview", default=True),
    st.Page(page_dir / "02_customer_intelligence.py", title="Customer intelligence"),
    st.Page(page_dir / "03_delivery_research.py", title="Delivery & satisfaction"),
    st.Page(page_dir / "04_methodology.py", title="Methodology & reproducibility"),
])
navigation.run()
