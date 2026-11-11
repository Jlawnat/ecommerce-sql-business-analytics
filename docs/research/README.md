# Research index

The research program answers two decision areas: customer repeat behavior and the association between delivery timing and satisfaction. Commercial summaries and category concentration provide the operating context. This index points to the authoritative definitions and results rather than restating every estimate.

## Research case studies

### Customer repeat purchase

- **Business question:** How often and how quickly do customers place a second observed delivered order?
- **Methods:** acquisition-cohort retention with explicit censoring, deterministic RFM snapshots, and Kaplan–Meier time to second observed delivered purchase.
- **Evidence:** [Phase 2 results](../../reports/PHASE2_RESULTS.md), [Phase 2.5 methods](../PHASE25_STATISTICAL_METHODS.md), and [`09_repeat_purchase_research.sql`](../../sql/analysis/09_repeat_purchase_research.sql).
- **Interpretation:** observed repeat incidence reaches 2.13% by day 90 and 3.81% by day 365 in this historical marketplace coverage.
- **Boundary:** first observed purchase is not proven acquisition; censoring is not churn; off-platform and post-August 2018 activity are unavailable.

### Delivery and satisfaction

- **Business question:** How strongly is late delivery associated with a low order-level review after measured adjustment?
- **Methods:** order-level review aggregation, Wilson intervals, grouped-binomial logistic regression, standardized risks, diagnostics, subgroup heterogeneity, alternative outcome/single-seller sensitivity, and extreme missing-review bounds.
- **Evidence:** [Phase 2.5 research results](../../reports/PHASE25_RESEARCH_RESULTS.md), [`10_delivery_satisfaction_research.sql`](../../sql/analysis/10_delivery_satisfaction_research.sql), and [`scripts/phase25_research.py`](../../scripts/phase25_research.py).
- **Interpretation:** low-review rates are 53.99% for late orders and 9.19% for on-time/early orders; the adjusted odds ratio is 11.41 (95% CI 10.81–12.04), with a standardized risk difference of +42.49 percentage points (95% CI +41.30 to +43.69).
- **Boundary:** this is an in-sample observational association, not a causal delivery effect or externally validated intervention estimate.

## Methodology navigation

| Topic | Definition | Implementation or validation |
|---|---|---|
| Cohort retention and censoring | [Metric definitions](../METRIC_DEFINITIONS.md) | [`05_customer_cohort_retention.sql`](../../sql/analysis/05_customer_cohort_retention.sql) |
| RFM scoring and cutoff | [Metric definitions](../METRIC_DEFINITIONS.md) | [`06_rfm_segmentation.sql`](../../sql/analysis/06_rfm_segmentation.sql) |
| Kaplan–Meier and Greenwood intervals | [Statistical methods](../PHASE25_STATISTICAL_METHODS.md) | [`test_phase25_statistics.py`](../../tests/test_phase25_statistics.py) |
| Delivery exposure and review outcome | [Metric definitions](../METRIC_DEFINITIONS.md) | [`10_delivery_satisfaction_research.sql`](../../sql/analysis/10_delivery_satisfaction_research.sql) |
| Adjusted logistic model and standardization | [Statistical methods](../PHASE25_STATISTICAL_METHODS.md) | [`scripts/phase25_research.py`](../../scripts/phase25_research.py) |
| Independent real-data anchors | [Phase 2.5 audit](../PHASE25_AUDIT.md) | [`test_phase25_audit.py`](../../tests/test_phase25_audit.py) |

## Scientific reading guide

- Merchandise value is item price only; it is not profit, margin, payment receipts, or universal GMV.
- Observed repeat ordering is not confirmed loyalty, and inactivity is not confirmed churn.
- A censored retention cell is unavailable follow-up; an observed zero is a measured zero.
- An odds ratio is not a risk ratio. The standardized risk difference provides an absolute model-based contrast.
- Adjustment, diagnostics, and sensitivity analyses improve transparency; none creates randomization or causal identification.
- AUC and Brier score are in-sample diagnostics for this historical model, not external validation.

Read the consolidated [research limitations](LIMITATIONS.md) before reusing any finding.
