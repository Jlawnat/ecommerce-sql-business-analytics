# SQL engineering highlights

## Source design

[`sql/schema/001_create_tables.sql`](../../sql/schema/001_create_tables.sql) creates nine normalized source tables with primary/composite keys, foreign keys, type checks, non-negative price constraints, review-score bounds, and indexes. [`src/ingest.py`](../../src/ingest.py) stages a complete rebuild and atomically replaces the previous database only after validation succeeds.

## Grain and fan-out prevention

Items, payments, and reviews are all one-to-many children of an order. Joining all three before aggregation duplicates facts: the Phase 1 audit measured 118,307 naive child-join rows versus 112,650 source item rows, an excess of 5,657 rows (about 5.02%).

The repository therefore follows these rules:

- merchandise value remains additive at item grain;
- payments and reviews are reduced to one row per order before joining;
- multiple reviews are averaged to one order-level score for delivery research;
- category delivery analysis deterministically assigns one dominant-value category per order;
- customer analysis uses `customer_unique_id`, not order-specific `customer_id`;
- every mart declares its binding grain before facts are materialized.

See [`00_data_quality.sql`](../../sql/analysis/00_data_quality.sql), [`001_build_analytics_mart.sql`](../../sql/marts/001_build_analytics_mart.sql), and the [data-quality framework](../DATA_QUALITY.md).

## Analytical SQL map

| Module | Purpose |
|---|---|
| [`01_monthly_merchandise_value.sql`](../../sql/analysis/01_monthly_merchandise_value.sql) | Delivered merchandise value at purchase-month grain |
| [`02_category_sales_concentration.sql`](../../sql/analysis/02_category_sales_concentration.sql) | Ranked category value and cumulative share |
| [`05_customer_cohort_retention.sql`](../../sql/analysis/05_customer_cohort_retention.sql) | Acquisition cohorts, exact-month returns, and censoring |
| [`06_rfm_segmentation.sql`](../../sql/analysis/06_rfm_segmentation.sql) | Fixed-cutoff, tie-preserving RFM scoring |
| [`08_delivery_segment_analysis.sql`](../../sql/analysis/08_delivery_segment_analysis.sql) | State/category timing diagnostics at order grain |
| [`09_repeat_purchase_research.sql`](../../sql/analysis/09_repeat_purchase_research.sql) | Time-to-second-purchase population |
| [`10_delivery_satisfaction_research.sql`](../../sql/analysis/10_delivery_satisfaction_research.sql) | Adjustment profiles, subgroup tables, and missing-review inputs |

## Integrity assertions

The separate analytics mart runs 12 blocking assertions covering source populations, unique keys, foreign keys, required fields, monetary reconciliation, customer cutoff eligibility, reviewed-order population, and SQLite foreign-key integrity. A failed assertion prevents replacement of the last good mart. The independent evidence is in [Phase 2.5 audit](../PHASE25_AUDIT.md) and [`tests/test_analytics_mart.py`](../../tests/test_analytics_mart.py).
