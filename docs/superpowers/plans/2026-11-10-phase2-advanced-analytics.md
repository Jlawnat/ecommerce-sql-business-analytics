# Phase 2 Advanced E-Commerce Analytics Implementation Plan

> **For agentic workers:** Implement this plan task-by-task in the current session. Steps use checkbox (`- [ ]`) syntax for tracking. Do not commit: the project brief explicitly prohibits commits and pushes.

**Goal:** Add reproducible cohort, RFM, sales/category, and delivery/satisfaction analytics, validated on the real Olist SQLite database and documented as a portfolio-quality Phase 2 study.

**Architecture:** Keep SQLite SQL as the source of truth and expose each module as a checked-in multi-result query. Add one standard-library Python runner that reads those result sets, performs documented statistical inference, writes machine-readable extracts, and renders reproducible SVG charts without changing Phase 1 tables or queries.

**Tech Stack:** SQLite 3 window functions/CTEs, Python 3.11 standard library, `unittest`, SVG.

**Spec:** User-supplied Phase 2 mission in the 2026-11-10 conversation.

## Global Constraints

- Preserve the Phase 1 delivered-order definition, full-timestamp lateness rule, and merchandise value as item price excluding freight.
- Customer identity is `customer_unique_id`; pre-aggregate every one-to-many child table before cross-domain joins.
- Do not interpret censored cohort cells as zero, boundary-month growth as representative, merchandise value as profit/revenue, or observational delivery associations as causal.
- Use no records after the reproducible RFM cutoff date; report coverage, missingness, uncertainty, and statistical assumptions.
- Preserve all Phase 1 files and tests; do not implement a Phase 3 dashboard; do not commit or push.

## Review Focus

- A cohort month without enough follow-up must emit `NULL` retention, not zero; test an immature month explicitly.
- RFM frequency ties—especially the one-order mass—must stay together rather than be split by arbitrary row-number quintiles; test tied frequencies.
- Orders with multiple items, categories, payments, or reviews must remain one order in order-level outputs; test fan-out and attribution totals.
- Missing delivery/review timestamps must have explicit coverage denominators and never enter inferential samples; test sample reconciliation.
- Sparse first/last months must be flagged and excluded from interpretable month-over-month comparisons; test boundary flags.

---

### Task 1: Cohort retention query

**Files:** Create `sql/analysis/05_customer_cohort_retention.sql`; modify `tests/test_analysis.py`.

**Interfaces:** Consumes delivered orders, customers, and order-item prices. Produces cohort summary plus long-form observed retention cells with `is_observed` and `NULL` for censored rates.

- [x] Add fixture tests for unique-customer acquisition assignment, month-index retention, cohort denominators, value per customer, and right-censoring.
- [x] Implement delivered customer-month CTEs, first-purchase cohorts, integer month offsets, conditional retention, and observed-window flags.
- [x] Run the focused cohort tests and confirm all Phase 1 tests still pass.

### Task 2: RFM segmentation query

**Files:** Create `sql/analysis/06_rfm_segmentation.sql`; modify `tests/test_analysis.py` and `docs/METRIC_DEFINITIONS.md`.

**Interfaces:** Produces one customer-level RFM result set and a segment summary. Uses a fixed cutoff of `2018-09-01 00:00:00`; scores are deterministic threshold/rank rules that preserve ties.

- [x] Add tests for cutoff exclusion, recency, distinct-order frequency, monetary reconciliation, null safety, tied frequency scores, and segment summaries.
- [x] Implement R/F/M distributions and scores, named operational segments, and segment contribution/repeat summaries.
- [x] Document cutoff, scoring/tie policy, and observed-inactivity limitation; run focused and regression tests.

### Task 3: Sales/category intelligence query

**Files:** Create `sql/analysis/07_sales_category_trends.sql`; modify `tests/test_analysis.py`.

**Interfaces:** Produces monthly trend/boundary results, overall Pareto results, and monthly category-mix changes.

- [x] Add tests for merchandise reconciliation, average order value, MoM calculation, cumulative share, and incomplete-boundary flags.
- [x] Implement order-grain monthly trends, Pareto concentration, and category mix delta using windows.
- [x] Run focused and regression tests.

### Task 4: Delivery/satisfaction query and inference

**Files:** Create `sql/analysis/08_delivery_segment_analysis.sql`, `scripts/phase2_analysis.py`; modify `tests/test_analysis.py`.

**Interfaces:** SQL produces coverage, timing comparison, state/category summaries, and month×state×value-band strata. Python exposes deterministic confidence-interval/test helpers and consumes these result sets.

- [x] Add tests for review pre-aggregation, dominant-category attribution with deterministic mixed-category tie handling, order-grain counts, sample coverage, and reproducible interval/test calculations.
- [x] Implement defensible dominant-value order category attribution, region/category comparisons, covariate strata, and missingness outputs.
- [x] Implement Welch-style large-sample mean-difference inference, Wilson intervals, two-proportion tests, and Mantel–Haenszel stratified association with documented assumptions.
- [x] Run focused and regression tests.

### Task 5: Reproducible extracts and visualizations

**Files:** Modify `scripts/phase2_analysis.py`, `scripts/run_analysis.py`, `requirements.txt`; create outputs under `reports/phase2_outputs/` and five SVG files under `visualizations/`.

**Interfaces:** Command accepts `--database`, executes checked-in SQL, writes CSV/JSON evidence and cohort/RFM/monthly/Pareto/delivery-review charts.

- [x] Add deterministic SVG/CSV generation using only the Python standard library and document that no new runtime dependency is required.
- [x] Register Phase 2 SQL files with the existing analysis runner.
- [x] Execute against `data/processed/olist.sqlite` and independently reconcile key totals to Phase 1.

### Task 6: Final documentation and validation

**Files:** Create `reports/PHASE2_RESULTS.md`; modify `README.md`, `docs/METRIC_DEFINITIONS.md`.

**Interfaces:** Report cites generated SQL extracts/statistics and provides exact rerun commands.

- [x] Write the executive summary, methods, verified results, statistical evidence, recommendations tied to findings, limitations/confounders, reproduction steps, and Phase 3 direction.
- [x] Run every SQL file on the real database, run the complete automated suite, inspect generated SVG/XML and output reconciliation, and record exact results.
- [x] Review the worktree to confirm Phase 1 is preserved and no commit was created.
