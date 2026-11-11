# Dashboard V2 Delivery Research Implementation Plan

> **For agentic workers:** Implement natively in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the approved Executive Overview and Customer Intelligence evidence displays, then add a complete Delivery & Satisfaction research page from verified Phase 2–2.5 aggregates.

**Architecture:** Extend the deterministic Python publisher with a third aggregate-only contract and stronger semantic assertions for the existing contracts. Keep the approved Next.js shell and premium framed-sheet design, add focused client interactions for RFM and delivery comparisons, and validate every page against the published historical snapshot without exposing row-level data.

**Tech Stack:** Next.js App Router, React, TypeScript, Recharts, Tailwind CSS 4, Python standard library, project unittest and SQL fixtures.

**Spec:** User checkpoint brief dated 2026-11-11 and `docs/design-v2/{DESIGN_AUDIT,DESIGN_SYSTEM,INFORMATION_ARCHITECTURE}.md`

## Global Constraints

- Preserve the approved Executive Overview and Customer Intelligence direction; refine rather than redesign.
- Preserve all Phase 1–2.5 research results and definitions.
- Publish verified aggregates only; no raw customer or order records in the frontend bundle.
- Describe delivery/review findings as observational associations, never causal effects.
- Keep RFM snapshot dates explicit and never treat `Inactive in observed window` as confirmed churn.
- Do not modify Streamlit or implement Methodology V2.
- Do not commit, push, or deploy.

## Review Focus

- The Pareto annotation must identify both the 80% reference and the verified category-18 crossing at 81.29% without clipping at phone width.
- The 2016-12 cohort cell must disclose 1 acquired customer, 1 retained customer, 20 mature observable follow-up months, and an explicit small-sample warning.
- The KM visualization must not interpolate unobserved event times between the five published horizons.
- RFM mode switching must change labels, scales, accessibility copy, and tooltip values while retaining the fixed 2018-09-01 snapshot definition.
- Delivery comparisons must preserve denominators, uncertainty, missing-review bounds, subgroup eligibility rules, and non-causal language at every width.

---

### Task 1: Targeted evidence refinements

**Files:** Modify `scripts/publish_web_aggregates.py`, `web/lib/contracts.ts`, `web/components/charts/category-pareto-chart.tsx`, `web/components/cohort-heatmap.tsx`, `web/components/charts/repeat-incidence-chart.tsx`, `web/components/charts/rfm-distribution-chart.tsx`, `web/components/customer-intelligence.tsx`, and contract tests.

**Interfaces:**
- Consumes: checked-in Pareto, cohort, selected-horizon KM, and RFM aggregate files.
- Produces: stronger customer metadata and UI annotations without changing research definitions.

- [x] Assert the Pareto crossing at rank 18 and 81.29%, then render a labelled threshold marker.
- [x] Assert and publish cohort maturity plus small-sample status, including the verified 2016-12 M1 counts.
- [x] Replace the connected KM curve with discrete selected-horizon estimates and 95% intervals.
- [x] Add an accessible Customers / Merchandise Value RFM comparison and snapshot/churn caveats.
- [x] Run focused data-contract and frontend checks.

### Task 2: Delivery aggregate publication contract

**Files:** Modify `scripts/publish_web_aggregates.py`, `web/lib/contracts.ts`, `tests/test_web_data_contract.py`; create `web/public/data/delivery-satisfaction.json`.

**Interfaces:**
- Consumes: Phase 2 delivery coverage/state/category aggregates and Phase 2.5 model, subgroup, sensitivity, and missing-review results.
- Produces: `DeliverySatisfactionContract` plus `parseDeliverySatisfaction(raw)`.

- [x] Write contract tests for 53.99%, 9.19%, OR 11.41, CI 10.81–12.04, +42.49 pp, diagnostic values, subgroup counts and missing-review bounds.
- [x] Publish only state/category/subgroup aggregate rows and model summaries with explicit denominators and eligibility rules.
- [x] Add strict TypeScript parsing and semantic anchor validation.
- [x] Regenerate all frontend JSON contracts and run the contract suite.

### Task 3: Delivery & Satisfaction research page

**Files:** Create `web/app/delivery-satisfaction/page.tsx`, `web/components/delivery-satisfaction.tsx`, and focused delivery chart components; modify navigation and `web/app/globals.css`.

**Interfaces:**
- Consumes: `DeliverySatisfactionContract`.
- Produces: responsive `/delivery-satisfaction` research view.

- [x] Lead with observed late/on-time risk contrast and adjusted association with confidence intervals.
- [x] Add interactive state and category comparisons that expose sample-size guardrails.
- [x] Show subgroup heterogeneity, model diagnostics, sensitivity results, and missing-review bounds.
- [x] Add evidence-linked recommendations with prospective validation and operational guardrails.
- [x] Keep limitations and observational language adjacent to the corresponding evidence.

### Task 4: Full validation and browser QA

**Files:** Create screenshots under `visualizations/screenshots/v2/`; update only implementation files needed to repair verified defects.

**Interfaces:**
- Consumes: production build and locally served Next.js application.
- Produces: final validation results and desktop/tablet/mobile screenshots.

- [x] Run TypeScript, ESLint, production build, frontend contract tests, and the complete Python/SQL suite with `.venv`.
- [x] Inspect Executive Overview, Customer Intelligence, and Delivery & Satisfaction at desktop, tablet, and mobile widths in a real browser.
- [x] Run the app-screen design linter and equivalent real-Chrome CDP inspection, fix failures and review defensible warnings, then repeat visual inspection.
- [x] Confirm Streamlit and Methodology V2 remain untouched and report remaining blockers in Chinese.
