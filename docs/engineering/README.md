# Engineering and reproducibility guide

## Requirements

- Python 3.11 or newer
- Node.js 22 and npm for Dashboard V2
- SQLite through Python's standard-library `sqlite3`
- Nine Olist source CSVs only when rebuilding or auditing against the real dataset

The checked-in aggregate outputs are sufficient to run both dashboards. Raw CSVs and generated databases are intentionally absent from Git.

## Install

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.lock
cd web
npm ci
cd ..
```

`requirements.txt` pins the three direct application dependencies; `requirements.lock` records the complete tested Python environment. `web/package-lock.json` locks the complete frontend dependency tree.

## Run Dashboard V2

```bash
cd web
npm run dev
```

Open `http://localhost:3000`. The `predev` hook deterministically republishes the checked-in aggregate contracts before Next.js starts.

For a production-mode local check:

```bash
cd web
npm run build
npm start
```

No public Next.js deployment is claimed by this repository. A deployment should run the same build command, expose no raw/database files, and be verified before a URL is added to the README.

## Run the preserved Streamlit application

```bash
.venv/bin/streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`. Streamlit reads checked-in aggregates through `dashboard/data.py`; it remains separate from Dashboard V2.

## Reproduce from licensed source data

1. Follow [source acquisition and licensing](../DATA_SOURCE.md).
2. Place exactly nine CSV files directly in `data/raw/`.
3. Execute:

```bash
.venv/bin/python scripts/build_database.py
.venv/bin/python scripts/run_analysis.py
.venv/bin/python scripts/phase2_analysis.py
.venv/bin/python scripts/build_analytics_mart.py
.venv/bin/python scripts/phase25_research.py
.venv/bin/python scripts/publish_web_aggregates.py
```

Generated SQLite databases remain under ignored `data/processed/`. The scripts replace outputs deterministically only after their checks pass.

## Test

Run all locally available tests:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Run frontend validation:

```bash
cd web
npm run typecheck
npm run lint
npm run build
```

Run documentation, Mermaid-source, screenshot, privacy, and workflow checks:

```bash
.venv/bin/python scripts/check_repository.py
```

The exact clean-CI and licensed-data boundaries are documented in [CI](CI.md).

## Deployment preparation

Dashboard V2 is a static-compatible Next.js application whose data is checked-in aggregate JSON. Before deploying:

1. Run the full frontend and repository checks.
2. Confirm `git ls-files` contains no ignored raw, database, environment, cache, or dependency files.
3. Build with `npm ci && npm run build` from `web/`.
4. Configure the hosting project root as `web/` if the platform requires one.
5. Verify all four routes, source links, mobile layouts, and the aggregate-only download policy on the deployed origin.
6. Add a public URL only after that verification succeeds.

See [system architecture](../architecture/README.md), [SQL engineering](SQL_ENGINEERING.md), and [dashboard data contracts](../PHASE3_DATA_CONTRACTS.md).
