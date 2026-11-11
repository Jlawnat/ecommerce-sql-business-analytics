#!/usr/bin/env python3
"""Publish the small, allowlisted aggregate contract consumed by ``web/``.

This publisher deliberately reads only checked-in month- and category-grain
outputs. It never opens raw source CSVs, SQLite databases, or customer-grain
research assets.
"""

from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MONTHLY_SOURCE = ROOT / "reports/phase2_outputs/monthly_sales.csv"
CATEGORY_SOURCE = ROOT / "reports/phase2_outputs/category_pareto.csv"
DEFAULT_OUTPUT = ROOT / "web/public/data/executive-overview.json"
CUSTOMER_OUTPUT = ROOT / "web/public/data/customer-intelligence.json"
DELIVERY_OUTPUT = ROOT / "web/public/data/delivery-satisfaction.json"
KM_SOURCE = ROOT / "reports/phase25_outputs/repeat_km_primary.csv"
COHORT_SOURCE = ROOT / "reports/phase2_outputs/cohort_retention.csv"
RFM_SOURCE = ROOT / "reports/phase2_outputs/rfm_segments.csv"
RESEARCH_SOURCE = ROOT / "reports/phase25_outputs/research_results.json"
STATISTICAL_SOURCE = ROOT / "reports/phase2_outputs/statistical_results.json"
DELIVERY_COVERAGE_SOURCE = ROOT / "reports/phase2_outputs/delivery_coverage.csv"
DELIVERY_TIMING_SOURCE = ROOT / "reports/phase2_outputs/delivery_timing.csv"
DELIVERY_STATE_SOURCE = ROOT / "reports/phase2_outputs/delivery_by_state.csv"
DELIVERY_CATEGORY_SOURCE = ROOT / "reports/phase2_outputs/delivery_by_category.csv"
DELIVERY_SUBGROUP_SOURCE = ROOT / "reports/phase25_outputs/delivery_subgroup_tables.csv"

MONTHLY_COLUMNS = (
    "purchase_month",
    "delivered_orders",
    "merchandise_value",
    "avg_merchandise_value_per_order",
    "raw_merchandise_value_mom_pct",
    "interpretable_mom_pct",
    "observation_status",
)
CATEGORY_COLUMNS = (
    "category",
    "delivered_orders",
    "merchandise_value",
    "value_rank",
    "merchandise_share_pct",
    "cumulative_share_pct",
    "contributes_to_first_80_pct",
)
VALID_OBSERVATION_STATES = {
    "complete_or_well_represented",
    "incomplete_first_month",
    "incomplete_last_month",
    "sparse_month",
}
KM_COLUMNS = (
    "horizon_days", "customers", "survival_no_second_purchase",
    "repeat_cumulative_incidence", "repeat_ci_95_low", "repeat_ci_95_high",
    "risk_set_at_last_event_or_censor", "events_at_last_time",
)
COHORT_COLUMNS = (
    "cohort_month", "month_number", "acquired_customers", "is_observed",
    "retained_customers", "retention_rate_pct",
)
RFM_COLUMNS = (
    "rfm_segment", "customers", "customer_share_pct", "merchandise_value",
    "merchandise_share_pct", "avg_purchase_frequency", "repeat_customer_share_pct",
)
DELIVERY_COVERAGE_COLUMNS = (
    "delivered_orders", "timing_eligible_orders", "reviewed_orders",
    "inference_eligible_orders", "missing_actual_delivery_timestamp",
    "missing_estimated_delivery_timestamp", "missing_order_level_review",
)
DELIVERY_TIMING_COLUMNS = (
    "delivery_timing", "timing_eligible_orders", "reviewed_orders",
    "avg_review_score", "mean_squared_review_score", "low_review_orders",
    "low_review_share_pct", "avg_days_vs_estimate",
)
DELIVERY_STATE_COLUMNS = (
    "customer_state", "timing_eligible_orders", "late_orders",
    "late_delivery_rate_pct", "reviewed_orders", "avg_review_score",
)
DELIVERY_CATEGORY_COLUMNS = (
    "attributed_category", "timing_eligible_orders", "mixed_category_orders",
    "late_orders", "late_delivery_rate_pct", "reviewed_orders", "avg_review_score",
)
DELIVERY_SUBGROUP_COLUMNS = (
    "subgroup_type", "subgroup_value", "late_reviewed", "late_low",
    "on_time_reviewed", "on_time_low",
)


class PublishContractError(ValueError):
    """Raised when a checked-in aggregate no longer satisfies its contract."""


def _rows(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != columns:
            raise PublishContractError(
                f"{path.relative_to(ROOT)} columns changed: {reader.fieldnames}"
            )
        return list(reader)


def _money(value: str | Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def build_contract() -> dict[str, Any]:
    monthly_source = _rows(MONTHLY_SOURCE, MONTHLY_COLUMNS)
    category_source = _rows(CATEGORY_SOURCE, CATEGORY_COLUMNS)

    if not monthly_source or not category_source:
        raise PublishContractError("Aggregate sources must not be empty")
    if [row["purchase_month"] for row in monthly_source] != sorted(
        row["purchase_month"] for row in monthly_source
    ):
        raise PublishContractError("Monthly rows must be sorted by purchase_month")
    if any(row["observation_status"] not in VALID_OBSERVATION_STATES for row in monthly_source):
        raise PublishContractError("Unexpected monthly observation status")

    ranks = [int(row["value_rank"]) for row in category_source]
    if ranks != list(range(1, len(ranks) + 1)):
        raise PublishContractError("Category ranks must be contiguous and ordered")
    cumulative = [Decimal(row["cumulative_share_pct"]) for row in category_source]
    if cumulative != sorted(cumulative) or cumulative[-1] != Decimal("100.0"):
        raise PublishContractError("Category cumulative shares must be monotonic and close at 100%")

    delivered_orders = sum(int(row["delivered_orders"]) for row in monthly_source)
    merchandise_value = sum((_money(row["merchandise_value"]) for row in monthly_source), Decimal("0"))
    average_order_value = _money(merchandise_value / delivered_orders)
    threshold = next(row for row in category_source if Decimal(row["cumulative_share_pct"]) >= Decimal("80"))

    # Anchor assertions make upstream semantic drift explicit instead of silently
    # changing the public dashboard.
    if (delivered_orders, merchandise_value, average_order_value) != (
        96_478,
        Decimal("13221498.11"),
        Decimal("137.04"),
    ):
        raise PublishContractError("Executive anchor metrics no longer reconcile")
    if threshold["category"] != "pet_shop" or int(threshold["value_rank"]) != 18:
        raise PublishContractError("The verified 80% Pareto threshold changed")

    monthly = [
        {
            "month": row["purchase_month"],
            "deliveredOrders": int(row["delivered_orders"]),
            "merchandiseValue": float(_money(row["merchandise_value"])),
            "averageOrderValue": float(_money(row["avg_merchandise_value_per_order"])),
            "observationStatus": row["observation_status"],
        }
        for row in monthly_source
    ]
    categories = [
        {
            "category": row["category"],
            "rank": int(row["value_rank"]),
            "deliveredOrders": int(row["delivered_orders"]),
            "merchandiseValue": float(_money(row["merchandise_value"])),
            "sharePct": float(Decimal(row["merchandise_share_pct"])),
            "cumulativeSharePct": float(Decimal(row["cumulative_share_pct"])),
            "inFirst80Pct": row["contributes_to_first_80_pct"] == "1",
        }
        for row in category_source[:20]
    ]

    return {
        "schemaVersion": 1,
        "dataset": {
            "name": "Olist Brazilian E-Commerce Public Dataset",
            "observationWindow": "2016-09 to 2018-08",
            "observationEnd": "2018-08",
            "status": "verified_historical_snapshot",
        },
        "summary": {
            "deliveredOrders": delivered_orders,
            "merchandiseValue": float(merchandise_value),
            "averageOrderValue": float(average_order_value),
            "topCategory": category_source[0]["category"],
            "topCategorySharePct": float(Decimal(category_source[0]["merchandise_share_pct"])),
            "categoriesToReach80Pct": int(threshold["value_rank"]),
            "thresholdCategory": threshold["category"],
            "thresholdCumulativeSharePct": float(Decimal(threshold["cumulative_share_pct"])),
        },
        "monthly": monthly,
        "categories": categories,
        "lineage": {
            "monthlySource": "reports/phase2_outputs/monthly_sales.csv",
            "monthlySql": "sql/analysis/07_sales_category_trends.sql",
            "categorySource": "reports/phase2_outputs/category_pareto.csv",
            "categorySql": "sql/analysis/07_sales_category_trends.sql",
        },
    }


def build_customer_contract() -> dict[str, Any]:
    """Build the customer page from research-approved aggregate tables only."""
    km_source = _rows(KM_SOURCE, KM_COLUMNS)
    cohort_source = _rows(COHORT_SOURCE, COHORT_COLUMNS)
    rfm_source = _rows(RFM_SOURCE, RFM_COLUMNS)
    research = json.loads(RESEARCH_SOURCE.read_text(encoding="utf-8"))
    stability = research["repeat_purchase"]["rfm_stability"]

    horizons = [int(row["horizon_days"]) for row in km_source]
    if horizons != [30, 60, 90, 180, 365]:
        raise PublishContractError("Kaplan-Meier horizons changed")
    if {int(row["customers"]) for row in km_source} != {93_358}:
        raise PublishContractError("Kaplan-Meier population changed")

    for row in cohort_source:
        observed = row["is_observed"] == "1"
        if not observed and (row["retained_customers"] or row["retention_rate_pct"]):
            raise PublishContractError("Censored cohort cells must remain unavailable")
        if int(row["month_number"]) == 0 and (
            not observed or Decimal(row["retention_rate_pct"]) != Decimal("100.0")
        ):
            raise PublishContractError("Month 0 retention must be 100% by construction")

    if sum(int(row["customers"]) for row in rfm_source) != 93_358:
        raise PublishContractError("RFM population no longer reconciles")

    km = [
        {
            "horizonDays": int(row["horizon_days"]),
            "customers": int(row["customers"]),
            "repeatIncidence": float(Decimal(row["repeat_cumulative_incidence"])),
            "ci95Low": float(Decimal(row["repeat_ci_95_low"])),
            "ci95High": float(Decimal(row["repeat_ci_95_high"])),
            "riskSet": int(row["risk_set_at_last_event_or_censor"]),
        }
        for row in km_source
    ]
    by_horizon = {row["horizonDays"]: row for row in km}
    if by_horizon[90]["repeatIncidence"] != float(Decimal("0.021279730139541764")):
        raise PublishContractError("Verified 90-day repeat estimate changed")
    if by_horizon[365]["repeatIncidence"] != float(Decimal("0.038117413841527226")):
        raise PublishContractError("Verified 365-day repeat estimate changed")

    return {
        "schemaVersion": 1,
        "dataset": {
            "name": "Olist Brazilian E-Commerce Public Dataset",
            "observationWindow": "2016-09 to 2018-08",
            "observationEnd": "2018-08",
            "status": "verified_historical_snapshot",
        },
        "summary": {
            "observedCustomers": 93_358,
            "repeat90": by_horizon[90],
            "repeat365": by_horizon[365],
            "stability": {
                "exactAgreement": float(stability["exact_segment_agreement"]),
                "cohenKappa": float(stability["cohen_kappa"]),
                "commonCustomers": int(stability["common_customers"]),
                "earlierCutoff": stability["earlier_cutoff"][:10],
                "laterCutoff": stability["later_cutoff"][:10],
            },
        },
        "km": km,
        "cohorts": [
            {
                "cohortMonth": row["cohort_month"][:7],
                "monthNumber": int(row["month_number"]),
                "acquiredCustomers": int(row["acquired_customers"]),
                "observed": row["is_observed"] == "1",
                "retainedCustomers": int(row["retained_customers"]) if row["retained_customers"] else None,
                "retentionRatePct": float(Decimal(row["retention_rate_pct"])) if row["retention_rate_pct"] else None,
            }
            for row in cohort_source
        ],
        "rfm": [
            {
                "segment": row["rfm_segment"],
                "customers": int(row["customers"]),
                "customerSharePct": float(Decimal(row["customer_share_pct"])),
                "merchandiseValue": float(_money(row["merchandise_value"])),
                "merchandiseSharePct": float(Decimal(row["merchandise_share_pct"])),
                "averagePurchaseFrequency": float(Decimal(row["avg_purchase_frequency"])),
                "repeatCustomerSharePct": float(Decimal(row["repeat_customer_share_pct"])),
            }
            for row in rfm_source
        ],
        "lineage": {
            "kmSource": "reports/phase25_outputs/repeat_km_primary.csv",
            "cohortSource": "reports/phase2_outputs/cohort_retention.csv",
            "rfmSource": "reports/phase2_outputs/rfm_segments.csv",
            "researchSummary": "reports/PHASE25_RESEARCH_RESULTS.md",
        },
    }


def build_delivery_contract() -> dict[str, Any]:
    """Build delivery research from approved order-level aggregate outputs."""
    coverage_rows = _rows(DELIVERY_COVERAGE_SOURCE, DELIVERY_COVERAGE_COLUMNS)
    timing_rows = _rows(DELIVERY_TIMING_SOURCE, DELIVERY_TIMING_COLUMNS)
    state_rows = _rows(DELIVERY_STATE_SOURCE, DELIVERY_STATE_COLUMNS)
    category_rows = _rows(DELIVERY_CATEGORY_SOURCE, DELIVERY_CATEGORY_COLUMNS)
    subgroup_rows = _rows(DELIVERY_SUBGROUP_SOURCE, DELIVERY_SUBGROUP_COLUMNS)
    research = json.loads(RESEARCH_SOURCE.read_text(encoding="utf-8"))["delivery_satisfaction"]
    statistics = json.loads(STATISTICAL_SOURCE.read_text(encoding="utf-8"))

    if len(coverage_rows) != 1 or {row["delivery_timing"] for row in timing_rows} != {"late", "on_time_or_early"}:
        raise PublishContractError("Delivery coverage or timing aggregate changed")
    coverage = {key: int(value) for key, value in coverage_rows[0].items()}
    timing_by_group = {row["delivery_timing"]: row for row in timing_rows}
    late, on_time = timing_by_group["late"], timing_by_group["on_time_or_early"]
    raw_contrast = statistics["low_review_share_difference_late_minus_on_time"]
    primary = research["primary_adjusted_model"]

    anchors = (
        coverage["delivered_orders"], coverage["inference_eligible_orders"],
        Decimal(late["low_review_share_pct"]), Decimal(on_time["low_review_share_pct"]),
        Decimal(str(primary["late_odds_ratio"])).quantize(Decimal("0.01")),
        Decimal(str(primary["standardized_risk_difference"] * 100)).quantize(Decimal("0.01")),
    )
    if anchors != (96_478, 95_824, Decimal("53.9877"), Decimal("9.1875"), Decimal("11.41"), Decimal("42.49")):
        raise PublishContractError("Delivery research anchors changed")

    state_intervals = statistics["state_late_rate_wilson_95_ci_minimum_500_orders"]
    category_intervals = statistics["category_late_rate_wilson_95_ci_minimum_500_orders"]
    state_lookup = {row["customer_state"]: row for row in state_rows}
    category_lookup = {row["attributed_category"]: row for row in category_rows}

    states = sorted(({
        "group": state,
        "eligibleOrders": int(interval["orders"]),
        "lateOrders": int(state_lookup[state]["late_orders"]),
        "lateRate": float(interval["rate"]),
        "ci95Low": float(interval["ci_95_low"]),
        "ci95High": float(interval["ci_95_high"]),
        "averageReviewScore": float(Decimal(state_lookup[state]["avg_review_score"])),
    } for state, interval in state_intervals.items()), key=lambda row: (-row["lateRate"], row["group"]))
    categories = sorted(({
        "group": category,
        "eligibleOrders": int(interval["orders"]),
        "lateOrders": int(category_lookup[category]["late_orders"]),
        "lateRate": float(interval["rate"]),
        "ci95Low": float(interval["ci_95_low"]),
        "ci95High": float(interval["ci_95_high"]),
        "averageReviewScore": float(Decimal(category_lookup[category]["avg_review_score"])),
    } for category, interval in category_intervals.items()), key=lambda row: (-row["lateRate"], row["group"]))

    heterogeneity = {row["subgroup_type"]: row for row in research["heterogeneity"]}
    subgroup_effects = []
    included_counts = {"month": 0, "state": 0, "category": 0}
    for row in subgroup_rows:
        late_reviewed = int(row["late_reviewed"])
        on_time_reviewed = int(row["on_time_reviewed"])
        if late_reviewed < 20 or on_time_reviewed < 20:
            continue
        included_counts[row["subgroup_type"]] += 1
        late_risk = int(row["late_low"]) / late_reviewed
        on_time_risk = int(row["on_time_low"]) / on_time_reviewed
        subgroup_effects.append({
            "type": row["subgroup_type"],
            "group": row["subgroup_value"],
            "lateReviewed": late_reviewed,
            "lateLowReviews": int(row["late_low"]),
            "onTimeReviewed": on_time_reviewed,
            "onTimeLowReviews": int(row["on_time_low"]),
            "lateRisk": late_risk,
            "onTimeRisk": on_time_risk,
            "riskDifference": late_risk - on_time_risk,
        })
    for group_type, count in included_counts.items():
        if count != heterogeneity[group_type]["included_groups"]:
            raise PublishContractError(f"{group_type} subgroup eligibility changed")

    def model_summary(key: str, label: str) -> dict[str, Any]:
        model = research[key]
        return {
            "key": key,
            "label": label,
            "outcome": model["outcome"],
            "reviewedOrders": int(model["reviewed_orders"]),
            "events": int(model["events"]),
            "oddsRatio": float(model["late_odds_ratio"]),
            "orCi95Low": float(model["late_or_ci_95_low"]),
            "orCi95High": float(model["late_or_ci_95_high"]),
            "standardizedLateRisk": float(model["standardized_late_risk"]),
            "standardizedOnTimeRisk": float(model["standardized_on_time_risk"]),
            "riskDifference": float(model["standardized_risk_difference"]),
            "rdCi95Low": float(model["risk_difference_ci_95_low"]),
            "rdCi95High": float(model["risk_difference_ci_95_high"]),
            "auc": float(model["auc"]),
            "brierScore": float(model["brier_score"]),
            "parameters": int(model["parameters"]),
            "iterations": int(model["iterations"]),
            "converged": bool(model["converged"]),
        }

    return {
        "schemaVersion": 1,
        "dataset": {
            "name": "Olist Brazilian E-Commerce Public Dataset",
            "observationWindow": "2016-09 to 2018-08",
            "observationEnd": "2018-08",
            "status": "verified_historical_snapshot",
        },
        "coverage": coverage,
        "observedContrast": {
            "lateReviewed": int(late["reviewed_orders"]),
            "lateLowReviews": int(late["low_review_orders"]),
            "lateRisk": float(Decimal(late["low_review_share_pct"]) / 100),
            "lateCi95Low": float(statistics["late_low_review_share_wilson_95_ci"]["low"]),
            "lateCi95High": float(statistics["late_low_review_share_wilson_95_ci"]["high"]),
            "onTimeReviewed": int(on_time["reviewed_orders"]),
            "onTimeLowReviews": int(on_time["low_review_orders"]),
            "onTimeRisk": float(Decimal(on_time["low_review_share_pct"]) / 100),
            "onTimeCi95Low": float(statistics["on_time_low_review_share_wilson_95_ci"]["low"]),
            "onTimeCi95High": float(statistics["on_time_low_review_share_wilson_95_ci"]["high"]),
            "riskDifference": float(raw_contrast["difference"]),
            "rdCi95Low": float(raw_contrast["ci_95_low"]),
            "rdCi95High": float(raw_contrast["ci_95_high"]),
        },
        "primaryModel": model_summary("primary_adjusted_model", "Primary adjusted model"),
        "sensitivities": [
            model_summary("single_seller_sensitivity", "Single-seller orders"),
            model_summary("score_one_sensitivity", "Score = 1 outcome"),
        ],
        "missingReviewBounds": {
            "lateMissingReviews": int(research["missing_review_bounds"]["late_missing_reviews"]),
            "onTimeMissingReviews": int(research["missing_review_bounds"]["on_time_missing_reviews"]),
            "observedRiskDifference": float(research["missing_review_bounds"]["observed_risk_difference"]),
            "worstCaseMinimum": float(research["missing_review_bounds"]["worst_case_minimum"]),
            "worstCaseMaximum": float(research["missing_review_bounds"]["worst_case_maximum"]),
        },
        "comparisons": {"minimumEligibleOrders": 500, "states": states, "categories": categories},
        "heterogeneity": [{
            "type": group_type,
            "includedGroups": int(heterogeneity[group_type]["included_groups"]),
            "minimumOrdersPerTimingGroup": int(heterogeneity[group_type]["minimum_orders_per_timing_group"]),
            "q": float(heterogeneity[group_type]["q"]),
            "degreesFreedom": int(heterogeneity[group_type]["df"]),
            "pValue": float(heterogeneity[group_type]["p_value"]),
            "iSquared": float(heterogeneity[group_type]["i_squared"]),
        } for group_type in ("month", "state", "category")],
        "subgroupEffects": subgroup_effects,
        "lineage": {
            "phase2Summary": "reports/PHASE2_RESULTS.md",
            "researchSummary": "reports/PHASE25_RESEARCH_RESULTS.md",
            "stateSource": "reports/phase2_outputs/delivery_by_state.csv",
            "categorySource": "reports/phase2_outputs/delivery_by_category.csv",
            "modelSource": "reports/phase25_outputs/research_results.json",
            "researchSql": "sql/analysis/10_delivery_satisfaction_research.sql",
        },
    }


def publish(output: Path = DEFAULT_OUTPUT) -> Path:
    payload = build_contract()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def publish_customer(output: Path = CUSTOMER_OUTPUT) -> Path:
    payload = build_customer_contract()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def publish_delivery(output: Path = DELIVERY_OUTPUT) -> Path:
    payload = build_delivery_contract()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(publish(args.output))
    print(publish_customer())
    print(publish_delivery())


if __name__ == "__main__":
    main()

