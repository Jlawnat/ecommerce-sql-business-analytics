-- Grain: one row per purchase month. Cohort: delivered orders only.
-- Merchandise value is item price only; freight and payment value are excluded.
WITH order_merchandise AS (
    SELECT
        oi.order_id,
        SUM(oi.price) AS merchandise_value
    FROM order_items AS oi
    GROUP BY oi.order_id
),
monthly AS (
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
        COUNT(*) AS delivered_orders,
        ROUND(SUM(om.merchandise_value), 2) AS merchandise_value,
        ROUND(AVG(om.merchandise_value), 2) AS avg_merchandise_value_per_order
    FROM orders AS o
    JOIN order_merchandise AS om ON om.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
)
SELECT
    purchase_month,
    delivered_orders,
    merchandise_value,
    avg_merchandise_value_per_order,
    ROUND(
        100.0 * (merchandise_value - LAG(merchandise_value) OVER (ORDER BY purchase_month))
        / NULLIF(LAG(merchandise_value) OVER (ORDER BY purchase_month), 0),
        2
    ) AS merchandise_value_mom_pct
FROM monthly
ORDER BY purchase_month;
