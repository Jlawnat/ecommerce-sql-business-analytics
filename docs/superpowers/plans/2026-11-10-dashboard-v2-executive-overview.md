# Dashboard V2 Executive Overview Implementation Plan

> **For agentic workers:** Implement natively in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and visually verify a standalone premium Next.js Executive Overview that publishes only validated non-customer aggregates.

**Architecture:** A deterministic Python publisher validates checked-in Phase 2 CSVs and writes one versioned JSON contract into `web/public/data`. A static Next.js App Router client validates that contract again, renders a responsive Monitor surface, and leaves the Streamlit application untouched.

**Tech Stack:** Next.js App Router, React, TypeScript, Tailwind CSS 4, Recharts, Lucide, Python standard library.

**Spec:** `docs/design-v2/{DESIGN_AUDIT,DESIGN_SYSTEM,INFORMATION_ARCHITECTURE}.md`

## Global Constraints

- No raw CSV, SQLite, customer-level records, or mock metrics in the frontend bundle.
- Preserve all Phase 1–2.5 definitions and exact aggregate values.
- Implement Executive Overview only; no production Streamlit changes; no commit or push.
- Check 1440, 1024, 768, and 390 widths with no page-level horizontal overflow.

## Review Focus

- Long BRL values must never collide or truncate.
- The 2018 filter must not imply August is complete.
- CSV export must contain only the currently displayed allowlisted month-level aggregate.
- Chart tooltips and annotations must retain units and historical scope.
- Navigation for unimplemented pages must not masquerade as working links.

---

### Task 1: Aggregate publication contract

**Files:** Create `scripts/publish_web_aggregates.py`, `web/lib/contracts.ts`, `web/public/data/executive-overview.json`; test `tests/test_web_data_contract.py`.

- [ ] Validate exact source paths, columns, types, observation statuses, totals, ordering, and Pareto monotonicity.
- [ ] Publish only month-grain sales and category-grain Pareto rows plus derived values proven from those rows.
- [ ] Revalidate the JSON contract in TypeScript before rendering.

### Task 2: Frontend foundation and design system

**Files:** Create `web/package.json`, framework config, `web/app/{layout,page,globals}.tsx`, shared UI components.

- [ ] Implement framed-sheet shell, responsive navigation, tokens, focus, loading/error states, and all named reusable primitives.
- [ ] Keep future destinations disabled and labelled as planned.

### Task 3: Executive Overview

**Files:** Create `web/components/executive-overview.tsx`, `web/components/charts/*.tsx`.

- [ ] Render exact KPI semantics, functional period filters, trend, Pareto, decision priorities, sources, caveat, and aggregate-only export.
- [ ] Add accessible summaries and responsive chart adaptations.

### Task 4: Verification and visual repair

**Files:** Update V2 QA notes and screenshots under `visualizations/screenshots/v2/`.

- [ ] Run publisher tests, existing Python suite, lint, TypeScript/build, and production server.
- [ ] Inspect 1440/1024/768/390 screenshots, run app lint/inspector, fix visible and measured failures, then repeat.

