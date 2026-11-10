"""Shared Streamlit presentation primitives and accessibility-minded styling."""

from __future__ import annotations

from html import escape

import streamlit as st

from dashboard.data import DataUnavailable


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&display=swap');
        :root { --ledger-blue:#1d5fbf; --ledger-ink:#141414; --ledger-muted:#60646c; }
        html, body, .stApp, .stApp div, .stApp p, .stApp h1, .stApp h2, .stApp h3,
        .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp select {
          font-family:'Geist', Arial, sans-serif !important;
        }
        .stApp code, .stApp pre { font-family:'Source Code Pro', monospace !important; }
        .stApp span[translate="no"] { font-family:'Material Symbols Rounded' !important; }
        .stApp { background:#f2f4f7; color:#141414; }
        [data-testid="stSidebar"] { background:#f2f4f7; border-right:1px solid #e2e5e9; box-shadow:none !important; }
        [data-testid="stSidebarNav"] span { font-size:14px; }
        .block-container { max-width:1320px; padding-top:3.25rem; padding-bottom:4rem; }
        h1 { font-size:24px !important; line-height:1.25 !important; letter-spacing:-.01em; }
        h2 { font-size:17px !important; margin-top:1.8rem !important; }
        h3 { font-size:15px !important; }
        p, li, label { font-size:14px; line-height:1.55; }
        [data-testid="stMetric"] { background:transparent; }
        [data-testid="stMetricValue"] { font-size:28px; font-variant-numeric:tabular-nums; }
        [data-testid="stMetricLabel"] { color:#60646c; }
        .ledger-brand { padding:4px 6px 18px; border-bottom:1px solid #e2e5e9; margin-bottom:12px; }
        .ledger-mark { width:18px; height:18px; display:inline-grid; place-items:center; border:1px solid #141414; border-radius:50%; font-size:10px; margin-right:8px; }
        .ledger-brand strong { font-size:15px; font-weight:600; }
        .ledger-scope { color:#60646c; font-size:12px; margin:5px 0 0 27px; }
        .page-kicker { color:#60646c; font-size:12px; margin-bottom:4px; }
        .page-finding { font-size:16px; line-height:1.45; margin:.3rem 0 1rem; max-width:900px; }
        .metric-strip { display:grid; grid-template-columns:repeat(var(--metric-count), minmax(0,1fr)); background:#fff; border:1px solid #e4e6e9; border-radius:8px; margin:14px 0 20px; }
        .metric-cell { padding:17px 20px; min-width:0; }
        .metric-cell + .metric-cell { border-left:1px solid #eceef0; }
        .metric-label { color:#60646c; font-size:12px; margin-bottom:7px; }
        .metric-value { font-size:27px; line-height:1.1; font-weight:500; font-variant-numeric:tabular-nums; white-space:nowrap; }
        .metric-note { color:#60646c; font-size:12px; margin-top:7px; }
        .evidence-note { background:#fff; border:1px solid #e4e6e9; border-left:3px solid #1d5fbf; border-radius:6px; padding:13px 15px; margin:12px 0; }
        .evidence-note strong { font-size:13px; }
        .evidence-note p { color:#4e535a; margin:5px 0 0; font-size:13px; }
        .boundary-note { background:#fffbeb; color:#713f12; border:1px solid #fde68a; border-radius:6px; padding:10px 13px; font-size:13px; margin:10px 0 16px; }
        .source-line { color:#60646c; font-size:12px; margin-top:-4px; margin-bottom:12px; }
        .source-line code { color:#30343a; background:#eef0f2; padding:2px 5px; border-radius:4px; font-size:16px !important; }
        div[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #e4e6e9; border-radius:8px; padding:4px; }
        div[data-testid="stDataFrame"] { border:1px solid #e4e6e9; border-radius:8px; overflow:hidden; }
        .stButton button, .stDownloadButton button, a[data-testid="stLinkButton"] { min-height:40px; border-radius:6px; }
        button:focus-visible, a:focus-visible { outline:3px solid rgba(29,95,191,.35) !important; outline-offset:2px; }
        @media (max-width: 900px) {
          .block-container { padding:3.25rem 1rem 3rem; }
          .metric-strip { grid-template-columns:repeat(2,minmax(0,1fr)); }
          .metric-cell:nth-child(odd):not(:first-child) { border-left:0; }
          .metric-cell:nth-child(n+3) { border-top:1px solid #eceef0; }
        }
        @media (max-width: 520px) {
          .metric-strip { grid-template-columns:1fr; }
          .metric-cell + .metric-cell { border-left:0; border-top:1px solid #eceef0; }
          .metric-value { font-size:24px; }
          h1 { font-size:22px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    st.sidebar.markdown(
        '<div class="ledger-brand"><span class="ledger-mark">OE</span><strong>Olist Evidence Lab</strong>'
        '<div class="ledger-scope">Historical marketplace research · 2016–2018</div></div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, question: str, finding: str, source_scope: str) -> None:
    st.markdown(f'<div class="page-kicker">{escape(source_scope)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-finding"><strong>{escape(question)}</strong><br>{escape(finding)}</div>', unsafe_allow_html=True)


def metric_strip(items: list[tuple[str, str, str]]) -> None:
    cells = "".join(
        f'<div class="metric-cell"><div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>'
        for label, value, note in items
    )
    st.markdown(
        f'<div class="metric-strip" style="--metric-count:{len(items)}">{cells}</div>',
        unsafe_allow_html=True,
    )


def evidence_note(title: str, body: str) -> None:
    st.markdown(
        f'<div class="evidence-note"><strong>{escape(title)}</strong><p>{escape(body)}</p></div>',
        unsafe_allow_html=True,
    )


def boundary_note(text: str) -> None:
    st.markdown(f'<div class="boundary-note">{escape(text)}</div>', unsafe_allow_html=True)


def source_caption(grain: str, observation: str, source: str, source_url: str) -> None:
    st.markdown(
        f'<div class="source-line">Grain: {escape(grain)} · Observation: {escape(observation)} · '
        f'<a href="{escape(source_url)}" target="_blank">SQL / code evidence</a> · <code>{escape(source)}</code></div>',
        unsafe_allow_html=True,
    )


def render_data_error(error: Exception) -> None:
    if isinstance(error, DataUnavailable):
        st.error("Verified aggregate outputs are not available yet.", icon=None)
        st.code("python3 scripts/phase2_analysis.py\npython3 scripts/build_analytics_mart.py\npython3 scripts/phase25_research.py", language="bash")
        st.caption(str(error))
    else:
        st.error("A checked-in dashboard asset failed its data contract.", icon=None)
        st.code(str(error))


def format_brl(value: float) -> str:
    return f"BRL {value:,.2f}"


def format_int(value: int | float) -> str:
    return f"{int(value):,}"


def format_pct(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}%"
