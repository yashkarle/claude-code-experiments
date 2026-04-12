"""
portfolio.py — Data classes and tax calculations for NRI portfolio planner.

FY in India runs April 1 → March 31.
LTCG on equity MFs: ₹1,25,000 exempt per FY; 12.5% on gains above that.
Proportional redemption model: each rupee redeemed carries gain in proportion
to the fund's current gain ratio (unrealised_gain / current_value).
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Literal, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FundHolding:
    name: str
    invested: float        # cost basis ₹
    current_value: float   # current market value ₹
    xirr: float            # annualised return as decimal (e.g. 0.1359 for 13.59%)
    is_long_term: bool = True  # held >12 months → LTCG treatment

    @property
    def unrealized_gain(self) -> float:
        return self.current_value - self.invested

    @property
    def gain_ratio(self) -> float:
        """Fraction of current value that is unrealised gain."""
        if self.current_value == 0:
            return 0.0
        return max(0.0, self.unrealized_gain / self.current_value)

    @property
    def monthly_return(self) -> float:
        """Geometric monthly return derived from annual XIRR."""
        return (1 + self.xirr) ** (1 / 12) - 1


@dataclass
class TaxState:
    fy_exemption_limit: float = 125_000.0  # ₹1.25L LTCG exemption per FY
    already_realized: float = 0.0          # LTCG realised so far this FY

    @property
    def remaining_exemption(self) -> float:
        return max(0.0, self.fy_exemption_limit - self.already_realized)

    def tax_on_gain(self, gain: float) -> float:
        """LTCG tax: 0 up to remaining exemption, 12.5% above."""
        taxable = max(0.0, gain - self.remaining_exemption)
        return taxable * 0.125

    def tax_on_withdrawal(self, withdrawal: float, gain_ratio: float) -> float:
        realized_gain = withdrawal * gain_ratio
        return self.tax_on_gain(realized_gain)


@dataclass
class Portfolio:
    funds: list[FundHolding]
    tax_state: TaxState
    as_of_date: datetime.date = field(default_factory=datetime.date.today)

    @property
    def total_invested(self) -> float:
        return sum(f.invested for f in self.funds)

    @property
    def total_current_value(self) -> float:
        return sum(f.current_value for f in self.funds)

    @property
    def total_unrealized_gain(self) -> float:
        return sum(f.unrealized_gain for f in self.funds)

    @property
    def blended_gain_ratio(self) -> float:
        if self.total_current_value == 0:
            return 0.0
        return self.total_unrealized_gain / self.total_current_value

    def months_to_next_fy(self) -> int:
        """Calendar months (ceiling) until next April 1."""
        today = self.as_of_date
        year = today.year if today.month < 4 else today.year + 1
        next_fy = datetime.date(year, 4, 1)
        delta_days = (next_fy - today).days
        return max(1, -(-delta_days // 30))  # ceiling division

    def fy_boundary_months(self, horizon: int) -> list[int]:
        """
        Returns 1-based month indices (within [1, horizon]) that fall on or
        after an April 1 boundary, i.e. the first month of each new FY.
        """
        boundaries = []
        m_to_fy = self.months_to_next_fy()
        m = m_to_fy
        while m <= horizon:
            boundaries.append(m)
            m += 12
        return boundaries

    def fund_by_name(self, name: str) -> Optional[FundHolding]:
        for f in self.funds:
            if f.name == name:
                return f
        return None


# ---------------------------------------------------------------------------
# Default portfolio (Apr 2026 actuals from screenshot)
# ---------------------------------------------------------------------------

DEFAULT_PORTFOLIO = Portfolio(
    funds=[
        FundHolding(
            name="Parag Parikh Flexi Cap",
            invested=903_555.0,
            current_value=1_396_100.0,
            xirr=0.1359,
        ),
        FundHolding(
            name="ICICI Pru Large Cap",
            invested=674_966.0,
            current_value=976_571.0,
            xirr=0.1320,
        ),
    ],
    tax_state=TaxState(
        fy_exemption_limit=125_000.0,
        already_realized=0.0,  # FY26-27 fresh start; all prior sells in FY25-26
    ),
    as_of_date=datetime.date(2026, 4, 11),
)


# ---------------------------------------------------------------------------
# Tax calculation helpers
# ---------------------------------------------------------------------------

def projected_gain_ratio(fund: FundHolding, projected_value: float) -> float:
    """
    At a future month T, cost basis stays fixed while value grows.
    gain_ratio_T = (projected_value - cost_basis) / projected_value
    This increases over time (more of each rupee redeemed is gain).
    """
    gain = projected_value - fund.invested
    if projected_value <= 0:
        return 0.0
    return max(0.0, gain / projected_value)


def compute_withdrawal_tax_impact(
    portfolio: Portfolio,
    fund_name: str,
    withdrawal_amount: float,
    projected_value: float,
    tax_state_override: Optional[TaxState] = None,
) -> dict:
    """
    Compute tax impact of withdrawing `withdrawal_amount` from a single fund
    at a future date when its value is `projected_value`.

    Returns informational breakdown — not used to drive fund choice.
    """
    fund = portfolio.fund_by_name(fund_name)
    if fund is None:
        return {}

    ts = tax_state_override or portfolio.tax_state
    gr = projected_gain_ratio(fund, projected_value)
    realized_gain = withdrawal_amount * gr
    tax = ts.tax_on_gain(realized_gain)
    net_received = withdrawal_amount - tax

    return {
        "fund": fund_name,
        "withdrawal": withdrawal_amount,
        "projected_value": projected_value,
        "gain_ratio": gr,
        "realized_gain": realized_gain,
        "exemption_used": min(realized_gain, ts.remaining_exemption),
        "taxable_gain": max(0.0, realized_gain - ts.remaining_exemption),
        "tax": tax,
        "net_received": net_received,
        "effective_tax_rate": tax / withdrawal_amount if withdrawal_amount > 0 else 0.0,
    }


def compute_portfolio_withdrawal_tax(
    portfolio: Portfolio,
    allocations: dict[str, float],      # {fund_name: amount}
    projected_values: dict[str, float], # {fund_name: projected_value at withdrawal month}
    tax_state_override: Optional[TaxState] = None,
) -> dict:
    """
    Aggregate tax impact across all funds for a given withdrawal allocation.
    The ₹1.25L exemption applies to total LTCG across all equity funds in the FY.
    """
    ts = tax_state_override or portfolio.tax_state
    total_realized_gain = 0.0
    breakdown = {}

    for fund_name, amount in allocations.items():
        fund = portfolio.fund_by_name(fund_name)
        if fund is None or amount <= 0:
            continue
        pv = projected_values.get(fund_name, fund.current_value)
        gr = projected_gain_ratio(fund, pv)
        rg = amount * gr
        total_realized_gain += rg
        breakdown[fund_name] = {
            "withdrawal": amount,
            "gain_ratio": gr,
            "realized_gain": rg,
        }

    total_withdrawal = sum(allocations.values())
    taxable_gain = max(0.0, total_realized_gain - ts.remaining_exemption)
    total_tax = taxable_gain * 0.125
    net_received = total_withdrawal - total_tax

    return {
        "total_withdrawal": total_withdrawal,
        "total_realized_gain": total_realized_gain,
        "exemption_available": ts.remaining_exemption,
        "exemption_used": min(total_realized_gain, ts.remaining_exemption),
        "taxable_gain": taxable_gain,
        "total_tax": total_tax,
        "net_received": net_received,
        "effective_tax_rate": total_tax / total_withdrawal if total_withdrawal > 0 else 0.0,
        "fy_exemption_remaining_after": max(0.0, ts.remaining_exemption - total_realized_gain),
        "per_fund": breakdown,
    }


def suggest_proportional_split(
    portfolio: Portfolio,
    target_amount: float,
    projected_values: Optional[dict[str, float]] = None,
) -> dict[str, float]:
    """
    Default split proportional to each fund's projected (or current) value.
    Returns {fund_name: withdrawal_amount}.
    """
    pv = projected_values or {f.name: f.current_value for f in portfolio.funds}
    total_pv = sum(pv.values())
    if total_pv == 0:
        return {f.name: 0.0 for f in portfolio.funds}
    return {f.name: target_amount * (pv[f.name] / total_pv) for f in portfolio.funds}


def compute_todays_recommendation(portfolio: Portfolio, target_amount: float = 0.0) -> dict:
    """
    Heuristic 'today's guidance' based on FY calendar and tax headroom.

    Scoring:
      +2  if remaining_exemption > 0
      +1  if remaining_exemption > 0.5 * fy_exemption_limit
      +2  if months_to_next_fy <= 2  (use-it-or-lose-it pressure)
      -1  if months_to_next_fy >= 10

    Returns action string, headline, reasons list, and next optimal date hint.
    """
    ts = portfolio.tax_state
    months_left = portfolio.months_to_next_fy()
    score = 0
    reasons = []

    if ts.remaining_exemption > 0:
        score += 2
        reasons.append(f"₹{ts.remaining_exemption:,.0f} LTCG exemption still available this FY")
    if ts.remaining_exemption > 0.5 * ts.fy_exemption_limit:
        score += 1
        reasons.append("More than half the annual exemption is unused")
    if months_left <= 2:
        score += 2
        reasons.append(f"Only {months_left} month(s) left in FY — exemption resets Apr 1")
    if months_left >= 10:
        score -= 1
        reasons.append(f"FY resets in {months_left} months — plenty of time remaining")

    if target_amount > 0:
        blended = portfolio.blended_gain_ratio
        max_zero_tax = ts.remaining_exemption / blended if blended > 0 else float("inf")
        if target_amount <= max_zero_tax:
            score += 1
            reasons.append(f"Target withdrawal of ₹{target_amount:,.0f} fits within zero-tax window")
        else:
            reasons.append(
                f"Target ₹{target_amount:,.0f} exceeds zero-tax limit of ₹{max_zero_tax:,.0f}"
            )

    if score >= 4:
        action = "ACT NOW"
        headline = "Good window to withdraw — tax headroom available and FY deadline approaching."
    elif score >= 2:
        action = "CONSIDER"
        headline = "Reasonable time to plan a withdrawal — review the scenarios below."
    else:
        action = "WAIT"
        headline = "No urgency to act — monitor portfolio trajectory and revisit closer to FY end."

    # Next FY start
    today = portfolio.as_of_date
    next_fy_year = today.year if today.month < 4 else today.year + 1
    next_fy_date = datetime.date(next_fy_year, 4, 1)

    return {
        "action": action,
        "headline": headline,
        "reasons": reasons,
        "score": score,
        "remaining_exemption": ts.remaining_exemption,
        "months_to_fy_end": months_left,
        "next_fy_date": next_fy_date,
    }


# ---------------------------------------------------------------------------
# Multi-FY withdrawal optimizer — dataclasses
# ---------------------------------------------------------------------------

@dataclass
class WithdrawalTranche:
    """One scheduled withdrawal slice within a single Indian financial year."""

    fy_label: str                       # e.g. "FY 2026-27"
    month_index: int                    # 1-based month offset from today
    date: datetime.date                 # calendar date of the tranche
    total_amount: float                 # rupees withdrawn in this tranche
    allocations: dict[str, float]       # {fund_name: rupees}
    realized_gain: float                # LTCG triggered by this tranche
    taxable_gain: float                 # portion above this FY's exemption
    tax: float                          # 12.5% × taxable_gain

    @property
    def net_received(self) -> float:
        return self.total_amount - self.tax

    @property
    def effective_tax_rate(self) -> float:
        if self.total_amount <= 0:
            return 0.0
        return self.tax / self.total_amount


@dataclass
class WithdrawalSchedule:
    """A complete multi-tranche withdrawal plan across one or more FYs."""

    tranches: list[WithdrawalTranche]
    total_withdrawal: float
    total_tax: float
    total_net: float
    exemption_utilization: dict[str, float]   # fy_label -> fraction in [0, 1+]
    strategy: str                             # which strategy produced this
    target_amount: float                      # original target the user asked for
    shortfall: float = 0.0                    # rupees we could not schedule

    @property
    def effective_tax_rate(self) -> float:
        if self.total_withdrawal <= 0:
            return 0.0
        return self.total_tax / self.total_withdrawal


# ---------------------------------------------------------------------------
# Multi-FY withdrawal optimizer — helpers
# ---------------------------------------------------------------------------

def fy_label_for_date(d: datetime.date) -> str:
    """Return the Indian FY label that contains the given calendar date.

    Example: 2026-04-12 -> "FY 2026-27"; 2027-03-15 -> "FY 2026-27".
    """
    if d.month >= 4:
        start = d.year
    else:
        start = d.year - 1
    end_yy = (start + 1) % 100
    return f"FY {start}-{end_yy:02d}"


def fy_anchor_months(
    portfolio: Portfolio,
    horizon_months: int,
) -> list[tuple[str, int, datetime.date]]:
    """Enumerate the FYs that fall within the horizon and their anchor months.

    The anchor month for the *current* FY is month 1 (today). For every later
    FY it is the month index whose calendar date is on or after that FY's
    Apr 1 boundary (computed via ``Portfolio.fy_boundary_months``).

    Returns a list of ``(fy_label, anchor_month_index, anchor_date)`` tuples
    in chronological order, covering only FYs whose anchor lies within
    ``[1, horizon_months]``.
    """
    today = portfolio.as_of_date
    anchors: list[tuple[str, int, datetime.date]] = []

    # Current FY: anchor is "today" (month 1).
    anchors.append((fy_label_for_date(today), 1, today))

    for fy_m in portfolio.fy_boundary_months(horizon_months):
        anchor_date = today + datetime.timedelta(days=30 * int(fy_m))
        anchors.append((fy_label_for_date(anchor_date), int(fy_m), anchor_date))

    # De-duplicate consecutive identical labels (defensive — shouldn't happen).
    deduped: list[tuple[str, int, datetime.date]] = []
    seen_labels: set[str] = set()
    for label, m, d in anchors:
        if label in seen_labels:
            continue
        seen_labels.add(label)
        deduped.append((label, m, d))
    return deduped


def _projected_portfolio_value_at_month(
    portfolio: Portfolio,
    paths: dict[str, np.ndarray],
    month_index: int,
    risk_aware: bool,
) -> dict[str, float]:
    """Return per-fund projected value at month_index using p50 (or p10).

    ``paths[fund_name]`` has shape (n_samples, n_months). ``month_index`` is
    1-based and clamped to the available horizon.
    """
    percentile = 10 if risk_aware else 50
    n_months_available = next(iter(paths.values())).shape[1]
    idx = max(0, min(int(month_index) - 1, n_months_available - 1))
    return {
        f.name: float(np.percentile(paths[f.name][:, idx], percentile))
        for f in portfolio.funds
    }


# ---------------------------------------------------------------------------
# Multi-FY withdrawal optimizer — strategies
# ---------------------------------------------------------------------------

def _build_tranche(
    portfolio: Portfolio,
    fy_label: str,
    month_index: int,
    anchor_date: datetime.date,
    tranche_amount: float,
    proj_at_anchor: dict[str, float],
    fy_exemption: float,
) -> WithdrawalTranche:
    """Materialize a single tranche given an anchor month and amount."""
    if tranche_amount <= 0:
        return WithdrawalTranche(
            fy_label=fy_label,
            month_index=month_index,
            date=anchor_date,
            total_amount=0.0,
            allocations={f.name: 0.0 for f in portfolio.funds},
            realized_gain=0.0,
            taxable_gain=0.0,
            tax=0.0,
        )

    allocations = suggest_proportional_split(
        portfolio, tranche_amount, proj_at_anchor
    )
    fresh_state = TaxState(
        fy_exemption_limit=fy_exemption, already_realized=0.0
    )
    info = compute_portfolio_withdrawal_tax(
        portfolio,
        allocations,
        proj_at_anchor,
        tax_state_override=fresh_state,
    )
    return WithdrawalTranche(
        fy_label=fy_label,
        month_index=month_index,
        date=anchor_date,
        total_amount=tranche_amount,
        allocations=allocations,
        realized_gain=info["total_realized_gain"],
        taxable_gain=info["taxable_gain"],
        tax=info["total_tax"],
    )


def _tax_minimizing_schedule(
    portfolio: Portfolio,
    target_amount: float,
    horizon_months: int,
    paths: dict[str, np.ndarray],
    risk_aware: bool,
) -> WithdrawalSchedule:
    """Greedy: fill each FY's exemption exactly, in chronological order."""
    anchors = fy_anchor_months(portfolio, horizon_months)
    if not anchors:
        return WithdrawalSchedule(
            tranches=[],
            total_withdrawal=0.0,
            total_tax=0.0,
            total_net=0.0,
            exemption_utilization={},
            strategy="tax_minimizing",
            target_amount=target_amount,
            shortfall=target_amount,
        )

    remaining = float(target_amount)
    tranches: list[WithdrawalTranche] = []

    for i, (fy_label, anchor_m, anchor_d) in enumerate(anchors):
        if remaining <= 0:
            break

        proj = _projected_portfolio_value_at_month(
            portfolio, paths, anchor_m, risk_aware
        )
        total_pv = sum(proj.values())
        total_cost = sum(f.invested for f in portfolio.funds)
        if total_pv <= 0:
            blended_gr = 0.0
        else:
            blended_gr = max(0.0, (total_pv - total_cost) / total_pv)

        # Current FY uses the live remaining exemption; future FYs reset.
        if i == 0:
            fy_exemption = portfolio.tax_state.remaining_exemption
            fy_limit = portfolio.tax_state.fy_exemption_limit
        else:
            fy_exemption = portfolio.tax_state.fy_exemption_limit
            fy_limit = portfolio.tax_state.fy_exemption_limit

        if blended_gr > 0:
            max_zero_tax = fy_exemption / blended_gr
        else:
            max_zero_tax = remaining  # no gain → no tax regardless

        tranche_amount = min(max_zero_tax, remaining)
        tranche = _build_tranche(
            portfolio, fy_label, anchor_m, anchor_d,
            tranche_amount, proj, fy_limit,
        )
        tranches.append(tranche)
        remaining -= tranche_amount

    # Spill any leftover into the last FY at 12.5%.
    if remaining > 0 and tranches:
        last = tranches[-1]
        proj = _projected_portfolio_value_at_month(
            portfolio, paths, last.month_index, risk_aware
        )
        new_total = last.total_amount + remaining
        merged = _build_tranche(
            portfolio, last.fy_label, last.month_index, last.date,
            new_total, proj, portfolio.tax_state.fy_exemption_limit,
        )
        tranches[-1] = merged
        remaining = 0.0

    total_withdrawal = sum(t.total_amount for t in tranches)
    total_tax = sum(t.tax for t in tranches)
    total_net = total_withdrawal - total_tax

    exemption_util: dict[str, float] = {}
    for t in tranches:
        cap = portfolio.tax_state.fy_exemption_limit
        used = min(t.realized_gain, cap)
        exemption_util[t.fy_label] = used / cap if cap > 0 else 0.0

    return WithdrawalSchedule(
        tranches=tranches,
        total_withdrawal=total_withdrawal,
        total_tax=total_tax,
        total_net=total_net,
        exemption_utilization=exemption_util,
        strategy="tax_minimizing",
        target_amount=target_amount,
        shortfall=max(0.0, target_amount - total_withdrawal),
    )


def optimize_multi_fy_withdrawal(
    portfolio: Portfolio,
    target_amount: float,
    horizon_months: int,
    projected_paths: dict[str, np.ndarray],
    strategy: Literal[
        "tax_minimizing", "equal_split", "front_loaded", "back_loaded"
    ] = "tax_minimizing",
    risk_aware: bool = False,
) -> WithdrawalSchedule:
    """Compute a multi-FY withdrawal schedule for ``target_amount``.

    Parameters
    ----------
    portfolio : Portfolio
        Live portfolio with cost basis, current values, FY tax state.
    target_amount : float
        Total rupees the user wants to withdraw across the horizon.
    horizon_months : int
        Number of months from today to plan over (1 ≤ h ≤ 60 typically).
    projected_paths : dict[str, np.ndarray]
        Per-fund posterior-predictive value paths, shape (n_samples, n_months).
        Must include each fund name in ``portfolio.funds``. ``"total"`` is
        ignored — totals are recomputed per FY anchor.
    strategy : Literal[...]
        ``"tax_minimizing"`` (default) — greedy fill of each FY's exemption.
        ``"equal_split"``  — divide target evenly across FYs in horizon.
        ``"front_loaded"`` — withdraw all in the current FY (single tranche).
        ``"back_loaded"``  — withdraw all in the last FY of the horizon.
    risk_aware : bool
        If True, projected values use the p10 (pessimistic) percentile
        instead of the p50 median. Tightens the zero-tax window.
    """
    if target_amount <= 0:
        return WithdrawalSchedule(
            tranches=[], total_withdrawal=0.0, total_tax=0.0, total_net=0.0,
            exemption_utilization={}, strategy=strategy,
            target_amount=target_amount, shortfall=0.0,
        )

    if strategy == "tax_minimizing":
        return _tax_minimizing_schedule(
            portfolio, target_amount, horizon_months,
            projected_paths, risk_aware,
        )
    if strategy == "equal_split":
        return _equal_split_schedule(
            portfolio, target_amount, horizon_months,
            projected_paths, risk_aware,
        )
    if strategy == "front_loaded":
        return _front_loaded_schedule(
            portfolio, target_amount, horizon_months,
            projected_paths, risk_aware,
        )
    if strategy == "back_loaded":
        return _back_loaded_schedule(
            portfolio, target_amount, horizon_months,
            projected_paths, risk_aware,
        )
    raise ValueError(f"Unknown strategy: {strategy!r}")


def _equal_split_schedule(
    portfolio: Portfolio,
    target_amount: float,
    horizon_months: int,
    paths: dict[str, np.ndarray],
    risk_aware: bool,
) -> WithdrawalSchedule:
    """Divide target evenly across all FYs whose anchor falls in the horizon."""
    anchors = fy_anchor_months(portfolio, horizon_months)
    if not anchors:
        return WithdrawalSchedule(
            tranches=[], total_withdrawal=0.0, total_tax=0.0, total_net=0.0,
            exemption_utilization={}, strategy="equal_split",
            target_amount=target_amount, shortfall=target_amount,
        )

    per_tranche = float(target_amount) / len(anchors)
    tranches: list[WithdrawalTranche] = []
    for fy_label, anchor_m, anchor_d in anchors:
        proj = _projected_portfolio_value_at_month(
            portfolio, paths, anchor_m, risk_aware
        )
        tranches.append(_build_tranche(
            portfolio, fy_label, anchor_m, anchor_d,
            per_tranche, proj, portfolio.tax_state.fy_exemption_limit,
        ))

    total_withdrawal = sum(t.total_amount for t in tranches)
    total_tax = sum(t.tax for t in tranches)
    exemption_util = {
        t.fy_label: min(
            t.realized_gain, portfolio.tax_state.fy_exemption_limit
        ) / portfolio.tax_state.fy_exemption_limit
        for t in tranches
    }
    return WithdrawalSchedule(
        tranches=tranches,
        total_withdrawal=total_withdrawal,
        total_tax=total_tax,
        total_net=total_withdrawal - total_tax,
        exemption_utilization=exemption_util,
        strategy="equal_split",
        target_amount=target_amount,
        shortfall=max(0.0, target_amount - total_withdrawal),
    )


def _front_loaded_schedule(
    portfolio: Portfolio,
    target_amount: float,
    horizon_months: int,
    paths: dict[str, np.ndarray],
    risk_aware: bool,
) -> WithdrawalSchedule:
    """Withdraw the entire target in the current FY at month 1."""
    anchors = fy_anchor_months(portfolio, horizon_months)
    if not anchors:
        return WithdrawalSchedule(
            tranches=[], total_withdrawal=0.0, total_tax=0.0, total_net=0.0,
            exemption_utilization={}, strategy="front_loaded",
            target_amount=target_amount, shortfall=target_amount,
        )
    fy_label, anchor_m, anchor_d = anchors[0]
    proj = _projected_portfolio_value_at_month(
        portfolio, paths, anchor_m, risk_aware
    )
    tranche = _build_tranche(
        portfolio, fy_label, anchor_m, anchor_d,
        float(target_amount), proj, portfolio.tax_state.fy_exemption_limit,
    )
    return WithdrawalSchedule(
        tranches=[tranche],
        total_withdrawal=tranche.total_amount,
        total_tax=tranche.tax,
        total_net=tranche.net_received,
        exemption_utilization={
            tranche.fy_label: min(
                tranche.realized_gain, portfolio.tax_state.fy_exemption_limit
            ) / portfolio.tax_state.fy_exemption_limit
        },
        strategy="front_loaded",
        target_amount=target_amount,
        shortfall=0.0,
    )


def _back_loaded_schedule(
    portfolio: Portfolio,
    target_amount: float,
    horizon_months: int,
    paths: dict[str, np.ndarray],
    risk_aware: bool,
) -> WithdrawalSchedule:
    """Withdraw the entire target in the LAST FY of the horizon."""
    anchors = fy_anchor_months(portfolio, horizon_months)
    if not anchors:
        return WithdrawalSchedule(
            tranches=[], total_withdrawal=0.0, total_tax=0.0, total_net=0.0,
            exemption_utilization={}, strategy="back_loaded",
            target_amount=target_amount, shortfall=target_amount,
        )
    fy_label, anchor_m, anchor_d = anchors[-1]
    proj = _projected_portfolio_value_at_month(
        portfolio, paths, anchor_m, risk_aware
    )
    tranche = _build_tranche(
        portfolio, fy_label, anchor_m, anchor_d,
        float(target_amount), proj, portfolio.tax_state.fy_exemption_limit,
    )
    return WithdrawalSchedule(
        tranches=[tranche],
        total_withdrawal=tranche.total_amount,
        total_tax=tranche.tax,
        total_net=tranche.net_received,
        exemption_utilization={
            tranche.fy_label: min(
                tranche.realized_gain, portfolio.tax_state.fy_exemption_limit
            ) / portfolio.tax_state.fy_exemption_limit
        },
        strategy="back_loaded",
        target_amount=target_amount,
        shortfall=0.0,
    )
