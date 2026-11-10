"""Plotly figures with a restrained, shared visual grammar."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go

INK = "#141414"
MUTED = "#7a7d82"
BLUE = "#1d5fbf"
GRID = "#e7e9ec"
PAPER = "rgba(0,0,0,0)"


def _layout(fig: go.Figure, *, height: int, title: str, y_title: str = "", x_title: str = "") -> go.Figure:
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": INK}, "x": 0.02, "xanchor": "left"},
        height=height, margin={"l": 62, "r": 26, "t": 58, "b": 54},
        paper_bgcolor=PAPER, plot_bgcolor="#ffffff", showlegend=False,
        font={"family": "Geist, Arial, sans-serif", "size": 12, "color": INK},
        hoverlabel={"bgcolor": "#ffffff", "bordercolor": "#d9dce0", "font": {"color": INK}},
    )
    fig.update_xaxes(title=x_title, showline=True, linecolor=GRID, gridcolor="rgba(0,0,0,0)", tickfont={"color": MUTED})
    fig.update_yaxes(title=y_title, showline=False, gridcolor=GRID, gridwidth=1, zeroline=True, zerolinecolor="#c9ccd1", tickfont={"color": MUTED})
    return fig


def monthly_trend(frame: pd.DataFrame) -> go.Figure:
    data = frame.copy()
    data["purchase_month"] = pd.to_datetime(data["purchase_month"])
    fig = go.Figure(go.Scatter(
        x=data["purchase_month"], y=data["merchandise_value"], mode="lines",
        line={"color": BLUE, "width": 2},
        customdata=data[["delivered_orders", "avg_merchandise_value_per_order", "observation_status"]],
        hovertemplate="%{x|%b %Y}<br>Merchandise: BRL %{y:,.2f}<br>Orders: %{customdata[0]:,.0f}<br>Average/order: BRL %{customdata[1]:,.2f}<br>Status: %{customdata[2]}<extra></extra>",
    ))
    sparse = data[data["observation_status"] != "complete_or_well_represented"]
    fig.add_trace(go.Scatter(x=sparse["purchase_month"], y=sparse["merchandise_value"], mode="markers", marker={"color": "#92400e", "size": 8, "symbol": "diamond"}, hoverinfo="skip"))
    fig.update_xaxes(dtick="M3", tickformat="%b\n%Y")
    return _layout(fig, height=330, title="Delivered merchandise value by purchase month", y_title="BRL")


def category_pareto(frame: pd.DataFrame, top_n: int = 20) -> go.Figure:
    data = frame.head(top_n).copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data["category"], y=data["merchandise_value"], marker_color="#d9dde2", hovertemplate="%{x}<br>BRL %{y:,.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=data["category"], y=data["cumulative_share_pct"], yaxis="y2", mode="lines", line={"color": BLUE, "width": 2}, hovertemplate="%{x}<br>Cumulative %{y:.2f}%<extra></extra>"))
    fig.update_layout(yaxis2={"overlaying": "y", "side": "right", "range": [0, 100], "ticksuffix": "%", "showgrid": False, "title": "Cumulative share"})
    fig.update_xaxes(tickangle=0, tickmode="array", tickvals=data["category"][::3], ticktext=data["category"][::3])
    return _layout(fig, height=360, title=f"Category Pareto · top {top_n}", y_title="Merchandise value (BRL)")


def cohort_heatmap(frame: pd.DataFrame, max_month: int = 12) -> go.Figure:
    data = frame[frame["month_number"] <= max_month].copy()
    data["cohort"] = pd.to_datetime(data["cohort_month"]).dt.strftime("%Y-%m")
    pivot = data.pivot(index="cohort", columns="month_number", values="retention_rate_pct")
    # M0 is 100% by construction. Scale later-month retention separately so
    # genuine variation remains legible while M0 simply saturates the palette.
    later_values = data.loc[data["month_number"] > 0, "retention_rate_pct"].dropna()
    scale_max = max(1.0, float(later_values.quantile(.95))) if not later_values.empty else 1.0
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=[f"M{int(x)}" for x in pivot.columns], y=pivot.index,
        colorscale=[[0, "#f0f2f4"], [0.2, "#c9d7ed"], [1, BLUE]], zmin=0, zmax=scale_max,
        colorbar={"title": "% retained", "thickness": 10},
        hovertemplate="Cohort %{y}<br>Offset %{x}<br>Retention %{z:.2f}%<extra></extra>",
        xgap=1, ygap=1,
    ))
    return _layout(fig, height=520, title="Exact-month retention · grey gaps are right-censored", y_title="Acquisition cohort")


def rfm_distribution(frame: pd.DataFrame) -> go.Figure:
    data = frame.sort_values("customers", ascending=True)
    fig = go.Figure(go.Bar(
        x=data["customers"], y=data["rfm_segment"], orientation="h", marker_color=BLUE,
        customdata=data[["customer_share_pct", "merchandise_share_pct"]],
        hovertemplate="%{y}<br>Customers %{x:,.0f} (%{customdata[0]:.2f}%)<br>Merchandise share %{customdata[1]:.2f}%<extra></extra>",
    ))
    return _layout(fig, height=360, title="RFM customer distribution · snapshot 2018-09-01", x_title="Customers")


def km_curve(frame: pd.DataFrame) -> go.Figure:
    data = frame.sort_values("horizon_days")
    x = data["horizon_days"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=data["repeat_ci_95_high"] * 100, mode="lines", line={"width": 0}, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=x, y=data["repeat_ci_95_low"] * 100, mode="lines", line={"width": 0}, fill="tonexty", fillcolor="rgba(29,95,191,.14)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=x, y=data["repeat_cumulative_incidence"] * 100, mode="lines", line={"color": BLUE, "width": 2}, customdata=data[["repeat_ci_95_low", "repeat_ci_95_high"]] * 100, hovertemplate="Day %{x:.0f}<br>Repeat incidence %{y:.2f}%<br>95% CI %{customdata[0]:.2f}–%{customdata[1]:.2f}%<extra></extra>"))
    return _layout(fig, height=330, title="Second observed delivered purchase · Kaplan–Meier", x_title="Days since first observed purchase", y_title="Cumulative incidence (%)")


def ranked_late_rates(frame: pd.DataFrame, label: str, minimum_orders: int = 500, top_n: int = 12) -> go.Figure:
    data = frame[frame["timing_eligible_orders"] >= minimum_orders].nlargest(top_n, "late_delivery_rate_pct").sort_values("late_delivery_rate_pct")
    fig = go.Figure(go.Bar(x=data["late_delivery_rate_pct"], y=data[label], orientation="h", marker_color=BLUE, customdata=data[["timing_eligible_orders", "late_orders"]], hovertemplate="%{y}<br>Late %{x:.2f}%<br>Eligible %{customdata[0]:,.0f}<br>Late orders %{customdata[1]:,.0f}<extra></extra>"))
    return _layout(fig, height=380, title=f"Highest late-delivery rates · minimum {minimum_orders:,} orders", x_title="Late-delivery rate (%)")


def association_forest(delivery_timing: pd.DataFrame, research: dict) -> go.Figure:
    timing = delivery_timing.set_index("delivery_timing")
    late, ontime = timing.loc["late"], timing.loc["on_time_or_early"]
    a, b = float(late["low_review_orders"]), float(late["reviewed_orders"] - late["low_review_orders"])
    c, d = float(ontime["low_review_orders"]), float(ontime["reviewed_orders"] - ontime["low_review_orders"])
    raw_or = a * d / (b * c)
    se = math.sqrt(1/a + 1/b + 1/c + 1/d)
    adjusted = research["delivery_satisfaction"]["primary_adjusted_model"]
    labels = ["Unadjusted order-level", "Adjusted logistic model"]
    values = [raw_or, adjusted["late_odds_ratio"]]
    lows = [math.exp(math.log(raw_or)-1.95996398454*se), adjusted["late_or_ci_95_low"]]
    highs = [math.exp(math.log(raw_or)+1.95996398454*se), adjusted["late_or_ci_95_high"]]
    fig = go.Figure(go.Scatter(x=values, y=labels, mode="markers", marker={"color": BLUE, "size": 9}, error_x={"type": "data", "symmetric": False, "array": [h-v for h,v in zip(highs,values)], "arrayminus": [v-l for v,l in zip(values,lows)], "color": INK, "thickness": 1.5}, hovertemplate="%{y}<br>Odds ratio %{x:.2f}<extra></extra>"))
    fig.add_vline(x=1, line_width=1, line_dash="dash", line_color=MUTED)
    fig.update_xaxes(type="log", range=[0, math.log10(max(highs) * 1.18)])
    return _layout(fig, height=260, title="Low-review association · late versus on-time/early", x_title="Odds ratio (log scale)")


def heterogeneity_chart(research: dict) -> go.Figure:
    rows = pd.DataFrame(research["delivery_satisfaction"]["heterogeneity"])
    labels = rows["subgroup_type"].str.title()
    fig = go.Figure(go.Bar(x=labels, y=rows["i_squared"] * 100, marker_color=BLUE, customdata=rows[["q", "df", "p_value", "included_groups"]], hovertemplate="%{x}<br>I² %{y:.1f}%<br>Q %{customdata[0]:.2f}, df %{customdata[1]}<br>Groups %{customdata[3]}<extra></extra>"))
    fig.add_hline(y=75, line_dash="dash", line_color=MUTED, annotation_text="High heterogeneity reference")
    return _layout(fig, height=300, title="Exploratory subgroup heterogeneity", y_title="I² (%)")
