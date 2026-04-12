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
    WithdrawalSchedule,
    WithdrawalTranche,
    compute_portfolio_withdrawal_tax,
    compute_todays_recommendation,
    optimize_multi_fy_withdrawal,
    projected_gain_ratio,
    suggest_proportional_split,
)
from models import (
    build_hierarchical_model,
    compute_percentile_bands,
    compute_withdrawal_probability,
    generate_posterior_predictive,
    generate_scenario_paths,
    run_inference,
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
    pp_xirr = st.number_input(
        "XIRR (%)", value=13.59, step=0.01, format="%.2f", key="pp_xirr"
    ) / 100.0

    st.subheader("ICICI Pru Large Cap")
    ic_inv = st.number_input(
        "Invested (₹)", value=674_966.0, step=1000.0, format="%.0f", key="ic_inv"
    )
    ic_cur = st.number_input(
        "Current Value (₹)", value=976_571.0, step=1000.0, format="%.0f", key="ic_cur"
    )
    ic_xirr = st.number_input(
        "XIRR (%)", value=13.20, step=0.01, format="%.2f", key="ic_xirr"
    ) / 100.0

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
        FundHolding("Parag Parikh Flexi Cap", pp_inv, pp_cur, pp_xirr),
        FundHolding("ICICI Pru Large Cap", ic_inv, ic_cur, ic_xirr),
    ],
    tax_state=TaxState(fy_exemption_limit=125_000.0, already_realized=already_realized),
    as_of_date=datetime.date.today(),
)

fund_names = [f.name for f in portfolio.funds]
current_values = np.array([f.current_value for f in portfolio.funds])

# ---------------------------------------------------------------------------
# Cached MCMC inference
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_idata(
    _pp_inv: float, _pp_cur: float, _pp_xirr: float,
    _ic_inv: float, _ic_cur: float, _ic_xirr: float,
    _already_realized: float,
):
    observed = np.array([
        (1 + _pp_xirr) ** (1 / 12) - 1,
        (1 + _ic_xirr) ** (1 / 12) - 1,
    ])
    model = build_hierarchical_model(
        ["Parag Parikh Flexi Cap", "ICICI Pru Large Cap"],
        observed,
    )
    return run_inference(model, target_accept=0.98)


@st.cache_data(show_spinner=False)
def get_paths_and_bands(
    _idata_id: int,
    _pp_cur: float, _ic_cur: float,
    n_months: int = 36,
):
    idata = st.session_state["_cached_idata"]
    cur = np.array([_pp_cur, _ic_cur])
    paths = generate_posterior_predictive(
        idata, ["Parag Parikh Flexi Cap", "ICICI Pru Large Cap"],
        cur, n_months=n_months,
    )
    bands = compute_percentile_bands(paths)
    scenarios = generate_scenario_paths(
        idata, ["Parag Parikh Flexi Cap", "ICICI Pru Large Cap"],
        cur, n_months=n_months,
    )
    return paths, bands, scenarios


# ---------------------------------------------------------------------------
# Run inference (with spinner) and cache result in session state
# ---------------------------------------------------------------------------

with st.spinner("Running Bayesian inference (first load ~45s)…"):
    idata = get_idata(
        pp_inv, pp_cur, pp_xirr,
        ic_inv, ic_cur, ic_xirr,
        already_realized,
    )
    st.session_state["_cached_idata"] = idata

paths, bands, scenarios = get_paths_and_bands(
    id(idata), pp_cur, ic_cur
)
st.session_state["_cached_paths"] = paths

# Convenience: month index array and date labels
N_MONTHS = 36
months_idx = np.arange(1, N_MONTHS + 1)
today = datetime.date.today()
date_labels = [
    (today + datetime.timedelta(days=30 * int(m))).strftime("%b %Y")
    for m in months_idx
]
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
# Multi-FY optimizer cache wrapper
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def cached_multi_fy_schedule(
    _paths_id: int,
    _pp_inv: float, _pp_cur: float,
    _ic_inv: float, _ic_cur: float,
    _already_realized: float,
    target_amount: float,
    horizon_months: int,
    strategy: str,
    risk_aware: bool,
):
    """Cache key includes all portfolio scalars + optimizer inputs."""
    _paths = st.session_state["_cached_paths"]
    return optimize_multi_fy_withdrawal(
        portfolio=portfolio,
        target_amount=target_amount,
        horizon_months=horizon_months,
        projected_paths=_paths,
        strategy=strategy,  # type: ignore[arg-type]
        risk_aware=risk_aware,
    )


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab2b, tab3, tab4 = st.tabs(
    [
        "📈 Portfolio Trajectory",
        "💰 Withdrawal Planner",
        "🗓️ Multi-FY Plan",
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
        "Shaded band = 10th–90th percentile of 2,000 Bayesian Monte Carlo paths. "
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
# TAB 2 — Withdrawal Planner
# ============================================================

with tab2:
    st.subheader("Withdrawal Planner")
    st.caption(
        "Enter how much you need and when. The app shows probability of success "
        "across months and the estimated tax impact."
    )

    col_in, col_out = st.columns([2, 3])

    with col_in:
        target_amount = st.number_input(
            "Target withdrawal amount (₹)",
            min_value=10_000.0,
            max_value=float(portfolio.total_current_value * 2),
            value=500_000.0,
            step=10_000.0,
            format="%.0f",
        )
        horizon = st.slider(
            "Time horizon (months)",
            min_value=1, max_value=N_MONTHS, value=6,
        )
        split_mode = st.radio(
            "Fund split",
            ["Proportional to current value", "All from PP Flexi Cap", "All from ICICI Large Cap"],
            index=0,
        )

    # Compute withdrawal probability
    p_sufficient, first_month = compute_withdrawal_probability(paths, target_amount)

    # Determine allocation at horizon
    proj_at_horizon = {
        fn: float(bands[fn]["p50"][horizon - 1]) for fn in fund_names
    }

    if split_mode == "Proportional to current value":
        allocations = suggest_proportional_split(portfolio, target_amount, proj_at_horizon)
    elif split_mode == "All from PP Flexi Cap":
        allocations = {"Parag Parikh Flexi Cap": target_amount, "ICICI Pru Large Cap": 0.0}
    else:
        allocations = {"Parag Parikh Flexi Cap": 0.0, "ICICI Pru Large Cap": target_amount}

    # Use a fresh TaxState if the horizon crosses the FY boundary (Apr 1 reset)
    # — already_realized from a prior FY doesn't reduce next FY's exemption.
    horizon_tax_state = portfolio.tax_state
    if fy_boundaries and horizon >= fy_boundaries[0]:
        horizon_tax_state = TaxState(
            fy_exemption_limit=portfolio.tax_state.fy_exemption_limit,
            already_realized=0.0,
        )
    tax_info = compute_portfolio_withdrawal_tax(
        portfolio, allocations, proj_at_horizon, tax_state_override=horizon_tax_state
    )

    # Update recommendation with target
    rec_with_target = compute_todays_recommendation(portfolio, target_amount)

    with col_out:
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        r1c1.metric(
            "Earliest Safe Month",
            f"Month {first_month}" if first_month != -1 else "Beyond 36m",
            delta="≥80% confidence" if first_month != -1 else "Low probability",
            delta_color="normal" if first_month != -1 else "inverse",
        )
        r1c2.metric(
            f"P(Success) at Month {horizon}",
            f"{p_sufficient[horizon-1]*100:.1f}%",
            delta="above 80% threshold" if p_sufficient[horizon-1] >= 0.8 else "below 80%",
            delta_color="normal" if p_sufficient[horizon-1] >= 0.8 else "inverse",
        )
        r1c3.metric(
            "Estimated Tax",
            f"₹{tax_info['total_tax']:,.0f}",
            delta=f"{tax_info['effective_tax_rate']*100:.1f}% effective",
            delta_color="inverse",
        )
        r1c4.metric(
            "Net Received",
            f"₹{tax_info['net_received']:,.0f}",
            delta=f"after ₹{tax_info['total_tax']:,.0f} tax",
        )

    # Probability over time chart
    st.markdown("#### Probability of Portfolio ≥ Target Over Time")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=list(months_idx), y=p_sufficient * 100,
        mode="lines+markers",
        line=dict(color="steelblue", width=2),
        marker=dict(size=4),
        hovertemplate="Month %{x}: %{y:.1f}%<extra></extra>",
        name="P(portfolio ≥ target)",
    ))
    fig2.add_hline(
        y=80, line_dash="dash", line_color="green", line_width=1.5,
        annotation_text="80% confidence", annotation_position="right",
    )
    fig2.add_vline(
        x=horizon, line_dash="dot", line_color="royalblue", line_width=2,
        annotation_text=f"Your horizon: Month {horizon}",
        annotation_position="top right",
    )
    if first_month != -1:
        fig2.add_vline(
            x=first_month, line_dash="solid", line_color="green", line_width=1.5,
            annotation_text=f"Earliest safe: Month {first_month}",
            annotation_position="top left",
        )
    fig2.update_layout(
        yaxis_title="P(Portfolio ≥ Target) %",
        xaxis_title="Months from Today",
        yaxis_range=[0, 105],
        height=340,
        margin=dict(t=30, b=20),
        hovermode="x unified",
    )
    for fy_m in fy_boundaries:
        fig2.add_vline(
            x=fy_m, line_dash="dash", line_color="orange",
            line_width=1, opacity=0.5,
        )
    st.plotly_chart(fig2, use_container_width=True)

    # Fund split details
    with st.expander("Fund Split Details"):
        rows = []
        for fn, amt in allocations.items():
            pv = proj_at_horizon[fn]
            gr = projected_gain_ratio(portfolio.fund_by_name(fn), pv)
            rows.append({
                "Fund": fn,
                "Withdrawal (₹)": f"₹{amt:,.0f}",
                "Projected Value at Month": f"₹{pv:,.0f}",
                "Gain Ratio": f"{gr*100:.1f}%",
                "Realised Gain (₹)": f"₹{amt*gr:,.0f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.info(
            f"**Total LTCG realised:** ₹{tax_info['total_realized_gain']:,.0f}  \n"
            f"**Exemption applied:** ₹{tax_info['exemption_used']:,.0f}  \n"
            f"**Taxable gain:** ₹{tax_info['taxable_gain']:,.0f}  \n"
            f"**Tax @ 12.5%:** ₹{tax_info['total_tax']:,.0f}  \n"
            f"**Exemption remaining after withdrawal:** ₹{tax_info['fy_exemption_remaining_after']:,.0f}"
        )

    # FY boundary tip
    if fy_boundaries and horizon > fy_boundaries[0]:
        fy_m = fy_boundaries[0]
        st.info(
            f"**FY tip:** Your horizon ({horizon} months) crosses an FY boundary at month {fy_m}. "
            f"Consider splitting the withdrawal: one tranche before month {fy_m} "
            f"(uses this FY's remaining ₹{portfolio.tax_state.remaining_exemption:,.0f} exemption) "
            f"and one after (unlocks the full ₹1,25,000 fresh exemption). "
            f"Check the Tax Impact tab for details."
        )


# ============================================================
# TAB 3 — Tax Impact Heatmap
# ============================================================

with tab3:
    st.subheader("Tax Impact Across Withdrawal Amounts & Timing")
    st.caption(
        "Colour shows estimated LTCG tax for different withdrawal amounts at different months. "
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
# TAB 4 — Scenarios
# ============================================================

with tab4:
    st.subheader("Bull / Base / Bear Scenario Trajectories")
    st.caption(
        "Scenarios are derived by stratifying the posterior: "
        "Bull = top 25% of sampled fund return rates, "
        "Base = middle 20%, "
        "Bear = bottom 25%."
    )

    SCENARIO_COLORS = {"bull": "#2ca02c", "base": "#1f77b4", "bear": "#d62728"}
    SCENARIO_LABELS = {
        "bull": "Bull (top 25% returns)",
        "base": "Base (median returns)",
        "bear": "Bear (bottom 25% returns)",
    }

    # Total portfolio fan chart
    fig4 = go.Figure()
    for sc_name, sc_data in scenarios.items():
        fig4.add_trace(go.Scatter(
            x=date_labels, y=sc_data["total"],
            mode="lines", line=dict(color=SCENARIO_COLORS[sc_name], width=2.5),
            name=SCENARIO_LABELS[sc_name],
            hovertemplate=f"{SCENARIO_LABELS[sc_name]}: ₹%{{y:,.0f}}<extra></extra>",
        ))

    fig4.add_hline(
        y=portfolio.total_current_value,
        line_dash="dot", line_color="gray", line_width=1.5,
        annotation_text="Today", annotation_position="right",
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
        height=400, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Snapshot table at 12, 24, 36 months
    st.markdown("#### Portfolio Value Snapshots")
    snap_months = [12, 24, 36]
    snap_rows = []
    for sc_name in ["bull", "base", "bear"]:
        row = {"Scenario": SCENARIO_LABELS[sc_name]}
        for sm in snap_months:
            if sm <= N_MONTHS:
                val = scenarios[sc_name]["total"][sm - 1]
                row[f"Month {sm} ({date_labels[sm-1]})"] = f"₹{val:,.0f}"
        snap_rows.append(row)

    st.dataframe(pd.DataFrame(snap_rows), use_container_width=True, hide_index=True)

    # Per-fund scenario breakdown
    st.markdown("#### Per-Fund Scenario at Month 36")
    fund_snap_rows = []
    for fn in fund_names:
        row = {"Fund": fn}
        for sc_name in ["bull", "base", "bear"]:
            val = scenarios[sc_name][fn][-1]
            row[SCENARIO_LABELS[sc_name]] = f"₹{val:,.0f}"
        fund_snap_rows.append(row)
    st.dataframe(pd.DataFrame(fund_snap_rows), use_container_width=True, hide_index=True)

    # MCMC diagnostics
    with st.expander("Model Diagnostics (PyMC)"):
        st.caption("Divergences and R-hat values from the Bayesian sampler.")
        n_div = int(idata.sample_stats.diverging.sum())
        st.metric("MCMC Divergences", n_div, delta="0 is ideal", delta_color="inverse" if n_div > 0 else "off")

        # R-hat summary
        try:
            summary = az.summary(idata, var_names=["mu_fund", "sigma_fund", "group_mu", "group_sigma"])
            st.dataframe(summary[["mean", "sd", "hdi_3%", "hdi_97%", "r_hat"]], use_container_width=True)
        except Exception:
            st.info("Run a full model refresh to see diagnostics.")


# ============================================================
# TAB 2b — Multi-FY Plan
# ============================================================

with tab2b:
    st.subheader("Multi-FY Withdrawal Optimizer")
    st.caption(
        "Plan a large withdrawal across multiple Indian financial years to "
        "maximise use of the ₹1,25,000 LTCG exemption per FY. The default "
        "strategy fills each FY's exemption exactly in chronological order."
    )

    mcol_in, mcol_out = st.columns([2, 3])

    with mcol_in:
        m_target = st.number_input(
            "Total amount to withdraw (₹)",
            min_value=10_000.0,
            max_value=float(portfolio.total_current_value * 3),
            value=2_000_000.0,
            step=50_000.0,
            format="%.0f",
            key="multi_fy_target",
        )
        m_horizon_years = st.slider(
            "Time horizon (years)",
            min_value=1, max_value=5, value=3,
            key="multi_fy_horizon_years",
        )
        m_strategy_label = st.radio(
            "Strategy",
            [
                "Tax-minimising (recommended)",
                "Equal split across FYs",
                "Front-loaded (this FY)",
                "Back-loaded (last FY)",
            ],
            index=0,
            key="multi_fy_strategy",
        )
        m_risk_aware = st.toggle(
            "Risk-aware (use p10 instead of p50)",
            value=False,
            help=(
                "If on, the optimizer assumes the pessimistic 10th-percentile "
                "growth path. This produces a lower gain ratio and a slightly "
                "larger zero-tax withdrawal window per FY."
            ),
            key="multi_fy_risk_aware",
        )

    strategy_map = {
        "Tax-minimising (recommended)": "tax_minimizing",
        "Equal split across FYs": "equal_split",
        "Front-loaded (this FY)": "front_loaded",
        "Back-loaded (last FY)": "back_loaded",
    }
    m_strategy = strategy_map[m_strategy_label]
    m_horizon_months = m_horizon_years * 12

    schedule = cached_multi_fy_schedule(
        id(paths),
        pp_inv, pp_cur, ic_inv, ic_cur, already_realized,
        m_target, m_horizon_months, m_strategy, m_risk_aware,
    )
    baseline = cached_multi_fy_schedule(
        id(paths),
        pp_inv, pp_cur, ic_inv, ic_cur, already_realized,
        m_target, m_horizon_months, "front_loaded", m_risk_aware,
    )
    tax_saved = max(0.0, baseline.total_tax - schedule.total_tax)

    with mcol_out:
        s1, s2, s3, s4 = st.columns(4)
        s1.metric(
            "Total Tax",
            f"₹{schedule.total_tax:,.0f}",
            delta=f"{schedule.effective_tax_rate*100:.2f}% effective",
            delta_color="inverse",
        )
        s2.metric(
            "Net Received",
            f"₹{schedule.total_net:,.0f}",
        )
        s3.metric(
            "Tranches",
            f"{len(schedule.tranches)}",
            delta=f"{m_horizon_years}-year horizon",
        )
        s4.metric(
            "Tax Saved vs Single Withdrawal",
            f"₹{tax_saved:,.0f}",
            delta=(
                "vs front-loaded baseline"
                if tax_saved > 0
                else "no savings (single tranche fits)"
            ),
        )

        if schedule.shortfall > 0:
            st.warning(
                f"Could only schedule ₹{schedule.total_withdrawal:,.0f} of the "
                f"₹{m_target:,.0f} target within {m_horizon_years} year(s). "
                f"Shortfall: ₹{schedule.shortfall:,.0f}."
            )

    st.markdown("#### Tranche Schedule")
    if not schedule.tranches:
        st.info("No tranches scheduled. Adjust the target or horizon.")
    else:
        table_rows = []
        for t in schedule.tranches:
            table_rows.append({
                "FY": t.fy_label,
                "Date": t.date.strftime("%b %Y"),
                "Month #": t.month_index,
                "Amount (₹)": f"₹{t.total_amount:,.0f}",
                "Realised Gain (₹)": f"₹{t.realized_gain:,.0f}",
                "Taxable Gain (₹)": f"₹{t.taxable_gain:,.0f}",
                "Tax (₹)": f"₹{t.tax:,.0f}",
                "Net (₹)": f"₹{t.net_received:,.0f}",
                "Exemption Used": f"{schedule.exemption_utilization.get(t.fy_label, 0)*100:.0f}%",
            })
        st.dataframe(
            pd.DataFrame(table_rows),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("#### FY Exemption Utilisation")
    if schedule.exemption_utilization:
        util_labels = list(schedule.exemption_utilization.keys())
        util_values = [
            min(1.0, schedule.exemption_utilization[lbl]) * 100
            for lbl in util_labels
        ]
        fig_util = go.Figure(go.Bar(
            x=util_labels,
            y=util_values,
            marker_color=[
                "#2ca02c" if v >= 99 else ("#ffbb33" if v >= 60 else "#aec7e8")
                for v in util_values
            ],
            text=[f"{v:.0f}%" for v in util_values],
            textposition="outside",
            hovertemplate="%{x}<br>Exemption used: %{y:.1f}%<extra></extra>",
        ))
        fig_util.update_layout(
            yaxis_title="₹1.25L Exemption Used",
            yaxis_range=[0, 115],
            height=320,
            margin=dict(t=20, b=20),
            showlegend=False,
        )
        fig_util.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_util, use_container_width=True)

    st.markdown("#### Withdrawal Timeline")
    if schedule.tranches:
        timeline_labels = [t.fy_label for t in schedule.tranches]
        timeline_amounts = [t.total_amount for t in schedule.tranches]
        timeline_taxes = [t.tax for t in schedule.tranches]

        fig_tl = go.Figure()
        fig_tl.add_trace(go.Bar(
            x=timeline_labels,
            y=[a - tx for a, tx in zip(timeline_amounts, timeline_taxes)],
            name="Net received",
            marker_color="#2ca02c",
            hovertemplate="%{x}<br>Net: ₹%{y:,.0f}<extra></extra>",
        ))
        fig_tl.add_trace(go.Bar(
            x=timeline_labels,
            y=timeline_taxes,
            name="Tax",
            marker_color="#d62728",
            hovertemplate="%{x}<br>Tax: ₹%{y:,.0f}<extra></extra>",
        ))
        for t in schedule.tranches:
            fig_tl.add_annotation(
                x=t.fy_label,
                y=0,
                xref="x", yref="paper",
                yanchor="top", yshift=-30,
                text=t.date.strftime("%b %Y"),
                showarrow=False,
                font=dict(size=10, color="gray"),
            )
        fig_tl.update_layout(
            barmode="stack",
            height=380,
            yaxis_title="Rupees",
            xaxis_title="Financial Year",
            margin=dict(t=20, b=70),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        fig_tl.update_yaxes(tickformat=",.0f", tickprefix="₹")
        st.plotly_chart(fig_tl, use_container_width=True)
    else:
        st.info("No timeline to display.")

    with st.expander("Compare strategies side-by-side"):
        comparison_rows = []
        for strat_name, strat_label in [
            ("tax_minimizing", "Tax-minimising"),
            ("equal_split", "Equal split"),
            ("front_loaded", "Front-loaded"),
            ("back_loaded", "Back-loaded"),
        ]:
            sch = cached_multi_fy_schedule(
                id(paths),
                pp_inv, pp_cur, ic_inv, ic_cur, already_realized,
                m_target, m_horizon_months, strat_name, m_risk_aware,
            )
            comparison_rows.append({
                "Strategy": strat_label,
                "Tranches": len(sch.tranches),
                "Total Tax (₹)": f"₹{sch.total_tax:,.0f}",
                "Net Received (₹)": f"₹{sch.total_net:,.0f}",
                "Effective Rate": f"{sch.effective_tax_rate*100:.2f}%",
            })
        st.dataframe(
            pd.DataFrame(comparison_rows),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Tax-minimising fills each FY's ₹1.25L exemption exactly in "
            "chronological order. Front-loaded compresses everything into the "
            "current FY (worst case for tax). Back-loaded delays the entire "
            "withdrawal to the final FY (also worst case)."
        )

    with st.expander("How it works"):
        st.markdown(
            """
**Algorithm:** Greedy fill of each FY's ₹1,25,000 LTCG exemption in
chronological order. Because the LTCG tax rule is piecewise linear (0% below
the exemption, 12.5% above), filling each FY exactly is a strong heuristic.

**Per-FY anchor month:** the first month of each FY within the horizon. The
projected portfolio value at that month determines the blended gain ratio
used to compute the maximum zero-tax rupee amount for that FY.

**Gain ratio drift:** because the cost basis is fixed but the projected
value grows, the blended gain ratio increases each FY. This means the rupee
amount that fits inside ₹1.25L of LTCG **shrinks** every year — the
optimizer accounts for this automatically.

**Risk-aware mode:** uses the 10th-percentile (pessimistic) projected value
instead of the median. Lower projected value → lower gain ratio → larger
zero-tax window per FY (you can withdraw slightly more rupees tax-free in
the current FY).
"""
        )
