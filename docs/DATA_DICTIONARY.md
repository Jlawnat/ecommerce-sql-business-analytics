# Data Dictionary

All timestamps are parsed with Python's ISO-compatible parser and stored as normalized SQLite `TEXT` (`YYYY-MM-DD HH:MM:SS[.ffffff]`). Blank source fields become `NULL`. Currency-like fields use SQLite `REAL`, matching the source precision for analysis; no currency conversion is performed.

## Tables and grains

### `customers`

One row per order-specific `customer_id`. `customer_unique_id` links different order-specific customer records believed to represent the same anonymized customer.

| Column | Type | Meaning |
|---|---|---|
| `customer_id` | TEXT PK | Order-facing customer identifier |
| `customer_unique_id` | TEXT NOT NULL | Cross-order anonymized customer identifier |
| `customer_zip_code_prefix` | INTEGER | ZIP-code prefix |
| `customer_city`, `customer_state` | TEXT | Customer location labels |

### `orders`

One row per `order_id`; mandatory many-to-one relationship to `customers`.

| Column | Type | Meaning |
|---|---|---|
| `order_id` | TEXT PK | Order identifier |
| `customer_id` | TEXT FK | Order-specific customer |
| `order_status` | TEXT | Source fulfillment status |
| `order_purchase_timestamp` | TEXT | Purchase event |
| `order_approved_at` | TEXT nullable | Approval event |
| `order_delivered_carrier_date` | TEXT nullable | Carrier handoff event |
| `order_delivered_customer_date` | TEXT nullable | Customer delivery event |
| `order_estimated_delivery_date` | TEXT nullable | Promised/estimated delivery |

### `order_items`

One row per `(order_id, order_item_id)`; foreign keys point to orders, products, and sellers.

| Column | Type | Meaning |
|---|---|---|
| `order_id`, `order_item_id` | TEXT, INTEGER composite PK | Item sequence within an order |
| `product_id`, `seller_id` | TEXT FK | Product and seller identifiers |
| `shipping_limit_date` | TEXT nullable | Seller shipping deadline |
| `price` | REAL | Item merchandise price, non-negative |
| `freight_value` | REAL | Allocated freight, non-negative |

### `order_payments`

One row per `(order_id, payment_sequential)`. An order can have multiple payment records.

| Column | Type | Meaning |
|---|---|---|
| `order_id`, `payment_sequential` | TEXT, INTEGER composite PK | Payment sequence within order |
| `payment_type` | TEXT nullable | Payment method |
| `payment_installments` | INTEGER nullable | Installment count |
| `payment_value` | REAL nullable | Recorded payment amount |

### `order_reviews`

One row per source CSV record, keyed by `source_row_number`. `review_id` is preserved but not assumed unique; an order may have multiple rows.

| Column | Type | Meaning |
|---|---|---|
| `source_row_number` | INTEGER PK | Stable 1-based data-row position in source file |
| `review_id` | TEXT | Source review identifier |
| `order_id` | TEXT FK | Reviewed order |
| `review_score` | INTEGER nullable | Score constrained to 1–5 |
| `review_comment_title`, `review_comment_message` | TEXT nullable | Optional free text |
| `review_creation_date`, `review_answer_timestamp` | TEXT nullable | Review events |

### `products`

One row per `product_id`.

| Column | Type | Meaning |
|---|---|---|
| `product_id` | TEXT PK | Product identifier |
| `product_category_name` | TEXT nullable | Portuguese category key |
| `product_name_lenght`, `product_description_lenght` | INTEGER nullable | Source spelling retained; text-length metadata |
| `product_photos_qty` | INTEGER nullable | Photo count |
| `product_weight_g` | INTEGER nullable | Weight in grams |
| `product_length_cm`, `product_height_cm`, `product_width_cm` | INTEGER nullable | Dimensions in centimeters |

### `sellers`

One row per `seller_id`, with ZIP prefix, city, and state.

### `category_translation`

One row per Portuguese `product_category_name`, mapped to `product_category_name_english`. Product category is not enforced as a foreign key because missing categories and missing translations are valid quality conditions to measure.

### `geolocation`

One row per source CSV record, keyed by `source_row_number`, with ZIP prefix, latitude, longitude, city, and state. ZIP prefixes are intentionally non-unique; no customer/seller foreign key points here because such a relationship would be many-to-many and could multiply rows.

## Relationship summary

```text
customers 1 ── * orders 1 ── * order_items * ── 1 products
                     │              │
                     │              * ── 1 sellers
                     ├── * order_payments
                     └── * order_reviews

products * ── 0..1 category_translation  (logical left join)
```
