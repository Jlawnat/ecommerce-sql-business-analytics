PRAGMA foreign_keys = ON;

CREATE TABLE mart_customer_snapshot (
    customer_unique_id TEXT PRIMARY KEY,
    analysis_cutoff TEXT NOT NULL,
    first_purchase_timestamp TEXT NOT NULL,
    second_purchase_timestamp TEXT,
    last_purchase_timestamp TEXT NOT NULL,
    frequency_orders INTEGER NOT NULL CHECK (frequency_orders >= 1),
    monetary_value REAL NOT NULL CHECK (monetary_value >= 0),
    recency_days INTEGER NOT NULL CHECK (recency_days >= 0),
    time_to_second_days REAL CHECK (time_to_second_days >= 0)
) WITHOUT ROWID;

INSERT INTO mart_customer_snapshot
WITH order_merchandise AS (
    SELECT order_id, SUM(price) AS merchandise_value
    FROM source.order_items GROUP BY order_id
), eligible AS (
    SELECT c.customer_unique_id, o.order_id, o.order_purchase_timestamp,
        COALESCE(m.merchandise_value, 0.0) AS merchandise_value,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id
            ORDER BY datetime(o.order_purchase_timestamp), o.order_id
        ) AS purchase_number
    FROM source.orders AS o
    JOIN source.customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN order_merchandise AS m ON m.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')
)
SELECT customer_unique_id, '2018-09-01 00:00:00',
    MIN(order_purchase_timestamp),
    MAX(CASE WHEN purchase_number = 2 THEN order_purchase_timestamp END),
    MAX(order_purchase_timestamp), COUNT(DISTINCT order_id), SUM(merchandise_value),
    CAST(julianday('2018-09-01') - julianday(date(MAX(order_purchase_timestamp))) AS INTEGER),
    julianday(MAX(CASE WHEN purchase_number = 2 THEN order_purchase_timestamp END))
        - julianday(MIN(order_purchase_timestamp))
FROM eligible GROUP BY customer_unique_id;

CREATE TABLE mart_delivered_orders (
    order_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    customer_state TEXT NOT NULL,
    purchase_timestamp TEXT NOT NULL,
    purchase_month TEXT NOT NULL,
    delivered_customer_timestamp TEXT,
    estimated_delivery_timestamp TEXT,
    timing_eligible INTEGER NOT NULL CHECK (timing_eligible IN (0, 1)),
    is_late INTEGER CHECK (is_late IN (0, 1)),
    merchandise_value REAL NOT NULL CHECK (merchandise_value >= 0),
    freight_value REAL NOT NULL CHECK (freight_value >= 0),
    item_count INTEGER NOT NULL CHECK (item_count >= 1),
    seller_count INTEGER NOT NULL CHECK (seller_count >= 1),
    single_seller INTEGER NOT NULL CHECK (single_seller IN (0, 1)),
    category_count INTEGER NOT NULL CHECK (category_count >= 1),
    attributed_category TEXT NOT NULL,
    category_attribution_method TEXT NOT NULL,
    review_record_count INTEGER NOT NULL CHECK (review_record_count >= 0),
    review_score REAL CHECK (review_score BETWEEN 1 AND 5)
) WITHOUT ROWID;

INSERT INTO mart_delivered_orders
WITH item_category AS (
    SELECT oi.order_id,
        COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]') AS category,
        SUM(oi.price) AS category_value
    FROM source.order_items AS oi
    JOIN source.products AS p ON p.product_id = oi.product_id
    LEFT JOIN source.category_translation AS ct ON ct.product_category_name = p.product_category_name
    GROUP BY oi.order_id, category
), category_ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY category_value DESC, category) AS category_rank,
        COUNT(*) OVER (PARTITION BY order_id) AS category_count
    FROM item_category
), attributed AS (
    SELECT order_id, category AS attributed_category, category_count
    FROM category_ranked WHERE category_rank = 1
), item_orders AS (
    SELECT order_id, SUM(price) AS merchandise_value, SUM(freight_value) AS freight_value,
        COUNT(*) AS item_count, COUNT(DISTINCT seller_id) AS seller_count
    FROM source.order_items GROUP BY order_id
), reviews AS (
    SELECT order_id, COUNT(review_score) AS review_record_count, AVG(review_score) AS review_score
    FROM source.order_reviews GROUP BY order_id
)
SELECT o.order_id, c.customer_unique_id, c.customer_state, o.order_purchase_timestamp,
    strftime('%Y-%m', o.order_purchase_timestamp), o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL,
    CASE WHEN o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
         THEN datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date) END,
    i.merchandise_value, i.freight_value, i.item_count, i.seller_count, i.seller_count = 1,
    a.category_count, a.attributed_category,
    CASE WHEN a.category_count = 1 THEN 'single_category' ELSE 'dominant_merchandise_value' END,
    COALESCE(r.review_record_count, 0), r.review_score
FROM source.orders AS o
JOIN source.customers AS c ON c.customer_id = o.customer_id
JOIN item_orders AS i ON i.order_id = o.order_id
JOIN attributed AS a ON a.order_id = o.order_id
LEFT JOIN reviews AS r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered';

CREATE TABLE mart_delivered_order_items (
    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,
    customer_unique_id TEXT NOT NULL,
    purchase_timestamp TEXT NOT NULL,
    product_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    freight_value REAL NOT NULL CHECK (freight_value >= 0),
    product_weight_g INTEGER,
    seller_state TEXT,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES mart_delivered_orders(order_id)
) WITHOUT ROWID;

INSERT INTO mart_delivered_order_items
SELECT oi.order_id, oi.order_item_id, c.customer_unique_id, o.order_purchase_timestamp,
    oi.product_id, oi.seller_id,
    COALESCE(ct.product_category_name_english, p.product_category_name, '[uncategorized]'),
    oi.price, oi.freight_value, p.product_weight_g, s.seller_state
FROM source.order_items AS oi
JOIN source.orders AS o ON o.order_id = oi.order_id AND o.order_status = 'delivered'
JOIN source.customers AS c ON c.customer_id = o.customer_id
JOIN source.products AS p ON p.product_id = oi.product_id
JOIN source.sellers AS s ON s.seller_id = oi.seller_id
LEFT JOIN source.category_translation AS ct ON ct.product_category_name = p.product_category_name;

CREATE TABLE mart_reviewed_orders (
    order_id TEXT PRIMARY KEY,
    review_record_count INTEGER NOT NULL CHECK (review_record_count >= 1),
    order_review_score REAL NOT NULL CHECK (order_review_score BETWEEN 1 AND 5),
    low_review INTEGER NOT NULL CHECK (low_review IN (0, 1)),
    score_one INTEGER NOT NULL CHECK (score_one IN (0, 1)),
    FOREIGN KEY (order_id) REFERENCES mart_delivered_orders(order_id)
) WITHOUT ROWID;

INSERT INTO mart_reviewed_orders
SELECT o.order_id, COUNT(r.review_score), AVG(r.review_score),
    AVG(r.review_score) <= 2, AVG(r.review_score) = 1
FROM source.orders AS o
JOIN source.order_reviews AS r ON r.order_id = o.order_id AND r.review_score IS NOT NULL
WHERE o.order_status = 'delivered'
GROUP BY o.order_id;

CREATE INDEX idx_mart_orders_customer ON mart_delivered_orders(customer_unique_id);
CREATE INDEX idx_mart_orders_month ON mart_delivered_orders(purchase_month);
CREATE INDEX idx_mart_orders_category ON mart_delivered_orders(attributed_category);
CREATE INDEX idx_mart_items_product ON mart_delivered_order_items(product_id);
CREATE INDEX idx_mart_items_seller ON mart_delivered_order_items(seller_id);
