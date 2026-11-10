# Phase 2.5 Research Rigor and Analytics Audit Implementation Plan

> **For agentic workers:** Implement this plan task-by-task in the current session. Steps use checkbox (`- [ ]`) syntax. Do not commit or push; the project brief explicitly prohibits both.

**Goal:** Independently audit Phase 2, add a constrained analytical mart, and produce reproducible retention and delivery-satisfaction research with transparent uncertainty and decision guidance.

**Architecture:** Preserve Phase 1/2 SQL and build a separate SQLite analytical database from the source database using checked-in DDL/DML. Keep research source populations in SQL; use standard-library Python for Kaplan–Meier estimation, sparse binomial logistic regression, diagnostics, sensitivity analyses, and deterministic SVG/JSON/CSV outputs.

**Tech Stack:** SQLite 3, Python 3.11 standard library, `unittest`, SVG, primary-method literature.

**Spec:** User-supplied “Phase 2.5 — Research Rigor and Analytics Audit” mission dated 2026-11-10.

## Global Constraints

- Do not redesign or duplicate existing modules and do not modify raw data.
- Fix confirmed Phase 2 defects before new features; retain validated descriptive and Mantel–Haenszel results.
- Customer non-return is censored observed behavior, never confirmed churn.
- Delivery/review analysis is observational and must not claim causality.
- SQL defines populations and grains; Python performs reproducible estimation and rendering.
- Run every existing and new test, independently reproduce critical figures, and do not commit or push.

## Review Focus

- Administrative censoring must occur at the requested cutoff and never allow post-cutoff second orders; test a post-cutoff purchase.
- The mart must preserve exact order/item/customer/review grains with zero monetary fan-out; test uniqueness and reconciliation.
- Logistic regression must converge on deterministic synthetic data and return finite covariance-based intervals; test known-direction data.
- Missing reviews must remain outside the primary outcome while best/worst-case bounds expose selection sensitivity; test both bounds.
- Published figures must match independently recomputed source-table results to documented precision; assert Phase 1/2 anchors.

---

### Task 1: Independent Phase 2 audit and confirmed fixes

**Files:** Create `docs/PHASE25_AUDIT.md`, `tests/test_phase25_audit.py`; modify Phase 2 files only for confirmed defects.

**Interfaces:** Produces a PASS/WARNING/FAIL matrix with executable checks for population, cutoff, grain, formulas, outputs, and repository hygiene.

- [x] Add independent source-table checks for KPI, cohort, RFM, delivery, output-file, and confidence-interval reproduction.
- [x] Run audit checks, record defects and warnings, fix confirmed defects, and rerun before later tasks.

### Task 2: Tested analytical data mart

**Files:** Create `sql/marts/001_build_analytics_mart.sql`, `sql/marts/002_validate_analytics_mart.sql`, `scripts/build_analytics_mart.py`, `tests/test_analytics_mart.py`; update data documentation.

**Interfaces:** `build_analytics_mart(source: Path, target: Path)` atomically materializes `mart_delivered_orders`, `mart_delivered_order_items`, `mart_customer_snapshot`, and `mart_reviewed_orders` with keys and foreign keys.

- [x] Add fixture tests for grains, uniqueness, nulls, relationships, item/order/customer/review reconciliation, and idempotent atomic rebuild.
- [x] Implement explicit schemas and order-grain pre-aggregation without altering the source database.
- [x] Run mart validations on fixture and real data.

### Task 3: Repeat-purchase survival research

**Files:** Create `sql/analysis/09_repeat_purchase_research.sql`, `scripts/phase25_research.py`, `tests/test_phase25_statistics.py`; create repeat research outputs/charts.

**Interfaces:** Python exposes `kaplan_meier(records, horizons)`, log-log Greenwood intervals, cutoff sensitivity, and RFM stability summaries.

- [x] Test event/censor construction, post-cutoff exclusion, KM estimates/intervals, and cutoff stability calculations.
- [x] Implement first-to-second observed purchase timing and administrative censoring at fixed sensitivity cutoffs.
- [x] Execute KM at 30/60/90/180/365 days and compare RFM classifications across cutoffs without churn labels.

### Task 4: Adjusted delivery-satisfaction research

**Files:** Create `sql/analysis/10_delivery_satisfaction_research.sql`; extend `scripts/phase25_research.py` and statistical tests; create model outputs/charts.

**Interfaces:** SQL returns grouped binomial rows and review-missingness tables. Python exposes sparse IRLS logistic regression, covariance intervals, standardized risk difference, diagnostics, subgroup heterogeneity, and sensitivity models.

- [x] Test grouped-binomial coefficients, odds-ratio intervals, diagnostics, heterogeneity, and missing-review bounds.
- [x] Fit primary adjusted low-review model with month/state/category/value/seller controls; report eligibility and diagnostics.
- [x] Run month/state/category subgroup summaries, heterogeneity tests, missing-review bounds, single-seller restriction, and score-1 alternative outcome.

### Task 5: Research documentation and business decisions

**Files:** Create `docs/PHASE25_STATISTICAL_METHODS.md`, `reports/PHASE25_RESEARCH_RESULTS.md`, `reports/PHASE25_EXECUTIVE_BRIEF.md`; modify `README.md`; create deterministic charts.

**Interfaces:** Documents cite primary/authoritative sources and link every decision recommendation to generated evidence, uncertainty, actions, metrics, and prospective validation.

- [x] Document dimensional modeling, censoring/KM, observational inference, controlled experiments, and data-quality methods with primary references.
- [x] Write at least three complete decision cards and one future randomized experiment without hypothetical outcomes.
- [x] Run all SQL, scripts, tests, independent reconciliations, SVG parsing, causal-language scan, secret/raw-data hygiene checks, and record exact results.
