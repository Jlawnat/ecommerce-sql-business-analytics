# Ecommerce Analytics Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible SQLite warehouse, validation suite, and initial SQL analyses for the nine Olist CSV files.

**Architecture:** A standard-library Python loader validates the input manifest, stages a new SQLite database, parses timestamps explicitly, enforces source-grain keys, and atomically replaces the output. SQL files own schema, validation, and analysis logic; unittest fixtures prove behavior without requiring the full dataset.

**Tech Stack:** Python 3 standard library (`csv`, `sqlite3`, `unittest`), SQLite SQL, Markdown

**Spec:** User-provided Phase 1 requirements in the 2026-11-10 conversation.

## Global Constraints

- Use the real Olist Brazilian E-Commerce Public Dataset; never fabricate measurements.
- Use built-in `sqlite3`; do not require cloud services, paid tools, credentials, or unnecessary packages.
- Never commit raw data, SQLite databases, credentials, or large generated files.
- Preserve source IDs and grains; document status filters, fan-out risks, licensing, and analytical limitations.
- Do not enter Phase 2/3, commit, or push.

## Review Focus

- A missing or renamed CSV must fail before replacing an existing database.
- Blank optional values and valid timestamps must load as `NULL` and normalized timestamp text.
- Duplicate source keys and broken mandatory relationships must fail transactionally.
- Re-running the loader over identical inputs must preserve counts and KPI results.
- KPI queries must aggregate each one-to-many table before cross-domain joins.

---

### Task 1: Repository contract and source manifest

**Files:** Create `.gitignore`, `requirements.txt`, `src/olist_config.py`, `docs/DATA_SOURCE.md`; replace `README.md`; test in `tests/test_ingestion.py`.

**Interfaces:** Produces `CSV_SPECS`, `EXPECTED_FILENAMES`, and documented download/placement commands.

- [x] Write tests asserting the exact nine filenames and missing-file diagnostics.
- [x] Run the focused tests and confirm they fail before implementation.
- [x] Implement the manifest and repository/source documentation.
- [x] Run the focused tests and confirm they pass.

### Task 2: Schema and transactional ingestion

**Files:** Create `sql/schema/001_create_tables.sql`, `src/ingest.py`, `scripts/build_database.py`; extend `tests/test_ingestion.py`.

**Interfaces:** Consumes `CSV_SPECS`; produces `build_database(raw_dir: Path, database_path: Path) -> dict[str, int]` and nine normalized tables.

- [x] Add fixture tests for parsing, row counts, keys, foreign keys, duplicate rejection, and idempotent reruns.
- [x] Run tests and confirm ingestion behavior is initially absent.
- [x] Implement explicit column mapping, timestamp normalization, staged database construction, indexes, and FK checks.
- [x] Run ingestion tests and confirm all pass.

### Task 3: Validation and KPI analyses

**Files:** Create `sql/analysis/00_data_quality.sql`, `01_monthly_merchandise_value.sql`, `02_category_sales_concentration.sql`, `03_late_delivery_review_scores.sql`; create `scripts/run_analysis.py`; add `tests/test_analysis.py`.

**Interfaces:** Consumes the schema; produces named result sections on stdout and reusable SQL queries with an explicit delivered-status cohort.

- [x] Add tests for merchandise-value reconciliation, repeat-safe cardinality, windowed category shares, late-delivery grouping, and fan-out diagnostics.
- [x] Run tests and confirm analysis files/interfaces are initially absent.
- [x] Implement CTE-based queries that isolate one-to-many grains before joining.
- [x] Run all analysis tests and confirm expected fixture values.

### Task 4: Documentation and genuine run report

**Files:** Create `docs/DATA_DICTIONARY.md`, `docs/METRIC_DEFINITIONS.md`, `docs/DATA_QUALITY.md`, `reports/PHASE1_RESULTS.md`; update `README.md`.

**Interfaces:** Documents commands, table grains, semantics, limitations, pending/full-dataset results, and traceability to SQL.

- [x] Attempt authenticated Kaggle retrieval only if existing authentication is detected.
- [x] Run the complete test suite and record the genuine outcome.
- [x] If all nine CSVs exist, build the database and record measured counts/findings; otherwise mark every measurement pending and provide exact acquisition steps.
- [x] Self-review all requirements, inspect Git status, and confirm no raw/generated artifacts are tracked.
