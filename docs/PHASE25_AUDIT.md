# Phase 2.5 Independent Analytics Audit

**Audit date:** 2026-11-10  
**Audited baseline:** Phase 1 and Phase 2 at repository HEAD `d51d5f7`  
**Scope:** SQL populations, grains, censoring, cutoff leakage, monetary reconciliation, statistical formulas, published outputs, repository hygiene.

## Status definitions

- **PASS:** independently reproduced and covered by an executable assertion.
- **WARNING:** method is internally valid but interpretation depends on an untestable assumption or incomplete source coverage.
- **FAIL:** confirmed defect that can change a reported result or prevent reproducibility.
- **RESOLVED:** a FAIL found during this audit and fixed before final Phase 2.5 estimation.

## Audit matrix

| Area | Status | Independent evidence |
|---|---|---|
| Delivered-order population | PASS | Direct source-table recount reproduced 96,478 distinct delivered orders. |
| Merchandise definition | PASS | Item-grain `SUM(price)` reproduced BRL 13,221,498.11; order and item mart sums reconcile to six decimals. Freight and payments remain excluded. |
| Customer identity | PASS | `customer_unique_id` produced 93,358 delivered customers and 2,801 customers with at least two distinct delivered orders. |
| Cohort allocation | PASS | Every customer appears in one first-observed purchase-month cohort; cohort totals reproduce customer and merchandise anchors. |
| Cohort censoring | PASS | Immature exact-month cells are `NULL`; observable no-return cells are zero. Month 4+ is correctly documented as ever-returned after offset 4, not exact-month retention. |
| Cohort interpretation | WARNING | First observed purchase is not proven lifetime acquisition; early cohorts and follow-up near August 2018 are incomplete. |
| RFM cutoff | PASS | SQL excludes timestamps at or after `2018-09-01 00:00:00`; an injected post-cutoff order is excluded by tests. Real source contains no delivered purchase after the cutoff. |
| RFM scoring | PASS | Explicit thresholds preserve equal-value ties and avoid frequency quintiles in a 97% one-order population. |
| RFM temporal stability | WARNING | June-to-September exact segment agreement is 57.76% (κ = 0.426); labels are snapshot-dependent and should not be treated as stable traits. |
| Join cardinality | PASS | Reviews and items are independently pre-aggregated before order-level joins. Mart order, item, customer, and reviewed-order keys are unique; all FKs pass. |
| Category attribution | PASS/WARNING | Dominant item-price category with alphabetical tie-breaking preserves one order per denominator. It is reproducible but simplifies 780 mixed-category timing-eligible orders. |
| Phase 2 confidence intervals | PASS | Wilson, unpooled risk-difference, and large-sample unequal-variance mean-difference calculations reproduce published endpoints. |
| Mantel–Haenszel calculation | PASS | Order-level stratum counts reproduce common OR 10.54 and CMH χ² 8,394.63. |
| Review eligibility | PASS/WARNING | 95,824 orders have timing and review outcomes; 646 delivered orders lack an order-level review, creating possible selection bias. |
| Published Phase 2 figures | PASS | CSV/JSON figures reproduce to their published precision from independent source queries. |
| Phase 2 p-value serialization | RESOLVED | IEEE underflow had serialized extreme p-values as `0.0`. Outputs now retain the numeric value and add an explicit reporting field `<1e-300`. |
| Initial adjusted model convergence | RESOLVED | A first 69-parameter model failed its convergence threshold because one-order months/very small states caused near separation. Prespecified grouping of pre-2017 months and states with fewer than 200 eligible orders yields convergence in 7–8 iterations while full subgroups remain separately reported. |
| Adjusted delivery model | PASS/WARNING | Primary, single-seller, and score-1 models converge and preserve the Phase 2 population. Estimates remain associational because important carrier, distance, seller, and expectation variables are unavailable. |
| Raw data / credentials | PASS | Raw CSVs and SQLite databases remain ignored; tracked-file scan found no credential files or raw data. |

## Analytics mart assertions

The separate `olist_analytics.sqlite` build executes 12 blocking assertions:

1. unique delivered-order key;
2. delivered-order source population;
3. delivered-item composite key and source population;
4. item-to-order foreign keys;
5. order merchandise reconciliation;
6. item merchandise reconciliation;
7. unique customer snapshot key;
8. cutoff-eligible customer population;
9. customer monetary reconciliation;
10. reviewed-order population;
11. required order-field null checks;
12. SQLite foreign-key check.

All 12 passed on the real database. The source database is attached read-only in practice, all mart objects are written to a separate temporary database, and the target is atomically replaced only after validation.

## Unresolved limitations

- Administrative censoring is defensible for the known dataset endpoint, but independent censoring cannot be empirically proven. Acquisition date and off-platform purchases are unobserved.
- Repeat-purchase KM estimates describe second *observed delivered* purchases. They do not estimate customer loyalty outside this marketplace.
- Complete-review logistic analysis may be biased if review missingness depends jointly on delivery timing and latent satisfaction. Extreme-case bounds are reported, but no missing-at-random claim is made.
- The adjusted odds ratio is conditional and non-collapsible. The standardized risk difference is supplied for an absolute-scale interpretation, but neither estimand is causal.
- Subgroup heterogeneity is substantial and exploratory; multiple subgroup comparisons are not treated as confirmatory discoveries.
- The public data lacks carrier, route distance, promised lead-time construction, returns, contacts, marketing exposure, and experiment assignment.

## Reproduction commands

```bash
python3 scripts/phase2_analysis.py
python3 scripts/build_analytics_mart.py
python3 scripts/phase25_research.py
python3 -m unittest discover -s tests -v
```

The real-data audit lives in `tests/test_phase25_audit.py`; it skips only when the licensed/manual source database is unavailable.
