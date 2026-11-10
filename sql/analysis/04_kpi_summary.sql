-- Portfolio summary KPIs. Commercial metrics use delivered orders only.
-- Every one-to-many domain is reduced to order grain before combination.
WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value
    FROM order_items
    GROUP BY order_id
),
delivered AS (
    SELECT
        o.order_id,
        c.customer_unique_id,
        om.merchandise_value,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN order_merchandise AS om ON om.order_id = o.order_id
    WHERE o.order_status = 'delivered'
),
customer_orders AS (
    SELECT customer_unique_id, COUNT(DISTINCT order_id) AS delivered_order_count
    FROM delivered
    GROUP BY customer_unique_id
),
reviewed_orders AS (
    SELECT DISTINCT r.order_id
    FROM order_reviews AS r
    JOIN delivered AS d ON d.order_id = r.order_id
    WHERE r.review_score IS NOT NULL
)
SELECT
    (SELECT COUNT(*) FROM delivered) AS delivered_orders,
    (SELECT COUNT(merchandise_value) FROM delivered) AS delivered_orders_with_items,
    (SELECT ROUND(SUM(merchandise_value), 2) FROM delivered) AS merchandise_value,
    (SELECT ROUND(AVG(merchandise_value), 2) FROM delivered) AS avg_merchandise_value_per_order,
    (SELECT COUNT(*) FROM customer_orders) AS unique_delivered_customers,
    (SELECT COUNT(*) FROM customer_orders WHERE delivered_order_count >= 2) AS repeat_customers,
    (SELECT ROUND(100.0 * AVG(delivered_order_count >= 2), 2) FROM customer_orders) AS repeat_customer_share_pct,
    (SELECT COUNT(*) FROM delivered
     WHERE order_delivered_customer_date IS NOT NULL
       AND order_estimated_delivery_date IS NOT NULL) AS delivery_timing_eligible_orders,
    (SELECT COUNT(*) FROM reviewed_orders) AS reviewed_delivered_orders;

-- Source-review-record distribution. This is record-weighted, not order-weighted.
WITH delivered_review_records AS (
    SELECT r.review_score
    FROM order_reviews AS r
    JOIN orders AS o ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND r.review_score IS NOT NULL
),
distribution AS (
    SELECT review_score, COUNT(*) AS review_records
    FROM delivered_review_records
    GROUP BY review_score
)
SELECT
    review_score,
    review_records,
    ROUND(100.0 * review_records / SUM(review_records) OVER (), 2) AS review_record_share_pct
FROM distribution
ORDER BY review_score;
