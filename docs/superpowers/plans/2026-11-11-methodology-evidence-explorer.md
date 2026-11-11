# Methodology & Evidence Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the fourth Dashboard V2 page as an interactive, traceable research explorer without changing analytical definitions or exposing restricted data.

**Architecture:** Store reviewed methodology copy and repository paths in a typed frontend content module. Render it through one client component that owns pipeline selection, metric filtering, and progressive disclosure, while reusing `ApplicationShell` and global V2 tokens. Add source-link contract tests and validate all four routes in production and real browsers.

**Tech Stack:** Next.js 16, React 19, TypeScript, plain CSS, Lucide, Python `unittest`, Chrome DevTools Protocol.

**Spec:** User request “Dashboard V2 — Methodology & Evidence Explorer”, 2026-11-11.

## Global Constraints

- Do not modify the research engine, existing KPI definitions, Streamlit, raw data, customer-level records, or privacy guardrails.
- Every displayed result must trace to validated aggregate outputs or documented research sources.
- Do not commit, push, merge, or deploy.
- Preserve the approved V2 framed-sheet design system and all existing pages.

## Review Focus

- A search with no metric matches must show an accessible empty state and retain filter controls.
- Source links must resolve to tracked repository paths and never target raw data, databases, or customer-level exports.
- Pipeline and method controls must be keyboard operable and expose selected state to assistive technology.
- Dense evidence content must not cause page-level horizontal overflow at 390px.
- Existing four-page navigation and all pre-existing aggregate contracts must remain valid.

---

### Task 1: Typed evidence catalogue and traceability tests

**Files:**
- Create: `web/lib/methodology-content.ts`
- Modify: `tests/test_web_data_contract.py`

**Interfaces:**
- Produces: typed `pipelineStages`, `metricDefinitions`, `statisticalMethods`, `qualityEvidence`, and `evidenceResources` collections.
- Produces: repository-relative `sources` values suitable for GitHub links.

- [ ] Add tests asserting the methodology catalogue exists, source paths are tracked and allowlisted, and restricted raw/customer assets are absent.
- [ ] Run the focused contract tests and confirm the new assertions fail before implementation.
- [ ] Implement the catalogue using only `docs/`, `reports/`, `sql/`, `scripts/`, and aggregate contract sources already reviewed.
- [ ] Re-run the focused contract tests and confirm they pass.

### Task 2: Interactive Methodology page

**Files:**
- Create: `web/app/methodology/page.tsx`
- Create: `web/components/methodology-evidence.tsx`
- Modify: `web/components/sidebar-navigation.tsx`
- Modify: `web/app/globals.css`

**Interfaces:**
- Consumes: collections from `web/lib/methodology-content.ts`.
- Produces: `/methodology`, pipeline stage selection, metric search/family filters, expandable method details, evidence links, and reproduction guidance.

- [ ] Add the route and enable its navigation destination.
- [ ] Implement the pipeline selector with selected-stage grain, checks, outputs, and source links.
- [ ] Implement the metric dictionary search/filter with definition, unit, denominator, window, exclusions, missingness, and SQL lineage.
- [ ] Implement statistical method disclosures covering cohort censoring, RFM sensitivity, selected-horizon KM estimates, logistic adjustment, OR versus risk difference, diagnostics, and robustness.
- [ ] Implement Phase 1 quality findings, mart integrity assertions, deterministic publishing, evidence/licensing, download policy, and observational limitations.
- [ ] Add responsive V2 CSS with visible focus, 44px mobile controls, and no page-level horizontal scroll.

### Task 3: Automated validation

**Files:**
- Modify only if validation reveals a defect in the files above.

- [ ] Run `npm run typecheck` in `web` and fix all failures.
- [ ] Run `npm run lint` in `web` and fix all failures.
- [ ] Run `npm run build` in `web` and verify all four routes build.
- [ ] Run `.venv/bin/python -m unittest discover -s tests -v` and verify the full Python/SQL and frontend contract suite.
- [ ] Run the app-screen design linter and resolve or document every warning.

### Task 4: Four-page browser QA and evidence capture

**Files:**
- Create: `visualizations/screenshots/v2/methodology-*.png`
- Create: `visualizations/screenshots/v2/cross-page-*.png` only when needed to document repaired defects.

- [ ] Start the production server and inspect `/`, `/customer-intelligence`, `/delivery-satisfaction`, and `/methodology` at 1440, 1024, 768, and 390px.
- [ ] Exercise pipeline, metric filter/search, method disclosures, navigation, and external source links using keyboard and pointer interactions.
- [ ] Capture genuine final screenshots and inspect every image for hierarchy, clipping, overflow, and statistical wording.
- [ ] Correct visible defects, rerun affected automated checks, and record any remaining tooling blocker.

## Completion and final app-screen critique

Implementation completed in-session without commit, push, merge or deployment.

1. The screen's first question is answered by the dark evidence-chain introduction and its 9 / 12 / 3 / 4 verified structure counts.
2. All blocks share the content sheet edges; no page-level overflow or unbalanced desktop row was observed at 1440, 1024, 768 or 390px.
3. Colour remains on verified selection, quality status and evidence accents; the tinted frame and IBM Plex face preserve the product identity.
4. Counts and definitions are copied from documented evidence, and every repeated value was checked against its named report or contract.
5. Missingness is described in words; censored retention remains null and observed zero remains zero on the analytical pages.
6. This screen uses no decorative chart legend; source labels match their linked documentation, SQL, code, test or aggregate type.
7. On phone, navigation folds, page controls reach 44px, and the only horizontal movement is contained inside intentional pipeline, method or heatmap scrollers.

