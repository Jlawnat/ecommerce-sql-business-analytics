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

## Delivery timeliness

Eligible records are delivered orders with both actual and estimated customer-delivery timestamps.

- **Late:** `order_delivered_customer_date > order_estimated_delivery_date` using full timestamps.
- **On time or early:** actual timestamp is less than or equal to estimated timestamp.
- **Days versus estimate:** actual minus estimated timestamp in fractional days; positive means late.

Missing delivery timestamps are excluded from timeliness rates and separately flagged by quality checks.

## Review score distribution

Scores are constrained to the source scale 1–5. A source-record distribution groups non-null `review_score` values and reports both count and share; its grain must be labeled **review records**, because an order can have multiple review rows. When the unit of analysis is an order, as in the delivery comparison, multiple review rows are first averaged to one order-level score before joining to orders. This prevents review count from weighting or duplicating the order. `reviewed_orders` is reported so missing-review coverage remains visible, and low-review share uses reviewed orders—not all delivered orders—as its denominator. A score of 1 or 2 is classified as low for the descriptive comparison.

Delivery timing and review score are observational associations. Customer mix, product, seller, region, seasonality, and other confounders are not controlled, so results are not causal.

## Unsupported metrics

The source lacks site sessions/visitors, ad exposure and spend, cost of goods, complete operating costs, and randomized assignments. It therefore cannot directly establish:

- true ecommerce conversion rate;
- return on ad spend (ROAS);
- customer acquisition cost (CAC);
- product or order profit/margin;
- causal or randomized A/B-test lift.
