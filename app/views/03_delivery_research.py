"""Delivery and satisfaction association research with explicit uncertainty."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from dashboard.charts import association_forest, heterogeneity_chart, ranked_late_rates
from dashboard.data import DashboardRepository, DataContractError, DataUnavailable
from dashboard.ui import boundary_note, format_int, format_pct, metric_strip, page_header, render_data_error, source_caption

repo = DashboardRepository()
try:
    timing = repo.csv("delivery_timing")
    states = repo.csv("delivery_state")
    categories = repo.csv("delivery_category")
    coverage = repo.csv("delivery_coverage").iloc[0]
    research = repo.json("research_results")
except (DataUnavailable, DataContractError) as error:
    render_data_error(error)
    st.stop()

model = research["delivery_satisfaction"]["primary_adjusted_model"]
bounds = research["delivery_satisfaction"]["missing_review_bounds"]
late = timing.set_index("delivery_timing").loc["late"]
on_time = timing.set_index("delivery_timing").loc["on_time_or_early"]

page_header(
    "Delivery & satisfaction research",
    "Does the low-review association persist after measured adjustment?",
    "Late delivery remains associated with substantially higher low-review odds after adjustment for purchase month, state, category group, and order-value band.",
    "Delivered orders · full-timestamp lateness rule · reviewed inference population",
)
metric_strip([
    ("Inference population", format_int(model["reviewed_orders"]), "Timing + review eligible"),
    ("Late low reviews", format_pct(late["low_review_share_pct"]), f"n = {int(late['reviewed_orders']):,}"),
    ("On-time low reviews", format_pct(on_time["low_review_share_pct"]), f"n = {int(on_time['reviewed_orders']):,}"),
    ("Adjusted odds ratio", f"{model['late_odds_ratio']:.2f}", f"95% CI {model['late_or_ci_95_low']:.2f}–{model['late_or_ci_95_high']:.2f}"),
])
boundary_note("Association is not causation. Delivery timing was not randomized, reviews are missing for some orders, and residual confounding and selection bias may remain.")

left, right = st.columns([1.35, 1], gap="large")
with left:
    st.plotly_chart(association_forest(timing, research), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Unadjusted and adjusted odds ratios for low review among late versus on-time delivered orders, with 95 percent confidence intervals.")
    c = repo.contract("research_results")
    source_caption(c.grain, c.observation, c.source, repo.source_url("research_results"))
with right:
    st.subheader("Model diagnostics")
    st.markdown(f"**Convergence**  \n{'Yes' if model['converged'] else 'No'} · {model['iterations']} iterations")
    st.markdown(f"**In-sample discrimination**  \nAUC {model['auc']:.3f}")
    st.markdown(f"**In-sample probability error**  \nBrier score {model['brier_score']:.3f}")
    st.markdown(f"**Adjusted absolute difference**  \n{model['standardized_risk_difference']*100:.2f} pp (95% CI {model['risk_difference_ci_95_low']*100:.2f}–{model['risk_difference_ci_95_high']*100:.2f})")
    st.caption("AUC and Brier score are in-sample diagnostics, not external validation performance.")

st.subheader("Where is lateness elevated?")
dimension = st.radio("Dimension", ["State", "Order-attributed category"], horizontal=True)
if dimension == "State":
    fig = ranked_late_rates(states, "customer_state")
    key = "delivery_state"
else:
    fig = ranked_late_rates(categories, "attributed_category")
    key = "delivery_category"
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt=f"Ranked late-delivery rates by {dimension.lower()} among groups with at least five hundred eligible orders.")
c = repo.contract(key)
source_caption(c.grain, c.observation, c.source, repo.source_url(key))

st.subheader("Robustness and heterogeneity")
left, right = st.columns([1.2, 1], gap="large")
with left:
    st.plotly_chart(heterogeneity_chart(research), width="stretch", config={"displayModeBar": False, "displaylogo": False}, alt="Exploratory I squared heterogeneity estimates across month, state, and category subgroups.")
with right:
    st.markdown("**Missing-review sensitivity**")
    st.markdown(f"Observed low-review risk difference: {bounds['observed_risk_difference']*100:.2f} pp")
    st.markdown(f"Extreme-case range: {bounds['worst_case_minimum']*100:.2f}–{bounds['worst_case_maximum']*100:.2f} pp")
    st.caption(f"Missing order-level reviews: {int(bounds['late_missing_reviews'])} late and {int(bounds['on_time_missing_reviews'])} on-time/early.")
    st.markdown("**Sensitivity models**")
    single = research["delivery_satisfaction"]["single_seller_sensitivity"]
    score1 = research["delivery_satisfaction"]["score_one_sensitivity"]
    st.markdown(f"Single-seller OR {single['late_odds_ratio']:.2f} (95% CI {single['late_or_ci_95_low']:.2f}–{single['late_or_ci_95_high']:.2f})")
    st.markdown(f"One-star outcome OR {score1['late_odds_ratio']:.2f} (95% CI {score1['late_or_ci_95_low']:.2f}–{score1['late_or_ci_95_high']:.2f})")

st.caption(f"Coverage: {int(coverage['delivered_orders']):,} delivered · {int(coverage['timing_eligible_orders']):,} timing eligible · {int(coverage['reviewed_orders']):,} reviewed · {int(coverage['inference_eligible_orders']):,} inference eligible.")
st.download_button("Download state aggregate", repo.export_csv("delivery_state"), "delivery_state_aggregate.csv", "text/csv")

