# Olist Ecommerce SQL Business Analytics

A reproducible, portfolio-oriented SQL and Python case study built from the **Olist Brazilian E-Commerce Public Dataset** (anonymized marketplace orders from 2016–2018). Phase 1 creates a normalized SQLite database, validates source quality, and implements three traceable business analyses without inventing missing business context or results.

## What is included

- Standard-library Python ingestion with explicit type and timestamp handling
- Nine source-grain SQLite tables with keys, relationships, checks, and indexes
- Transactional, idempotent rebuild: a failed load never replaces the last good database
- Data-quality SQL for counts, missingness, keys, joins, chronology, cardinality, categories, and fan-out risk
- Delivered-order KPI queries for summary/repeat behavior, monthly merchandise value, category concentration, review distribution, and delivery timeliness versus reviews
- Deterministic fixture tests that require no private data or third-party packages

## Repository layout

```text
data/raw/          # Place the nine source CSVs here (ignored by Git)
data/processed/    # Generated SQLite database (ignored by Git)
docs/              # Source, dictionary, metric, and quality documentation
reports/           # Reproducible run reports
scripts/           # User-facing build and analysis commands
sql/schema/        # SQLite DDL
sql/analysis/      # Quality checks and business queries
src/               # Ingestion implementation and source manifest
tests/             # Small synthetic fixtures and behavior tests
visualizations/    # Reserved for a later phase; no Phase 2 work included
```

## Quick start

Requirements: Python 3.11 or newer. Phase 1 uses only the Python standard library.

1. Obtain the dataset using [docs/DATA_SOURCE.md](docs/DATA_SOURCE.md) and place all nine CSVs directly in `data/raw/`.
2. Build the database:

   ```bash
   python3 scripts/build_database.py
   ```

3. Run every quality check and analysis:

   ```bash
   python3 scripts/run_analysis.py
   ```

4. Run the tests:

   ```bash
   python3 -m unittest discover -s tests -v
   ```

Run one analysis only with, for example:

```bash
python3 scripts/run_analysis.py --query 01_monthly_merchandise_value.sql
```

The default generated database is `data/processed/olist.sqlite`. Both raw data and generated databases are intentionally ignored by Git.

## Analytical policy

Commercial KPIs use only `order_status = 'delivered'`: this represents completed fulfillment and avoids treating canceled, unavailable, or still-processing orders as realized merchandise activity. Merchandise value is `SUM(order_items.price)` and explicitly excludes freight. Payments and reviews are pre-aggregated to order grain before any cross-domain join.

This public historical dataset is not the author's Shopify store. It does not contain sessions, ad spend, cost of goods, or randomized treatment assignment, so it cannot establish true site conversion, ROAS, CAC, product profit, or A/B-test lift. Delivery/review results are associations, not causal effects. See [metric definitions](docs/METRIC_DEFINITIONS.md) for full semantics.

## Documentation

- [Data source, attribution, license, and download](docs/DATA_SOURCE.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Metric definitions](docs/METRIC_DEFINITIONS.md)
- [Data-quality framework](docs/DATA_QUALITY.md)
- [Phase 1 run status](reports/PHASE1_RESULTS.md)
SQL and Python analytics on real-world ecommerce data
