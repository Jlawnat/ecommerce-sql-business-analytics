# Phase 3 Dashboard Data Contracts

## Presentation boundary

The dashboard is an aggregate presentation layer over verified Phase 2 and Phase 2.5 outputs. It does not query raw CSVs, rebuild statistical models, or expose customer-level records. The local SQLite databases are optional for the app and are used only for an availability diagnostic on the methodology page.

All commercial KPIs retain the existing delivered-order definition. Merchandise value excludes freight and is never labelled profit or accounting revenue. The observed period ends in August 2018.

## Contracted assets

| Dashboard asset | Checked-in source | Grain | Used by |
|---|---|---|---|
| `monthly_sales` | `reports/phase2_outputs/monthly_sales.csv` | Purchase month | Overview trend and anchors |
| `category_pareto` | `reports/phase2_outputs/category_pareto.csv` | Translated category | Overview concentration |
| `cohort_retention` | `reports/phase2_outputs/cohort_retention.csv` | Cohort × month offset | Retention heatmap |
| `cohort_summary` | `reports/phase2_outputs/cohort_summary.csv` | Acquisition cohort | Maturity table |
| `rfm_segments` | `reports/phase2_outputs/rfm_segments.csv` | RFM segment | Segment distribution |
| `delivery_state` | `reports/phase2_outputs/delivery_by_state.csv` | Customer state | Late-rate ranking |
| `delivery_category` | `reports/phase2_outputs/delivery_by_category.csv` | Order-attributed category | Late-rate ranking |
| `delivery_timing` | `reports/phase2_outputs/delivery_timing.csv` | Timing group | Review risks and unadjusted OR |
| `delivery_coverage` | `reports/phase2_outputs/delivery_coverage.csv` | Coverage summary | Population disclosure |
| `phase2_statistics` | `reports/phase2_outputs/statistical_results.json` | Statistical result | Contracted Phase 2 evidence |
| `repeat_km` | `reports/phase25_outputs/repeat_km_primary.csv` | Time horizon | KM curve and confidence band |
| `research_results` | `reports/phase25_outputs/research_results.json` | Research result | Models, sensitivity, stability |
| `delivery_subgroups` | `reports/phase25_outputs/delivery_subgroup_tables.csv` | Subgroup 2×2 table | Contracted heterogeneity evidence |

Required columns, source SQL or script, observation scope, and grain are declared in `dashboard/data.py`. A missing file raises an actionable `DataUnavailable` state; a schema mismatch raises `DataContractError`.

## Precomputed and dynamic presentation

Precomputed assets supply every published KPI, cohort cell, RFM segment, Kaplan–Meier estimate, confidence interval, adjusted model result, diagnostic, sensitivity bound, and subgroup statistic. Python does not refit models in the dashboard.

Dynamic presentation is limited to:

- changing the visible retention horizon without replacing censored nulls;
- switching state/category rankings and applying the disclosed minimum of 500 timing-eligible orders;
- choosing the top 20 category Pareto display;
- reconstructing the unadjusted order-level odds ratio and Wald interval from the pre-aggregated two-row delivery timing table;
- responsive formatting, sorting, tooltips, and chart layout.

## Export and privacy contract

`DashboardRepository.export_csv()` accepts only keys in `EXPORT_ALLOWLIST`. The allowlist contains non-customer aggregates. In particular, `rfm_customers.csv`, `delivery_model_population.csv`, analytics-mart rows, raw Olist files, and SQLite databases are not dashboard exports. Automated tests scan page sources and enforce the allowlist.

## Empty states and licensing

The dashboard can run from checked-in aggregates without licensed raw data. If aggregates are absent, it displays the exact Phase 2/2.5 reproduction commands rather than a traceback. Dataset attribution and CC BY-NC-SA 4.0 constraints remain documented in [DATA_SOURCE.md](DATA_SOURCE.md); this repository does not redistribute the dataset.

