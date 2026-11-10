# Phase 2.5 Statistical and Data-Engineering Methods

## 1. Analytical layer and grain

The mart follows the dimensional-design rule that grain is declared before facts and that different grains are kept in different physical tables. This follows the [Kimball Group four-step process](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/) and its guidance on [declaring grain](https://www.kimballgroup.com/2003/03/declaring-the-grain/).

| Table | Binding grain | Primary key | Main additive facts |
|---|---|---|---|
| `mart_delivered_orders` | one source delivered order with at least one item | `order_id` | merchandise value, freight, item/seller/category counts |
| `mart_delivered_order_items` | one item line in a delivered order | `(order_id, order_item_id)` | item price, freight |
| `mart_customer_snapshot` | one unique customer with a delivered purchase before 2018-09-01 | `customer_unique_id` | order frequency, merchandise, recency, first/second purchase time |
| `mart_reviewed_orders` | one delivered order with at least one non-null review | `order_id` | averaged score and review count |

The mart is materialized in a separate SQLite database; source tables are never updated. Monetary facts are summed only at their native order-item grain and then reconciled at order and customer grain. Assertions address accuracy, completeness, consistency, and fitness for use rather than accuracy alone, consistent with Wang and Strong's data-quality framework ([DOI 10.1080/07421222.1996.11518099](https://doi.org/10.1080/07421222.1996.11518099)).

## 2. Repeat-purchase time-to-event analysis

### Population and estimand

The origin is a customer's first observed delivered purchase before a specified cutoff. The event is the second observed delivered purchase before that cutoff. Customers without an event are administratively right-censored at the cutoff. Time is fractional days between purchase timestamps; post-cutoff purchases are unavailable to that snapshot.

The Kaplan–Meier product-limit estimator follows Kaplan and Meier's treatment of incomplete observations ([1958 paper, DOI 10.1080/01621459.1958.10501452](https://doi.org/10.1080/01621459.1958.10501452)). Pointwise 95% intervals use Greenwood variance and a complementary log-log transform, which keeps survival limits inside 0–1; the formulas are also summarized in the [NCBI time-to-event methods appendix](https://www.ncbi.nlm.nih.gov/books/NBK610554/).

Reported values are cumulative incidence of a second purchase, `1 - S(t)`, at 30, 60, 90, 180, and 365 days. The median time to repeat is not estimable because the curve never approaches 50% incidence. Cutoff sensitivity repeats the entire construction at 2018-03-01, 2018-06-01, and 2018-09-01.

### Assumptions

- Censoring at the dataset cutoff is treated as non-informative conditional on observed history.
- First observed purchase is used as a practical origin but is not proven acquisition.
- Delivery completion is required, so cancellation and still-open ordering behavior is outside the estimand.
- Off-platform or post-dataset purchases are unobserved; non-return is never labeled confirmed churn.

RFM stability compares deterministic segment labels for customers present at both June and September cutoffs. Exact agreement and Cohen's κ are descriptive snapshot-stability measures, not validity scores.

## 3. Delivery-satisfaction association

### Population, exposure, and outcomes

The primary complete-outcome population contains delivered orders with both actual and estimated timestamps and at least one non-null review: 95,824 orders. Exposure is the full-timestamp late indicator. Multiple reviews are averaged before outcome classification.

- Primary outcome: averaged order review score ≤2.
- Alternative outcome: averaged order review score exactly 1.
- Main controls: purchase-period fixed effects, customer-state fixed effects, top-15 merchandise category plus other, order merchandise-value band, and single- versus multi-seller status.
- Sparse controls: pre-2017 months are combined; states with fewer than 200 timing-eligible orders form a low-volume group. Full month/state/category tables remain available for subgroup assessment.

### Adjusted logistic model

Rows with identical covariates are represented as grouped binomial counts. Newton–Raphson/IRLS maximizes the same Bernoulli likelihood as expanding those rows to individual orders. The late coefficient is exponentiated to a conditional adjusted odds ratio; its model-based 95% interval uses the inverse observed information matrix.

Because odds ratios are non-collapsible and hard to interpret as absolute risk, the model also predicts every empirical covariate profile under late=1 and late=0, averages those predictions over the observed covariate distribution, and reports the standardized risk difference. Its interval uses the delta method and the coefficient covariance matrix. This remains a model-standardized association, not a causal effect.

Diagnostics include convergence, iteration and parameter counts, outcome prevalence, AUC discrimination, and Brier score. Sensitivity analyses restrict to single-seller orders and replace the outcome with score=1.

### Heterogeneity and missing reviews

Month, state, and full attributed-category 2×2 tables are retained when both timing groups contain at least 20 reviewed orders. Inverse-variance Cochran Q and I² summarize whether log odds ratios vary more than sampling error alone. These exploratory tests are not multiplicity-adjusted subgroup claims.

Primary complete-review estimates are accompanied by deterministic extreme bounds. The minimum association assigns every missing late review as non-low and every missing on-time review as low; the maximum does the reverse. This is deliberately more transparent than assuming reviews are missing at random.

The report structure follows the [STROBE observational reporting checklist](https://www.strobe-statement.org/), including eligibility, variable definitions, confounding controls, missingness, subgroup methods, and sensitivity analyses. Adjustment reduces measured imbalance but cannot establish causality.

## 4. Future randomized validation

Random assignment is reserved for future prospective validation. The experiment design uses intention-to-treat analysis, predeclared success and guardrail metrics, sample-size planning before launch, stable assignment, and an A/A instrumentation check. These practices align with Kohavi, Henne, and Sommerfield's [practical guide to controlled web experiments](https://ai.stanford.edu/~ronnyk/GuideControlledExperiments.pdf). No hypothetical treatment effect is reported as observed.

## 5. Reproducibility and numerical precision

The project uses Python's standard library and SQLite only. SQL defines every population and aggregate. Python implements documented estimators, writes JSON/CSV evidence, and produces SVG charts. Tests cover synthetic known-answer cases, real-data anchors, model convergence, censoring, cutoff leakage, mart constraints, confidence intervals, and output parsing. Extreme p-values that underflow double precision are displayed as `<1e-300`, never as evidence of an exact zero probability.
