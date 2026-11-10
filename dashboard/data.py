"""Authoritative aggregate contracts for the Streamlit dashboard.

The dashboard intentionally excludes customer-level exports and never recomputes a
Phase 1–2.5 metric from raw tables.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/Jlawnat/ecommerce-sql-business-analytics"


@dataclass(frozen=True)
class AssetContract:
    path: str
    source: str
    grain: str
    observation: str
    required_columns: tuple[str, ...] = ()


ASSETS: dict[str, AssetContract] = {
    "monthly_sales": AssetContract("reports/phase2_outputs/monthly_sales.csv", "sql/analysis/07_sales_category_trends.sql", "purchase month", "2016-09 to 2018-08", ("purchase_month", "delivered_orders", "merchandise_value", "avg_merchandise_value_per_order", "observation_status")),
    "category_pareto": AssetContract("reports/phase2_outputs/category_pareto.csv", "sql/analysis/07_sales_category_trends.sql", "translated category", "delivered orders through 2018-08", ("category", "delivered_orders", "merchandise_value", "merchandise_share_pct", "cumulative_share_pct")),
    "cohort_retention": AssetContract("reports/phase2_outputs/cohort_retention.csv", "sql/analysis/05_customer_cohort_retention.sql", "cohort month × month offset", "last observed purchase month 2018-08", ("cohort_month", "month_number", "acquired_customers", "is_observed", "retained_customers", "retention_rate_pct")),
    "cohort_summary": AssetContract("reports/phase2_outputs/cohort_summary.csv", "sql/analysis/05_customer_cohort_retention.sql", "acquisition cohort month", "last observed purchase month 2018-08", ("cohort_month", "acquired_customers", "repeat_customers", "repeat_purchase_rate_pct", "merchandise_value_per_customer")),
    "rfm_segments": AssetContract("reports/phase2_outputs/rfm_segments.csv", "sql/analysis/06_rfm_segmentation.sql", "RFM segment", "snapshot 2018-09-01", ("rfm_segment", "customers", "customer_share_pct", "merchandise_value", "merchandise_share_pct", "avg_purchase_frequency")),
    "delivery_state": AssetContract("reports/phase2_outputs/delivery_by_state.csv", "sql/analysis/08_delivery_segment_analysis.sql", "customer state", "delivered orders through 2018-08", ("customer_state", "timing_eligible_orders", "late_orders", "late_delivery_rate_pct", "reviewed_orders")),
    "delivery_category": AssetContract("reports/phase2_outputs/delivery_by_category.csv", "sql/analysis/08_delivery_segment_analysis.sql", "order-attributed category", "delivered orders through 2018-08", ("attributed_category", "timing_eligible_orders", "mixed_category_orders", "late_orders", "late_delivery_rate_pct")),
    "delivery_timing": AssetContract("reports/phase2_outputs/delivery_timing.csv", "sql/analysis/08_delivery_segment_analysis.sql", "delivery timing group", "delivered orders through 2018-08", ("delivery_timing", "timing_eligible_orders", "reviewed_orders", "avg_review_score", "low_review_orders", "low_review_share_pct")),
    "delivery_coverage": AssetContract("reports/phase2_outputs/delivery_coverage.csv", "sql/analysis/08_delivery_segment_analysis.sql", "single coverage summary", "delivered orders through 2018-08", ("delivered_orders", "timing_eligible_orders", "reviewed_orders", "inference_eligible_orders")),
    "phase2_statistics": AssetContract("reports/phase2_outputs/statistical_results.json", "scripts/phase2_analysis.py", "statistical result", "generated from Phase 2 SQL aggregates"),
    "repeat_km": AssetContract("reports/phase25_outputs/repeat_km_primary.csv", "sql/analysis/09_repeat_purchase_research.sql", "time horizon", "cutoff 2018-09-01", ("horizon_days", "customers", "repeat_cumulative_incidence", "repeat_ci_95_low", "repeat_ci_95_high")),
    "research_results": AssetContract("reports/phase25_outputs/research_results.json", "scripts/phase25_research.py", "research result", "cutoff 2018-09-01"),
    "delivery_subgroups": AssetContract("reports/phase25_outputs/delivery_subgroup_tables.csv", "sql/analysis/10_delivery_satisfaction_research.sql", "subgroup 2×2 table", "95,824 timing/review eligible orders", ("subgroup_type", "subgroup_value", "late_reviewed", "late_low", "on_time_reviewed", "on_time_low")),
}

# Only non-customer aggregates may be offered through dashboard download buttons.
EXPORT_ALLOWLIST = frozenset({
    "monthly_sales", "category_pareto", "cohort_retention", "cohort_summary",
    "rfm_segments", "delivery_state", "delivery_category", "delivery_timing",
    "delivery_coverage", "repeat_km", "delivery_subgroups",
})


class DataUnavailable(RuntimeError):
    def __init__(self, key: str, path: Path):
        self.key = key
        self.path = path
        super().__init__(
            f"Verified dashboard asset is missing: {path}. "
            "Run `python3 scripts/phase2_analysis.py`, "
            "`python3 scripts/build_analytics_mart.py`, and "
            "`python3 scripts/phase25_research.py`."
        )


class DataContractError(RuntimeError):
    pass


class DashboardRepository:
    def __init__(self, root: Path = PROJECT_ROOT):
        self.root = Path(root)

    def path(self, key: str) -> Path:
        return self.root / ASSETS[key].path

    def contract(self, key: str) -> AssetContract:
        return ASSETS[key]

    def availability(self) -> dict[str, bool]:
        return {key: self.path(key).is_file() for key in ASSETS}

    @lru_cache(maxsize=None)
    def csv(self, key: str) -> pd.DataFrame:
        contract = ASSETS[key]
        path = self.path(key)
        if not path.is_file():
            raise DataUnavailable(key, path)
        frame = pd.read_csv(path)
        missing = set(contract.required_columns) - set(frame.columns)
        if missing:
            raise DataContractError(f"{key} is missing required columns: {sorted(missing)}")
        return frame.copy()

    @lru_cache(maxsize=None)
    def json(self, key: str) -> dict:
        path = self.path(key)
        if not path.is_file():
            raise DataUnavailable(key, path)
        with path.open(encoding="utf-8") as source:
            return json.load(source)

    def export_csv(self, key: str) -> bytes:
        if key not in EXPORT_ALLOWLIST:
            raise PermissionError(f"Dashboard export is not allowed for {key}")
        return self.csv(key).to_csv(index=False).encode("utf-8")

    def anchor_metrics(self) -> dict[str, float | int | str]:
        monthly = self.csv("monthly_sales")
        category = self.csv("category_pareto")
        coverage = self.csv("delivery_coverage").iloc[0]
        return {
            "delivered_orders": int(monthly["delivered_orders"].sum()),
            "merchandise_value": round(float(monthly["merchandise_value"].sum()), 2),
            "average_order_value": round(float(monthly["merchandise_value"].sum() / monthly["delivered_orders"].sum()), 2),
            "top_category": str(category.iloc[0]["category"]),
            "top_category_share_pct": float(category.iloc[0]["merchandise_share_pct"]),
            "inference_eligible_orders": int(coverage["inference_eligible_orders"]),
            "observation_window": "2016-09 to 2018-08",
        }

    def source_url(self, key: str) -> str:
        return f"{REPO_URL}/blob/main/{ASSETS[key].source}"

    def sqlite_status(self) -> dict[str, bool]:
        return {
            "source_database": (self.root / "data/processed/olist.sqlite").is_file(),
            "analytics_mart": (self.root / "data/processed/olist_analytics.sqlite").is_file(),
        }
