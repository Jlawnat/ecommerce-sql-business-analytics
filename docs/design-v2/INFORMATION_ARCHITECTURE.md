# Dashboard V2 Information Architecture

## Product shell

1. Executive overview — implemented in Checkpoint V2-B.
2. Customer intelligence — visible as planned, not interactive in this checkpoint.
3. Delivery & satisfaction — visible as planned, not interactive in this checkpoint.
4. Methodology — visible as planned, not interactive in this checkpoint.

The sidebar contains page destinations, not in-page anchors. On tablet and mobile it folds into a 48px header and modal navigation sheet.

## Executive Overview reading order

1. **Scope and trust:** product, historical window, verified aggregate status.
2. **Primary finding:** BRL 13.22M delivered merchandise value is diversified; 18 categories are required to pass 80% of value.
3. **Decision controls:** full/2017/2018 observation window and aggregate-only export.
4. **Core metrics:** delivered orders, merchandise value, average per order, largest-category share.
5. **Historical trajectory:** monthly delivered merchandise value, with incomplete/sparse boundary months explicitly annotated and excluded from interpreted growth claims.
6. **Category concentration:** Pareto evidence with 80% threshold and category rank.
7. **Decision priorities:** retention measurement, fulfilment diagnostics, and category-mix monitoring, each linked to authoritative research/code.
8. **Research boundary and lineage:** historical-only caveat and exact aggregate/SQL provenance.

## First-screen target at 1440×900

The user sees product scope, title, lead finding, all four KPI labels/values, the time-window control, the beginning of the historical trend, and the 80% category threshold. This makes the central decision legible without scrolling while avoiding oversized vanity metrics.

## Responsive reordering

- 1024/768: navigation folds; lead finding precedes a 2×2 metric strip; trend and Pareto stack.
- 390: title + finding, compact metric list, one-row period control, then trend. The Pareto staircase becomes a ranked compact list with the 80% threshold preserved.
- No data field is dropped on mobile; secondary definitions move below values.

## Future page boundaries

- Customer Intelligence owns Kaplan–Meier uncertainty, cohort censoring, RFM, and snapshot stability.
- Delivery & Satisfaction owns absolute risk differences, adjusted odds ratio, confidence interval, heterogeneity, sensitivity, and diagnostics.
- Methodology owns pipeline, source attribution, KPI dictionary, SQL lineage, validation, limitations, and repository links.

These boundaries prevent the Executive Overview from becoming a catch-all research console.

