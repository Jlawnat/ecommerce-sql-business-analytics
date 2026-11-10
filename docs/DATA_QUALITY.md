# Data Quality Framework

Run all checks with:

```bash
python3 scripts/run_analysis.py --query 00_data_quality.sql
```

The source-of-truth checks are in [`sql/analysis/00_data_quality.sql`](../sql/analysis/00_data_quality.sql). They execute in the following order:

1. **Row counts:** all nine normalized tables.
2. **Missingness:** mandatory and analytically important optional fields in orders, products, and reviews.
3. **Duplicate keys:** every asserted natural or composite source key. SQLite constraints also reject duplicates during ingestion.
4. **Join coverage:** order coverage for customers, items, payments, and reviews, with child tables reduced to distinct order IDs before joining.
5. **Order statuses:** full status distribution; KPIs subsequently use only delivered orders.
6. **Event chronology:** approval before purchase, carrier handoff before approval, delivery before carrier, delivered status without actual delivery timestamp, and actual delivery after estimate.
7. **Child cardinality and fan-out:** counts multi-item, multi-payment, and multi-review orders and compares the potential naive three-child join size with source item rows.
8. **Product categories:** missing source category and source categories lacking an English translation.
9. **Unusual delivery dates:** actual or estimated delivery before purchase and actual duration over 365 days.

## Fan-out rule

Never directly join `order_items`, `order_payments`, and `order_reviews` and then aggregate money. Each is one-to-many from orders. For an order with two items, two payments, and two reviews, a naive join can produce eight rows and duplicate item price. Aggregate each domain to one row per order first, then join the aggregates. Category analysis may remain at item grain but must not join unaggregated payments or reviews.

## Load-time enforcement

The loader also provides:

- exact nine-file and required-column validation;
- explicit numeric/timestamp parsing with file, row, and column diagnostics;
- primary, composite, foreign-key, non-negative-price, and review-score checks;
- a post-load `PRAGMA foreign_key_check`;
- staging plus atomic replacement, so invalid input cannot corrupt the last good database;
- complete rebuild semantics, making reruns idempotent.

## Interpretation

Quality flags are not silently repaired. They remain traceable to the source and should be quantified before analysis. Missing optional lifecycle fields can be expected for some statuses, while impossible chronology or broken required relationships warrants investigation. No full-dataset quality counts are claimed until the real CSV files are loaded.
