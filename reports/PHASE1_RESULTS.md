# Phase 1 Results

**Run date:** 2026-11-10 (Australia/Sydney)  
**Status:** Complete against all nine manually supplied Olist CSVs.

## Dataset acquisition

All nine expected CSV files were detected in `data/raw/` after manual placement. The database was built from those files without Kaggle credentials. Raw files, Windows download metadata, and the generated database are ignored by Git; see [`docs/DATA_SOURCE.md`](../docs/DATA_SOURCE.md) for the reproducible acquisition procedure.

## Database and verified counts

The loader and independent SQL recount produced the same table counts:

| Table | Rows |
|---|---:|
| `customers` | 99,441 |
| `geolocation` | 1,000,163 |
| `orders` | 99,441 |
| `order_items` | 112,650 |
| `order_payments` | 103,886 |
| `order_reviews` | 99,224 |
| `products` | 32,951 |
| `sellers` | 3,095 |
| `category_translation` | 71 |

The build completed with no post-load foreign-key violations. Asserted customer, order, order-item, payment, product, and seller key duplicate groups were all zero.

## Implemented analyses

All commercial figures use only `order_status = 'delivered'`. Merchandise value is item `price` only and excludes freight.

- **Delivered orders:** 96,478. All 96,478 had at least one item.
- **Delivered merchandise value:** BRL 13,221,498.11; average BRL 137.04 per delivered order.
- **Customer repeat behavior:** 93,358 unique delivered customers by `customer_unique_id`; 2,801 had at least two delivered orders, a 3.00% observed repeat-customer share within dataset coverage.
- **Monthly trend:** the highest monthly merchandise value was May 2018 at BRL 977,544.69. The highest delivered-order count was November 2017 at 7,289. Sparse early months (including only one represented delivered order in September and December 2016) make their month-over-month percentages unsuitable for trend interpretation.
- **Category concentration:** `health_beauty` ranked first at BRL 1,233,131.72 and 9.33% of delivered merchandise value. The top five categories represented 39.83%; the top ten represented 62.43%. Uncategorized items represented BRL 170,726.63, or 1.29%.
- **Delivery and reviews:** among 96,470 delivered orders eligible for timeliness analysis, 7,826 were late (8.11%). Late orders with reviews averaged 2.57 versus 4.29 for on-time/early orders. Low-score share (1–2) was 53.99% for late versus 9.19% for on-time/early orders. This is an observed association, not a causal effect.
- **Review records:** delivered-order review records were 9.76% score 1, 3.05% score 2, 8.26% score 3, 19.70% score 4, and 59.22% score 5. This distribution is explicitly record-weighted; 95,832 delivered orders had at least one non-null review score.

## Tests

Command:

```bash
python3 -m unittest discover -s tests -v
```

Observed result on 2026-11-10: **11 tests passed, 0 failed** (`Ran 11 tests ... OK`). Coverage includes the exact source manifest, missing-file diagnostics, ingestion and timestamp/null parsing, primary/composite-key enforcement, foreign keys, failure atomicity, idempotent reruns, monthly and summary KPI reconciliation, repeat-customer logic, category shares, review pre-aggregation and missing-review denominators, and demonstrated naive-join fan-out risk.

## Data-quality results

Measured issues and coverage gaps:

- 160 orders lacked approval timestamps; 2,965 lacked customer-delivery timestamps. Eight records labeled `delivered` lacked an actual customer-delivery timestamp.
- 775 orders had no item rows, one had no payment row, and 768 had no review row. Required parent relationships passed foreign-key validation.
- 610 of 32,951 products lacked a source category; 13 categorized product rows lacked an English translation.
- Optional review text was sparse: 87,658 review rows lacked a title and 58,274 lacked a message.
- Chronology checks found 1,359 carrier timestamps before approval and 23 customer-delivery timestamps before carrier handoff. No approval preceded purchase; no actual/estimated delivery preceded purchase; no measured purchase-to-delivery duration exceeded 365 days.
- 9,803 orders had multiple items, 2,961 had multiple payments, and 547 had multiple review rows. A naive join of all three child domains would produce 118,307 rows versus 112,650 source item rows, an excess of 5,657 rows (about 5.02%) before monetary aggregation.
- The source status distribution was 96,478 delivered, 1,107 shipped, 625 canceled, 609 unavailable, 314 invoiced, 301 processing, five created, and two approved.

## Remaining blocker

No Phase 1 blocker remains. Raw data must still be acquired manually in a fresh clone because licensing and repository hygiene prevent redistribution. The measured quality issues above should remain visible rather than being silently repaired.

## Recommended Phase 2 direction

After the real-data build succeeds and Phase 1 quality outputs are reviewed, Phase 2 should turn the validated KPIs into a compact exploratory notebook or dashboard with time-series, category concentration, repeat-customer, and delivery/review views. It should consume the checked-in SQL semantics rather than redefine metrics. Phase 2 was not started here.
