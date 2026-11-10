-- Runs against the analytical mart. Result 1: grouped binomial model rows.
WITH category_value AS (
    SELECT attributed_category, SUM(merchandise_value) AS merchandise_value
    FROM mart_delivered_orders GROUP BY attributed_category
), category_rank AS (
    SELECT attributed_category, ROW_NUMBER() OVER (ORDER BY merchandise_value DESC, attributed_category) AS value_rank
    FROM category_value
), state_counts AS (
    SELECT customer_state, COUNT(*) AS timing_orders
    FROM mart_delivered_orders WHERE timing_eligible = 1 GROUP BY customer_state
), eligible AS (
    SELECT CASE WHEN o.purchase_month < '2017-01' THEN '2016_sparse_period' ELSE o.purchase_month END AS purchase_month,
        CASE WHEN s.timing_orders < 200 THEN '[low_volume_states]' ELSE o.customer_state END AS customer_state,
        CASE WHEN r.value_rank <= 15 THEN o.attributed_category ELSE '[other_categories]' END AS category_group,
        CASE WHEN o.merchandise_value < 50 THEN '01_under_50'
             WHEN o.merchandise_value < 100 THEN '02_50_to_99'
             WHEN o.merchandise_value < 200 THEN '03_100_to_199' ELSE '04_200_plus' END AS value_band,
        o.single_seller, o.is_late, o.review_score <= 2 AS low_review, o.review_score = 1 AS score_one
    FROM mart_delivered_orders AS o JOIN category_rank AS r USING(attributed_category)
    JOIN state_counts AS s USING(customer_state)
    WHERE o.timing_eligible = 1 AND o.review_score IS NOT NULL
)
SELECT purchase_month, customer_state, category_group, value_band, single_seller, is_late,
    COUNT(*) AS reviewed_orders, SUM(low_review) AS low_reviews, SUM(score_one) AS score_one_reviews
FROM eligible GROUP BY purchase_month, customer_state, category_group, value_band, single_seller, is_late
ORDER BY purchase_month, customer_state, category_group, value_band, single_seller, is_late;

-- Result 2: review-selection sensitivity by exposure.
SELECT is_late, COUNT(*) AS timing_eligible_orders, COUNT(review_score) AS reviewed_orders,
    SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) AS observed_low_reviews
FROM mart_delivered_orders WHERE timing_eligible = 1 GROUP BY is_late ORDER BY is_late;

-- Result 3: subgroup 2x2 tables for heterogeneity assessment.
WITH eligible AS (
    SELECT * FROM mart_delivered_orders WHERE timing_eligible = 1 AND review_score IS NOT NULL
), dimensions AS (
    SELECT 'month' AS subgroup_type, purchase_month AS subgroup_value, is_late, review_score <= 2 AS low_review FROM eligible
    UNION ALL SELECT 'state', customer_state, is_late, review_score <= 2 FROM eligible
    UNION ALL SELECT 'category', attributed_category, is_late, review_score <= 2 FROM eligible
)
SELECT subgroup_type, subgroup_value,
    SUM(is_late) AS late_reviewed, SUM(is_late AND low_review) AS late_low,
    SUM(NOT is_late) AS on_time_reviewed, SUM(NOT is_late AND low_review) AS on_time_low
FROM dimensions GROUP BY subgroup_type, subgroup_value
ORDER BY subgroup_type, subgroup_value;
