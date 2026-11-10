SELECT 'order_grain_unique' AS check_name,
    COUNT(*) - COUNT(DISTINCT order_id) AS violations,
    COUNT(*) AS actual, COUNT(DISTINCT order_id) AS expected
FROM mart_delivered_orders;

SELECT 'order_population_reconciliation' AS check_name,
    ABS((SELECT COUNT(*) FROM mart_delivered_orders)
        - (SELECT COUNT(*) FROM source.orders WHERE order_status = 'delivered')) AS violations,
    (SELECT COUNT(*) FROM mart_delivered_orders) AS actual,
    (SELECT COUNT(*) FROM source.orders WHERE order_status = 'delivered') AS expected;

SELECT 'item_grain_and_population' AS check_name,
    ABS((SELECT COUNT(*) FROM mart_delivered_order_items)
        - (SELECT COUNT(*) FROM source.order_items AS i JOIN source.orders AS o USING(order_id) WHERE o.order_status = 'delivered')) AS violations,
    (SELECT COUNT(*) FROM mart_delivered_order_items) AS actual,
    (SELECT COUNT(*) FROM source.order_items AS i JOIN source.orders AS o USING(order_id) WHERE o.order_status = 'delivered') AS expected;

SELECT 'order_item_foreign_keys' AS check_name, COUNT(*) AS violations, COUNT(*) AS actual, 0 AS expected
FROM mart_delivered_order_items AS i
LEFT JOIN mart_delivered_orders AS o ON o.order_id = i.order_id
WHERE o.order_id IS NULL;

SELECT 'order_merchandise_reconciliation' AS check_name,
    ROUND(ABS((SELECT SUM(merchandise_value) FROM mart_delivered_orders)
        - (SELECT SUM(price) FROM source.order_items AS i JOIN source.orders AS o USING(order_id) WHERE o.order_status = 'delivered')), 6) > 0.000001 AS violations,
    ROUND((SELECT SUM(merchandise_value) FROM mart_delivered_orders), 2) AS actual,
    ROUND((SELECT SUM(price) FROM source.order_items AS i JOIN source.orders AS o USING(order_id) WHERE o.order_status = 'delivered'), 2) AS expected;

SELECT 'item_merchandise_reconciliation' AS check_name,
    ROUND(ABS((SELECT SUM(price) FROM mart_delivered_order_items)
        - (SELECT SUM(merchandise_value) FROM mart_delivered_orders)), 6) > 0.000001 AS violations,
    ROUND((SELECT SUM(price) FROM mart_delivered_order_items), 2) AS actual,
    ROUND((SELECT SUM(merchandise_value) FROM mart_delivered_orders), 2) AS expected;

SELECT 'customer_snapshot_unique' AS check_name,
    COUNT(*) - COUNT(DISTINCT customer_unique_id) AS violations,
    COUNT(*) AS actual, COUNT(DISTINCT customer_unique_id) AS expected
FROM mart_customer_snapshot;

SELECT 'customer_snapshot_population' AS check_name,
    ABS((SELECT COUNT(*) FROM mart_customer_snapshot) - (
        SELECT COUNT(DISTINCT c.customer_unique_id)
        FROM source.orders AS o JOIN source.customers AS c USING(customer_id)
        WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')
    )) AS violations,
    (SELECT COUNT(*) FROM mart_customer_snapshot) AS actual,
    (SELECT COUNT(DISTINCT c.customer_unique_id) FROM source.orders AS o JOIN source.customers AS c USING(customer_id)
     WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')) AS expected;

SELECT 'customer_snapshot_monetary' AS check_name,
    ROUND(ABS((SELECT SUM(monetary_value) FROM mart_customer_snapshot) - (
        SELECT SUM(i.price) FROM source.order_items AS i JOIN source.orders AS o USING(order_id)
        WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')
    )), 6) > 0.000001 AS violations,
    ROUND((SELECT SUM(monetary_value) FROM mart_customer_snapshot), 2) AS actual,
    ROUND((SELECT SUM(i.price) FROM source.order_items AS i JOIN source.orders AS o USING(order_id)
     WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')), 2) AS expected;

SELECT 'reviewed_order_population' AS check_name,
    ABS((SELECT COUNT(*) FROM mart_reviewed_orders) - (
        SELECT COUNT(DISTINCT r.order_id) FROM source.order_reviews AS r
        JOIN source.orders AS o ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered' AND r.review_score IS NOT NULL
    )) AS violations,
    (SELECT COUNT(*) FROM mart_reviewed_orders) AS actual,
    (SELECT COUNT(DISTINCT r.order_id) FROM source.order_reviews AS r JOIN source.orders AS o ON o.order_id = r.order_id
     WHERE o.order_status = 'delivered' AND r.review_score IS NOT NULL) AS expected;

SELECT 'required_nulls' AS check_name,
    SUM(order_id IS NULL OR customer_unique_id IS NULL OR customer_state IS NULL OR purchase_timestamp IS NULL
        OR merchandise_value IS NULL OR attributed_category IS NULL) AS violations,
    SUM(order_id IS NULL OR customer_unique_id IS NULL OR customer_state IS NULL OR purchase_timestamp IS NULL
        OR merchandise_value IS NULL OR attributed_category IS NULL) AS actual, 0 AS expected
FROM mart_delivered_orders;

SELECT 'sqlite_foreign_key_check' AS check_name, COUNT(*) AS violations, COUNT(*) AS actual, 0 AS expected
FROM pragma_foreign_key_check;
