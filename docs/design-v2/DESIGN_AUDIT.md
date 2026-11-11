# Dashboard V2 Design Audit

## Scope and evidence reviewed

This audit covers the existing Streamlit Executive Overview, its desktop/mobile screenshots, shared UI primitives, Plotly chart construction, aggregate data contracts, and the Phase 1–2.5 research documentation. The Streamlit application remains the production fallback and is not modified by Dashboard V2.

## Skills and references inspected

- `design-taste-frontend` v2 and its complete `app-screens.md` guidance: established the Monitor surface, medium-density framed-sheet shell, data-first color budget, KPI-strip rules, responsive navigation fold, and mandatory real-browser look-and-fix loop.
- `claude-design` v1.1.0: supplied the surface-first decision, explicit anti-slop diagnostic, state coverage, and the rule that product UI hierarchy precedes decoration.
- `popular-web-designs` v1.0.0: IBM contributed enterprise typography, flat tonal layering, strict spacing, and tabular numeric posture. Linear and Sentry were reviewed as contrasting references but their violet/dark/glow vocabularies were rejected.
- `sketch` v1.0.1: reviewed for its variant-comparison method. It explicitly excludes production implementations, so its stance-comparison method is documented here instead of generating disposable HTML.
- `claude-design` and `writing-plans` together define the repo-native implementation and verification workflow. The implementation plan is stored in `docs/superpowers/plans/2026-11-10-dashboard-v2-executive-overview.md`.

## Existing UX problems

1. **The main finding is typographically subordinate.** The question and answer appear as ordinary body text, so the screen opens as a report header rather than an executive decision surface.
2. **KPI collision at desktop widths.** `BRL 13,221,498.11` visibly collides with `BRL 137.04` in the four-cell metric strip, reducing trust in otherwise correct values.
3. **The mobile first screen is consumed by vertically stacked KPI cells.** The historical trend and decision priorities begin below the first viewport.
4. **Everything uses nearly the same surface treatment.** White cards with identical borders make KPI, caveat, main chart, sources, and decision notes feel equally important.
5. **The Pareto evidence is delayed.** The strongest portfolio insight—18 categories are needed to pass 80% of value—is not the first analytical object.
6. **Annotations are present but detached.** Boundary-month warnings and source lineage sit outside the visual event they explain.
7. **Navigation and product identity are generic.** The small `OE` mark and plain Streamlit navigation do not create a distinctive evidence product.
8. **Controls are framework utilities, not product jobs.** “Deploy” and the overflow menu appear in the screenshots while the real job—changing the historical window or exporting safe aggregates—is visually secondary.
9. **Responsive behavior is stacking rather than recomposition.** Desktop regions simply become a long mobile column, with no first-screen prioritization.
10. **Current slop diagnostic: 3/10.** Default type, equal-weight tile treatment, and a weak Monitor composition fire. Gradients, glass, decorative icon toppers, and rainbow charts are already absent.

## Two coherent directions considered

### Direction A — Quantitative terminal

A true-dark, near-black research console with condensed density, mono numeric treatment, selection lines, and charts designed for prolonged analyst sessions.

- Strengths: unmistakably technical; excellent for comparison and diagnostics.
- Risks: overstates “live monitoring,” makes historical caveats feel secondary, and conflicts with the requested warm analytical canvas.
- Decision: rejected for Executive Overview; useful as a future optional posture for deep methodology inspection only.

### Direction B — Evidence sheet (selected)

The dealt `framed-sheet` app direction (seed `1671233279`): a low-chroma blue-grey L-frame around a white analytical sheet, IBM Plex Sans, one teal/cobalt data family, flat tonal layers, and a 24px evidence grid.

- Strengths: reads as a credible enterprise research product; supports information density without turning the page into a debug console; cleanly separates application scope from evidence.
- Product face: Olist’s 80% category threshold becomes a “Pareto staircase” signature element. It is built from the verified category aggregate and appears in the first desktop screen.
- Primary question: **Where is historical merchandise value concentrated, and which decision deserves attention first?**
- Primary job: change the verified observation window and export the aggregate currently shown.

## Design consequences

- No dark sidebar against a light page: the skill’s measured app guidance found none in credible light screens. The requested deep-nav influence is translated into charcoal typography and a navy product mark inside a cool frame, not a saturated navigation slab.
- No hero marketing composition: `InsightHero` is a compact analytical lead, not a landing-page hero.
- Color belongs to data, status, focus, and one primary action. Amber is reserved for historical uncertainty.
- KPI values use responsive formatting (`BRL 13.22M` with exact values in accessible labels/tooltips) to prevent truncation while preserving numerical consistency.

