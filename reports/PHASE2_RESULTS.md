# Phase 2 — Advanced E-Commerce Business Analytics

**Run date:** 2026-11-10 (Australia/Sydney)  
**Database:** `data/processed/olist.sqlite`  
**Status:** Complete; Phase 1 definitions and all Phase 1 queries were preserved.

## 1. Executive summary

Phase 2 confirms that observed customer return behavior is low and heavily censored near the dataset boundary. Across mature cells, weighted exact-month retention was 0.48% in month 1, 0.34% in month 2, 0.25% in month 3, and 0.26% in month 4. These are exact-month activity rates, not lifetime retention. The RFM distribution explains why frequency quintiles would be misleading: 90,557 of 93,358 customers (97.00%) had exactly one delivered order, while only 2,801 were observed repeat purchasers.

Delivered merchandise value remained BRL 13,221,498.11 across every independent reconciliation. The first 18 categories reached 81.29% of value; the largest category, `health_beauty`, contributed 9.33%, so concentration is broad rather than dependent on one category. May 2018 had the highest monthly merchandise value (BRL 977,544.69), but boundary and sparse months are excluded from interpretable growth comparisons.

Delivery timing has a large observational association with satisfaction. Among reviewed and timing-eligible orders, late orders averaged 2.5665 versus 4.2943 for on-time/early orders, a difference of -1.7278 points (95% CI -1.7657 to -1.6899). Low reviews (score 1–2 after order-level review aggregation) occurred in 53.99% of late orders versus 9.19% of on-time/early orders, a +44.80 percentage-point difference (95% CI +43.67 to +45.93). The association remained strong after stratifying by purchase month, customer state, and merchandise-value band (Mantel–Haenszel common odds ratio 10.54; CMH p < 1e-300), but it is not causal.

## 2. Research questions

1. How do monthly acquisition cohorts retain, repeat, and accumulate merchandise value?
2. How can customers be segmented reproducibly by recency, frequency, and monetary value without splitting the one-order mass arbitrarily?
3. How do delivered merchandise value, orders, average order value, category concentration, and category mix change over time?
4. Which states and order-level categories show elevated late-delivery shares, and does the delivery/review association persist within observed covariate strata?

## 3. Dataset and metric definitions

All commercial analyses use `orders.order_status = 'delivered'`. Customer identity is `customer_unique_id`. Merchandise value is `SUM(order_items.price)` and excludes freight; it is not accounting revenue, profit, or payment receipts. Orders are assigned to purchase month. Late delivery retains the Phase 1 full-timestamp rule: actual customer delivery strictly later than the estimated timestamp.

The RFM cutoff is fixed at `2018-09-01 00:00:00`; no later purchase can enter RFM. Recency is calendar days since last delivered purchase, frequency is distinct delivered orders, and monetary is item price. Frequency scores are 1/3/5 for one/two/three-or-more orders, preserving ties. Recency and monetary use the explicit bands documented in [`docs/METRIC_DEFINITIONS.md`](../docs/METRIC_DEFINITIONS.md).

Cohort month is the first *observed* delivered purchase month. Exact month-N retention requires activity in that calendar offset. A cell is `NULL` when follow-up is not yet observable and zero only when the follow-up month is observable with no return. “Month 4+” is an ever-returned-after-month-4 measure. Overall repeat rate and cohort retention therefore answer different questions.

## 4. SQL methodology

- [`05_customer_cohort_retention.sql`](../sql/analysis/05_customer_cohort_retention.sql) uses CTEs, calendar month offsets, conditional aggregation, and a recursive offset series to produce cohort summaries and censor-aware heatmap cells.
- [`06_rfm_segmentation.sql`](../sql/analysis/06_rfm_segmentation.sql) reduces items to order grain, aggregates by unique customer before the cutoff, applies tie-preserving scores, and returns customer and segment results.
- [`07_sales_category_trends.sql`](../sql/analysis/07_sales_category_trends.sql) uses `LAG` for MoM changes, windowed cumulative shares for Pareto analysis, and a dense month/category grid. “Interpretable” changes require consecutive months, at least 100 delivered orders in each, and no boundary month.
- [`08_delivery_segment_analysis.sql`](../sql/analysis/08_delivery_segment_analysis.sql) first averages multiple review rows per order. Mixed-category orders are assigned to their greatest item-price category, with alphabetical tie-breaking; 780 of 96,470 eligible orders (0.81%) used mixed-order attribution. The query produces coverage, state/category comparisons, and month × state × value-band strata without joining payments.

SQL remains the source of KPI truth. [`phase2_analysis.py`](../scripts/phase2_analysis.py) executes those queries, writes extracts, calculates inference from SQL aggregates, and draws SVG files.

## 5. Verified analytical results

### Cohort and retention

The cohort query reconciled to 93,358 customers, 2,801 repeat customers, and BRL 13,221,498.11. Across all observable cohorts, weighted exact-month retention was:

| Offset | Returning customers | Eligible cohort denominator | Retention |
|---:|---:|---:|---:|
| Month 1 | 421 | 87,214 | 0.48% |
| Month 2 | 273 | 81,265 | 0.34% |
| Month 3 | 192 | 75,387 | 0.25% |
| Month 4 | 176 | 68,881 | 0.26% |

The 2017 cohorts generally show repeat-purchase rates around 2.60%–7.25%. Later-cohort repeat rates fall as low as 0.55%, but those cohorts have less follow-up and must not be read as deterioration. The September 2016 and December 2016 cohorts each contain one customer and are explicitly sparse.

### RFM segmentation

| Segment | Customers | Customer share | Merchandise value | Value share |
|---|---:|---:|---:|---:|
| Inactive in observed window | 36,392 | 38.98% | BRL 5,080,115.48 | 38.42% |
| Recent customers | 30,822 | 33.01% | BRL 2,541,320.44 | 19.22% |
| Other established customers | 15,259 | 16.34% | BRL 1,243,637.24 | 9.41% |
| High-value one-time customers | 8,084 | 8.66% | BRL 3,628,016.20 | 27.44% |
| Loyal repeat customers | 1,233 | 1.32% | BRL 228,703.63 | 1.73% |
| Repeat customers at risk | 997 | 1.07% | BRL 248,766.51 | 1.88% |
| Champions | 571 | 0.61% | BRL 250,938.61 | 1.90% |

“Inactive” means only that the last observed purchase was more than 365 days before the cutoff. The data cannot prove churn. High-value one-time customers are only 8.66% of customers but contribute 27.44% of merchandise value, making them a distinct follow-up population without implying that outreach will cause another purchase.

### Sales and category intelligence

May 2018 led merchandise value at BRL 977,544.69; November 2017 led delivered orders at 7,289. Among comparable months, the largest positive MoM changes included February 2017 (+109.51%), March 2017 (+53.36%), and November 2017 (+52.37%); the largest decline was December 2017 (-26.50%). September 2016, December 2016, and August 2018 are marked incomplete/sparse and their adjacent growth calculations are not used as trend evidence.

The top five categories contributed 39.83%, the top ten 62.43%, and the first 18 reached 81.29%. Relevant mix changes in consecutive well-represented months included `computers` rising 5.84 percentage points in August 2017 then falling 5.24 points in November 2017; `bed_bath_table` rose 5.03 points in July 2017; and `toys` fell 5.27 points in January 2018. These are composition changes, not demand-causal explanations.

### Delivery, region, category, and satisfaction

Of 96,478 delivered orders, 96,470 had both delivery timestamps, 95,832 had an order-level review, and 95,824 had both. Eight delivered orders lacked actual delivery time; 646 lacked an order-level non-null review.

States with at least 500 eligible orders and elevated late shares included MA at 19.67% (95% Wilson CI 16.92%–22.73%), CE at 15.32% (13.45%–17.40%), BA at 14.04% (12.88%–15.27%), and RJ at 13.47% (12.88%–14.09%). SP, the largest sample, was 5.89% (5.67%–6.13%). AL was higher descriptively at 23.93%, but its 397 orders fall below the report's 500-order comparison guardrail.

Among attributed categories with at least 500 eligible orders, `electronics` had a 9.87% late share (95% CI 8.76%–11.10%), `baby` 9.29% (8.26%–10.43%), `office_furniture` 9.19% (7.71%–10.92%), and `health_beauty` 8.99% (8.40%–9.61%). These differences may reflect geography, seller mix, item characteristics, or other confounding.

## 6. Statistical evidence and uncertainty

The analysis unit is an order. Multiple reviews are averaged before joining, and low-review denominators include reviewed orders only.

| Contrast | Estimate | 95% confidence interval | Test |
|---|---:|---:|---:|
| Late minus on-time/early mean review score | -1.7278 | -1.7657 to -1.6899 | large-sample Welch-style z = -89.38, p < 1e-300 |
| Late minus on-time/early low-review share | +44.80 pp | +43.67 to +45.93 pp | two-proportion z = 112.70, p < 1e-300 |
| Late low-review share | 53.99% | 52.87% to 55.10% | Wilson interval, n = 7,661 |
| On-time/early low-review share | 9.19% | 9.00% to 9.38% | Wilson interval, n = 88,163 |

The stratified analysis used 1,003 informative purchase-month × state × value-band strata. The Mantel–Haenszel common odds ratio for a low review comparing late with on-time/early orders was 10.54; CMH χ²(1) = 8,394.63, p < 1e-300. This shows the observed association is not explained away by those three stratification variables. Residual and unmeasured confounding remains, independence may be imperfect across customers/sellers, and significance is partly driven by the large sample.

## 7. Business recommendations

1. **Prioritize diagnostic review of MA, CE, BA, and RJ fulfillment lanes.** Their state-level late rates and confidence intervals are materially above SP's 5.89% benchmark. Start with seller/carrier and route decomposition; the current analysis supports prioritization, not a promised improvement.
2. **Build a service-recovery trigger for observed late orders and evaluate it prospectively.** Late orders have a 44.80-point higher low-review share and the association persists in observed strata. Any effect of outreach must be tested; this study does not estimate uplift.
3. **Treat high-value one-time customers as a separate research population.** They contribute 27.44% of merchandise value from 8.66% of customers. Investigate category, delivery, and subsequent-channel eligibility before designing retention experiments; do not equate one observed order with churn.
4. **Use cohort maturity gates in retention reporting.** Exact-month retention is below 0.5% after acquisition, but later cohorts are censored. Operational reporting should display only observable cells and keep overall repeat rate separate.
5. **Plan inventory/category reviews around a diversified top set, not one flagship category.** Eighteen categories are required to pass 80% of value, while month-to-month mix shifts can exceed five points. Monitor the top 18 and investigate the documented `computers`, `bed_bath_table`, and `toys` shifts before making stocking claims.
6. **Audit electronics, baby, office furniture, and health/beauty fulfillment at seller/route level.** These high-volume categories have late shares near 9%–10%; order-level dominant-category attribution and category-specific physical/logistical differences should be checked before action.

## 8. Limitations and potential confounders

- Data ends during August 2018. August is incomplete, future returns are unknown, and first observed purchase may not be true acquisition.
- Customer activity outside Olist is unavailable. “Inactive” is not observed churn.
- The source lacks sessions, marketing exposure/spend, costs, returns, carrier service levels, and randomized treatments. It cannot support conversion, CAC, ROAS, profit, or causal uplift.
- Review nonresponse affects 646 delivered orders; review aggregation gives each order equal weight but does not remove selection bias.
- State, month, and value stratification does not control seller, distance, product dimensions, carrier, promised lead time, or customer expectations.
- Dominant-value category attribution prevents order duplication but simplifies 780 mixed-category eligible orders.
- The 100-order month rule and 500-order region/category guardrail are transparent descriptive thresholds, not guarantees of representativeness.

## 9. Reproducibility

From the repository root with Python 3.11+:

```bash
python3 scripts/build_database.py
python3 scripts/run_analysis.py
python3 scripts/phase2_analysis.py
python3 -m unittest discover -s tests -v
```

The Phase 2 command writes 12 CSV extracts plus [`statistical_results.json`](phase2_outputs/statistical_results.json) and these charts:

- [`cohort_retention_heatmap.svg`](../visualizations/cohort_retention_heatmap.svg)
- [`rfm_segment_distribution.svg`](../visualizations/rfm_segment_distribution.svg)
- [`monthly_merchandise_trends.svg`](../visualizations/monthly_merchandise_trends.svg)
- [`category_pareto.svg`](../visualizations/category_pareto.svg)
- [`delivery_satisfaction.svg`](../visualizations/delivery_satisfaction.svg)

Independent checks, separate from the Phase 2 query CTEs, reproduced 96,478 delivered orders, BRL 13,221,498.11, 93,358 unique delivered customers, 2,801 repeat customers, 96,470 timing-eligible orders, and 7,826 late orders.

Final validation on 2026-11-10: `python3 -m unittest discover -s tests -v` ran **16 tests with 16 passed, 0 failures**. This includes the original 11 Phase 1 tests plus five Phase 2 test methods covering unique-customer cohorts, retention censoring/denominators, cutoff and score ties, monetary reconciliation, boundary months, payment/review fan-out safety, category attribution, order-grain samples, and deterministic inference. Every checked-in SQL statement executed against the real database, and all five SVG files passed XML parsing.

## 10. Suggested Phase 3 direction

Build a read-only portfolio dashboard that consumes the checked-in SQL extracts rather than reimplementing metrics. It should expose cohort censoring, RFM definitions, boundary-month warnings, confidence intervals, sample thresholds, and category-attribution notes in the UI. A second track could add seller/route diagnostics and a documented experiment design for service recovery or retention outreach. Phase 3 should not claim outcomes until new data or a controlled evaluation exists.
