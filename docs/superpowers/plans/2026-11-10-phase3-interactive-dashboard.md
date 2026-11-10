# Phase 3 Interactive Analytics Portfolio Implementation Plan

> **For agentic workers:** Implement this plan checkpoint-by-checkpoint in the current session. Steps use checkbox (`- [ ]`) syntax. Do not commit or push.

**Goal:** Build a four-page Streamlit/Plotly portfolio dashboard that presents the verified Phase 1–2.5 evidence without redefining metrics.

**Architecture:** A pure data-contract layer reads only checked-in aggregate CSV/JSON outputs; page modules consume typed bundles and Plotly figure builders. SQLite is optional and used only for source-availability diagnostics, so the published dashboard has useful empty states without licensed raw data.

**Tech Stack:** Python 3.11, Streamlit, pandas, Plotly, unittest, Streamlit AppTest.

**Spec:** User-supplied “Phase 3 — Interactive Analytics Portfolio” mission dated 2026-11-10.

## Global Constraints

- Preserve Phase 1–2.5 metrics and historical research outputs.
- Never read or export customer-level extracts from the dashboard.
- Label populations, units, dates, in-sample diagnostics, uncertainty, censoring, and non-causality.
- Provide missing-output and missing-database states; do not require SQLite for aggregate dashboard startup.
- Keep raw data, databases, credentials, and customer-level exports out of Git.
- Implement and verify checkpoints 3A, 3B, and 3C; do not commit or push.

## Review Focus

- A displayed KPI must equal the checked-in authoritative output exactly; add anchor tests.
- Missing aggregate files must return a precise recovery command instead of a traceback; test an empty directory.
- Charts must retain fixed dimensions, accessible labels, uncertainty and censoring marks; test figure contracts.
- Download controls must expose aggregated rows only and never `rfm_customers.csv` or mart/customer data; assert the allowlist.
- Every page must start under AppTest with no uncaught exception and remain usable without SQLite; smoke test all four page files.

---

### Checkpoint 3A: Dashboard architecture and data contracts

**Files:** Create `dashboard/data.py`, `dashboard/ui.py`, `dashboard/charts.py`, `dashboard/__init__.py`, `.streamlit/config.toml`, `app/streamlit_app.py`, `tests/test_dashboard_data.py`; modify `requirements.txt`.

**Interfaces:** `DashboardRepository(root).load_*()` returns aggregate DataFrames/dicts; `DataUnavailable` carries missing paths and recovery commands. `EXPORT_ALLOWLIST` contains aggregate-only artifacts.

- [x] Add tests for Phase 1/2.5 metric anchors, required columns/types, absent-output recovery, and export safety.
- [x] Implement cached aggregate readers, provenance metadata, formatting helpers, shared app shell, and chart tokens.
- [x] Install declared dependencies and verify the default app route starts.

### Checkpoint 3B: Four analytical pages

**Files:** Create `app/views/01_executive_overview.py`, `02_customer_intelligence.py`, `03_delivery_research.py`, `04_methodology.py`; extend `dashboard/charts.py` and `dashboard/ui.py`. (`views/` avoids Streamlit legacy `pages/` deep-link bypass.)

**Interfaces:** Each page renders from `DashboardRepository`, declares its question/finding, and cites aggregate/SQL lineage. Figure functions return deterministic Plotly `Figure` objects.

- [x] Build overview KPI strip, monthly trend, Pareto concentration, actions and evidence rail.
- [x] Build cohort heatmap, censoring/maturity explanation, RFM snapshot, KM curve with CI, and stability warning.
- [x] Build state/category late-rate views, adjusted/unadjusted estimates, diagnostics, heterogeneity and missing-review sensitivity with explicit non-causality.
- [x] Build methodology lineage, definitions, quality checks, assumptions, commands, test status, licensing and optional-database state.
- [x] Run AppTest and metric checks after all four pages.

### Checkpoint 3C: Validation, visual QA and documentation

**Files:** Create `tests/test_dashboard_charts.py`, `tests/test_dashboard_smoke.py`, `docs/PHASE3_DATA_CONTRACTS.md`, `reports/PHASE3_IMPLEMENTATION.md`, `visualizations/screenshots/*`; modify `README.md` and `.gitignore` if required.

**Interfaces:** Smoke tests start every page; chart tests pin dimensions/traces/labels; README provides setup, screenshots, deployment and data-license constraints.

- [x] Verify all existing/new tests, Streamlit headless startup and aggregate-only export policy.
- [x] Run the app-screen lint/inspect gate at desktop/tablet/phone, capture screenshots, critique, fix the top visual issues, and rerun.
- [x] Validate responsive CSS, keyboard/focus states, chart captions, missing-data cases, tracked-file hygiene and licensing notes.
- [x] Document precomputed versus dynamic data, local/cloud deployment, exact commands and final test evidence.
