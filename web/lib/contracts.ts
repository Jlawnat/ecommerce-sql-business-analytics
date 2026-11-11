export type ObservationStatus =
  | "complete_or_well_represented"
  | "incomplete_first_month"
  | "incomplete_last_month"
  | "sparse_month";

export interface MonthlyAggregate {
  month: string;
  deliveredOrders: number;
  merchandiseValue: number;
  averageOrderValue: number;
  observationStatus: ObservationStatus;
}

export interface CategoryAggregate {
  category: string;
  rank: number;
  deliveredOrders: number;
  merchandiseValue: number;
  sharePct: number;
  cumulativeSharePct: number;
  inFirst80Pct: boolean;
}

export interface ExecutiveOverviewContract {
  schemaVersion: 1;
  dataset: {
    name: string;
    observationWindow: string;
    observationEnd: string;
    status: "verified_historical_snapshot";
  };
  summary: {
    deliveredOrders: number;
    merchandiseValue: number;
    averageOrderValue: number;
    topCategory: string;
    topCategorySharePct: number;
    categoriesToReach80Pct: number;
    thresholdCategory: string;
    thresholdCumulativeSharePct: number;
  };
  monthly: MonthlyAggregate[];
  categories: CategoryAggregate[];
  lineage: {
    monthlySource: string;
    monthlySql: string;
    categorySource: string;
    categorySql: string;
  };
}

export interface RepeatEstimate {
  horizonDays: number;
  customers: number;
  repeatIncidence: number;
  ci95Low: number;
  ci95High: number;
  riskSet: number;
}

export interface CohortCell {
  cohortMonth: string;
  monthNumber: number;
  acquiredCustomers: number;
  observed: boolean;
  retainedCustomers: number | null;
  retentionRatePct: number | null;
}

export interface RfmSegment {
  segment: string;
  customers: number;
  customerSharePct: number;
  merchandiseValue: number;
  merchandiseSharePct: number;
  averagePurchaseFrequency: number;
  repeatCustomerSharePct: number;
}

export interface CustomerIntelligenceContract {
  schemaVersion: 1;
  dataset: ExecutiveOverviewContract["dataset"];
  summary: {
    observedCustomers: number;
    repeat90: RepeatEstimate;
    repeat365: RepeatEstimate;
    stability: {
      exactAgreement: number;
      cohenKappa: number;
      commonCustomers: number;
      earlierCutoff: string;
      laterCutoff: string;
    };
  };
  km: RepeatEstimate[];
  cohorts: CohortCell[];
  rfm: RfmSegment[];
  lineage: {
    kmSource: string;
    cohortSource: string;
    rfmSource: string;
    researchSummary: string;
  };
}

export interface DeliveryComparison {
  group: string;
  eligibleOrders: number;
  lateOrders: number;
  lateRate: number;
  ci95Low: number;
  ci95High: number;
  averageReviewScore: number;
}

export interface DeliveryModelSummary {
  key: string;
  label: string;
  outcome: string;
  reviewedOrders: number;
  events: number;
  oddsRatio: number;
  orCi95Low: number;
  orCi95High: number;
  standardizedLateRisk: number;
  standardizedOnTimeRisk: number;
  riskDifference: number;
  rdCi95Low: number;
  rdCi95High: number;
  auc: number;
  brierScore: number;
  parameters: number;
  iterations: number;
  converged: boolean;
}

export type DeliverySubgroupType = "month" | "state" | "category";

export interface DeliverySubgroupEffect {
  type: DeliverySubgroupType;
  group: string;
  lateReviewed: number;
  lateLowReviews: number;
  onTimeReviewed: number;
  onTimeLowReviews: number;
  lateRisk: number;
  onTimeRisk: number;
  riskDifference: number;
}

export interface DeliverySatisfactionContract {
  schemaVersion: 1;
  dataset: ExecutiveOverviewContract["dataset"];
  coverage: {
    delivered_orders: number;
    timing_eligible_orders: number;
    reviewed_orders: number;
    inference_eligible_orders: number;
    missing_actual_delivery_timestamp: number;
    missing_estimated_delivery_timestamp: number;
    missing_order_level_review: number;
  };
  observedContrast: {
    lateReviewed: number;
    lateLowReviews: number;
    lateRisk: number;
    lateCi95Low: number;
    lateCi95High: number;
    onTimeReviewed: number;
    onTimeLowReviews: number;
    onTimeRisk: number;
    onTimeCi95Low: number;
    onTimeCi95High: number;
    riskDifference: number;
    rdCi95Low: number;
    rdCi95High: number;
  };
  primaryModel: DeliveryModelSummary;
  sensitivities: DeliveryModelSummary[];
  missingReviewBounds: {
    lateMissingReviews: number;
    onTimeMissingReviews: number;
    observedRiskDifference: number;
    worstCaseMinimum: number;
    worstCaseMaximum: number;
  };
  comparisons: {
    minimumEligibleOrders: number;
    states: DeliveryComparison[];
    categories: DeliveryComparison[];
  };
  heterogeneity: Array<{
    type: DeliverySubgroupType;
    includedGroups: number;
    minimumOrdersPerTimingGroup: number;
    q: number;
    degreesFreedom: number;
    pValue: number;
    iSquared: number;
  }>;
  subgroupEffects: DeliverySubgroupEffect[];
  lineage: {
    phase2Summary: string;
    researchSummary: string;
    stateSource: string;
    categorySource: string;
    modelSource: string;
    researchSql: string;
  };
}

const STATUSES = new Set<ObservationStatus>([
  "complete_or_well_represented",
  "incomplete_first_month",
  "incomplete_last_month",
  "sparse_month",
]);

function record(value: unknown, name: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${name} must be an object`);
  }
  return value as Record<string, unknown>;
}

function number(value: unknown, name: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`${name} must be a finite number`);
  }
  return value;
}

function string(value: unknown, name: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${name} must be a non-empty string`);
  }
  return value;
}

export function parseExecutiveOverview(raw: unknown): ExecutiveOverviewContract {
  const root = record(raw, "contract");
  if (root.schemaVersion !== 1) throw new Error("Unsupported aggregate schema version");
  const dataset = record(root.dataset, "dataset");
  const summary = record(root.summary, "summary");
  const lineage = record(root.lineage, "lineage");
  if (dataset.status !== "verified_historical_snapshot") throw new Error("Unverified dataset status");
  if (!Array.isArray(root.monthly) || !Array.isArray(root.categories)) {
    throw new Error("Aggregate collections are missing");
  }

  const monthly = root.monthly.map((item, index): MonthlyAggregate => {
    const row = record(item, `monthly[${index}]`);
    const status = string(row.observationStatus, `monthly[${index}].observationStatus`) as ObservationStatus;
    if (!STATUSES.has(status)) throw new Error(`Unknown observation status: ${status}`);
    return {
      month: string(row.month, `monthly[${index}].month`),
      deliveredOrders: number(row.deliveredOrders, `monthly[${index}].deliveredOrders`),
      merchandiseValue: number(row.merchandiseValue, `monthly[${index}].merchandiseValue`),
      averageOrderValue: number(row.averageOrderValue, `monthly[${index}].averageOrderValue`),
      observationStatus: status,
    };
  });
  const categories = root.categories.map((item, index): CategoryAggregate => {
    const row = record(item, `categories[${index}]`);
    if (typeof row.inFirst80Pct !== "boolean") throw new Error("Category threshold flag must be boolean");
    return {
      category: string(row.category, `categories[${index}].category`),
      rank: number(row.rank, `categories[${index}].rank`),
      deliveredOrders: number(row.deliveredOrders, `categories[${index}].deliveredOrders`),
      merchandiseValue: number(row.merchandiseValue, `categories[${index}].merchandiseValue`),
      sharePct: number(row.sharePct, `categories[${index}].sharePct`),
      cumulativeSharePct: number(row.cumulativeSharePct, `categories[${index}].cumulativeSharePct`),
      inFirst80Pct: row.inFirst80Pct,
    };
  });
  if (monthly.length !== 23 || categories.length !== 20) throw new Error("Unexpected aggregate row count");
  if (summary.deliveredOrders !== 96478 || summary.merchandiseValue !== 13221498.11) {
    throw new Error("Executive anchors failed frontend validation");
  }

  return {
    schemaVersion: 1,
    dataset: {
      name: string(dataset.name, "dataset.name"),
      observationWindow: string(dataset.observationWindow, "dataset.observationWindow"),
      observationEnd: string(dataset.observationEnd, "dataset.observationEnd"),
      status: "verified_historical_snapshot",
    },
    summary: {
      deliveredOrders: number(summary.deliveredOrders, "summary.deliveredOrders"),
      merchandiseValue: number(summary.merchandiseValue, "summary.merchandiseValue"),
      averageOrderValue: number(summary.averageOrderValue, "summary.averageOrderValue"),
      topCategory: string(summary.topCategory, "summary.topCategory"),
      topCategorySharePct: number(summary.topCategorySharePct, "summary.topCategorySharePct"),
      categoriesToReach80Pct: number(summary.categoriesToReach80Pct, "summary.categoriesToReach80Pct"),
      thresholdCategory: string(summary.thresholdCategory, "summary.thresholdCategory"),
      thresholdCumulativeSharePct: number(summary.thresholdCumulativeSharePct, "summary.thresholdCumulativeSharePct"),
    },
    monthly,
    categories,
    lineage: {
      monthlySource: string(lineage.monthlySource, "lineage.monthlySource"),
      monthlySql: string(lineage.monthlySql, "lineage.monthlySql"),
      categorySource: string(lineage.categorySource, "lineage.categorySource"),
      categorySql: string(lineage.categorySql, "lineage.categorySql"),
    },
  };
}

function nullableNumber(value: unknown, name: string): number | null {
  return value === null ? null : number(value, name);
}

function repeatEstimate(value: unknown, name: string): RepeatEstimate {
  const row = record(value, name);
  return {
    horizonDays: number(row.horizonDays, `${name}.horizonDays`),
    customers: number(row.customers, `${name}.customers`),
    repeatIncidence: number(row.repeatIncidence, `${name}.repeatIncidence`),
    ci95Low: number(row.ci95Low, `${name}.ci95Low`),
    ci95High: number(row.ci95High, `${name}.ci95High`),
    riskSet: number(row.riskSet, `${name}.riskSet`),
  };
}

function deliveryModel(value: unknown, name: string): DeliveryModelSummary {
  const row = record(value, name);
  if (typeof row.converged !== "boolean") throw new Error(`${name}.converged must be boolean`);
  return {
    key: string(row.key, `${name}.key`),
    label: string(row.label, `${name}.label`),
    outcome: string(row.outcome, `${name}.outcome`),
    reviewedOrders: number(row.reviewedOrders, `${name}.reviewedOrders`),
    events: number(row.events, `${name}.events`),
    oddsRatio: number(row.oddsRatio, `${name}.oddsRatio`),
    orCi95Low: number(row.orCi95Low, `${name}.orCi95Low`),
    orCi95High: number(row.orCi95High, `${name}.orCi95High`),
    standardizedLateRisk: number(row.standardizedLateRisk, `${name}.standardizedLateRisk`),
    standardizedOnTimeRisk: number(row.standardizedOnTimeRisk, `${name}.standardizedOnTimeRisk`),
    riskDifference: number(row.riskDifference, `${name}.riskDifference`),
    rdCi95Low: number(row.rdCi95Low, `${name}.rdCi95Low`),
    rdCi95High: number(row.rdCi95High, `${name}.rdCi95High`),
    auc: number(row.auc, `${name}.auc`),
    brierScore: number(row.brierScore, `${name}.brierScore`),
    parameters: number(row.parameters, `${name}.parameters`),
    iterations: number(row.iterations, `${name}.iterations`),
    converged: row.converged,
  };
}

function deliveryComparison(value: unknown, name: string): DeliveryComparison {
  const row = record(value, name);
  return {
    group: string(row.group, `${name}.group`),
    eligibleOrders: number(row.eligibleOrders, `${name}.eligibleOrders`),
    lateOrders: number(row.lateOrders, `${name}.lateOrders`),
    lateRate: number(row.lateRate, `${name}.lateRate`),
    ci95Low: number(row.ci95Low, `${name}.ci95Low`),
    ci95High: number(row.ci95High, `${name}.ci95High`),
    averageReviewScore: number(row.averageReviewScore, `${name}.averageReviewScore`),
  };
}

export function parseCustomerIntelligence(raw: unknown): CustomerIntelligenceContract {
  const root = record(raw, "customer contract");
  if (root.schemaVersion !== 1) throw new Error("Unsupported customer schema version");
  const dataset = record(root.dataset, "dataset");
  const summary = record(root.summary, "summary");
  const stability = record(summary.stability, "summary.stability");
  const lineage = record(root.lineage, "lineage");
  if (dataset.status !== "verified_historical_snapshot") throw new Error("Unverified dataset status");
  if (!Array.isArray(root.km) || !Array.isArray(root.cohorts) || !Array.isArray(root.rfm)) {
    throw new Error("Customer aggregate collections are missing");
  }
  const km = root.km.map((value, index) => repeatEstimate(value, `km[${index}]`));
  const cohorts = root.cohorts.map((value, index): CohortCell => {
    const row = record(value, `cohorts[${index}]`);
    if (typeof row.observed !== "boolean") throw new Error("Cohort observed flag must be boolean");
    const retainedCustomers = nullableNumber(row.retainedCustomers, `cohorts[${index}].retainedCustomers`);
    const retentionRatePct = nullableNumber(row.retentionRatePct, `cohorts[${index}].retentionRatePct`);
    if (!row.observed && (retainedCustomers !== null || retentionRatePct !== null)) {
      throw new Error("Censored cohort cells must remain null");
    }
    return {
      cohortMonth: string(row.cohortMonth, `cohorts[${index}].cohortMonth`),
      monthNumber: number(row.monthNumber, `cohorts[${index}].monthNumber`),
      acquiredCustomers: number(row.acquiredCustomers, `cohorts[${index}].acquiredCustomers`),
      observed: row.observed,
      retainedCustomers,
      retentionRatePct,
    };
  });
  const rfm = root.rfm.map((value, index): RfmSegment => {
    const row = record(value, `rfm[${index}]`);
    return {
      segment: string(row.segment, `rfm[${index}].segment`),
      customers: number(row.customers, `rfm[${index}].customers`),
      customerSharePct: number(row.customerSharePct, `rfm[${index}].customerSharePct`),
      merchandiseValue: number(row.merchandiseValue, `rfm[${index}].merchandiseValue`),
      merchandiseSharePct: number(row.merchandiseSharePct, `rfm[${index}].merchandiseSharePct`),
      averagePurchaseFrequency: number(row.averagePurchaseFrequency, `rfm[${index}].averagePurchaseFrequency`),
      repeatCustomerSharePct: number(row.repeatCustomerSharePct, `rfm[${index}].repeatCustomerSharePct`),
    };
  });
  const repeat90 = repeatEstimate(summary.repeat90, "summary.repeat90");
  const repeat365 = repeatEstimate(summary.repeat365, "summary.repeat365");
  if (summary.observedCustomers !== 93358 || repeat90.horizonDays !== 90 || repeat365.horizonDays !== 365) {
    throw new Error("Customer research anchors failed frontend validation");
  }
  if (cohorts.some((row) => row.monthNumber === 0 && row.retentionRatePct !== 100)) {
    throw new Error("Month 0 cohort invariant failed");
  }
  return {
    schemaVersion: 1,
    dataset: {
      name: string(dataset.name, "dataset.name"),
      observationWindow: string(dataset.observationWindow, "dataset.observationWindow"),
      observationEnd: string(dataset.observationEnd, "dataset.observationEnd"),
      status: "verified_historical_snapshot",
    },
    summary: {
      observedCustomers: number(summary.observedCustomers, "summary.observedCustomers"),
      repeat90,
      repeat365,
      stability: {
        exactAgreement: number(stability.exactAgreement, "summary.stability.exactAgreement"),
        cohenKappa: number(stability.cohenKappa, "summary.stability.cohenKappa"),
        commonCustomers: number(stability.commonCustomers, "summary.stability.commonCustomers"),
        earlierCutoff: string(stability.earlierCutoff, "summary.stability.earlierCutoff"),
        laterCutoff: string(stability.laterCutoff, "summary.stability.laterCutoff"),
      },
    },
    km,
    cohorts,
    rfm,
    lineage: {
      kmSource: string(lineage.kmSource, "lineage.kmSource"),
      cohortSource: string(lineage.cohortSource, "lineage.cohortSource"),
      rfmSource: string(lineage.rfmSource, "lineage.rfmSource"),
      researchSummary: string(lineage.researchSummary, "lineage.researchSummary"),
    },
  };
}

export function parseDeliverySatisfaction(raw: unknown): DeliverySatisfactionContract {
  const root = record(raw, "delivery contract");
  if (root.schemaVersion !== 1) throw new Error("Unsupported delivery schema version");
  const dataset = record(root.dataset, "dataset");
  const coverage = record(root.coverage, "coverage");
  const observed = record(root.observedContrast, "observedContrast");
  const missing = record(root.missingReviewBounds, "missingReviewBounds");
  const comparisons = record(root.comparisons, "comparisons");
  const lineage = record(root.lineage, "lineage");
  if (dataset.status !== "verified_historical_snapshot") throw new Error("Unverified dataset status");
  if (!Array.isArray(root.sensitivities) || !Array.isArray(root.heterogeneity) || !Array.isArray(root.subgroupEffects)) {
    throw new Error("Delivery research collections are missing");
  }
  if (!Array.isArray(comparisons.states) || !Array.isArray(comparisons.categories)) {
    throw new Error("Delivery comparison collections are missing");
  }
  const subgroupTypes = new Set<DeliverySubgroupType>(["month", "state", "category"]);
  const primaryModel = deliveryModel(root.primaryModel, "primaryModel");
  const result: DeliverySatisfactionContract = {
    schemaVersion: 1,
    dataset: {
      name: string(dataset.name, "dataset.name"),
      observationWindow: string(dataset.observationWindow, "dataset.observationWindow"),
      observationEnd: string(dataset.observationEnd, "dataset.observationEnd"),
      status: "verified_historical_snapshot",
    },
    coverage: {
      delivered_orders: number(coverage.delivered_orders, "coverage.delivered_orders"),
      timing_eligible_orders: number(coverage.timing_eligible_orders, "coverage.timing_eligible_orders"),
      reviewed_orders: number(coverage.reviewed_orders, "coverage.reviewed_orders"),
      inference_eligible_orders: number(coverage.inference_eligible_orders, "coverage.inference_eligible_orders"),
      missing_actual_delivery_timestamp: number(coverage.missing_actual_delivery_timestamp, "coverage.missing_actual_delivery_timestamp"),
      missing_estimated_delivery_timestamp: number(coverage.missing_estimated_delivery_timestamp, "coverage.missing_estimated_delivery_timestamp"),
      missing_order_level_review: number(coverage.missing_order_level_review, "coverage.missing_order_level_review"),
    },
    observedContrast: {
      lateReviewed: number(observed.lateReviewed, "observedContrast.lateReviewed"),
      lateLowReviews: number(observed.lateLowReviews, "observedContrast.lateLowReviews"),
      lateRisk: number(observed.lateRisk, "observedContrast.lateRisk"),
      lateCi95Low: number(observed.lateCi95Low, "observedContrast.lateCi95Low"),
      lateCi95High: number(observed.lateCi95High, "observedContrast.lateCi95High"),
      onTimeReviewed: number(observed.onTimeReviewed, "observedContrast.onTimeReviewed"),
      onTimeLowReviews: number(observed.onTimeLowReviews, "observedContrast.onTimeLowReviews"),
      onTimeRisk: number(observed.onTimeRisk, "observedContrast.onTimeRisk"),
      onTimeCi95Low: number(observed.onTimeCi95Low, "observedContrast.onTimeCi95Low"),
      onTimeCi95High: number(observed.onTimeCi95High, "observedContrast.onTimeCi95High"),
      riskDifference: number(observed.riskDifference, "observedContrast.riskDifference"),
      rdCi95Low: number(observed.rdCi95Low, "observedContrast.rdCi95Low"),
      rdCi95High: number(observed.rdCi95High, "observedContrast.rdCi95High"),
    },
    primaryModel,
    sensitivities: root.sensitivities.map((value, index) => deliveryModel(value, `sensitivities[${index}]`)),
    missingReviewBounds: {
      lateMissingReviews: number(missing.lateMissingReviews, "missingReviewBounds.lateMissingReviews"),
      onTimeMissingReviews: number(missing.onTimeMissingReviews, "missingReviewBounds.onTimeMissingReviews"),
      observedRiskDifference: number(missing.observedRiskDifference, "missingReviewBounds.observedRiskDifference"),
      worstCaseMinimum: number(missing.worstCaseMinimum, "missingReviewBounds.worstCaseMinimum"),
      worstCaseMaximum: number(missing.worstCaseMaximum, "missingReviewBounds.worstCaseMaximum"),
    },
    comparisons: {
      minimumEligibleOrders: number(comparisons.minimumEligibleOrders, "comparisons.minimumEligibleOrders"),
      states: comparisons.states.map((value, index) => deliveryComparison(value, `states[${index}]`)),
      categories: comparisons.categories.map((value, index) => deliveryComparison(value, `categories[${index}]`)),
    },
    heterogeneity: root.heterogeneity.map((value, index) => {
      const row = record(value, `heterogeneity[${index}]`);
      const type = string(row.type, `heterogeneity[${index}].type`) as DeliverySubgroupType;
      if (!subgroupTypes.has(type)) throw new Error(`Unknown subgroup type: ${type}`);
      return {
        type,
        includedGroups: number(row.includedGroups, `heterogeneity[${index}].includedGroups`),
        minimumOrdersPerTimingGroup: number(row.minimumOrdersPerTimingGroup, `heterogeneity[${index}].minimumOrdersPerTimingGroup`),
        q: number(row.q, `heterogeneity[${index}].q`),
        degreesFreedom: number(row.degreesFreedom, `heterogeneity[${index}].degreesFreedom`),
        pValue: number(row.pValue, `heterogeneity[${index}].pValue`),
        iSquared: number(row.iSquared, `heterogeneity[${index}].iSquared`),
      };
    }),
    subgroupEffects: root.subgroupEffects.map((value, index) => {
      const row = record(value, `subgroupEffects[${index}]`);
      const type = string(row.type, `subgroupEffects[${index}].type`) as DeliverySubgroupType;
      if (!subgroupTypes.has(type)) throw new Error(`Unknown subgroup effect type: ${type}`);
      return {
        type,
        group: string(row.group, `subgroupEffects[${index}].group`),
        lateReviewed: number(row.lateReviewed, `subgroupEffects[${index}].lateReviewed`),
        lateLowReviews: number(row.lateLowReviews, `subgroupEffects[${index}].lateLowReviews`),
        onTimeReviewed: number(row.onTimeReviewed, `subgroupEffects[${index}].onTimeReviewed`),
        onTimeLowReviews: number(row.onTimeLowReviews, `subgroupEffects[${index}].onTimeLowReviews`),
        lateRisk: number(row.lateRisk, `subgroupEffects[${index}].lateRisk`),
        onTimeRisk: number(row.onTimeRisk, `subgroupEffects[${index}].onTimeRisk`),
        riskDifference: number(row.riskDifference, `subgroupEffects[${index}].riskDifference`),
      };
    }),
    lineage: {
      phase2Summary: string(lineage.phase2Summary, "lineage.phase2Summary"),
      researchSummary: string(lineage.researchSummary, "lineage.researchSummary"),
      stateSource: string(lineage.stateSource, "lineage.stateSource"),
      categorySource: string(lineage.categorySource, "lineage.categorySource"),
      modelSource: string(lineage.modelSource, "lineage.modelSource"),
      researchSql: string(lineage.researchSql, "lineage.researchSql"),
    },
  };
  if (result.coverage.inference_eligible_orders !== 95824 || Math.abs(result.observedContrast.lateRisk - 0.539877) > 0.000001) {
    throw new Error("Delivery observed anchors failed frontend validation");
  }
  if (Math.abs(primaryModel.oddsRatio - 11.407611357421521) > 1e-12 || Math.abs(primaryModel.riskDifference - 0.4249428982461647) > 1e-12) {
    throw new Error("Delivery model anchors failed frontend validation");
  }
  return result;
}
