"""Exact source-file and column contract for the public Olist dataset."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CsvSpec:
    filename: str
    table: str
    columns: tuple[str, ...]
    timestamp_columns: tuple[str, ...] = ()
    integer_columns: tuple[str, ...] = ()
    real_columns: tuple[str, ...] = ()
    add_source_row_number: bool = False


CSV_SPECS = (
    CsvSpec(
        "olist_customers_dataset.csv",
        "customers",
        ("customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"),
        integer_columns=("customer_zip_code_prefix",),
    ),
    CsvSpec(
        "olist_geolocation_dataset.csv",
        "geolocation",
        ("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"),
        integer_columns=("geolocation_zip_code_prefix",),
        real_columns=("geolocation_lat", "geolocation_lng"),
        add_source_row_number=True,
    ),
    CsvSpec(
        "olist_order_items_dataset.csv",
        "order_items",
        ("order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"),
        timestamp_columns=("shipping_limit_date",),
        integer_columns=("order_item_id",),
        real_columns=("price", "freight_value"),
    ),
    CsvSpec(
        "olist_order_payments_dataset.csv",
        "order_payments",
        ("order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"),
        integer_columns=("payment_sequential", "payment_installments"),
        real_columns=("payment_value",),
    ),
    CsvSpec(
        "olist_order_reviews_dataset.csv",
        "order_reviews",
        ("review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"),
        timestamp_columns=("review_creation_date", "review_answer_timestamp"),
        integer_columns=("review_score",),
        add_source_row_number=True,
    ),
    CsvSpec(
        "olist_orders_dataset.csv",
        "orders",
        ("order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"),
        timestamp_columns=("order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"),
    ),
    CsvSpec(
        "olist_products_dataset.csv",
        "products",
        ("product_id", "product_category_name", "product_name_lenght", "product_description_lenght", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"),
        integer_columns=("product_name_lenght", "product_description_lenght", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"),
    ),
    CsvSpec(
        "olist_sellers_dataset.csv",
        "sellers",
        ("seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"),
        integer_columns=("seller_zip_code_prefix",),
    ),
    CsvSpec(
        "product_category_name_translation.csv",
        "category_translation",
        ("product_category_name", "product_category_name_english"),
    ),
)

EXPECTED_FILENAMES = tuple(spec.filename for spec in CSV_SPECS)
