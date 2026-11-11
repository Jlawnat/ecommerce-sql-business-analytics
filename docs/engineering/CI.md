# Continuous integration and test boundaries

The GitHub Actions workflow is deliberately split so a green clean-checkout build does not imply that licensed real-data audits ran.

## CI jobs

| Job | Runs in a clean checkout | What it proves |
|---|---:|---|
| Documentation, privacy, and repository hygiene | Yes | Relative links, Mermaid source structure, screenshot assets, workflow policy, forbidden paths, secret patterns, and frontend row-identifier boundary |
| Python and SQL tests without licensed Olist data | Yes | Synthetic ingestion, SQL logic, mart behavior, dashboard contracts/charts/smoke tests, statistical known answers, and deterministic web contracts |
| Next.js type, lint, contract, and production checks | Yes | Exact npm install, TypeScript, ESLint, aggregate contract validation, deterministic publishing, and production compilation |

The workflow lives at [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

## Intentionally excluded from clean CI

[`tests/test_phase25_audit.py`](../../tests/test_phase25_audit.py) contains four tests that independently query `data/processed/olist.sqlite`. The licensed raw CSVs and generated database are correctly absent from GitHub. These four tests are therefore not included in the clean-data CI command and are not reported as CI passes.

Run them locally after acquiring and building the dataset:

```bash
.venv/bin/python scripts/build_database.py
.venv/bin/python -m unittest tests.test_phase25_audit -v
```

The tests verify delivered-order/customer/value anchors, cohort and RFM reconciliation, delivery statistics at order grain, sample preservation, and adjusted-model convergence.

## CI-equivalent local commands

```bash
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m unittest -v \
  tests.test_ingestion \
  tests.test_analysis \
  tests.test_analytics_mart \
  tests.test_dashboard_charts \
  tests.test_dashboard_data \
  tests.test_dashboard_smoke \
  tests.test_phase25_statistics \
  tests.test_web_data_contract \
  tests.test_repository_hygiene

cd web
npm ci
npm run typecheck
npm run lint
npm run build
```

The full local suite may be run with `python -m unittest discover -s tests -v`; its output must be read for skips rather than summarized only by exit code.
