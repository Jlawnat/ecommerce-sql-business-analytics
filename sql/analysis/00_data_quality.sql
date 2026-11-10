-- Each SELECT is an independently reproducible quality check.

SELECT 'category_translation' AS table_name, COUNT(*) AS row_count FROM category_translation
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'geolocation', COUNT(*) FROM geolocation
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sellers', COUNT(*) FROM sellers
ORDER BY table_name;

SELECT 'orders' AS table_name, 'customer_id' AS column_name,
       SUM(customer_id IS NULL) AS missing_count, COUNT(*) AS total_rows FROM orders
UNION ALL SELECT 'orders', 'order_purchase_timestamp', SUM(order_purchase_timestamp IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'orders', 'order_approved_at', SUM(order_approved_at IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'orders', 'order_delivered_customer_date', SUM(order_delivered_customer_date IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'products', 'product_category_name', SUM(product_category_name IS NULL), COUNT(*) FROM products
UNION ALL SELECT 'order_reviews', 'review_comment_title', SUM(review_comment_title IS NULL), COUNT(*) FROM order_reviews
UNION ALL SELECT 'order_reviews', 'review_comment_message', SUM(review_comment_message IS NULL), COUNT(*) FROM order_reviews
ORDER BY table_name, column_name;

SELECT 'customers.customer_id' AS key_name, COUNT(*) AS duplicate_groups
FROM (SELECT customer_id FROM customers GROUP BY customer_id HAVING COUNT(*) > 1)
UNION ALL
SELECT 'orders.order_id', COUNT(*)
FROM (SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*) > 1)
UNION ALL
SELECT 'order_items.(order_id,order_item_id)', COUNT(*)
FROM (SELECT order_id, order_item_id FROM order_items GROUP BY order_id, order_item_id HAVING COUNT(*) > 1)
UNION ALL
SELECT 'order_payments.(order_id,payment_sequential)', COUNT(*)
FROM (SELECT order_id, payment_sequential FROM order_payments GROUP BY order_id, payment_sequential HAVING COUNT(*) > 1)
UNION ALL
SELECT 'products.product_id', COUNT(*)
FROM (SELECT product_id FROM products GROUP BY product_id HAVING COUNT(*) > 1)
UNION ALL
SELECT 'sellers.seller_id', COUNT(*)
FROM (SELECT seller_id FROM sellers GROUP BY seller_id HAVING COUNT(*) > 1);

SELECT
    COUNT(*) AS orders,
    SUM(c.customer_id IS NOT NULL) AS orders_with_customer,
    SUM(i.order_id IS NOT NULL) AS orders_with_items,
    SUM(p.order_id IS NOT NULL) AS orders_with_payments,
    SUM(r.order_id IS NOT NULL) AS orders_with_reviews
FROM orders AS o
LEFT JOIN customers AS c ON c.customer_id = o.customer_id
LEFT JOIN (SELECT DISTINCT order_id FROM order_items) AS i ON i.order_id = o.order_id
LEFT JOIN (SELECT DISTINCT order_id FROM order_payments) AS p ON p.order_id = o.order_id
LEFT JOIN (SELECT DISTINCT order_id FROM order_reviews) AS r ON r.order_id = o.order_id;

SELECT order_status, COUNT(*) AS orders
FROM orders
GROUP BY order_status
ORDER BY orders DESC, order_status;

SELECT
    SUM(order_approved_at < order_purchase_timestamp) AS approval_before_purchase,
    SUM(order_delivered_carrier_date < order_approved_at) AS carrier_before_approval,
    SUM(order_delivered_customer_date < order_delivered_carrier_date) AS customer_before_carrier,
    SUM(order_status = 'delivered' AND order_delivered_customer_date IS NULL) AS delivered_without_delivery_timestamp,
    SUM(order_delivered_customer_date > order_estimated_delivery_date) AS delivered_after_estimate
FROM orders;

WITH item_counts AS (
    SELECT order_id, COUNT(*) AS item_count FROM order_items GROUP BY order_id
), payment_counts AS (
    SELECT order_id, COUNT(*) AS payment_count FROM order_payments GROUP BY order_id
), review_counts AS (
    SELECT order_id, COUNT(*) AS review_count FROM order_reviews GROUP BY order_id
)
SELECT
    COUNT(*) AS orders_with_any_child,
    SUM(COALESCE(item_count, 0) > 1) AS multi_item_orders,
    SUM(COALESCE(payment_count, 0) > 1) AS multi_payment_orders,
    SUM(COALESCE(review_count, 0) > 1) AS multi_review_orders,
    SUM(COALESCE(item_count, 0) * COALESCE(payment_count, 0) * MAX(COALESCE(review_count, 0), 1)) AS naive_join_rows,
    SUM(COALESCE(item_count, 0)) AS source_item_rows
FROM orders AS o
LEFT JOIN item_counts AS i ON i.order_id = o.order_id
LEFT JOIN payment_counts AS p ON p.order_id = o.order_id
LEFT JOIN review_counts AS r ON r.order_id = o.order_id
WHERE i.order_id IS NOT NULL OR p.order_id IS NOT NULL OR r.order_id IS NOT NULL;

SELECT
    SUM(p.product_category_name IS NULL) AS products_without_category,
    SUM(p.product_category_name IS NOT NULL AND ct.product_category_name IS NULL) AS categories_without_translation
FROM products AS p
LEFT JOIN category_translation AS ct ON ct.product_category_name = p.product_category_name;

SELECT
    SUM(order_delivered_customer_date < order_purchase_timestamp) AS delivered_before_purchase,
    SUM(order_estimated_delivery_date < order_purchase_timestamp) AS estimate_before_purchase,
    SUM(
        order_delivered_customer_date IS NOT NULL
        AND ABS(julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)) > 365
    ) AS delivery_duration_over_365_days
FROM orders;
