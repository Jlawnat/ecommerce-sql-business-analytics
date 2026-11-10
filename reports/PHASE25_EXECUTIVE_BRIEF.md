# Phase 2.5 Executive Brief

## Decision summary

The audit found no discrepancy in the Phase 1/2 commercial anchors: 96,478 delivered orders, BRL 13,221,498.11 merchandise value, 93,358 delivered customers, and 2,801 observed repeat customers. A separate analytical mart now enforces four explicit grains and passes 12 source reconciliation, uniqueness, null, and relationship checks.

Customer return is both uncommon and follow-up dependent. Kaplan–Meier estimated a second observed delivered purchase for 2.13% of customers by 90 days (95% CI 2.04%–2.22%) and 3.81% by 365 days (3.66%–3.97%). RFM exact segment agreement between June and September snapshots was only 57.76%; segments should always be date-stamped and should not be treated as stable customer identities or churn labels.

Late delivery remains strongly associated with low reviews after measured adjustment. The adjusted odds ratio was 11.41 (95% CI 10.81–12.04), and the model-standardized absolute difference was +42.49 percentage points (41.30–43.69). Single-seller and score-1 sensitivities were consistent, and extreme missing-review assignments left the raw difference between +43.17 and +45.82 points. Strong month/state/category heterogeneity and unmeasured carrier/route factors prevent a causal interpretation.

## Recommended actions

1. Instrument late-order service recovery and validate it with a randomized holdout; measure low reviews and operational guardrails under intention to treat.
2. Add carrier/route/promise data and prioritize diagnostic work in higher-late-rate states and adequately sized categories before changing policy.
3. Replace static “churn” lists with maturity-aware KM reporting and date-stamped RFM; test any retention outreach prospectively among eligible one-order customers.

## What management should not infer

- The data does not show that a recovery message, routing change, or retention offer will improve an outcome.
- Non-returning customers are not confirmed churners.
- Merchandise value is not revenue, margin, or profit.
- Statistical significance does not remove selection bias, residual confounding, or subgroup variation.

Full evidence: [`PHASE25_RESEARCH_RESULTS.md`](PHASE25_RESEARCH_RESULTS.md), [`PHASE25_AUDIT.md`](../docs/PHASE25_AUDIT.md), and [`PHASE25_STATISTICAL_METHODS.md`](../docs/PHASE25_STATISTICAL_METHODS.md).
