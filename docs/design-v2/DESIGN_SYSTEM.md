# Dashboard V2 Design System

## Foundations

### Color

| Token | Value | Role |
|---|---:|---|
| `canvas` | `#F3F6F6` | Application frame |
| `sheet` | `#FBFCFB` | Primary analytical surface |
| `surface-muted` | `#F5F7F6` | Secondary evidence regions |
| `ink` | `#15211F` | Primary text |
| `ink-muted` | `#586662` | Secondary text, WCAG AA on light surfaces |
| `line` | `#E2E8E5` | Structural boundaries |
| `control` | `#C7D1CD` | Interactive outlines |
| `accent` | `#0B6B69` | Main data and verified selection |
| `accent-2` | `#1F66B2` | Secondary comparison only |
| `positive` | `#287A55` | Semantically favorable state |
| `negative` | `#B73337` | Semantically unfavorable state |
| `warning` | `#9A6200` | Uncertainty, censoring, historical boundary |

Chrome remains below roughly 3% chromatic pixels. No gradients, glass, or resting-card shadows.

### Typography

- Primary: IBM Plex Sans, weights 400/500/600.
- Technical identifiers only: IBM Plex Mono.
- Scale: 12 / 14 / 16 / 22 / 28 / 36 responsive pixels. The 36px insight figure is the single permitted lead number and drops to 30px on mobile.
- All metrics use `font-variant-numeric: tabular-nums`.
- Sentence case throughout; no tracked uppercase labels.

### Grid and spacing

- 4px base; working steps 8, 12, 16, 24, 32, 48.
- Desktop: 228px sidebar, 48px top rail, 8px sheet inset, 24px sheet padding, 12-column content grid.
- Tablet (<=1100px): navigation folds; content remains two-column where each panel retains at least 340px.
- Mobile (<=640px): 16px outer margin; 44px minimum touch targets; charts 180–220px tall; no page-level horizontal scroll.

### Shape and elevation

- Sheet radius 16px; panels 8px; controls 6px; status chips 999px.
- One-pixel borders are permitted for app surfaces and tables.
- Shadows only for menus, tooltips, and dialogs that genuinely float.

### Interaction and accessibility

- Focus: 3px teal outline with 2px offset; never color alone.
- Hover: tonal surface shift or underline; no layout shift.
- Disabled: retains 4.5:1 label contrast and explains unavailable routes.
- `prefers-reduced-motion` removes nonessential transitions.
- Charts include textual summaries, units, periods, denominators, and keyboard-readable tooltips.
- Missing data uses an em dash; observed zero remains `0`.

## Component contracts

- `ApplicationShell`: product identity, responsive navigation, content sheet, skip link.
- `SidebarNavigation`: route-level destinations only; future pages are visibly unavailable until implemented.
- `PageHeader`: noun title, scope, status, and real actions.
- `InsightHero`: one verified finding, its evidence, and a signature data visualization.
- `MetricCard`: label, formatted value, exact accessible value, definition note.
- `EvidenceCard`: decision priority with linked supporting evidence.
- `ChartPanel`: title, analytical question, unit/period, chart, annotation, source.
- `FilterToolbar`: verified time-window control; updates every dependent aggregate.
- `ConfidenceIntervalDisplay`: point estimate plus labelled lower/upper bounds; reserved for uncertainty-bearing pages.
- `ResearchCaveat`: concise amber uncertainty disclosure, expandable when detail is long.
- `SourceLink`: direct code/SQL lineage link with descriptive label.
- `DataStatus`: checked-in snapshot state and observation end.
- `ExportAction`: allowlisted aggregate-only CSV download.

## Chart system

- Trend: straight 2px line, no smoothing, no point markers except hover/annotated boundaries, four horizontal gridlines maximum.
- Pareto: sorted bars for merchandise value plus cumulative-share line and an explicit 80% reference. Top 18 threshold is the lead annotation.
- One hue per subject: merchandise value uses teal; cumulative share uses ink; amber marks uncertainty only.
- Mobile axes use no more than four x labels and never rotate.

