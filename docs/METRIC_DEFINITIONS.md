# Metric Definitions

## Cohort policy

Unless a query explicitly says otherwise, business KPIs include only `orders.order_status = 'delivered'`. Delivered orders are the closest available proxy for completed fulfillment. Canceled, unavailable, created, approved, invoiced, processing, and shipped orders are excluded because merchandise activity may not be final. The quality report still profiles every status.

Time series assign an order to the calendar month of `order_purchase_timestamp`, not approval, shipping, or delivery month.

## Merchandise value

```sql
SUM(order_items.price)
```

Computed for items attached to delivered orders. Freight is excluded. This is merchandise value, not accounting revenue, gross merchandise value under every possible industry definition, payment receipts, or profit. Payment totals are not substituted for item prices because they can include freight and can have multiple rows per order.

## Order count and monthly trend

- **Order count:** `COUNT(DISTINCT order_id)` within the delivered cohort. Queries that first aggregate to one row per order can safely use `COUNT(*)`.
- **Monthly merchandise trend:** delivered merchandise value by purchase month.
- **Average merchandise value per order:** monthly merchandise value divided by delivered orders represented in `order_items`.
- **Month-over-month change:** `(current_month - previous_month) / previous_month`; the first month and any zero-base comparison return `NULL`.

The checked-in monthly query pre-aggregates items to order grain and uses `LAG`.

## Product and category sales distribution

- **Product/category merchandise value:** sum of item price within delivered orders.
- **Delivered orders:** distinct delivered orders containing the product/category.
- **Share:** category merchandise value divided by delivered merchandise value represented in categorized plus uncategorized items.
- Missing category is labeled `[uncategorized]`; untranslated Portuguese categories retain the source category name.
- Ranked and cumulative shares are computed with window functions.

## Customer repeat purchase

Customer identity uses `customers.customer_unique_id`, never `customer_id` (which is order-specific). A repeat purchaser is a unique customer with at least two distinct delivered orders:

```sql
HAVING COUNT(DISTINCT o.order_id) >= 2
```

This is observed repeat ordering inside the dataset's marketplace/time coverage, not lifetime retention. The dataset does not prove a complete acquisition cohort or all customer activity outside Olist.

## Acquisition cohorts and retention

- **Acquisition cohort:** calendar month of a customer's first delivered purchase, keyed by `customer_unique_id`.
- **Month N retention:** share of the original cohort with at least one delivered purchase in the exact Nth calendar month after acquisition. Month 0 is 100% by construction.
- **Month 4+ return:** share with at least one delivered purchase in any observed month at offset 4 or later; unlike exact-month retention, it is an ever-returned-after-month-4 measure.
- **Cohort repeat purchase rate:** share with at least two distinct delivered orders anywhere in the observed history, including multiple orders in the acquisition month. It is therefore distinct from exact-month retention.
- **Censoring:** a retention cell is `NULL` when the dataset's last delivered purchase month (`2018-08`) is earlier than the cell's required follow-up month. An observed month with no returning customers is zero.

The first/last months and very small early cohorts are sparse. Cohorts are based on first purchase *observed in this dataset*, not proven lifetime acquisition, and activity after August 2018 is unknown.

## RFM segmentation

The reproducible cutoff is `2018-09-01 00:00:00`; delivered purchases at or after it are excluded.

- **Recency:** integer calendar days from `2018-09-01` to the date of the last delivered purchase.
- **Frequency:** distinct delivered orders before cutoff.
- **Monetary:** sum of item price before cutoff, excluding freight.
- **R score:** 5/4/3/2/1 for recency of at most 90/180/270/365/over 365 days.
- **F score:** 1 for one order, 3 for two, and 5 for three or more. This preserves the large one-order tie instead of splitting it into artificial quintiles.
- **M score:** 1/2/3/4/5 for merchandise value below BRL 50/100/200/500, or at least BRL 500.

All equal values receive equal scores. Segment labels are deterministic combinations of these scores. “Inactive in observed window” describes recency inside the historical sample and is not a claim that the customer truly churned.

## Sales and category intelligence

Phase 2 preserves the Phase 1 monthly and category definitions. It adds a raw month-over-month value change plus an `interpretable_mom_pct` that is populated only when both months have at least 100 delivered orders and neither is a boundary month. Category mix changes are likewise interpreted only for consecutive, sufficiently represented, non-boundary months. The 100-order rule is a transparent descriptive guardrail, not a statistical completeness guarantee.

## Delivery timeliness

Eligible records are delivered orders with both actual and estimated customer-delivery timestamps.

- **Late:** `order_delivered_customer_date > order_estimated_delivery_date` using full timestamps.
- **On time or early:** actual timestamp is less than or equal to estimated timestamp.
- **Days versus estimate:** actual minus estimated timestamp in fractional days; positive means late.

Missing delivery timestamps are excluded from timeliness rates and separately flagged by quality checks.

## Review score distribution

Scores are constrained to the source scale 1–5. A source-record distribution groups non-null `review_score` values and reports both count and share; its grain must be labeled **review records**, because an order can have multiple review rows. When the unit of analysis is an order, as in the delivery comparison, multiple review rows are first averaged to one order-level score before joining to orders. This prevents review count from weighting or duplicating the order. `reviewed_orders` is reported so missing-review coverage remains visible, and low-review share uses reviewed orders—not all delivered orders—as its denominator. A score of 1 or 2 is classified as low for the descriptive comparison.

Delivery timing and review score are observational associations. Customer mix, product, seller, region, seasonality, and other confounders are not controlled, so results are not causal.

Phase 2 assigns each delivered order to exactly one category for delivery analysis: a single-category order keeps that category; a mixed order is assigned to the category with the greatest item-price value, with alphabetical tie-breaking. Mixed-order counts are reported. Statistical comparisons use the order as the analysis unit, Wilson 95% intervals for proportions, large-sample mean/proportion tests, and a Cochran–Mantel–Haenszel test stratified by purchase month, customer state, and merchandise-value band. These adjustments address only observed covariates and do not support causal claims.

## Unsupported metrics

The source lacks site sessions/visitors, ad exposure and spend, cost of goods, complete operating costs, and randomized assignments. It therefore cannot directly establish:

- true ecommerce conversion rate;
- return on ad spend (ROAS);
- customer acquisition cost (CAC);
- product or order profit/margin;
- causal or randomized A/B-test lift.
