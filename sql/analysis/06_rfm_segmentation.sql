-- Fixed analysis cutoff: records at or after 2018-09-01 00:00:00 are excluded.
-- Scores use explicit business-readable bands, so equal values always receive equal scores.
-- Frequency deliberately does not force the predominantly one-order population into quintiles.
WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value
    FROM order_items
    GROUP BY order_id
),
customer_rfm AS (
    SELECT
        c.customer_unique_id,
        CAST(julianday('2018-09-01') - julianday(date(MAX(o.order_purchase_timestamp))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency_orders,
        SUM(COALESCE(om.merchandise_value, 0.0)) AS monetary_value
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN order_merchandise AS om ON om.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')
    GROUP BY c.customer_unique_id
),
scored AS (
    SELECT *,
        CASE WHEN recency_days <= 90 THEN 5 WHEN recency_days <= 180 THEN 4
             WHEN recency_days <= 270 THEN 3 WHEN recency_days <= 365 THEN 2 ELSE 1 END AS r_score,
        CASE WHEN frequency_orders = 1 THEN 1 WHEN frequency_orders = 2 THEN 3 ELSE 5 END AS f_score,
        CASE WHEN monetary_value < 50 THEN 1 WHEN monetary_value < 100 THEN 2
             WHEN monetary_value < 200 THEN 3 WHEN monetary_value < 500 THEN 4 ELSE 5 END AS m_score
    FROM customer_rfm
),
segmented AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 3 AND r_score >= 3 THEN 'Loyal repeat customers'
            WHEN f_score >= 3 AND r_score <= 2 THEN 'Repeat customers at risk'
            WHEN f_score = 1 AND m_score >= 4 AND r_score >= 3 THEN 'High-value one-time customers'
            WHEN r_score >= 4 THEN 'Recent customers'
            WHEN r_score <= 2 THEN 'Inactive in observed window'
            ELSE 'Other established customers'
        END AS rfm_segment
    FROM scored
)
SELECT
    customer_unique_id, recency_days, frequency_orders, ROUND(monetary_value, 2) AS monetary_value,
    r_score, f_score, m_score, rfm_segment, '2018-09-01 00:00:00' AS analysis_cutoff
FROM segmented
ORDER BY customer_unique_id;

WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value FROM order_items GROUP BY order_id
),
customer_rfm AS (
    SELECT c.customer_unique_id,
        CAST(julianday('2018-09-01') - julianday(date(MAX(o.order_purchase_timestamp))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency_orders,
        SUM(COALESCE(om.merchandise_value, 0.0)) AS monetary_value
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN order_merchandise AS om ON om.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')
    GROUP BY c.customer_unique_id
),
scored AS (
    SELECT *,
        CASE WHEN recency_days <= 90 THEN 5 WHEN recency_days <= 180 THEN 4 WHEN recency_days <= 270 THEN 3 WHEN recency_days <= 365 THEN 2 ELSE 1 END AS r_score,
        CASE WHEN frequency_orders = 1 THEN 1 WHEN frequency_orders = 2 THEN 3 ELSE 5 END AS f_score,
        CASE WHEN monetary_value < 50 THEN 1 WHEN monetary_value < 100 THEN 2 WHEN monetary_value < 200 THEN 3 WHEN monetary_value < 500 THEN 4 ELSE 5 END AS m_score
    FROM customer_rfm
),
segmented AS (
    SELECT *, CASE
        WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND r_score >= 3 THEN 'Loyal repeat customers'
        WHEN f_score >= 3 AND r_score <= 2 THEN 'Repeat customers at risk'
        WHEN f_score = 1 AND m_score >= 4 AND r_score >= 3 THEN 'High-value one-time customers'
        WHEN r_score >= 4 THEN 'Recent customers'
        WHEN r_score <= 2 THEN 'Inactive in observed window'
        ELSE 'Other established customers' END AS rfm_segment
    FROM scored
),
summary AS (
    SELECT rfm_segment, COUNT(*) AS customers, SUM(monetary_value) AS merchandise_value,
        AVG(frequency_orders) AS avg_purchase_frequency, AVG(frequency_orders >= 2) AS repeat_customer_share
    FROM segmented GROUP BY rfm_segment
)
SELECT rfm_segment, customers,
    ROUND(100.0 * customers / SUM(customers) OVER (), 2) AS customer_share_pct,
    ROUND(merchandise_value, 2) AS merchandise_value,
    ROUND(100.0 * merchandise_value / SUM(merchandise_value) OVER (), 2) AS merchandise_share_pct,
    ROUND(avg_purchase_frequency, 2) AS avg_purchase_frequency,
    ROUND(100.0 * repeat_customer_share, 2) AS repeat_customer_share_pct
FROM summary
ORDER BY merchandise_value DESC, rfm_segment;
