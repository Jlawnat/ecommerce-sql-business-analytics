-- Association only, not a causal estimate. One row per timeliness group.
-- Multiple source review rows are first averaged to one score per order.
WITH review_per_order AS (
    SELECT order_id, AVG(review_score) AS order_review_score
    FROM order_reviews
    WHERE review_score IS NOT NULL
    GROUP BY order_id
),
eligible_orders AS (
    SELECT
        o.order_id,
        CASE
            WHEN datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date)
                THEN 'late'
            ELSE 'on_time_or_early'
        END AS delivery_timing,
        julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS days_vs_estimate,
        r.order_review_score
    FROM orders AS o
    LEFT JOIN review_per_order AS r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT
    delivery_timing,
    COUNT(*) AS delivered_orders,
    COUNT(order_review_score) AS reviewed_orders,
    ROUND(AVG(order_review_score), 2) AS avg_review_score,
    ROUND(100.0 * AVG(
        CASE
            WHEN order_review_score IS NULL THEN NULL
            WHEN order_review_score <= 2 THEN 1.0
            ELSE 0.0
        END
    ), 2) AS low_review_share_pct,
    ROUND(AVG(days_vs_estimate), 2) AS avg_days_vs_estimate
FROM eligible_orders
GROUP BY delivery_timing
ORDER BY delivery_timing;
