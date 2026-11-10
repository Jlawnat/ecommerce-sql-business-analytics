-- Grain: one row per translated category. Cohort: delivered orders only.
WITH category_value AS (
    SELECT
        COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]') AS category,
        COUNT(DISTINCT oi.order_id) AS delivered_orders,
        ROUND(SUM(oi.price), 2) AS merchandise_value
    FROM order_items AS oi
    JOIN orders AS o ON o.order_id = oi.order_id AND o.order_status = 'delivered'
    JOIN products AS p ON p.product_id = oi.product_id
    LEFT JOIN category_translation AS ct
        ON ct.product_category_name = p.product_category_name
    GROUP BY COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]')
),
ranked AS (
    SELECT
        category,
        delivered_orders,
        merchandise_value,
        RANK() OVER (ORDER BY merchandise_value DESC) AS value_rank,
        SUM(merchandise_value) OVER () AS total_merchandise_value,
        SUM(merchandise_value) OVER (
            ORDER BY merchandise_value DESC, category
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_merchandise_value
    FROM category_value
)
SELECT
    category,
    delivered_orders,
    merchandise_value,
    value_rank,
    ROUND(100.0 * merchandise_value / NULLIF(total_merchandise_value, 0), 2) AS merchandise_share_pct,
    ROUND(100.0 * cumulative_merchandise_value / NULLIF(total_merchandise_value, 0), 2) AS cumulative_share_pct
FROM ranked
ORDER BY merchandise_value DESC, category;
