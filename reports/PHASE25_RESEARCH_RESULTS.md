# Phase 2.5 Research Results

**Run date:** 2026-11-10 (Australia/Sydney)  
**Design:** retrospective observational analysis with administrative right censoring  
**Primary cutoff:** 2018-09-01 00:00:00

## Research populations

| Analysis | Eligible unit | N | Event / outcome |
|---|---|---:|---:|
| Repeat-purchase survival | unique customer with first observed delivered purchase before cutoff | 93,358 | 2,801 second observed purchases |
| Delivery timing | delivered order with actual and estimated timestamps | 96,470 | 7,826 late orders |
| Adjusted satisfaction model | timing-eligible order with order-level review | 95,824 | 12,236 low reviews |
| Single-seller sensitivity | timing/review eligible single-seller order | 94,563 | 11,640 low reviews |

Population definitions originate in [`09_repeat_purchase_research.sql`](../sql/analysis/09_repeat_purchase_research.sql) and [`10_delivery_satisfaction_research.sql`](../sql/analysis/10_delivery_satisfaction_research.sql). The analytical mart and its 12 blocking checks are documented in [`PHASE25_AUDIT.md`](../docs/PHASE25_AUDIT.md).

## Customer repeat-purchase research

### Kaplan–Meier estimates

The event is a second observed delivered purchase. Non-events are right-censored at the analysis cutoff; they are not labeled churned.

| Horizon after first observed purchase | KM repeat incidence | 95% log-log Greenwood CI | Customers at baseline |
|---:|---:|---:|---:|
| 30 days | 1.52% | 1.45%–1.61% | 93,358 |
| 60 days | 1.87% | 1.79%–1.96% | 93,358 |
| 90 days | 2.13% | 2.04%–2.22% | 93,358 |
| 180 days | 2.74% | 2.63%–2.86% | 93,358 |
| 365 days | 3.81% | 3.66%–3.97% | 93,358 |

The median time to repeat cannot be estimated because estimated repeat incidence never approaches 50%. Among the 2,801 observed repeaters only, the descriptive median time to second order is 28.98 days; conditioning on future repeat status means this is not a population retention estimand.

### Cutoff sensitivity

| Cutoff | Customers | Observed repeat events | KM repeat by 90 days | KM repeat by 365 days |
|---|---:|---:|---:|---:|
| 2018-03-01 | 55,525 | 1,623 | 2.46% | 4.45% |
| 2018-06-01 | 75,387 | 2,230 | 2.28% | 4.12% |
| 2018-09-01 | 93,358 | 2,801 | 2.13% | 3.81% |

Administrative censoring is handled correctly at each cutoff, but changing customer/cohort composition remains. The monotonic decline across later cutoffs should not be interpreted as a causal deterioration.

### RFM stability

Among 75,387 customers present at both June and September cutoffs, exact segment agreement was 57.76% and Cohen's κ was 0.426. RFM is therefore useful as a dated operational snapshot, not a permanent customer attribute. Scores and segment dates must travel together.

## Delivery and satisfaction research

### Adjusted model

The primary grouped-binomial logistic model adjusted for purchase period, customer-state group, top-15 merchandise category versus other, merchandise-value band, and single- versus multi-seller status. Sparse pre-2017 months and states with fewer than 200 timing-eligible orders were grouped before fitting. The model converged in 7 iterations with 64 parameters.

| Estimand / diagnostic | Result |
|---|---:|
| Adjusted conditional odds ratio, late vs on-time/early | 11.41 |
| 95% CI | 10.81–12.04 |
| Standardized low-review risk if late | 51.73% |
| Standardized low-review risk if on-time/early | 9.24% |
| Standardized absolute risk difference | +42.49 pp |
| 95% CI for risk difference | +41.30 to +43.69 pp |
| AUC | 0.712 |
| Brier score | 0.0933 |

The adjusted OR is conditional and non-collapsible. The standardized risk contrast is easier to interpret but remains model-dependent and observational. Neither is a causal delivery effect.

### Sensitivity checks

- **Single-seller orders:** adjusted OR 11.51 (95% CI 10.90–12.15), standardized risk difference +42.67 pp (95% CI +41.46 to +43.87). The primary association is not driven by multi-seller orders.
- **Alternative score=1 outcome:** adjusted OR 11.80 (95% CI 11.15–12.48), standardized risk difference +36.92 pp (95% CI +35.74 to +38.11).
- **Missing reviews:** 165 late and 481 on-time/early timing-eligible orders lack a review. Under deliberately extreme assignments, the raw low-review risk difference ranges from +43.17 to +45.82 pp, versus observed +44.80 pp. This narrow bound reflects low missingness but does not prove missing-at-random.
- **Heterogeneity:** Cochran Q rejected a common unadjusted log-OR across month (Q=166.36, df=19, p=1.46e-25, I²=88.6%), state (Q=121.61, df=21, p=3.61e-16, I²=82.7%), and category (Q=113.41, df=33, p=9.44e-11, I²=70.9%). The direction is broadly adverse, but magnitude varies materially; one pooled number should not drive every operational subgroup decision.

## Business decision framework

### Recommendation 1 — Late-order service recovery, prospectively tested

- **Business problem:** late orders are associated with substantially more low reviews.
- **Evidence:** adjusted OR 11.41; standardized difference +42.49 pp; single-seller and score-1 checks remain large.
- **Potentially affected population:** historically 7,826 timing-eligible late orders, including 7,661 with observed reviews.
- **Uncertainty:** observational confounding, review selection, and strong subgroup heterogeneity remain; the model does not prove recovery outreach will improve ratings.
- **Operational action:** instrument a real-time late-order flag and a standardized, low-friction service-recovery workflow. Preserve a no-contact control group during validation.
- **Success metrics:** order-level low-review share and mean review score under intention to treat.
- **Guardrails:** review completion, customer-contact rate, complaint/escalation rate, refunds/credits per order, and contact latency.
- **Prospective validation:** randomized customer-level experiment among newly detected late orders, with stable 1:1 assignment, predeclared analysis window, A/A instrumentation check, and no peeking-based stopping. Sample size must be set from the chosen minimum detectable effect before launch.

### Recommendation 2 — Prioritize route/seller diagnosis where exposure and heterogeneity are high

- **Business problem:** late-delivery exposure is uneven across geography and category.
- **Evidence:** Phase 2 late rates were MA 19.67%, CE 15.32%, BA 14.04%, RJ 13.47%, versus SP 5.89%; month/state/category Q tests show material heterogeneity.
- **Potentially affected population:** 17,602 historical timing-eligible orders across MA, CE, BA, and RJ; category diagnostics should focus on adequately sized electronics, baby, office-furniture, and health/beauty groups.
- **Uncertainty:** no carrier, route distance, promised-time construction, or causal treatment variable is available. Subgroup tests are exploratory and not multiplicity-adjusted.
- **Operational action:** add carrier, seller, origin-destination, and promise-construction fields; decompose late rates and p90 delay before changing routing policy.
- **Success metrics:** late rate and p90 days-versus-estimate by prespecified lane.
- **Guardrails:** on-time rate outside targeted lanes, cancellation rate, freight cost per order, and sample-size/coverage thresholds.
- **Prospective validation:** validate any routing rule in a staged or randomized eligible-lane rollout, with lane-level balance and a predeclared holdout.

### Recommendation 3 — Replace static “churn” targeting with maturity-aware repeat measurement

- **Business problem:** 97.00% of customers have one observed delivered order, but later customers have unequal follow-up and RFM labels change with the snapshot.
- **Evidence:** KM second-purchase incidence is 2.13% by 90 days and 3.81% by 365 days; June-to-September RFM agreement is 57.76% (κ=0.426). The Phase 2 high-value one-time segment contains 8,084 customers and 27.44% of merchandise value.
- **Potentially affected population:** one-order customers with at least the chosen 30/90/180-day maturity window; high-value one-time customers are a practical research stratum, not proven churners.
- **Uncertainty:** first observed purchase may not be acquisition, off-platform purchases are absent, and cutoff sensitivity changes the estimated curve.
- **Operational action:** date-stamp RFM snapshots, enforce minimum follow-up, and report KM repeat incidence with risk-set/CI information instead of labeling non-returners churned.
- **Success metrics:** intention-to-treat second delivered purchase by 90/180 days and time-to-second-purchase KM curve.
- **Guardrails:** unsubscribe/complaint rate, discount or contact cost, cancellation rate, and merchandise-value distribution balance.
- **Prospective validation:** if a retention message is proposed, randomize eligible mature one-order customers within prespecified value strata; analyze assignment, not message opens, and report both absolute difference and confidence interval. No effect is assumed in advance.

## Interpretation boundaries

This research strengthens population control, censoring, adjustment, and uncertainty reporting. It does not convert observational marketplace history into a randomized causal study. The operational recommendations are priorities for measurement and prospective testing, not claims of achieved uplift, profit, or customer churn.

## Reproducibility

```bash
python3 scripts/phase2_analysis.py
python3 scripts/build_analytics_mart.py
python3 scripts/phase25_research.py
python3 -m unittest discover -s tests -v
```

Machine-readable evidence is under `reports/phase25_outputs/`; charts are [`phase25_repeat_km.svg`](../visualizations/phase25_repeat_km.svg) and [`phase25_adjusted_delivery.svg`](../visualizations/phase25_adjusted_delivery.svg).

Final validation ran **26 tests: 26 passed, 0 failed**. Both research SQL files executed on the real databases; all seven project SVGs parsed as valid XML; tracked raw/processed data contains only `.gitkeep`; the credential-pattern scan returned no tracked matches; and the source SQLite SHA-256 remained `ef912124ab82ec5217ec3cd602affa115ad8520027ebefdcc3251197b5da3090` before and after mart/research generation.
