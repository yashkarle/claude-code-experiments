"""
app.py — NRI Portfolio Withdrawal Planner
Streamlit web app with PyMC-backed probabilistic forecasts.

Run: streamlit run portfolio_app/app.py
"""
from __future__ import annotations

import datetime
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import arviz as az
from plotly.subplots import make_subplots

from portfolio import (
    DEFAULT_PORTFOLIO,
    FundHolding,
    Portfolio,
    TaxState,
    compute_portfolio_withdrawal_tax,
    compute_todays_recommendation,
    projected_gain_ratio,
    suggest_proportional_split,
)
from data_sources import INDEX_TICKERS, load_history_for_funds
from factor_model import (
    build_factor_model,
    compute_percentile_bands,
    current_factor_regime,
    generate_factor_forecast,
    prepare_training_data,
    run_factor_inference,
)
from withdrawal_planner import (
    ExitTimingRecord,
    build_exit_timing_table,
    recommend_today,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Portfolio Withdrawal Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .rec-box { border-radius:8px; padding:16px 20px; margin-bottom:8px; }
    .act-now  { background:#d4edda; border-left:5px solid #28a745; }
    .consider { background:#fff3cd; border-left:5px solid #ffc107; }
    .wait     { background:#e9ecef; border-left:5px solid #6c757d; }
    .rec-title { font-size:1.3rem; font-weight:700; margin-bottom:4px; }
    .metric-label { font-size:0.75rem; color:#6c757d; }
    .metric-value { font-size:1.5rem; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — Portfolio Inputs
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Portfolio Inputs")
    st.caption("Edit to match your current Scripbox holdings.")

    st.subheader("Parag Parikh Flexi Cap")
    pp_inv = st.number_input(
        "Invested (₹)", value=903_555.0, step=1000.0, format="%.0f", key="pp_inv"
    )
    pp_cur = st.number_input(
        "Current Value (₹)", value=1_396_100.0, step=1000.0, format="%.0f", key="pp_cur"
    )

    st.subheader("ICICI Pru Large Cap")
    ic_inv = st.number_input(
        "Invested (₹)", value=674_966.0, step=1000.0, format="%.0f", key="ic_inv"
    )
    ic_cur = st.number_input(
        "Current Value (₹)", value=976_571.0, step=1000.0, format="%.0f", key="ic_cur"
    )

    st.subheader("Tax State (FY 26-27)")
    already_realized = st.number_input(
        "LTCG already realised this FY (₹)",
        value=0.0,
        step=1000.0,
        format="%.0f",
        key="already_realized",
        help="Enter any LTCG realised since Apr 1, 2026.",
    )

    st.divider()
    refresh = st.button("🔄 Refresh Model", use_container_width=True)
    if refresh:
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# ---------------------------------------------------------------------------
# Build Portfolio object
# ---------------------------------------------------------------------------

portfolio = Portfolio(
    funds=[
        FundHolding(
            name="Parag Parikh Flexi Cap",
            invested=pp_inv,
            current_value=pp_cur,
            scheme_code=122639,
        ),
        FundHolding(
            name="ICICI Pru Large Cap",
            invested=ic_inv,
            current_value=ic_cur,
            scheme_code=120586,
        ),
    ],
    tax_state=TaxState(fy_exemption_limit=125_000.0, already_realized=already_realized),
    as_of_date=datetime.date.today(),
)

fund_names = [f.name for f in portfolio.funds]
current_values = np.array([f.current_value for f in portfolio.funds])
scheme_codes = {f.name: f.scheme_code for f in portfolio.funds}

# ---------------------------------------------------------------------------
# Phase 1: load historical NAV + factor data (cached parquet under .cache/)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_history(_schemes_key: str):
    """Load NAV + factor history. Keyed by a string of sorted scheme codes."""
    schemes = dict(code.split("=") for code in _schemes_key.split(","))
    schemes = {k: int(v) for k, v in schemes.items()}
    return load_history_for_funds(schemes, lookback_years=5)


schemes_key = ",".join(f"{n}={c}" for n, c in sorted(scheme_codes.items()))

with st.spinner("Fetching NAV + market factor history (first load ~20s)…"):
    nav_df, factors_df = get_history(schemes_key)

# ---------------------------------------------------------------------------
# Phase 2: prepare training data + Bayesian factor inference
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_factor_idata(_schemes_key: str, _nrows: int):
    """Build + sample the factor model. Keyed by scheme codes and row count."""
    fund_returns, factor_returns = prepare_training_data(nav_df, factors_df)
    model = build_factor_model(
        fund_names=list(fund_returns.columns),
        fund_returns=fund_returns.values,
        factor_returns=factor_returns.values,
    )
    return run_factor_inference(model)


with st.spinner("Fitting Bayesian factor model (first load ~60–120s)…"):
    idata = get_factor_idata(schemes_key, len(nav_df))
    st.session_state["_cached_idata"] = idata

# ---------------------------------------------------------------------------
# Two horizons: long (36 months, trajectory/tax/scenarios) + short (≤60 business
# days, Withdrawal Planner). Both use the factor model; block bootstrap just
# changes n_business_days.
# ---------------------------------------------------------------------------

N_BDAYS_LONG = 252 * 3        # ~3 years


@st.cache_data(show_spinner=False)
def get_long_forecast(_schemes_key: str, _cur_tuple: tuple):
    fund_returns, factor_returns = prepare_training_data(nav_df, factors_df)
    paths = generate_factor_forecast(
        idata=st.session_state["_cached_idata"],
        fund_names=fund_names,
        factor_returns_history=factor_returns.values,
        current_values=np.array(_cur_tuple),
        n_business_days=N_BDAYS_LONG,
        n_samples=2000,
        block_size=15,
        random_seed=42,
    )
    return paths, compute_percentile_bands(paths)


@st.cache_data(show_spinner=False)
def get_short_forecast(_schemes_key: str, _cur_tuple: tuple, _n_bdays: int):
    fund_returns, factor_returns = prepare_training_data(nav_df, factors_df)
    paths = generate_factor_forecast(
        idata=st.session_state["_cached_idata"],
        fund_names=fund_names,
        factor_returns_history=factor_returns.values,
        current_values=np.array(_cur_tuple),
        n_business_days=_n_bdays,
        n_samples=3000,
        block_size=5,
        random_seed=99,
    )
    return paths, compute_percentile_bands(paths)


cur_tuple = tuple(current_values)
long_paths, long_bands = get_long_forecast(schemes_key, cur_tuple)

# Long-horizon business-day index → monthly date labels for Tab 1/3/4.
# We downsample from N_BDAYS_LONG to a monthly cadence by picking every ~21 bdays.
today = datetime.date.today()
long_bdays = pd.bdate_range(today, periods=N_BDAYS_LONG + 1)[1:]
long_month_idx = np.arange(0, N_BDAYS_LONG, 21)
long_date_labels = [long_bdays[int(i)].strftime("%b %Y") for i in long_month_idx]

# For Tab 1, use the downsampled monthly points; reuse `bands` name to minimise churn below.
bands = {
    k: {pct: v[long_month_idx] for pct, v in bnd.items()}
    for k, bnd in long_bands.items()
}
paths = {k: v[:, long_month_idx] for k, v in long_paths.items()}
date_labels = long_date_labels
months_idx = np.arange(1, len(date_labels) + 1)
N_MONTHS = len(date_labels)
fy_boundaries = portfolio.fy_boundary_months(N_MONTHS)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("NRI Portfolio Withdrawal Planner")
st.caption(
    f"As of {today.strftime('%d %b %Y')} · Bayesian Monte Carlo (PyMC v5) · "
    f"FY 2026-27 · LTCG exemption ₹1,25,000"
)

# Summary metrics
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Value", f"₹{portfolio.total_current_value:,.0f}")
m2.metric("Total Invested", f"₹{portfolio.total_invested:,.0f}")
m3.metric(
    "Unrealised Gain",
    f"₹{portfolio.total_unrealized_gain:,.0f}",
    delta=f"{portfolio.blended_gain_ratio*100:.1f}% gain ratio",
)
m4.metric(
    "FY Exemption Left",
    f"₹{portfolio.tax_state.remaining_exemption:,.0f}",
    delta=f"of ₹{portfolio.tax_state.fy_exemption_limit:,.0f}",
)
m5.metric(
    "Months to FY End",
    f"{portfolio.months_to_next_fy()}",
    delta="until Apr 1 reset",
)

st.divider()

# ---------------------------------------------------------------------------
# Today's Recommendation (no target amount here — shown with target in Tab 2)
# ---------------------------------------------------------------------------

rec = compute_todays_recommendation(portfolio)
css_class = {"ACT NOW": "act-now", "CONSIDER": "consider", "WAIT": "wait"}[rec["action"]]
emoji = {"ACT NOW": "🟢", "CONSIDER": "🟡", "WAIT": "⚪"}[rec["action"]]

reasons_html = "".join(f"<li>{r}</li>" for r in rec["reasons"])
st.markdown(
    f"""
    <div class="rec-box {css_class}">
      <div class="rec-title">{emoji} {rec["action"]}</div>
      <div>{rec["headline"]}</div>
      <ul style="margin-top:8px;margin-bottom:0">{reasons_html}</ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Portfolio Trajectory",
        "💰 Withdrawal Planner",
        "🧾 Tax Impact",
        "🌐 Scenarios",
    ]
)

# ============================================================
# TAB 1 — Portfolio Trajectory (probabilistic area chart)
# ============================================================

with tab1:
    st.subheader("Fund-Level Growth Forecast — 80% Credible Band")
    st.caption(
        "Shaded band = 10th–90th percentile of 2,000 Bayesian factor-model paths "
        "(historical NAV calibrated against NIFTY, SENSEX, VIX, gold, USD/INR, crude). "
        "Dashed orange lines mark FY start (Apr 1)."
    )

    COLORS = {
        "Parag Parikh Flexi Cap": ("rgba(31,119,180,0.15)", "rgb(31,119,180)"),
        "ICICI Pru Large Cap": ("rgba(44,160,44,0.15)", "rgb(44,160,44)"),
    }

    fig1 = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=["Parag Parikh Flexi Cap", "ICICI Pru Large Cap"],
        vertical_spacing=0.10,
    )

    for row_idx, fund_name in enumerate(fund_names, start=1):
        fill_color, line_color = COLORS[fund_name]
        b = bands[fund_name]
        # p10 invisible base for fill
        fig1.add_trace(
            go.Scatter(
                x=date_labels, y=b["p10"],
                mode="lines", line=dict(width=0),
                showlegend=False, hoverinfo="skip", name="p10",
            ),
            row=row_idx, col=1,
        )
        # p90 fills down to p10
        fig1.add_trace(
            go.Scatter(
                x=date_labels, y=b["p90"],
                mode="lines", line=dict(width=0),
                fill="tonexty", fillcolor=fill_color,
                showlegend=row_idx == 1,
                name="80% credible band",
                hoverinfo="skip",
            ),
            row=row_idx, col=1,
        )
        # p50 median
        fig1.add_trace(
            go.Scatter(
                x=date_labels, y=b["p50"],
                mode="lines", line=dict(color=line_color, width=2.5),
                showlegend=row_idx == 1,
                name="Median forecast",
                hovertemplate="%{x}<br>Median: ₹%{y:,.0f}<extra></extra>",
            ),
            row=row_idx, col=1,
        )
        # Current value reference
        fig1.add_hline(
            y=portfolio.fund_by_name(fund_name).current_value,
            line_dash="dot", line_color="gray", line_width=1,
            row=row_idx, col=1,
        )

    # FY boundary lines (add_shape avoids the categorical x-axis annotation bug)
    for fy_m in fy_boundaries:
        if fy_m - 1 < len(date_labels):
            lbl = date_labels[fy_m - 1]
            fig1.add_shape(
                type="line", x0=lbl, x1=lbl, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(dash="dash", color="orange", width=1.5),
            )
            fig1.add_annotation(
                x=lbl, y=1.03, xref="x", yref="paper",
                text="FY Reset", showarrow=False,
                font=dict(color="darkorange", size=10),
                yanchor="bottom", xanchor="left",
            )

    fig1.update_yaxes(tickformat=",.0f", tickprefix="₹")
    fig1.update_layout(
        height=550, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=20),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Total portfolio overlay
    st.subheader("Total Portfolio (all funds combined)")
    b_total = bands["total"]
    fig1b = go.Figure()
    fig1b.add_trace(go.Scatter(
        x=date_labels, y=b_total["p10"],
        mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig1b.add_trace(go.Scatter(
        x=date_labels, y=b_total["p90"],
        mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(148,103,189,0.15)",
        name="80% band", hoverinfo="skip",
    ))
    fig1b.add_trace(go.Scatter(
        x=date_labels, y=b_total["p50"],
        mode="lines", line=dict(color="rgb(148,103,189)", width=2.5),
        name="Median total",
        hovertemplate="%{x}<br>Total: ₹%{y:,.0f}<extra></extra>",
    ))
    fig1b.add_hline(
        y=portfolio.total_current_value,
        line_dash="dot", line_color="gray", line_width=1,
        annotation_text="Today", annotation_position="right",
    )
    for fy_m in fy_boundaries:
        if fy_m - 1 < len(date_labels):
            lbl = date_labels[fy_m - 1]
            fig1b.add_shape(
                type="line", x0=lbl, x1=lbl, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(dash="dash", color="orange", width=1.5),
            )
            fig1b.add_annotation(
                x=lbl, y=1.03, xref="x", yref="paper",
                text="FY Reset", showarrow=False,
                font=dict(color="darkorange", size=10),
                yanchor="bottom", xanchor="left",
            )
    fig1b.update_yaxes(tickformat=",.0f", tickprefix="₹")
    fig1b.update_layout(
        height=350, hovermode="x unified",
        margin=dict(t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig1b, use_container_width=True)


# ============================================================
# TAB 2 — Withdrawal Planner (Optimal Exit Timing)
# ============================================================

with tab2:
    st.subheader("Withdrawal Planner — Optimal Exit Timing")
    st.caption(
        "Given a hard deadline, the planner scores every business day between "
        "today and the deadline on a risk-adjusted basis and recommends the "
        "best day to exit. The question it answers is WHEN to withdraw, not "
        "whether you have enough."
    )

    ctrl_col, status_col = st.columns([2, 3])

    with ctrl_col:
        wp_target = st.number_input(
            "Target withdrawal amount (₹)",
            min_value=10_000.0,
            max_value=float(portfolio.total_current_value * 2),
            value=1_400_000.0,
            step=10_000.0,
            format="%.0f",
            key="wp_target",
        )
        wp_deadline = st.date_input(
            "Hard deadline",
            value=today + datetime.timedelta(days=60),
            min_value=today,
            max_value=today + datetime.timedelta(days=180),
            key="wp_deadline",
            help="Latest date by which you MUST have withdrawn the target amount.",
        )
        wp_risk = st.slider(
            "Risk aversion (λ)",
            min_value=0.0, max_value=1.0, value=0.30, step=0.05,
            help="0 = pure expected-value maximiser · 1 = conservative (maximise P10)",
            key="wp_risk",
        )
        wp_split_mode = st.radio(
            "Fund split",
            ["Proportional to current value", "All from PP Flexi Cap", "All from ICICI Large Cap"],
            index=0, key="wp_split",
        )

    # ---- Compute short-horizon forecast covering today → deadline ----
    bdays_to_deadline = len(
        pd.bdate_range(today + datetime.timedelta(days=1), wp_deadline)
    )
    bdays_to_deadline = max(1, bdays_to_deadline)
    short_paths, short_bands = get_short_forecast(
        schemes_key, cur_tuple, bdays_to_deadline
    )
    wp_table = build_exit_timing_table(
        short_paths, target_amount=wp_target, risk_aversion=wp_risk
    )
    wp_rec = recommend_today(wp_table, risk_aversion=wp_risk)
    wp_bdays_idx = pd.bdate_range(
        today + datetime.timedelta(days=1), periods=bdays_to_deadline
    )
    wp_day_labels = [d.strftime("%a %d %b") for d in wp_bdays_idx]

    # ---- Today's recommendation card ----
    with status_col:
        action_css = {"SELL_TODAY": "act-now", "WAIT": "consider"}[wp_rec["action"]]
        action_emoji = {"SELL_TODAY": "🟢", "WAIT": "🟡"}[wp_rec["action"]]
        action_label = {"SELL_TODAY": "SELL TODAY", "WAIT": "WAIT"}[wp_rec["action"]]

        st.markdown(
            f"""
            <div class="rec-box {action_css}">
              <div class="rec-title">{action_emoji} {action_label}</div>
              <div>{wp_rec['reason']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        opt = wp_table[wp_rec["optimal_day_index"]]
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Optimal exit day", f"Day {opt.day_index}",
                  delta=wp_day_labels[opt.day_index] if opt.day_index < len(wp_day_labels) else "today")
        t2.metric("Expected value then", f"₹{opt.mean:,.0f}",
                  delta=f"{(opt.mean / portfolio.total_current_value - 1)*100:+.2f}% vs today")
        t3.metric("Downside (P10)", f"₹{opt.p10:,.0f}",
                  delta=f"{(opt.p10 / portfolio.total_current_value - 1)*100:+.2f}%")
        t4.metric("Gain from waiting",
                  f"₹{wp_rec['expected_gain_from_waiting']:,.0f}",
                  delta=f"{wp_rec['regret_prob_if_waiting']*100:.0f}% regret prob")

    st.divider()
    st.markdown("#### Daily Portfolio Forecast — Today → Deadline")
    st.caption(
        "Median and 10–90% credible band of the portfolio value on every "
        "business day between today and your deadline. Zoomed to your actual "
        "exit window (not 36 months)."
    )

    fig_wp_fan = go.Figure()
    fig_wp_fan.add_trace(go.Scatter(
        x=wp_day_labels, y=short_bands["total"]["p10"],
        mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig_wp_fan.add_trace(go.Scatter(
        x=wp_day_labels, y=short_bands["total"]["p90"],
        mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(31,119,180,0.15)",
        name="10–90% band", hoverinfo="skip",
    ))
    fig_wp_fan.add_trace(go.Scatter(
        x=wp_day_labels, y=short_bands["total"]["p50"],
        mode="lines", line=dict(color="rgb(31,119,180)", width=2.5),
        name="Median",
        hovertemplate="%{x}<br>Median: ₹%{y:,.0f}<extra></extra>",
    ))
    fig_wp_fan.add_hline(
        y=wp_target, line_dash="dash", line_color="green", line_width=1.5,
    )
    fig_wp_fan.add_hline(
        y=portfolio.total_current_value, line_dash="dot", line_color="gray", line_width=1,
    )
    # Mark optimal exit day (string x-axis → use add_shape, not add_vline)
    if wp_rec["optimal_day_index"] < len(wp_day_labels):
        opt_lbl = wp_day_labels[wp_rec["optimal_day_index"]]
        fig_wp_fan.add_shape(
            type="line", x0=opt_lbl, x1=opt_lbl, y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(dash="solid", color="darkorange", width=2),
        )
        fig_wp_fan.add_annotation(
            x=opt_lbl, y=1.02, xref="x", yref="paper",
            text="Optimal exit", showarrow=False,
            font=dict(color="darkorange", size=11),
            yanchor="bottom", xanchor="center",
        )
    fig_wp_fan.update_yaxes(tickformat=",.0f", tickprefix="₹")
    fig_wp_fan.update_layout(
        height=380, hovermode="x unified",
        margin=dict(t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_wp_fan, use_container_width=True)

    st.markdown("#### Exit-Timing Ranking")
    st.caption(
        "Every business day between now and your deadline, scored on a "
        "risk-adjusted basis. `score = (1-λ)·mean + λ·P10`. Upside left = "
        "expected value on that day minus expected value today. Regret prob "
        "= P(value on that day < value today)."
    )

    rank_rows = []
    for r in wp_table:
        lbl = wp_day_labels[r.day_index] if r.day_index < len(wp_day_labels) else "today"
        rank_rows.append({
            "Day": f"{r.day_index} · {lbl}",
            "Median": f"₹{r.median:,.0f}",
            "P10": f"₹{r.p10:,.0f}",
            "P90": f"₹{r.p90:,.0f}",
            "Upside Left": f"₹{r.upside_left_from_today:,.0f}",
            "Regret Prob": f"{r.regret_prob_vs_today*100:.0f}%",
            "P(≥ target)": f"{r.prob_meets_target*100:.0f}%",
            "Score": round(r.score, 0),
        })
    rank_df = pd.DataFrame(rank_rows)

    def _highlight(row):
        return [
            "background-color: #fff3cd" if row.name == wp_rec["optimal_day_index"] else ""
            for _ in row
        ]
    st.dataframe(
        rank_df.style.apply(_highlight, axis=1),
        use_container_width=True,
        hide_index=True,
        height=min(400, 38 * (len(rank_df) + 1)),
    )

    with st.expander("Tax impact at optimal exit day (LTCG @ 12.5%)"):
        opt_day = wp_rec["optimal_day_index"]
        proj_at_opt = {
            fn: float(short_bands[fn]["p50"][opt_day]) for fn in fund_names
        }
        if wp_split_mode == "Proportional to current value":
            wp_alloc = suggest_proportional_split(portfolio, wp_target, proj_at_opt)
        elif wp_split_mode == "All from PP Flexi Cap":
            wp_alloc = {"Parag Parikh Flexi Cap": wp_target, "ICICI Pru Large Cap": 0.0}
        else:
            wp_alloc = {"Parag Parikh Flexi Cap": 0.0, "ICICI Pru Large Cap": wp_target}

        tax_info = compute_portfolio_withdrawal_tax(portfolio, wp_alloc, proj_at_opt)
        tax_rows = []
        for fn, amt in wp_alloc.items():
            pv = proj_at_opt[fn]
            gr = projected_gain_ratio(portfolio.fund_by_name(fn), pv)
            tax_rows.append({
                "Fund": fn,
                "Withdrawal (₹)": f"₹{amt:,.0f}",
                "Projected Value at Exit": f"₹{pv:,.0f}",
                "Gain Ratio": f"{gr*100:.1f}%",
                "Realised Gain (₹)": f"₹{amt*gr:,.0f}",
            })
        st.dataframe(pd.DataFrame(tax_rows), use_container_width=True, hide_index=True)
        st.info(
            f"**Total LTCG realised:** ₹{tax_info['total_realized_gain']:,.0f}  \n"
            f"**Exemption applied:** ₹{tax_info['exemption_used']:,.0f}  \n"
            f"**Taxable gain:** ₹{tax_info['taxable_gain']:,.0f}  \n"
            f"**Tax @ 12.5%:** ₹{tax_info['total_tax']:,.0f}  \n"
            f"**Net received:** ₹{tax_info['net_received']:,.0f}"
        )


# ============================================================
# TAB 3 — Tax Impact Heatmap
# ============================================================

with tab3:
    st.subheader("Tax Impact Across Withdrawal Amounts & Timing")
    st.caption(
        "Colour shows estimated LTCG tax for different withdrawal amounts at different months, "
        "using median projected values from the Bayesian factor model. "
        "Green = within/near ₹1.25L exemption (zero/low tax). Red = above exemption."
    )

    # Build heatmap grid
    w_amounts = np.linspace(50_000, min(1_500_000, portfolio.total_current_value * 0.9), 20)
    heatmap_months = list(range(1, N_MONTHS + 1, 2))  # every 2 months to keep chart readable
    heatmap_dates = [date_labels[m - 1] for m in heatmap_months]

    tax_matrix = np.zeros((len(w_amounts), len(heatmap_months)))

    for j, m in enumerate(heatmap_months):
        proj_m = {fn: float(bands[fn]["p50"][m - 1]) for fn in fund_names}
        for i, amt in enumerate(w_amounts):
            alloc = suggest_proportional_split(portfolio, float(amt), proj_m)
            t_info = compute_portfolio_withdrawal_tax(portfolio, alloc, proj_m)
            tax_matrix[i, j] = t_info["total_tax"]

    y_labels = [f"₹{a:,.0f}" for a in w_amounts]

    fig3 = go.Figure(go.Heatmap(
        z=tax_matrix,
        x=heatmap_dates,
        y=y_labels,
        colorscale="RdYlGn_r",
        colorbar=dict(title="Tax (₹)", tickformat=",.0f"),
        hovertemplate="Amount: %{y}<br>Month: %{x}<br>Tax: ₹%{z:,.0f}<extra></extra>",
        zmin=0,
        zmid=5_000,
    ))

    # Mark FY boundaries
    for fy_m in fy_boundaries:
        fy_m_idx = heatmap_months.index(fy_m) if fy_m in heatmap_months else None
        if fy_m_idx is not None:
            lbl = heatmap_dates[fy_m_idx]
            fig3.add_shape(
                type="line", x0=lbl, x1=lbl, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(dash="dash", color="white", width=2),
            )
            fig3.add_annotation(
                x=lbl, y=1.03, xref="x", yref="paper",
                text="FY Reset", showarrow=False,
                font=dict(color="white", size=10),
                yanchor="bottom", xanchor="left",
            )

    fig3.update_layout(
        height=480,
        xaxis_title="Withdrawal Month",
        yaxis_title="Withdrawal Amount",
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Summary table
    st.markdown("#### Zero-Tax Windows by Financial Year")
    ts = portfolio.tax_state
    blended_gr = portfolio.blended_gain_ratio

    fy_rows = []
    exemption = ts.fy_exemption_limit

    # Current FY
    max_zero_tax_now = ts.remaining_exemption / blended_gr if blended_gr > 0 else 0
    fy_rows.append({
        "Financial Year": "FY 2026-27 (current)",
        "Exemption Available": f"₹{ts.remaining_exemption:,.0f}",
        "Max Zero-Tax Withdrawal (today)": f"₹{max_zero_tax_now:,.0f}",
        "Note": "Uses today's gain ratio; increases as fund grows",
    })

    # Next FY (Apr 2027)
    if fy_boundaries:
        fy_m = fy_boundaries[0]
        proj_fy = {fn: float(bands[fn]["p50"][fy_m]) for fn in fund_names}
        total_proj = sum(proj_fy.values())
        total_cost = sum(f.invested for f in portfolio.funds)
        gr_next = max(0.0, (total_proj - total_cost) / total_proj) if total_proj > 0 else 0
        max_zero_next = exemption / gr_next if gr_next > 0 else 0
        fy_rows.append({
            "Financial Year": "FY 2027-28 (next, from Apr 2027)",
            "Exemption Available": f"₹{exemption:,.0f}",
            "Max Zero-Tax Withdrawal (at Apr 2027)": f"₹{max_zero_next:,.0f}",
            "Note": "Projected at median portfolio growth",
        })

    st.dataframe(pd.DataFrame(fy_rows), use_container_width=True, hide_index=True)

    st.info(
        "**Note on gain ratio:** As the portfolio grows, each rupee redeemed carries "
        "a higher proportion of gain. This means the zero-tax withdrawal *amount* does "
        "not grow at the same rate as the portfolio."
    )


# ============================================================
# TAB 4 — Scenarios (Factor Regime + Fan Forecast)
# ============================================================

with tab4:
    st.subheader("Market Factor Regime")
    st.caption(
        "What the market looks like right now, as seen by the factor model's "
        "inputs. These numbers condition all forecasts on this tab."
    )

    regime = current_factor_regime(factors_df, window=20)
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric(
        "NIFTY 20d ann. vol",
        f"{regime['nifty_trailing_vol_20d']*100:.1f}%",
    )
    g2.metric("India VIX", f"{regime['vix_level']:.1f}")
    g3.metric(
        "USD/INR 20d",
        f"{regime.get('usdinr_mom_20d', 0)*100:+.2f}%",
        delta=None,
    )
    g4.metric("Gold 20d", f"{regime.get('gold_mom_20d', 0)*100:+.2f}%")
    g5.metric("Crude 20d", f"{regime.get('crude_mom_20d', 0)*100:+.2f}%")

    st.divider()

    st.subheader("3-Year Fan Forecast (factor model)")
    st.caption(
        "10th / 50th / 90th percentile total portfolio value over the next 36 months "
        "from 2,000 Bayesian factor-model paths. Unlike the previous stratified-quartile "
        "scenarios, each path is a full simulation of correlated fund × factor dynamics."
    )

    b_total = long_bands["total"]
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=date_labels, y=b_total["p10"][long_month_idx],
        mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig4.add_trace(go.Scatter(
        x=date_labels, y=b_total["p90"][long_month_idx],
        mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(148,103,189,0.15)",
        name="10–90% band", hoverinfo="skip",
    ))
    fig4.add_trace(go.Scatter(
        x=date_labels, y=b_total["p50"][long_month_idx],
        mode="lines", line=dict(color="rgb(148,103,189)", width=2.5),
        name="Median total",
        hovertemplate="%{x}<br>Total: ₹%{y:,.0f}<extra></extra>",
    ))
    fig4.add_hline(
        y=portfolio.total_current_value,
        line_dash="dot", line_color="gray", line_width=1,
    )
    for fy_m in fy_boundaries:
        if fy_m - 1 < len(date_labels):
            lbl = date_labels[fy_m - 1]
            fig4.add_shape(
                type="line", x0=lbl, x1=lbl, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(dash="dash", color="orange", width=1.5),
            )
            fig4.add_annotation(
                x=lbl, y=1.03, xref="x", yref="paper",
                text="FY Reset", showarrow=False,
                font=dict(color="darkorange", size=10),
                yanchor="bottom", xanchor="left",
            )
    fig4.update_yaxes(tickformat=",.0f", tickprefix="₹")
    fig4.update_layout(
        height=420, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### Milestone Snapshots")
    snap_months = [12, 24, 36]
    snap_rows = []
    for pct_name, pct_key in [("P10 (bear)", "p10"), ("P50 (median)", "p50"), ("P90 (bull)", "p90")]:
        row = {"Percentile": pct_name}
        total_p = long_bands["total"][pct_key]
        for sm in snap_months:
            bday = min(sm * 21 - 1, len(total_p) - 1)
            row[f"Month {sm} ({long_bdays[bday].strftime('%b %Y')})"] = f"₹{total_p[bday]:,.0f}"
        snap_rows.append(row)
    st.dataframe(pd.DataFrame(snap_rows), use_container_width=True, hide_index=True)

    with st.expander("Model Diagnostics (PyMC)"):
        st.caption("Divergences and R-hat values from the factor-model sampler.")
        n_div = int(idata.sample_stats.diverging.sum())
        st.metric("MCMC Divergences", n_div, delta="0 is ideal", delta_color="inverse" if n_div > 0 else "off")

        try:
            summary = az.summary(
                idata,
                var_names=["alpha", "beta", "sigma_fund", "group_alpha", "group_beta"],
            )
            st.dataframe(
                summary[["mean", "sd", "hdi_3%", "hdi_97%", "r_hat"]],
                use_container_width=True,
            )
        except Exception:
            st.info("Run a full model refresh to see diagnostics.")

