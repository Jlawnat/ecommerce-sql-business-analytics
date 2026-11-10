-- Delivery/review analysis is observational. Reviews are averaged to order grain before joining.
-- Result 1: coverage and missingness.
WITH reviews AS (
    SELECT order_id, AVG(review_score) AS review_score FROM order_reviews
    WHERE review_score IS NOT NULL GROUP BY order_id
), delivered AS (
    SELECT o.order_id, o.order_delivered_customer_date, o.order_estimated_delivery_date, r.review_score
    FROM orders AS o LEFT JOIN reviews AS r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
)
SELECT COUNT(*) AS delivered_orders,
    SUM(order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL) AS timing_eligible_orders,
    SUM(review_score IS NOT NULL) AS reviewed_orders,
    SUM(order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL AND review_score IS NOT NULL) AS inference_eligible_orders,
    SUM(order_delivered_customer_date IS NULL) AS missing_actual_delivery_timestamp,
    SUM(order_estimated_delivery_date IS NULL) AS missing_estimated_delivery_timestamp,
    SUM(review_score IS NULL) AS missing_order_level_review
FROM delivered;

-- Result 2: order-level score distribution by full-timestamp delivery timing.
WITH reviews AS (
    SELECT order_id, AVG(review_score) AS review_score FROM order_reviews
    WHERE review_score IS NOT NULL GROUP BY order_id
), eligible AS (
    SELECT o.order_id,
        CASE WHEN datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date) THEN 'late' ELSE 'on_time_or_early' END AS delivery_timing,
        julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS days_vs_estimate,
        r.review_score
    FROM orders AS o LEFT JOIN reviews AS r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT delivery_timing, COUNT(*) AS timing_eligible_orders, COUNT(review_score) AS reviewed_orders,
    ROUND(AVG(review_score), 6) AS avg_review_score,
    ROUND(AVG(review_score * review_score), 6) AS mean_squared_review_score,
    SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) AS low_review_orders,
    ROUND(100.0 * AVG(CASE WHEN review_score IS NULL THEN NULL WHEN review_score <= 2 THEN 1.0 ELSE 0.0 END), 4) AS low_review_share_pct,
    ROUND(AVG(days_vs_estimate), 4) AS avg_days_vs_estimate
FROM eligible GROUP BY delivery_timing ORDER BY delivery_timing;

-- Result 3: customer-state delivery performance. Small samples remain visible and are not over-interpreted.
WITH reviews AS (
    SELECT order_id, AVG(review_score) AS review_score FROM order_reviews WHERE review_score IS NOT NULL GROUP BY order_id
), eligible AS (
    SELECT o.order_id, c.customer_state,
        datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date) AS is_late, r.review_score
    FROM orders AS o JOIN customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN reviews AS r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT customer_state, COUNT(*) AS timing_eligible_orders, SUM(is_late) AS late_orders,
    ROUND(100.0 * AVG(is_late), 2) AS late_delivery_rate_pct,
    COUNT(review_score) AS reviewed_orders, ROUND(AVG(review_score), 2) AS avg_review_score
FROM eligible GROUP BY customer_state ORDER BY late_delivery_rate_pct DESC, timing_eligible_orders DESC;

-- Result 4: category performance using one deterministic category per order.
-- Single-category orders keep that category. Mixed orders use the category with greatest item-price value;
-- ties resolve alphabetically. This avoids counting one order in multiple category denominators.
WITH item_category AS (
    SELECT oi.order_id, COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]') AS category,
        SUM(oi.price) AS category_value
    FROM order_items AS oi JOIN products AS p ON p.product_id = oi.product_id
    LEFT JOIN category_translation AS ct ON ct.product_category_name = p.product_category_name
    GROUP BY oi.order_id, category
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY category_value DESC, category) AS category_rank,
        COUNT(*) OVER (PARTITION BY order_id) AS category_count
    FROM item_category
), attribution AS (
    SELECT order_id, category AS attributed_category, category_count FROM ranked WHERE category_rank = 1
), reviews AS (
    SELECT order_id, AVG(review_score) AS review_score FROM order_reviews WHERE review_score IS NOT NULL GROUP BY order_id
), eligible AS (
    SELECT o.order_id, a.attributed_category, a.category_count,
        datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date) AS is_late, r.review_score
    FROM orders AS o JOIN attribution AS a ON a.order_id = o.order_id
    LEFT JOIN reviews AS r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT attributed_category, COUNT(*) AS timing_eligible_orders, SUM(category_count > 1) AS mixed_category_orders,
    SUM(is_late) AS late_orders, ROUND(100.0 * AVG(is_late), 2) AS late_delivery_rate_pct,
    COUNT(review_score) AS reviewed_orders, ROUND(AVG(review_score), 2) AS avg_review_score
FROM eligible GROUP BY attributed_category ORDER BY late_delivery_rate_pct DESC, timing_eligible_orders DESC;

-- Result 5: reviewed order counts for stratified association checks.
-- Strata adjust descriptively for purchase month, customer state, and order merchandise-value band.
WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value FROM order_items GROUP BY order_id
), reviews AS (
    SELECT order_id, AVG(review_score) AS review_score FROM order_reviews WHERE review_score IS NOT NULL GROUP BY order_id
), eligible AS (
    SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month, c.customer_state,
        CASE WHEN om.merchandise_value < 50 THEN '01_under_50'
             WHEN om.merchandise_value < 100 THEN '02_50_to_99'
             WHEN om.merchandise_value < 200 THEN '03_100_to_199' ELSE '04_200_plus' END AS value_band,
        datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date) AS is_late,
        r.review_score
    FROM orders AS o JOIN customers AS c ON c.customer_id = o.customer_id
    JOIN order_merchandise AS om ON om.order_id = o.order_id JOIN reviews AS r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT purchase_month, customer_state, value_band,
    SUM(is_late) AS late_reviewed_orders,
    SUM(is_late AND review_score <= 2) AS late_low_review_orders,
    SUM(NOT is_late) AS on_time_reviewed_orders,
    SUM(NOT is_late AND review_score <= 2) AS on_time_low_review_orders,
    ROUND(SUM(CASE WHEN is_late THEN review_score ELSE 0 END), 6) AS late_score_sum,
    ROUND(SUM(CASE WHEN NOT is_late THEN review_score ELSE 0 END), 6) AS on_time_score_sum
FROM eligible GROUP BY purchase_month, customer_state, value_band
ORDER BY purchase_month, customer_state, value_band;
