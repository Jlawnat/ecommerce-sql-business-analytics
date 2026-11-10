# Phase 3 Interactive Analytics Portfolio — Implementation Record

**Status:** Complete on 2026-11-10. No commit or push was performed.

## Checkpoint 3A — architecture and contracts

- Added a four-page `st.navigation` application with a shared responsive evidence-ledger visual system.
- Added cached CSV/JSON contracts covering grain, required schema, observation window, and SQL/Python lineage.
- Kept SQLite optional and constrained downloads to aggregate allowlisted artifacts.
- Reconciled dashboard anchors to 96,478 delivered orders, BRL 13,221,498.11 merchandise value, BRL 137.04 per delivered order, and 95,824 inference-eligible orders.

## Checkpoint 3B — analytical pages

- **Executive overview:** KPI anchors, boundary-aware monthly value, category Pareto, evidence-linked actions.
- **Customer intelligence:** censor-aware cohort heatmap, maturity table, RFM snapshot, KM cumulative repeat incidence and 95% CI, cutoff-stability warning.
- **Delivery & satisfaction:** state/category late rates, unadjusted and adjusted odds ratios, adjusted risk difference, in-sample diagnostics, heterogeneity, missing-review bounds, single-seller and one-star sensitivities, explicit non-causality language.
- **Methodology:** source dictionary, metric definitions, lineage links, data-quality controls, assumptions, limitations, reproduction commands, and optional-database state.

## Checkpoint 3C — validation and visual QA

- All 39 tests passed, including all pre-existing Phase 1–2.5 tests plus 13 dashboard data, figure, privacy, route, and startup tests.
- A real headless Streamlit server returned `ok` from `/_stcore/health`.
- AppTest started the entrypoint and every page without uncaught exceptions.
- Browser QA covered 1440, 768, and 390 pixel widths. Final overview, customer, and delivery quality gates each reported zero failures and zero warnings (documented allowances were limited to expected long-page flow and numeric table alignment before the final clean run).
- A real-launch defect missed by the first isolated AppTest was found during browser QA: the entrypoint lacked the repository root on `sys.path`. The entrypoint and its regression test were fixed before screenshots were accepted.
- Cold deep-link testing also exposed Streamlit's legacy `pages/` discovery path bypassing the shared shell. Page modules were moved to `app/views/`, all deep links now pass through `st.navigation`, and a route bootstrap regression test was added.
- Final screenshots were captured only after Plotly completed rendering.

## Verified presentation findings

- Delivered orders: **96,478**; merchandise value: **BRL 13,221,498.11**; average per delivered order: **BRL 137.04**.
- Largest category: **health_beauty, 9.33%** of delivered merchandise value.
- Repeat cumulative incidence: **2.13% at 90 days** (95% CI 2.04%–2.22%) and **3.81% at 365 days** (95% CI 3.66%–3.97%).
- RFM exact-segment stability between 2018-06-01 and 2018-09-01: **57.76%**, Cohen’s κ **0.426** among 75,387 common customers.
- Low-review share: **53.99% late** versus **9.19% on-time/early**.
- Adjusted late-delivery odds ratio: **11.41** (95% CI 10.81–12.04); standardized risk difference **42.49 percentage points** (95% CI 41.30–43.69).

These are historical associations and observed marketplace patterns, not current-market estimates or causal effects.

## Deployment options

1. Local: install `requirements.txt`, then run `.venv/bin/streamlit run app/streamlit_app.py`.
2. Streamlit Community Cloud: select `app/streamlit_app.py` as the entrypoint. Checked-in aggregates are sufficient; no secrets or databases are required.
3. Container or managed Python service: install the locked dependency ranges, expose Streamlit’s port, retain read-only aggregate files, and do not bake raw Olist data or SQLite files into the image.

External deployments must retain Olist attribution and comply with the dataset’s CC BY-NC-SA 4.0 terms.
