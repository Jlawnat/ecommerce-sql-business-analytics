# Research limitations

These boundaries apply across reports, dashboards, and portfolio claims.

## Historical scope

The Olist source represents anonymized Brazilian marketplace records from 2016–2018, with the analytical observation endpoint in August 2018. Results are historical evidence, not current Olist performance, current Brazilian ecommerce benchmarks, or transactions from the project author's store.

## Commercial interpretation

- **Merchandise value:** `SUM(order_items.price)` for delivered orders; freight is excluded.
- **Not available:** cost of goods, operating expenses, product margin, profit, site sessions, ad exposure/spend, CAC, ROAS, returns, or randomized treatment assignment.
- **Consequence:** no profit, conversion, marketing-efficiency, or experiment-lift claim is supported.

## Customer interpretation

- `customer_unique_id` is the best available marketplace identity, but the dataset does not prove lifetime acquisition or complete customer activity.
- A repeat event is a second observed delivered order within coverage.
- Customers without a repeat event may be administratively right-censored. They are not labeled churned.
- In cohort tables, censored cells are null; observable months with no return are zero.
- RFM labels depend on the declared snapshot cutoff. “Inactive” means inactive in the observed historical window only.

## Delivery association

- Late delivery and review outcomes are observational.
- The adjusted model represents purchase period, customer state, category group, merchandise-value band, and seller count. Carrier, route distance, promise construction, service recovery, and latent expectations remain unavailable.
- Odds ratios describe conditional odds, not risk ratios or percentage-point change.
- The standardized risk difference is model-based and remains associational.
- Missing-review bounds are deterministic extremes, not proof that review missingness is ignorable.
- Subgroup heterogeneity is exploratory and not multiplicity-adjusted.

## Validation scope

- Model discrimination and Brier score are evaluated on the fitted historical population.
- There is no held-out temporal, geographic, or external marketplace validation.
- Synthetic known-answer tests verify implementation behavior; real-data audit tests verify published anchors when the locally licensed source database is available.
- Clean GitHub CI intentionally does not claim that those local real-data audits ran. See [CI boundaries](../engineering/CI.md).
