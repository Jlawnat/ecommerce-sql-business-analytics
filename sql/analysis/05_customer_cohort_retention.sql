-- Result 1: one row per monthly acquisition cohort.
-- Cohort identity is customer_unique_id; all activity is delivered-order activity.
-- Retention is purchase-month activity, not survival or churn.
WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value
    FROM order_items
    GROUP BY order_id
),
delivered AS (
    SELECT
        o.order_id,
        c.customer_unique_id,
        date(o.order_purchase_timestamp, 'start of month') AS purchase_month,
        COALESCE(om.merchandise_value, 0.0) AS merchandise_value
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN order_merchandise AS om ON om.order_id = o.order_id
    WHERE o.order_status = 'delivered'
),
customer_first AS (
    SELECT customer_unique_id, MIN(purchase_month) AS cohort_month
    FROM delivered
    GROUP BY customer_unique_id
),
customer_activity AS (
    SELECT
        d.customer_unique_id,
        f.cohort_month,
        d.purchase_month,
        (CAST(strftime('%Y', d.purchase_month) AS INTEGER) - CAST(strftime('%Y', f.cohort_month) AS INTEGER)) * 12
          + CAST(strftime('%m', d.purchase_month) AS INTEGER) - CAST(strftime('%m', f.cohort_month) AS INTEGER) AS month_number
    FROM delivered AS d
    JOIN customer_first AS f USING (customer_unique_id)
    GROUP BY d.customer_unique_id, f.cohort_month, d.purchase_month
),
customer_totals AS (
    SELECT
        d.customer_unique_id,
        f.cohort_month,
        COUNT(DISTINCT d.order_id) AS delivered_orders,
        SUM(d.merchandise_value) AS merchandise_value
    FROM delivered AS d
    JOIN customer_first AS f USING (customer_unique_id)
    GROUP BY d.customer_unique_id, f.cohort_month
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*) AS acquired_customers,
        SUM(delivered_orders >= 2) AS repeat_customers,
        SUM(merchandise_value) AS merchandise_value
    FROM customer_totals
    GROUP BY cohort_month
),
retained AS (
    SELECT cohort_month, month_number, COUNT(*) AS retained_customers
    FROM customer_activity
    GROUP BY cohort_month, month_number
),
observation AS (
    SELECT MAX(purchase_month) AS last_observed_month FROM delivered
)
SELECT
    s.cohort_month,
    s.acquired_customers,
    s.repeat_customers,
    ROUND(100.0 * s.repeat_customers / NULLIF(s.acquired_customers, 0), 2) AS repeat_purchase_rate_pct,
    ROUND(s.merchandise_value, 2) AS cohort_merchandise_value,
    ROUND(s.merchandise_value / NULLIF(s.acquired_customers, 0), 2) AS merchandise_value_per_customer,
    100.0 AS retention_m0_pct,
    CASE WHEN date(s.cohort_month, '+1 month') <= o.last_observed_month
         THEN ROUND(100.0 * COALESCE(MAX(CASE WHEN r.month_number = 1 THEN r.retained_customers END), 0) / s.acquired_customers, 2) END AS retention_m1_pct,
    CASE WHEN date(s.cohort_month, '+2 months') <= o.last_observed_month
         THEN ROUND(100.0 * COALESCE(MAX(CASE WHEN r.month_number = 2 THEN r.retained_customers END), 0) / s.acquired_customers, 2) END AS retention_m2_pct,
    CASE WHEN date(s.cohort_month, '+3 months') <= o.last_observed_month
         THEN ROUND(100.0 * COALESCE(MAX(CASE WHEN r.month_number = 3 THEN r.retained_customers END), 0) / s.acquired_customers, 2) END AS retention_m3_pct,
    CASE WHEN date(s.cohort_month, '+4 months') <= o.last_observed_month
         THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN r.month_number >= 4 THEN a.customer_unique_id END) / s.acquired_customers, 2) END AS retention_m4_plus_pct,
    o.last_observed_month
FROM cohort_sizes AS s
CROSS JOIN observation AS o
LEFT JOIN retained AS r ON r.cohort_month = s.cohort_month
LEFT JOIN customer_activity AS a ON a.cohort_month = s.cohort_month AND a.month_number = r.month_number
GROUP BY s.cohort_month, s.acquired_customers, s.repeat_customers, s.merchandise_value, o.last_observed_month
ORDER BY s.cohort_month;

-- Result 2: long-form heatmap cells. Missing mature activity is zero; immature cells are NULL.
WITH RECURSIVE
delivered AS (
    SELECT
        c.customer_unique_id,
        date(o.order_purchase_timestamp, 'start of month') AS purchase_month
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
),
customer_first AS (
    SELECT customer_unique_id, MIN(purchase_month) AS cohort_month
    FROM delivered
    GROUP BY customer_unique_id
),
activity AS (
    SELECT
        d.customer_unique_id,
        f.cohort_month,
        (CAST(strftime('%Y', d.purchase_month) AS INTEGER) - CAST(strftime('%Y', f.cohort_month) AS INTEGER)) * 12
          + CAST(strftime('%m', d.purchase_month) AS INTEGER) - CAST(strftime('%m', f.cohort_month) AS INTEGER) AS month_number
    FROM delivered AS d
    JOIN customer_first AS f USING (customer_unique_id)
    GROUP BY d.customer_unique_id, f.cohort_month, d.purchase_month
),
cohorts AS (
    SELECT cohort_month, COUNT(*) AS acquired_customers
    FROM customer_first
    GROUP BY cohort_month
),
observation AS (
    SELECT MAX(purchase_month) AS last_observed_month FROM delivered
),
offsets(month_number) AS (
    SELECT 0
    UNION ALL
    SELECT month_number + 1 FROM offsets, observation
    WHERE month_number < (
        (CAST(strftime('%Y', last_observed_month) AS INTEGER) - CAST(strftime('%Y', (SELECT MIN(cohort_month) FROM cohorts)) AS INTEGER)) * 12
        + CAST(strftime('%m', last_observed_month) AS INTEGER) - CAST(strftime('%m', (SELECT MIN(cohort_month) FROM cohorts)) AS INTEGER)
    )
),
retained AS (
    SELECT cohort_month, month_number, COUNT(*) AS retained_customers
    FROM activity
    GROUP BY cohort_month, month_number
)
SELECT
    c.cohort_month,
    x.month_number,
    c.acquired_customers,
    CASE WHEN date(c.cohort_month, printf('+%d months', x.month_number)) <= o.last_observed_month THEN 1 ELSE 0 END AS is_observed,
    CASE WHEN date(c.cohort_month, printf('+%d months', x.month_number)) <= o.last_observed_month
         THEN COALESCE(r.retained_customers, 0) END AS retained_customers,
    CASE WHEN date(c.cohort_month, printf('+%d months', x.month_number)) <= o.last_observed_month
         THEN ROUND(100.0 * COALESCE(r.retained_customers, 0) / c.acquired_customers, 2) END AS retention_rate_pct
FROM cohorts AS c
CROSS JOIN offsets AS x
CROSS JOIN observation AS o
LEFT JOIN retained AS r ON r.cohort_month = c.cohort_month AND r.month_number = x.month_number
ORDER BY c.cohort_month, x.month_number;
