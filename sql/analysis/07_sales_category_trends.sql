-- Result 1: monthly delivered-order trends. Sparse/boundary comparisons remain visible but are flagged.
WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value FROM order_items GROUP BY order_id
),
monthly AS (
    SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
        COUNT(*) AS delivered_orders, SUM(om.merchandise_value) AS merchandise_value,
        AVG(om.merchandise_value) AS avg_merchandise_value_per_order
    FROM orders AS o JOIN order_merchandise AS om ON om.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
),
flagged AS (
    SELECT *,
        CASE WHEN purchase_month = MIN(purchase_month) OVER () THEN 'incomplete_first_month'
             WHEN purchase_month = MAX(purchase_month) OVER () THEN 'incomplete_last_month'
             WHEN delivered_orders < 100 THEN 'sparse_month'
             ELSE 'complete_or_well_represented' END AS observation_status
    FROM monthly
),
lagged AS (
    SELECT *, LAG(merchandise_value) OVER (ORDER BY purchase_month) AS prior_value,
        LAG(observation_status) OVER (ORDER BY purchase_month) AS prior_status
    FROM flagged
)
SELECT purchase_month, delivered_orders, ROUND(merchandise_value, 2) AS merchandise_value,
    ROUND(avg_merchandise_value_per_order, 2) AS avg_merchandise_value_per_order,
    ROUND(100.0 * (merchandise_value - prior_value) / NULLIF(prior_value, 0), 2) AS raw_merchandise_value_mom_pct,
    CASE WHEN observation_status = 'complete_or_well_represented' AND prior_status = 'complete_or_well_represented'
         THEN ROUND(100.0 * (merchandise_value - prior_value) / NULLIF(prior_value, 0), 2) END AS interpretable_mom_pct,
    observation_status
FROM lagged ORDER BY purchase_month;

-- Result 2: overall category Pareto distribution.
WITH category_value AS (
    SELECT COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]') AS category,
        COUNT(DISTINCT oi.order_id) AS delivered_orders, SUM(oi.price) AS merchandise_value
    FROM order_items AS oi
    JOIN orders AS o ON o.order_id = oi.order_id AND o.order_status = 'delivered'
    JOIN products AS p ON p.product_id = oi.product_id
    LEFT JOIN category_translation AS ct ON ct.product_category_name = p.product_category_name
    GROUP BY COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]')
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY merchandise_value DESC, category) AS value_rank,
        SUM(merchandise_value) OVER () AS total_value,
        SUM(merchandise_value) OVER (ORDER BY merchandise_value DESC, category ROWS UNBOUNDED PRECEDING) AS cumulative_value
    FROM category_value
)
SELECT category, delivered_orders, ROUND(merchandise_value, 2) AS merchandise_value, value_rank,
    ROUND(100.0 * merchandise_value / total_value, 2) AS merchandise_share_pct,
    ROUND(100.0 * cumulative_value / total_value, 2) AS cumulative_share_pct,
    CASE WHEN 100.0 * (cumulative_value - merchandise_value) / total_value < 80 THEN 1 ELSE 0 END AS contributes_to_first_80_pct
FROM ranked ORDER BY value_rank;

-- Result 3: dense monthly category mix, including zero-value months, with month-over-month share changes.
WITH months AS (
    SELECT strftime('%Y-%m', order_purchase_timestamp) AS purchase_month, COUNT(*) AS delivered_orders
    FROM orders WHERE order_status = 'delivered'
    GROUP BY strftime('%Y-%m', order_purchase_timestamp)
),
item_values AS (
    SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
        COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]') AS category,
        SUM(oi.price) AS merchandise_value
    FROM orders AS o JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN products AS p ON p.product_id = oi.product_id
    LEFT JOIN category_translation AS ct ON ct.product_category_name = p.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 2
), categories AS (
    SELECT DISTINCT category FROM item_values
), dense AS (
    SELECT m.purchase_month, m.delivered_orders, c.category, COALESCE(v.merchandise_value, 0.0) AS merchandise_value
    FROM months AS m CROSS JOIN categories AS c
    LEFT JOIN item_values AS v ON v.purchase_month = m.purchase_month AND v.category = c.category
), shares AS (
    SELECT *, 100.0 * merchandise_value / NULLIF(SUM(merchandise_value) OVER (PARTITION BY purchase_month), 0) AS share_pct
    FROM dense
), changed AS (
    SELECT *,
        LAG(share_pct) OVER (PARTITION BY category ORDER BY purchase_month) AS prior_share_pct,
        LAG(purchase_month) OVER (PARTITION BY category ORDER BY purchase_month) AS prior_purchase_month,
        LAG(delivered_orders) OVER (PARTITION BY category ORDER BY purchase_month) AS prior_delivered_orders,
        MIN(purchase_month) OVER () AS first_purchase_month,
        MAX(purchase_month) OVER () AS last_purchase_month
    FROM shares
)
SELECT purchase_month, category, ROUND(merchandise_value, 2) AS merchandise_value,
    ROUND(share_pct, 2) AS merchandise_share_pct,
    ROUND(share_pct - prior_share_pct, 2) AS raw_share_change_pp,
    CASE WHEN delivered_orders >= 100 AND prior_delivered_orders >= 100
           AND prior_purchase_month = strftime('%Y-%m', date(purchase_month || '-01', '-1 month'))
           AND purchase_month NOT IN (first_purchase_month, last_purchase_month)
         THEN ROUND(share_pct - prior_share_pct, 2) END AS interpretable_share_change_pp
FROM changed ORDER BY purchase_month, merchandise_value DESC, category;
