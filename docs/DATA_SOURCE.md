# Data Source

## Attribution and license

This project uses the **Brazilian E-Commerce Public Dataset by Olist**, published by Olist on Kaggle:

<https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>

The dataset contains anonymized marketplace records from 2016–2018. It is licensed under **CC BY-NC-SA 4.0**. Any reuse of this project's data-derived work must retain attribution, remain non-commercial, and use a compatible share-alike license. The dataset itself is not redistributed by this repository.

This is third-party historical marketplace data. It must never be represented as transactions from the project author's own ecommerce or Shopify store.

## Acquisition status

On 2026-11-10, all nine expected CSVs were detected after manual placement in `data/raw/`, and the real SQLite build completed successfully. The environment did not require a Kaggle CLI or repository-stored credentials. No credential was requested, created, printed, or stored, and the raw files remain excluded from Git. The procedures below document how to reproduce acquisition in a fresh clone.

## Browser download (no CLI required)

1. Open the Kaggle dataset page above while signed in.
2. Select **Download** to obtain the dataset ZIP.
3. Extract the ZIP outside the repository.
4. Copy exactly these files directly into `data/raw/`:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

From the repository root, verify placement without displaying data:

```bash
python3 -c "from pathlib import Path; from src.ingest import validate_source_files; validate_source_files(Path('data/raw')); print('All nine source files found')"
```

## Kaggle CLI option (only with preconfigured local authentication)

Install and authenticate the Kaggle CLI according to Kaggle's own documentation; do not add `kaggle.json` to this repository. Then run:

```bash
mkdir -p /tmp/olist-download
kaggle datasets download -d olistbr/brazilian-ecommerce -p /tmp/olist-download --unzip
cp /tmp/olist-download/*.csv data/raw/
python3 scripts/build_database.py
```

The `.gitignore` excludes `data/raw/*`, `kaggle.json`, archives, and generated SQLite files. Before publishing, confirm with `git status --short` that no source data or credentials are staged.
