-- Result 1: primary time-to-second-observed-purchase population at the Phase 2 cutoff.
WITH eligible AS (
    SELECT c.customer_unique_id, o.order_id, o.order_purchase_timestamp,
        ROW_NUMBER() OVER (PARTITION BY c.customer_unique_id ORDER BY datetime(o.order_purchase_timestamp), o.order_id) AS purchase_number
    FROM orders AS o JOIN customers AS c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')
), customer_times AS (
    SELECT customer_unique_id, MIN(order_purchase_timestamp) AS first_purchase_timestamp,
        MAX(CASE WHEN purchase_number = 2 THEN order_purchase_timestamp END) AS second_purchase_timestamp
    FROM eligible GROUP BY customer_unique_id
)
SELECT customer_unique_id, first_purchase_timestamp, second_purchase_timestamp,
    second_purchase_timestamp IS NOT NULL AS repeat_event,
    julianday(COALESCE(second_purchase_timestamp, '2018-09-01 00:00:00')) - julianday(first_purchase_timestamp) AS observed_days,
    '2018-09-01 00:00:00' AS analysis_cutoff
FROM customer_times ORDER BY customer_unique_id;

-- Result 2: the same administratively censored construction at three cutoffs.
WITH cutoffs(cutoff) AS (
    VALUES ('2018-03-01 00:00:00'), ('2018-06-01 00:00:00'), ('2018-09-01 00:00:00')
), eligible AS (
    SELECT x.cutoff, c.customer_unique_id, o.order_id, o.order_purchase_timestamp,
        ROW_NUMBER() OVER (PARTITION BY x.cutoff, c.customer_unique_id ORDER BY datetime(o.order_purchase_timestamp), o.order_id) AS purchase_number
    FROM cutoffs AS x JOIN orders AS o ON datetime(o.order_purchase_timestamp) < datetime(x.cutoff)
    JOIN customers AS c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
), customer_times AS (
    SELECT cutoff, customer_unique_id, MIN(order_purchase_timestamp) AS first_purchase_timestamp,
        MAX(CASE WHEN purchase_number = 2 THEN order_purchase_timestamp END) AS second_purchase_timestamp
    FROM eligible GROUP BY cutoff, customer_unique_id
)
SELECT cutoff, customer_unique_id, second_purchase_timestamp IS NOT NULL AS repeat_event,
    julianday(COALESCE(second_purchase_timestamp, cutoff)) - julianday(first_purchase_timestamp) AS observed_days
FROM customer_times ORDER BY cutoff, customer_unique_id;

-- Result 3: RFM segment labels at two cutoffs for stability assessment.
WITH cutoffs(cutoff) AS (VALUES ('2018-06-01 00:00:00'), ('2018-09-01 00:00:00')),
order_merchandise AS (SELECT order_id, SUM(price) AS merchandise_value FROM order_items GROUP BY order_id),
rfm AS (
    SELECT x.cutoff, c.customer_unique_id,
        CAST(julianday(date(x.cutoff)) - julianday(date(MAX(o.order_purchase_timestamp))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency_orders, SUM(COALESCE(m.merchandise_value, 0.0)) AS monetary_value
    FROM cutoffs AS x JOIN orders AS o ON datetime(o.order_purchase_timestamp) < datetime(x.cutoff)
    JOIN customers AS c ON c.customer_id = o.customer_id LEFT JOIN order_merchandise AS m ON m.order_id = o.order_id
    WHERE o.order_status = 'delivered' GROUP BY x.cutoff, c.customer_unique_id
), scored AS (
    SELECT *, CASE WHEN recency_days <= 90 THEN 5 WHEN recency_days <= 180 THEN 4 WHEN recency_days <= 270 THEN 3 WHEN recency_days <= 365 THEN 2 ELSE 1 END AS r_score,
        CASE WHEN frequency_orders = 1 THEN 1 WHEN frequency_orders = 2 THEN 3 ELSE 5 END AS f_score,
        CASE WHEN monetary_value < 50 THEN 1 WHEN monetary_value < 100 THEN 2 WHEN monetary_value < 200 THEN 3 WHEN monetary_value < 500 THEN 4 ELSE 5 END AS m_score
    FROM rfm
)
SELECT cutoff, customer_unique_id,
    CASE WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 4 THEN 'Champions'
         WHEN f_score >= 3 AND r_score >= 3 THEN 'Loyal repeat customers'
         WHEN f_score >= 3 AND r_score <= 2 THEN 'Repeat customers at risk'
         WHEN f_score = 1 AND m_score >= 4 AND r_score >= 3 THEN 'High-value one-time customers'
         WHEN r_score >= 4 THEN 'Recent customers'
         WHEN r_score <= 2 THEN 'Inactive in observed window'
         ELSE 'Other established customers' END AS rfm_segment
FROM scored ORDER BY cutoff, customer_unique_id;
