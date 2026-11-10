#!/usr/bin/env python3
"""Execute Phase 2 SQL, calculate documented inference, and render static SVG charts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
import sys
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_analysis import iter_statements

SQL_DIR = PROJECT_ROOT / "sql" / "analysis"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "phase2_outputs"
CHART_DIR = PROJECT_ROOT / "visualizations"
Z_975 = 1.959963984540054

QUERY_OUTPUTS = {
    "05_customer_cohort_retention.sql": ("cohort_summary", "cohort_retention"),
    "06_rfm_segmentation.sql": ("rfm_customers", "rfm_segments"),
    "07_sales_category_trends.sql": ("monthly_sales", "category_pareto", "category_monthly_mix"),
    "08_delivery_segment_analysis.sql": (
        "delivery_coverage", "delivery_timing", "delivery_by_state",
        "delivery_by_category", "delivery_strata",
    ),
}


def normal_two_sided_p(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2.0))


def wilson_interval(successes: int, total: int, z: float = Z_975) -> tuple[float, float]:
    if total <= 0:
        return (math.nan, math.nan)
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half_width = z * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total)) / denominator
    return centre - half_width, centre + half_width


def two_proportion_inference(successes_a: int, total_a: int, successes_b: int, total_b: int) -> dict[str, float]:
    p_a, p_b = successes_a / total_a, successes_b / total_b
    difference = p_a - p_b
    unpooled_se = math.sqrt(p_a * (1 - p_a) / total_a + p_b * (1 - p_b) / total_b)
    pooled = (successes_a + successes_b) / (total_a + total_b)
    pooled_se = math.sqrt(pooled * (1 - pooled) * (1 / total_a + 1 / total_b))
    z_value = difference / pooled_se if pooled_se else math.inf
    return {
        "proportion_a": p_a, "proportion_b": p_b, "difference": difference,
        "ci_95_low": difference - Z_975 * unpooled_se,
        "ci_95_high": difference + Z_975 * unpooled_se,
        "z_statistic": z_value, "p_value": normal_two_sided_p(z_value),
    }


def mean_difference_inference(
    n_a: int, mean_a: float, mean_square_a: float,
    n_b: int, mean_b: float, mean_square_b: float,
) -> dict[str, float]:
    variance_a = max(0.0, (mean_square_a - mean_a * mean_a) * n_a / (n_a - 1))
    variance_b = max(0.0, (mean_square_b - mean_b * mean_b) * n_b / (n_b - 1))
    standard_error = math.sqrt(variance_a / n_a + variance_b / n_b)
    difference = mean_a - mean_b
    z_value = difference / standard_error if standard_error else math.inf
    # With both groups in the thousands, the normal approximation and Welch-t are numerically equivalent.
    return {
        "mean_a": mean_a, "mean_b": mean_b, "difference": difference,
        "standard_error": standard_error,
        "ci_95_low": difference - Z_975 * standard_error,
        "ci_95_high": difference + Z_975 * standard_error,
        "z_statistic_large_sample": z_value, "p_value": normal_two_sided_p(z_value),
    }


def stratified_cmh(rows: list[dict]) -> dict[str, float | int]:
    """Mantel-Haenszel common OR and continuity-uncorrected CMH association test."""
    numerator_or = denominator_or = observed_minus_expected = variance_sum = 0.0
    usable = 0
    for row in rows:
        exposed_total = int(row["late_reviewed_orders"])
        unexposed_total = int(row["on_time_reviewed_orders"])
        a = int(row["late_low_review_orders"])
        c = int(row["on_time_low_review_orders"])
        b, d = exposed_total - a, unexposed_total - c
        total = exposed_total + unexposed_total
        cases = a + c
        controls = b + d
        if exposed_total == 0 or unexposed_total == 0 or total <= 1 or cases == 0 or controls == 0:
            continue
        usable += 1
        numerator_or += a * d / total
        denominator_or += b * c / total
        expected_a = exposed_total * cases / total
        observed_minus_expected += a - expected_a
        variance_sum += exposed_total * unexposed_total * cases * controls / (total * total * (total - 1))
    z_value = observed_minus_expected / math.sqrt(variance_sum) if variance_sum else math.nan
    return {
        "usable_strata": usable,
        "common_odds_ratio": numerator_or / denominator_or if denominator_or else math.inf,
        "cmh_z_statistic": z_value,
        "cmh_chi_square_1df": z_value * z_value,
        "p_value": normal_two_sided_p(z_value),
    }


def execute_phase2(connection: sqlite3.Connection) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    for filename, names in QUERY_OUTPUTS.items():
        statements = list(iter_statements((SQL_DIR / filename).read_text(encoding="utf-8")))
        if len(statements) != len(names):
            raise RuntimeError(f"{filename}: expected {len(names)} statements, found {len(statements)}")
        for name, statement in zip(names, statements):
            results[name] = [dict(row) for row in connection.execute(statement).fetchall()]
    return results


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def calculate_statistics(results: dict[str, list[dict]]) -> dict:
    timing = {row["delivery_timing"]: row for row in results["delivery_timing"]}
    late, on_time = timing["late"], timing["on_time_or_early"]
    mean_test = mean_difference_inference(
        late["reviewed_orders"], late["avg_review_score"], late["mean_squared_review_score"],
        on_time["reviewed_orders"], on_time["avg_review_score"], on_time["mean_squared_review_score"],
    )
    low_test = two_proportion_inference(
        late["low_review_orders"], late["reviewed_orders"],
        on_time["low_review_orders"], on_time["reviewed_orders"],
    )
    late_ci = wilson_interval(late["low_review_orders"], late["reviewed_orders"])
    on_time_ci = wilson_interval(on_time["low_review_orders"], on_time["reviewed_orders"])
    mean_test["p_value_reporting"] = "<1e-300" if mean_test["p_value"] == 0.0 else f"{mean_test['p_value']:.6g}"
    low_test["p_value_reporting"] = "<1e-300" if low_test["p_value"] == 0.0 else f"{low_test['p_value']:.6g}"
    state_intervals = {}
    for row in results["delivery_by_state"]:
        if row["timing_eligible_orders"] >= 500:
            low, high = wilson_interval(row["late_orders"], row["timing_eligible_orders"])
            state_intervals[row["customer_state"]] = {
                "orders": row["timing_eligible_orders"], "rate": row["late_orders"] / row["timing_eligible_orders"],
                "ci_95_low": low, "ci_95_high": high,
            }
    category_intervals = {}
    for row in results["delivery_by_category"]:
        if row["timing_eligible_orders"] >= 500:
            low, high = wilson_interval(row["late_orders"], row["timing_eligible_orders"])
            category_intervals[row["attributed_category"]] = {
                "orders": row["timing_eligible_orders"], "rate": row["late_orders"] / row["timing_eligible_orders"],
                "ci_95_low": low, "ci_95_high": high,
            }
    cmh = stratified_cmh(results["delivery_strata"])
    cmh["p_value_reporting"] = "<1e-300" if cmh["p_value"] == 0.0 else f"{cmh['p_value']:.6g}"
    return {
        "analysis_cutoff": "2018-09-01 00:00:00",
        "review_score_mean_difference_late_minus_on_time": mean_test,
        "low_review_share_difference_late_minus_on_time": low_test,
        "late_low_review_share_wilson_95_ci": {"low": late_ci[0], "high": late_ci[1]},
        "on_time_low_review_share_wilson_95_ci": {"low": on_time_ci[0], "high": on_time_ci[1]},
        "stratified_low_review_association": cmh,
        "state_late_rate_wilson_95_ci_minimum_500_orders": state_intervals,
        "category_late_rate_wilson_95_ci_minimum_500_orders": category_intervals,
        "assumptions": [
            "Order is the independent analysis unit; multiple reviews are averaged before joining.",
            "Large-sample normal inference is used for mean and proportion contrasts.",
            "CMH strata are purchase month x customer state x order merchandise-value band.",
            "P-values quantify association under model assumptions and do not establish causality.",
        ],
    }


def svg_document(title: str, body: str, width: int = 1000, height: int = 620) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="#fbfaf7"/>'
        '<style>text{font-family:Arial,sans-serif;fill:#17202a}.title{font-size:24px;font-weight:700}'
        '.axis{font-size:11px;fill:#566573}.label{font-size:13px}.grid{stroke:#d5d8dc;stroke-width:1}'
        '.note{font-size:11px;fill:#626567}</style>'
        f'<text x="55" y="38" class="title">{escape(title)}</text>{body}</svg>'
    )


def render_bar_chart(path: Path, title: str, labels: list[str], values: list[float], value_suffix: str = "") -> None:
    width, height, left, top, bottom = 1000, 620, 250, 70, 45
    plot_width = width - left - 70
    bar_height = min(48, (height - top - bottom) / max(len(labels), 1) * 0.65)
    gap = (height - top - bottom) / max(len(labels), 1)
    maximum = max(values) if values else 1
    parts = []
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * gap + (gap - bar_height) / 2
        bar_width = plot_width * value / maximum if maximum else 0
        parts.append(f'<text x="240" y="{y + bar_height * .68:.1f}" text-anchor="end" class="label">{escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="3" fill="#2874a6"/>')
        parts.append(f'<text x="{left + bar_width + 8:.1f}" y="{y + bar_height * .68:.1f}" class="label">{value:,.1f}{escape(value_suffix)}</text>')
    path.write_text(svg_document(title, "".join(parts), width, height), encoding="utf-8")


def render_monthly_line(path: Path, rows: list[dict]) -> None:
    width, height, left, right, top, bottom = 1000, 620, 75, 35, 75, 75
    values = [float(r["merchandise_value"]) for r in rows]
    maximum = max(values)
    x_step = (width - left - right) / max(len(rows) - 1, 1)
    y = lambda value: top + (height - top - bottom) * (1 - value / maximum)
    points = " ".join(f"{left + i*x_step:.1f},{y(v):.1f}" for i, v in enumerate(values))
    parts = [f'<polyline points="{points}" fill="none" stroke="#2874a6" stroke-width="3"/>']
    for i, row in enumerate(rows):
        x = left + i * x_step
        parts.append(f'<circle cx="{x:.1f}" cy="{y(values[i]):.1f}" r="4" fill="#d35400"/>')
        if i % 2 == 0 or i == len(rows) - 1:
            parts.append(f'<text x="{x:.1f}" y="{height-48}" text-anchor="end" transform="rotate(-45 {x:.1f} {height-48})" class="axis">{row["purchase_month"]}</text>')
    parts.append('<text x="75" y="590" class="note">Boundary and sparse months are flagged in monthly_sales.csv; raw MoM is not treated as representative there.</text>')
    path.write_text(svg_document("Monthly delivered merchandise value (BRL)", "".join(parts), width, height), encoding="utf-8")


def render_heatmap(path: Path, rows: list[dict]) -> None:
    cohorts = sorted({r["cohort_month"] for r in rows})
    max_month = min(12, max(r["month_number"] for r in rows))
    lookup = {(r["cohort_month"], r["month_number"]): r for r in rows}
    cell_w, cell_h, left, top = 58, 21, 160, 75
    parts = []
    for month in range(max_month + 1):
        parts.append(f'<text x="{left+month*cell_w+cell_w/2}" y="65" text-anchor="middle" class="axis">M{month}</text>')
    for row_index, cohort in enumerate(cohorts):
        y = top + row_index * cell_h
        parts.append(f'<text x="150" y="{y+15}" text-anchor="end" class="axis">{cohort[:7]}</text>')
        for month in range(max_month + 1):
            record = lookup.get((cohort, month))
            value = record.get("retention_rate_pct") if record else None
            fill = "#e5e7e9" if value is None else f"rgb({235-int(value*1.35)},{245-int(value*.9)},{250-int(value*.5)})"
            parts.append(f'<rect x="{left+month*cell_w}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" fill="{fill}"/>')
            if value is not None and (month <= 3 or value >= 5):
                parts.append(f'<text x="{left+month*cell_w+cell_w/2-1}" y="{y+14}" text-anchor="middle" class="axis">{value:.1f}</text>')
    parts.append(f'<text x="{left}" y="{top+len(cohorts)*cell_h+24}" class="note">Grey = right-censored / not yet observable. Values are % of acquisition cohort active in the exact month.</text>')
    height = max(620, top + len(cohorts) * cell_h + 55)
    path.write_text(svg_document("Monthly cohort retention (%)", "".join(parts), 1000, height), encoding="utf-8")


def render_pareto(path: Path, rows: list[dict]) -> None:
    top = rows[:20]
    width, height, left, right, top_y, bottom = 1000, 620, 70, 45, 75, 125
    plot_w, plot_h = width-left-right, height-top_y-bottom
    max_value = max(float(r["merchandise_value"]) for r in top)
    step = plot_w / len(top)
    parts = []
    line_points = []
    for i, row in enumerate(top):
        value, cumulative = float(row["merchandise_value"]), float(row["cumulative_share_pct"])
        x, bar_h = left+i*step, plot_h*value/max_value
        parts.append(f'<rect x="{x+2:.1f}" y="{top_y+plot_h-bar_h:.1f}" width="{step-4:.1f}" height="{bar_h:.1f}" fill="#5dade2"/>')
        parts.append(f'<text x="{x+step/2:.1f}" y="{height-bottom+10}" text-anchor="end" transform="rotate(-55 {x+step/2:.1f} {height-bottom+10})" class="axis">{escape(row["category"])}</text>')
        line_points.append(f'{x+step/2:.1f},{top_y+plot_h*(1-cumulative/100):.1f}')
    parts.append(f'<polyline points="{" ".join(line_points)}" fill="none" stroke="#c0392b" stroke-width="3"/>')
    parts.append(f'<line x1="{left}" y1="{top_y+plot_h*.2}" x2="{width-right}" y2="{top_y+plot_h*.2}" stroke="#7f8c8d" stroke-dasharray="5 5"/>')
    parts.append('<text x="920" y="150" class="note">80% cumulative share</text>')
    path.write_text(svg_document("Category Pareto: value bars and cumulative share", "".join(parts), width, height), encoding="utf-8")


def render_delivery_chart(path: Path, timing_rows: list[dict], statistics: dict) -> None:
    by_timing = {r["delivery_timing"]: r for r in timing_rows}
    labels = ["Late", "On time / early"]
    values = [by_timing["late"]["avg_review_score"], by_timing["on_time_or_early"]["avg_review_score"]]
    render_bar_chart(path, "Average order-level review score by delivery timing", labels, values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist.sqlite")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--chart-dir", type=Path, default=CHART_DIR)
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error(f"database not found: {args.database}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.chart_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(f"file:{args.database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        results = execute_phase2(connection)
    finally:
        connection.close()
    for name, rows in results.items():
        write_csv(args.output_dir / f"{name}.csv", rows)
    statistics = calculate_statistics(results)
    (args.output_dir / "statistical_results.json").write_text(
        json.dumps(statistics, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    render_heatmap(args.chart_dir / "cohort_retention_heatmap.svg", results["cohort_retention"])
    render_bar_chart(
        args.chart_dir / "rfm_segment_distribution.svg", "RFM customer segment distribution",
        [r["rfm_segment"] for r in results["rfm_segments"]],
        [float(r["customers"]) for r in results["rfm_segments"]], " customers",
    )
    render_monthly_line(args.chart_dir / "monthly_merchandise_trends.svg", results["monthly_sales"])
    render_pareto(args.chart_dir / "category_pareto.svg", results["category_pareto"])
    render_delivery_chart(args.chart_dir / "delivery_satisfaction.svg", results["delivery_timing"], statistics)
    print(f"Wrote {len(results)} CSV extracts, statistical_results.json, and 5 SVG charts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
