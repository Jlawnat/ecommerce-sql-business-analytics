export type EvidenceLink = {
  label: string;
  path: string;
  kind: "documentation" | "report" | "sql" | "code" | "test" | "aggregate";
};

export type PipelineStage = {
  id: string;
  title: string;
  summary: string;
  grain: string;
  checks: string[];
  outputs: string[];
  sources: EvidenceLink[];
};

export type MetricFamily = "Commercial" | "Customer" | "Delivery" | "Research";

export type MetricDefinition = {
  id: string;
  name: string;
  family: MetricFamily;
  definition: string;
  unit: string;
  population: string;
  denominator: string;
  window: string;
  exclusions: string;
  missingness: string;
  sources: EvidenceLink[];
};

export type StatisticalMethod = {
  id: string;
  title: string;
  businessReading: string;
  estimand: string;
  implementation: string[];
  limitations: string[];
  diagnostics: string[];
  sources: EvidenceLink[];
};

const link = (label: string, path: string, kind: EvidenceLink["kind"]): EvidenceLink => ({ label, path, kind });

export const pipelineStages: PipelineStage[] = [
  {
    id: "source",
    title: "Olist source data",
    summary: "Nine anonymized marketplace CSVs from the Brazilian E-Commerce Public Dataset by Olist; licensed data is acquired manually and never redistributed here.",
    grain: "Separate source grains: orders, item lines, payments, review records, customers, products, sellers, geolocation and category translation.",
    checks: ["Exact nine-file manifest", "Required-column validation", "Raw files excluded from Git"],
    outputs: ["Locally acquired source files", "Attribution and acquisition record"],
    sources: [link("Source attribution and license", "docs/DATA_SOURCE.md", "documentation")],
  },
  {
    id: "ingestion",
    title: "SQLite ingestion and quality",
    summary: "Typed parsing, relational constraints and atomic replacement turn the manually acquired files into a reproducible local source database.",
    grain: "Tables preserve their native source grain; parent and child relationships are enforced rather than flattened.",
    checks: ["Primary, composite and foreign keys", "Timestamp and numeric diagnostics", "Post-load foreign-key check", "Failure atomicity and idempotent rebuilds"],
    outputs: ["Normalized source tables", "Ordered quality-check result sets"],
    sources: [
      link("Database build", "scripts/build_database.py", "code"),
      link("Source schema", "sql/schema/001_create_tables.sql", "sql"),
      link("Quality checks", "sql/analysis/00_data_quality.sql", "sql"),
    ],
  },
  {
    id: "marts",
    title: "Analytics marts with declared grain",
    summary: "Orders, item lines, customer snapshots and reviewed orders live in separate physical tables so monetary and review facts cannot fan out across incompatible grains.",
    grain: "One delivered order; one delivered item line; one customer at the fixed cutoff; one reviewed delivered order.",
    checks: ["12 blocking integrity assertions", "Order/item/customer monetary reconciliation", "Unique mart keys", "Read-only source attachment in practice"],
    outputs: ["Delivered-order mart", "Delivered-item mart", "Customer snapshot", "Reviewed-order mart"],
    sources: [
      link("Mart build SQL", "sql/marts/001_build_analytics_mart.sql", "sql"),
      link("Mart assertions", "sql/marts/002_validate_analytics_mart.sql", "sql"),
      link("Independent audit", "docs/PHASE25_AUDIT.md", "documentation"),
    ],
  },
  {
    id: "analysis",
    title: "SQL analysis outputs",
    summary: "SQL defines the eligible population, unit of analysis and aggregation before any visualization or statistical estimator consumes the result.",
    grain: "Output grain is explicit per query: purchase month, category, cohort × month offset, RFM segment, state/category comparison or delivery timing group.",
    checks: ["Delivered-order population reused", "One-row-per-order review aggregation", "Censoring remains null", "Category attribution is deterministic"],
    outputs: ["Phase 2 aggregate CSVs", "Phase 2 statistical result JSON"],
    sources: [
      link("KPI summary SQL", "sql/analysis/04_kpi_summary.sql", "sql"),
      link("Cohort SQL", "sql/analysis/05_customer_cohort_retention.sql", "sql"),
      link("Delivery research SQL", "sql/analysis/10_delivery_satisfaction_research.sql", "sql"),
    ],
  },
  {
    id: "statistics",
    title: "Statistical research",
    summary: "Documented estimators add time-to-event uncertainty, adjusted associations, absolute risks, model diagnostics, heterogeneity and missing-review bounds.",
    grain: "Customer time-to-event records for repeat purchase; grouped order-level binomial profiles for delivery satisfaction.",
    checks: ["Known-answer synthetic tests", "Censoring and cutoff-leakage tests", "Convergence checks", "Real-data anchor reconciliation"],
    outputs: ["Kaplan–Meier horizons and intervals", "Adjusted model summaries", "Sensitivity and subgroup evidence"],
    sources: [
      link("Statistical methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"),
      link("Research implementation", "scripts/phase25_research.py", "code"),
      link("Research results", "reports/PHASE25_RESEARCH_RESULTS.md", "report"),
    ],
  },
  {
    id: "publishing",
    title: "Published aggregate contracts",
    summary: "A deterministic publisher converts checked-in aggregate evidence into versioned frontend contracts; the dashboard never loads raw or customer-level records.",
    grain: "Only presentation-safe aggregates: month, category, cohort cell, RFM segment, selected KM horizon, comparison group and model summary.",
    checks: ["Strict frontend parsing", "Verified anchor assertions", "Byte-identical repeat publishing", "Restricted export allowlist"],
    outputs: ["Executive contract", "Customer contract", "Delivery contract"],
    sources: [
      link("Aggregate publisher", "scripts/publish_web_aggregates.py", "code"),
      link("Dashboard contracts", "docs/PHASE3_DATA_CONTRACTS.md", "documentation"),
      link("Contract tests", "tests/test_web_data_contract.py", "test"),
    ],
  },
  {
    id: "decisions",
    title: "Dashboard and decisions",
    summary: "Four research views surface verified findings, uncertainty, limitations and evidence-linked actions without recalculating the research models in the browser.",
    grain: "Decision presentation over validated aggregate contracts; no row-level drill-through.",
    checks: ["Responsive accessibility QA", "Association-versus-causation language", "Aggregate-only downloads", "Source links beside claims"],
    outputs: ["Executive overview", "Customer intelligence", "Delivery and satisfaction", "Methodology and evidence"],
    sources: [
      link("Design system", "docs/design-v2/DESIGN_SYSTEM.md", "documentation"),
      link("Frontend contract parser", "web/lib/contracts.ts", "code"),
    ],
  },
];

export const metricFamilies: Array<"All" | MetricFamily> = ["All", "Commercial", "Customer", "Delivery", "Research"];

export const metricDefinitions: MetricDefinition[] = [
  {
    id: "delivered-orders",
    name: "Delivered orders",
    family: "Commercial",
    definition: "Distinct orders whose source status is delivered. Queries pre-aggregated to order grain may safely count rows.",
    unit: "Orders",
    population: "Source orders with order_status = delivered",
    denominator: "Not applicable; this is a count",
    window: "Purchase timestamp within the observed 2016–2018 marketplace window",
    exclusions: "Canceled, unavailable, created, approved, invoiced, processing and shipped orders",
    missingness: "All delivered-order KPIs require a source order row; downstream merchandise metrics additionally require item rows.",
    sources: [link("KPI definitions", "docs/METRIC_DEFINITIONS.md", "documentation"), link("KPI SQL", "sql/analysis/04_kpi_summary.sql", "sql")],
  },
  {
    id: "merchandise-value",
    name: "Delivered merchandise value",
    family: "Commercial",
    definition: "Sum of order-item price for delivered orders. It is merchandise value, not accounting revenue, payment receipts, profit or margin.",
    unit: "BRL",
    population: "Items attached to delivered orders",
    denominator: "Not applicable; additive item-price total",
    window: "Assigned to the calendar month of order purchase",
    exclusions: "Freight, payment totals, canceled/non-delivered orders",
    missingness: "Delivered orders without item rows cannot contribute merchandise value and are checked separately.",
    sources: [link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation"), link("Monthly SQL", "sql/analysis/01_monthly_merchandise_value.sql", "sql")],
  },
  {
    id: "average-order-value",
    name: "Average merchandise value per delivered order",
    family: "Commercial",
    definition: "Delivered merchandise value divided by represented delivered orders after item-level facts are aggregated to one row per order.",
    unit: "BRL per order",
    population: "Delivered orders represented in order items",
    denominator: "Distinct represented delivered orders",
    window: "Full observed window or selected purchase-month range",
    exclusions: "Freight and orders outside delivered status",
    missingness: "A zero denominator returns no rate; source coverage is disclosed rather than imputed.",
    sources: [link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation"), link("Monthly SQL", "sql/analysis/01_monthly_merchandise_value.sql", "sql")],
  },
  {
    id: "category-share",
    name: "Category merchandise share",
    family: "Commercial",
    definition: "Category merchandise value divided by delivered merchandise value represented across categorized and uncategorized items; cumulative share follows descending category rank.",
    unit: "Percent of merchandise value",
    population: "Delivered order items",
    denominator: "All represented delivered item price, including uncategorized items",
    window: "Full observed purchase window",
    exclusions: "Freight and non-delivered orders",
    missingness: "Missing category is retained as [uncategorized]; untranslated names retain the Portuguese source label.",
    sources: [link("Pareto SQL", "sql/analysis/02_category_sales_concentration.sql", "sql"), link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation")],
  },
  {
    id: "cohort-retention",
    name: "Exact-month cohort retention",
    family: "Customer",
    definition: "Share of an observed first-purchase cohort with at least one delivered purchase in the exact Nth calendar month after the cohort month.",
    unit: "Percent of acquisition cohort",
    population: "Unique customers keyed by customer_unique_id with a delivered order",
    denominator: "Customers in the observed first-purchase cohort",
    window: "Cohort month through the August 2018 observation endpoint",
    exclusions: "Non-delivered orders and activity outside dataset coverage",
    missingness: "Immature cells are null, while an observable month with no returning customers is zero. First observed purchase is not proven lifetime acquisition.",
    sources: [link("Cohort SQL", "sql/analysis/05_customer_cohort_retention.sql", "sql"), link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation")],
  },
  {
    id: "rfm",
    name: "RFM segment",
    family: "Customer",
    definition: "Deterministic segment from recency, distinct delivered-order frequency and item-price monetary thresholds at a fixed historical cutoff.",
    unit: "Customer count or merchandise value by segment",
    population: "Unique customers with a delivered purchase before 2018-09-01",
    denominator: "All cutoff-eligible observed customers for shares",
    window: "Snapshot cutoff 2018-09-01 00:00:00",
    exclusions: "Purchases at or after cutoff and non-delivered orders",
    missingness: "Inactive means inactive in the observed window; it is never treated as confirmed churn.",
    sources: [link("RFM SQL", "sql/analysis/06_rfm_segmentation.sql", "sql"), link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation")],
  },
  {
    id: "repeat-incidence",
    name: "Repeat-purchase cumulative incidence",
    family: "Research",
    definition: "One minus Kaplan–Meier survival for time from first to second observed delivered purchase, reported only at selected horizons.",
    unit: "Percent of customers by horizon",
    population: "Customers with a first observed delivered purchase before the cutoff",
    denominator: "Horizon-specific risk set under administrative censoring",
    window: "30, 60, 90, 180 and 365 days; cutoff sensitivity at three snapshots",
    exclusions: "Post-cutoff, non-delivered and off-platform purchases",
    missingness: "Customers without an observed second purchase are right-censored, not classified as churned.",
    sources: [link("Repeat-purchase SQL", "sql/analysis/09_repeat_purchase_research.sql", "sql"), link("Statistical methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation")],
  },
  {
    id: "late-rate",
    name: "Late-delivery rate",
    family: "Delivery",
    definition: "Share of timing-eligible delivered orders where actual customer delivery is later than the estimated delivery timestamp.",
    unit: "Percent of timing-eligible orders",
    population: "Delivered orders with actual and estimated customer-delivery timestamps",
    denominator: "Timing-eligible delivered orders",
    window: "Full observed purchase window",
    exclusions: "Orders missing either timestamp and all non-delivered orders",
    missingness: "Missing timestamp counts are disclosed separately; full timestamps, not calendar dates, define lateness.",
    sources: [link("Delivery SQL", "sql/analysis/08_delivery_segment_analysis.sql", "sql"), link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation")],
  },
  {
    id: "low-review-risk",
    name: "Low-review rate",
    family: "Delivery",
    definition: "Share of reviewed orders whose averaged order-level review score is at most 2.",
    unit: "Percent of reviewed orders",
    population: "Timing-eligible delivered orders with at least one non-null review",
    denominator: "Reviewed orders within the timing group",
    window: "Full observed purchase window",
    exclusions: "Missing order-level review outcomes and non-timing-eligible orders",
    missingness: "Multiple review rows are averaged before classification; missing-review sensitivity uses deterministic extreme bounds.",
    sources: [link("Delivery research SQL", "sql/analysis/10_delivery_satisfaction_research.sql", "sql"), link("Metric definition", "docs/METRIC_DEFINITIONS.md", "documentation")],
  },
  {
    id: "adjusted-or",
    name: "Adjusted odds ratio",
    family: "Research",
    definition: "Exponentiated late-delivery coefficient from the grouped-binomial logistic model, conditional on its measured adjustment set.",
    unit: "Odds ratio",
    population: "Complete timing-and-review outcome population",
    denominator: "Odds among on-time/early orders form the reference",
    window: "Full model population across the observed historical period",
    exclusions: "Orders without complete exposure or outcome; unmeasured factors cannot be adjusted",
    missingness: "Complete-review estimate is paired with missing-review bounds. The OR is non-collapsible and is not a risk ratio or causal effect.",
    sources: [link("Statistical methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"), link("Research implementation", "scripts/phase25_research.py", "code")],
  },
  {
    id: "standardized-rd",
    name: "Standardized risk difference",
    family: "Research",
    definition: "Average model-predicted low-review risk under late=1 minus the corresponding prediction under late=0 over the empirical covariate distribution.",
    unit: "Percentage points",
    population: "Empirical covariate profiles in the complete timing-and-review model population",
    denominator: "Model-standardized risks over the same empirical profiles",
    window: "Full model population across the observed historical period",
    exclusions: "Unobserved confounders and records outside complete outcome eligibility",
    missingness: "Delta-method confidence interval reflects model uncertainty, not identification uncertainty or causal transportability.",
    sources: [link("Statistical methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"), link("Research results", "reports/PHASE25_RESEARCH_RESULTS.md", "report")],
  },
];

export const statisticalMethods: StatisticalMethod[] = [
  {
    id: "cohort",
    title: "Cohort retention and censoring",
    businessReading: "Shows when customers return in an exact calendar month after their first purchase observed in this dataset.",
    estimand: "Exact-month return share within each observed first-purchase cohort.",
    implementation: ["Customer identity uses customer_unique_id.", "Month 0 is 100% by construction.", "A cell becomes null when August 2018 cannot supply the required follow-up."],
    limitations: ["Observed first purchase is not proven acquisition.", "Sparse early cohorts can produce extreme percentages.", "Post-August 2018 and off-platform behavior are unknown."],
    diagnostics: ["Cohort totals reconcile to observed customer counts.", "Null censoring and observed zero are tested separately."],
    sources: [link("Cohort SQL", "sql/analysis/05_customer_cohort_retention.sql", "sql"), link("Audit", "docs/PHASE25_AUDIT.md", "documentation")],
  },
  {
    id: "rfm",
    title: "RFM segmentation and cutoff sensitivity",
    businessReading: "Provides a reproducible historical snapshot for prioritization, not a permanent customer trait or confirmed churn label.",
    estimand: "Deterministic recency, frequency and merchandise-value segment at a declared cutoff.",
    implementation: ["Cutoff is 2018-09-01.", "Threshold scores preserve ties rather than forcing quintiles.", "June-to-September exact agreement and Cohen’s κ describe snapshot stability."],
    limitations: ["Segment membership moves with the cutoff.", "Inactive means no recent observed activity only.", "Scores are business rules, not learned probabilities."],
    diagnostics: ["Post-cutoff leakage test.", "Customer counts and merchandise totals reconcile across segments."],
    sources: [link("RFM SQL", "sql/analysis/06_rfm_segmentation.sql", "sql"), link("Audit", "docs/PHASE25_AUDIT.md", "documentation")],
  },
  {
    id: "km",
    title: "Kaplan–Meier and confidence intervals",
    businessReading: "Estimates the cumulative incidence of a second observed delivered purchase while retaining customers whose follow-up ends before they return.",
    estimand: "1 − S(t) at 30, 60, 90, 180 and 365 days.",
    implementation: ["Administrative right-censoring at the snapshot cutoff.", "Greenwood variance with complementary log-log pointwise 95% intervals.", "Dashboard displays selected horizons as points; it does not invent an intermediate step curve."],
    limitations: ["Independent censoring cannot be empirically proven.", "Median repeat time is not estimable because incidence stays below 50%.", "Marketplace coverage is incomplete."],
    diagnostics: ["Risk-set counts at each horizon.", "Three cutoff-sensitivity reconstructions.", "Known-answer survival tests."],
    sources: [link("Methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"), link("Research tests", "tests/test_phase25_statistics.py", "test")],
  },
  {
    id: "logistic",
    title: "Adjusted logistic regression",
    businessReading: "Compares low-review odds for late versus on-time/early orders after measured differences in period, state, category, value band and seller count are represented.",
    estimand: "Conditional adjusted odds ratio for the late indicator in the complete-review population.",
    implementation: ["Identical covariate profiles are grouped as binomial counts.", "Newton–Raphson/IRLS maximizes the Bernoulli likelihood.", "Sparse pre-2017 months and low-volume states use prespecified groups."],
    limitations: ["Residual confounding remains.", "Complete-review selection may be informative.", "Adjustment does not convert association into causation."],
    diagnostics: ["Convergence, iterations and parameter count.", "AUC and Brier score.", "Single-seller and score=1 sensitivity models."],
    sources: [link("Methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"), link("Research implementation", "scripts/phase25_research.py", "code")],
  },
  {
    id: "effect-scale",
    title: "Odds ratio versus risk difference",
    businessReading: "The odds ratio describes a conditional relative association; the standardized risk difference translates the same fitted model to an absolute percentage-point contrast.",
    estimand: "Conditional odds ratio and average standardized risk difference over observed covariate profiles.",
    implementation: ["Odds-ratio interval uses inverse observed information.", "Standardized risks predict every profile under late=1 and late=0.", "Risk-difference interval uses the delta method and fitted covariance matrix."],
    limitations: ["Odds are not probabilities.", "Odds ratios are non-collapsible.", "Both measures remain model-dependent observational associations."],
    diagnostics: ["Both scales and both 95% intervals are published together.", "Observed raw risks remain visible as a separate descriptive contrast."],
    sources: [link("Methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"), link("Executive research brief", "reports/PHASE25_EXECUTIVE_BRIEF.md", "report")],
  },
  {
    id: "robustness",
    title: "Diagnostics and robustness",
    businessReading: "Checks whether the main pattern depends on model convergence, outcome definition, seller structure, subgroup composition or missing reviews.",
    estimand: "Model performance summaries, prespecified sensitivity estimates, exploratory heterogeneity and deterministic missing-outcome bounds.",
    implementation: ["AUC measures ranking and Brier score probability error.", "Cochran Q and I² summarize subgroup heterogeneity.", "Missing reviews receive both extreme assignments to bound the raw contrast."],
    limitations: ["Subgroup analyses are exploratory and not multiplicity-adjusted.", "Extreme bounds are transparent, not a missing-at-random model.", "Diagnostics do not prove transportability or causal identification."],
    diagnostics: ["Primary and two sensitivity models converge.", "Month, state and category subgroup thresholds are prespecified.", "Extreme p-values report <1e-300 rather than exact zero."],
    sources: [link("Independent audit", "docs/PHASE25_AUDIT.md", "documentation"), link("Research results", "reports/PHASE25_RESEARCH_RESULTS.md", "report")],
  },
];

export const qualityEvidence = [
  { label: "Source key duplicates", value: "0", note: "Asserted customer, order, item, payment, product and seller keys", tone: "positive" },
  { label: "Foreign-key violations", value: "0", note: "Post-load database check", tone: "positive" },
  { label: "Delivered rows missing actual delivery", value: "8", note: "Retained as a visible quality issue", tone: "warning" },
  { label: "Naive child-join excess", value: "5,657", note: "Rows above source item grain; about 5.02%", tone: "warning" },
] as const;

export const validationLayers = [
  { title: "Load-time enforcement", detail: "Manifest, required columns, typed parsing, constraints, foreign keys and atomic replacement.", source: link("Ingestion tests", "tests/test_ingestion.py", "test") },
  { title: "Join fan-out prevention", detail: "Items, payments and reviews are reduced to the required grain before facts are combined.", source: link("Data quality framework", "docs/DATA_QUALITY.md", "documentation") },
  { title: "Mart integrity", detail: "12 blocking assertions cover uniqueness, populations, foreign keys, required fields and monetary reconciliation.", source: link("Mart tests", "tests/test_analytics_mart.py", "test") },
  { title: "Statistical known answers", detail: "Synthetic and real-data anchors cover intervals, censoring, cutoff leakage, convergence and output parsing.", source: link("Statistical tests", "tests/test_phase25_statistics.py", "test") },
  { title: "Deterministic publishing", detail: "Repeated aggregate publication must be byte-identical and frontend parsers reject missing or unverified anchors.", source: link("Web contract tests", "tests/test_web_data_contract.py", "test") },
] as const;

export const evidenceResources = [
  { group: "Research reports", description: "Findings, audit status and decision-facing interpretation.", links: [link("Phase 1 results", "reports/PHASE1_RESULTS.md", "report"), link("Phase 2 results", "reports/PHASE2_RESULTS.md", "report"), link("Phase 2.5 research", "reports/PHASE25_RESEARCH_RESULTS.md", "report")] },
  { group: "Definitions and methods", description: "Population rules, metric semantics, estimator choices and limitations.", links: [link("Metric definitions", "docs/METRIC_DEFINITIONS.md", "documentation"), link("Statistical methods", "docs/PHASE25_STATISTICAL_METHODS.md", "documentation"), link("Data contracts", "docs/PHASE3_DATA_CONTRACTS.md", "documentation")] },
  { group: "Executable evidence", description: "SQL populations, research implementation and deterministic publication.", links: [link("Analysis SQL directory", "sql/analysis/10_delivery_satisfaction_research.sql", "sql"), link("Phase 2 analysis", "scripts/phase2_analysis.py", "code"), link("Aggregate publisher", "scripts/publish_web_aggregates.py", "code")] },
] as const;

export const reproductionCommands = [
  "python3 scripts/build_database.py",
  "python3 scripts/phase2_analysis.py",
  "python3 scripts/build_analytics_mart.py",
  "python3 scripts/phase25_research.py",
  "python3 scripts/publish_web_aggregates.py",
  ".venv/bin/python -m unittest discover -s tests -v",
] as const;

