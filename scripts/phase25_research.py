#!/usr/bin/env python3
"""Run Phase 2.5 repeat-purchase and delivery-satisfaction research."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
import sys
from collections import defaultdict
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from scripts.run_analysis import iter_statements

Z975 = 1.959963984540054
OUTPUT_DIR = PROJECT_ROOT / "reports" / "phase25_outputs"
CHART_DIR = PROJECT_ROOT / "visualizations"


def kaplan_meier(records: list[dict], horizons: list[int]) -> list[dict]:
    """Estimate repeat cumulative incidence with administrative right censoring."""
    grouped: dict[float, list[int]] = defaultdict(lambda: [0, 0])
    for row in records:
        grouped[float(row["observed_days"])][0 if int(row["repeat_event"]) else 1] += 1
    at_risk, survival, greenwood = len(records), 1.0, 0.0
    timeline = []
    for time in sorted(grouped):
        events, censored = grouped[time]
        if events:
            survival *= 1.0 - events / at_risk
            if at_risk > events:
                greenwood += events / (at_risk * (at_risk - events))
        timeline.append((time, survival, greenwood, at_risk, events, censored))
        at_risk -= events + censored
    output = []
    for horizon in horizons:
        eligible = [row for row in timeline if row[0] <= horizon]
        if eligible:
            _, survival, variance_term, risk, events, _ = eligible[-1]
        else:
            survival, variance_term, risk, events = 1.0, 0.0, len(records), 0
        if 0.0 < survival < 1.0 and variance_term > 0:
            loglog = math.log(-math.log(survival))
            se = math.sqrt(variance_term) / abs(math.log(survival))
            survival_low = math.exp(-math.exp(loglog + Z975 * se))
            survival_high = math.exp(-math.exp(loglog - Z975 * se))
        else:
            survival_low = survival_high = survival
        output.append({
            "horizon_days": horizon, "customers": len(records), "survival_no_second_purchase": survival,
            "repeat_cumulative_incidence": 1.0 - survival,
            "repeat_ci_95_low": 1.0 - survival_high, "repeat_ci_95_high": 1.0 - survival_low,
            "risk_set_at_last_event_or_censor": risk, "events_at_last_time": events,
        })
    return output


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda r: abs(augmented[r][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise RuntimeError("singular information matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        for j in range(column, size + 1):
            augmented[column][j] /= scale
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                for j in range(column, size + 1):
                    augmented[row][j] -= factor * augmented[column][j]
    return [augmented[i][-1] for i in range(size)]


def invert_matrix(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    columns = []
    for column in range(size):
        unit = [0.0] * size
        unit[column] = 1.0
        columns.append(solve_linear(matrix, unit))
    return [[columns[j][i] for j in range(size)] for i in range(size)]


def sigmoid(value: float) -> float:
    if value >= 0:
        exp_neg = math.exp(-min(value, 700))
        return 1.0 / (1.0 + exp_neg)
    exp_value = math.exp(max(value, -700))
    return exp_value / (1.0 + exp_value)


def prepare_design(rows: list[dict]) -> tuple[list[str], list[tuple[list[int], int, int]], dict]:
    fields = ["purchase_month", "customer_state", "category_group", "value_band"]
    levels = {field: sorted({str(row[field]) for row in rows}) for field in fields}
    names = ["intercept", "late"]
    indexes = {}
    for field in fields:
        for level in levels[field][1:]:
            indexes[(field, level)] = len(names)
            names.append(f"{field}={level}")
    single_levels = sorted({int(row["single_seller"]) for row in rows})
    if len(single_levels) > 1:
        indexes[("single_seller", "1")] = len(names)
        names.append("single_seller=1")
    designs = []
    for row in rows:
        active = [0]
        if int(row["is_late"]):
            active.append(1)
        for field in fields:
            index = indexes.get((field, str(row[field])))
            if index is not None:
                active.append(index)
        if int(row["single_seller"]) and ("single_seller", "1") in indexes:
            active.append(indexes[("single_seller", "1")])
        designs.append((active, int(row["reviewed_orders"]), 0))
    return names, designs, indexes


def fit_grouped_logistic(rows: list[dict], outcome: str = "low_reviews") -> dict:
    names, base_designs, _ = prepare_design(rows)
    designs = [(active, total, int(row[outcome])) for (active, total, _), row in zip(base_designs, rows)]
    size, beta = len(names), [0.0] * len(names)
    total_events = sum(y for _, _, y in designs)
    total_orders = sum(n for _, n, _ in designs)
    beta[0] = math.log((total_events + 0.5) / (total_orders - total_events + 0.5))
    converged = False
    for iteration in range(1, 61):
        information = [[0.0] * size for _ in range(size)]
        score = [0.0] * size
        for active, total, events in designs:
            probability = min(max(sigmoid(sum(beta[i] for i in active)), 1e-9), 1 - 1e-9)
            weight = total * probability * (1 - probability)
            residual = events - total * probability
            for i in active:
                score[i] += residual
                for j in active:
                    information[i][j] += weight
        for i in range(1, size):
            information[i][i] += 1e-7
        delta = solve_linear(information, score)
        beta = [value + change for value, change in zip(beta, delta)]
        if max(abs(change) for change in delta) < 1e-8:
            converged = True
            break
    covariance = invert_matrix(information)
    late_se = math.sqrt(max(covariance[1][1], 0.0))
    predictions = []
    brier_sum = 0.0
    for active, total, events in designs:
        probability = sigmoid(sum(beta[i] for i in active))
        predictions.append((probability, total, events))
        brier_sum += events * (1 - probability) ** 2 + (total - events) * probability ** 2
    # Exact grouped AUC with half-credit for tied predicted probabilities.
    grouped_predictions = defaultdict(lambda: [0, 0])
    for probability, total, events in predictions:
        grouped_predictions[round(probability, 14)][0] += events
        grouped_predictions[round(probability, 14)][1] += total - events
    concordant = cumulative_negatives = 0.0
    for probability in sorted(grouped_predictions):
        positives, negatives = grouped_predictions[probability]
        concordant += positives * cumulative_negatives + 0.5 * positives * negatives
        cumulative_negatives += negatives
    auc = concordant / (total_events * (total_orders - total_events))
    # Standardize late/on-time risks over the empirical covariate distribution.
    risk_late = risk_on_time = 0.0
    gradient = [0.0] * size
    for (active, total, _), row in zip(designs, rows):
        without_late = [i for i in active if i != 1]
        with_late = without_late + [1]
        p1 = sigmoid(sum(beta[i] for i in with_late))
        p0 = sigmoid(sum(beta[i] for i in without_late))
        weight = total / total_orders
        risk_late += weight * p1
        risk_on_time += weight * p0
        for i in with_late:
            gradient[i] += weight * p1 * (1 - p1)
        for i in without_late:
            gradient[i] -= weight * p0 * (1 - p0)
    rd = risk_late - risk_on_time
    rd_variance = sum(gradient[i] * covariance[i][j] * gradient[j] for i in range(size) for j in range(size))
    rd_se = math.sqrt(max(rd_variance, 0.0))
    return {
        "outcome": outcome, "reviewed_orders": total_orders, "events": total_events,
        "parameters": size, "iterations": iteration, "converged": converged,
        "late_log_odds_coefficient": beta[1], "late_odds_ratio": math.exp(beta[1]),
        "late_or_ci_95_low": math.exp(beta[1] - Z975 * late_se),
        "late_or_ci_95_high": math.exp(beta[1] + Z975 * late_se),
        "standardized_late_risk": risk_late, "standardized_on_time_risk": risk_on_time,
        "standardized_risk_difference": rd,
        "risk_difference_ci_95_low": rd - Z975 * rd_se,
        "risk_difference_ci_95_high": rd + Z975 * rd_se,
        "auc": auc, "brier_score": brier_sum / total_orders,
        "reference_levels": {
            field: sorted({str(row[field]) for row in rows})[0]
            for field in ("purchase_month", "customer_state", "category_group", "value_band")
        },
        "coefficient_names": names,
    }


def gammaincc(a: float, x: float) -> float:
    if x <= 0:
        return 1.0
    if x < a + 1:
        term = total = 1.0 / a
        ap = a
        for _ in range(500):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
        lower = total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return max(0.0, 1.0 - lower)
    b = x + 1 - a
    c, d, h = 1e300, 1 / b, 1 / b
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-300: d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300: c = 1e-300
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-14: break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def heterogeneity(rows: list[dict], subgroup_type: str, minimum_per_timing: int = 20) -> dict:
    estimates = []
    for row in rows:
        if row["subgroup_type"] != subgroup_type:
            continue
        n1, a, n0, c = (int(row[k]) for k in ("late_reviewed", "late_low", "on_time_reviewed", "on_time_low"))
        if n1 < minimum_per_timing or n0 < minimum_per_timing:
            continue
        b, d = n1 - a, n0 - c
        a, b, c, d = (value + 0.5 if min(a, b, c, d) == 0 else value for value in (a, b, c, d))
        log_or = math.log(a * d / (b * c))
        variance = 1 / a + 1 / b + 1 / c + 1 / d
        estimates.append((row["subgroup_value"], log_or, variance))
    weights = [1 / variance for _, _, variance in estimates]
    pooled = sum(w * estimate[1] for w, estimate in zip(weights, estimates)) / sum(weights)
    q = sum(w * (estimate[1] - pooled) ** 2 for w, estimate in zip(weights, estimates))
    df = len(estimates) - 1
    return {"subgroup_type": subgroup_type, "included_groups": len(estimates), "q": q, "df": df,
            "p_value": gammaincc(df / 2, q / 2) if df > 0 else 1.0,
            "i_squared": max(0.0, (q - df) / q) if q else 0.0,
            "minimum_orders_per_timing_group": minimum_per_timing}


def missing_review_bounds(rows: list[dict]) -> dict:
    groups = {int(row["is_late"]): row for row in rows}
    late, ontime = groups[1], groups[0]
    lt, lr, ll = (int(late[k]) for k in ("timing_eligible_orders", "reviewed_orders", "observed_low_reviews"))
    ot, or_, ol = (int(ontime[k]) for k in ("timing_eligible_orders", "reviewed_orders", "observed_low_reviews"))
    observed = ll / lr - ol / or_
    minimum = ll / lt - (ol + ot - or_) / ot
    maximum = (ll + lt - lr) / lt - ol / ot
    return {"observed_risk_difference": observed, "worst_case_minimum": minimum,
            "worst_case_maximum": maximum, "late_missing_reviews": lt - lr,
            "on_time_missing_reviews": ot - or_}


def rfm_stability(rows: list[dict]) -> dict:
    by_cutoff = defaultdict(dict)
    for row in rows:
        by_cutoff[row["cutoff"]][row["customer_unique_id"]] = row["rfm_segment"]
    cutoffs = sorted(by_cutoff)
    common = sorted(set(by_cutoff[cutoffs[0]]) & set(by_cutoff[cutoffs[1]]))
    agreement = sum(by_cutoff[cutoffs[0]][customer] == by_cutoff[cutoffs[1]][customer] for customer in common)
    labels = sorted(set(by_cutoff[cutoffs[0]].values()) | set(by_cutoff[cutoffs[1]].values()))
    p_expected = sum(
        sum(by_cutoff[cutoffs[0]][c] == label for c in common) / len(common)
        * sum(by_cutoff[cutoffs[1]][c] == label for c in common) / len(common)
        for label in labels
    )
    observed = agreement / len(common)
    return {"earlier_cutoff": cutoffs[0], "later_cutoff": cutoffs[1], "common_customers": len(common),
            "exact_segment_agreement": observed, "cohen_kappa": (observed - p_expected) / (1 - p_expected)}


def execute_sql(database: Path, filename: str) -> list[list[dict]]:
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        sql = (PROJECT_ROOT / "sql" / "analysis" / filename).read_text(encoding="utf-8")
        return [[dict(row) for row in connection.execute(statement).fetchall()] for statement in iter_statements(sql)]
    finally:
        connection.close()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)


def render_km(path: Path, cutoff_results: dict[str, list[dict]]) -> None:
    colors = ["#1f77b4", "#d35400", "#2e8b57"]
    parts = ['<rect width="100%" height="100%" fill="#fbfaf7"/>',
             '<text x="55" y="38" font-family="Arial" font-size="24" font-weight="700">Repeat-purchase cumulative incidence</text>']
    for color, (cutoff, rows) in zip(colors, sorted(cutoff_results.items())):
        points = " ".join(f'{90 + (r["horizon_days"]/365)*820:.1f},{540-r["repeat_cumulative_incidence"]*9000:.1f}' for r in rows)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="720" y="{75+colors.index(color)*22}" font-family="Arial" font-size="13" fill="{color}">{escape(cutoff[:10])}</text>')
    parts.append('<text x="90" y="580" font-family="Arial" font-size="12">Days since first observed delivered purchase; curves are administratively censored at each cutoff.</text>')
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620">'+''.join(parts)+'</svg>', encoding="utf-8")


def render_delivery(path: Path, models: list[tuple[str, dict]]) -> None:
    parts = ['<rect width="100%" height="100%" fill="#fbfaf7"/>',
             '<text x="55" y="38" font-family="Arial" font-size="24" font-weight="700">Adjusted late-delivery odds ratios</text>']
    for index, (label, model) in enumerate(models):
        y = 120 + index * 105
        scale = 55
        x = 100 + math.log(model["late_odds_ratio"]) * scale
        low = 100 + math.log(model["late_or_ci_95_low"]) * scale
        high = 100 + math.log(model["late_or_ci_95_high"]) * scale
        parts.extend([f'<text x="90" y="{y-18}" font-family="Arial" font-size="14">{escape(label)}</text>',
                      f'<line x1="{low:.1f}" y1="{y}" x2="{high:.1f}" y2="{y}" stroke="#2874a6" stroke-width="4"/>',
                      f'<circle cx="{x:.1f}" cy="{y}" r="7" fill="#c0392b"/>',
                      f'<text x="{high+12:.1f}" y="{y+5}" font-family="Arial" font-size="13">OR {model["late_odds_ratio"]:.2f}</text>'])
    parts.append('<text x="55" y="590" font-family="Arial" font-size="12">95% model-based CI; observational association, not a causal effect.</text>')
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620">'+''.join(parts)+'</svg>', encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist.sqlite")
    parser.add_argument("--mart", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist_analytics.sqlite")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--chart-dir", type=Path, default=CHART_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True); args.chart_dir.mkdir(parents=True, exist_ok=True)
    primary_repeat, cutoff_repeat, rfm_rows = execute_sql(args.source, "09_repeat_purchase_research.sql")
    model_rows, missing_rows, subgroup_rows = execute_sql(args.mart, "10_delivery_satisfaction_research.sql")
    horizons = [30, 60, 90, 180, 365]
    primary_km = kaplan_meier(primary_repeat, horizons)
    sensitivity = {}
    for cutoff in sorted({row["cutoff"] for row in cutoff_repeat}):
        sensitivity[cutoff] = kaplan_meier([row for row in cutoff_repeat if row["cutoff"] == cutoff], horizons)
    primary_model = fit_grouped_logistic(model_rows)
    single_model = fit_grouped_logistic([row for row in model_rows if int(row["single_seller"]) == 1])
    score_one_model = fit_grouped_logistic(model_rows, "score_one_reviews")
    results = {
        "repeat_purchase": {"primary_cutoff": "2018-09-01 00:00:00", "primary_km": primary_km,
                            "cutoff_sensitivity": sensitivity, "rfm_stability": rfm_stability(rfm_rows)},
        "delivery_satisfaction": {"primary_adjusted_model": primary_model,
            "single_seller_sensitivity": single_model, "score_one_sensitivity": score_one_model,
            "missing_review_bounds": missing_review_bounds(missing_rows),
            "heterogeneity": [heterogeneity(subgroup_rows, dimension) for dimension in ("month", "state", "category")]},
    }
    (args.output_dir / "research_results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(args.output_dir / "repeat_km_primary.csv", primary_km)
    write_csv(args.output_dir / "delivery_model_population.csv", model_rows)
    write_csv(args.output_dir / "delivery_subgroup_tables.csv", subgroup_rows)
    render_km(args.chart_dir / "phase25_repeat_km.svg", sensitivity)
    render_delivery(args.chart_dir / "phase25_adjusted_delivery.svg",
                    [("Primary low review", primary_model), ("Single-seller orders", single_model), ("Score = 1", score_one_model)])
    print(f"Wrote Phase 2.5 research outputs for {len(primary_repeat):,} customers and {primary_model['reviewed_orders']:,} reviewed orders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
