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
from typing import Optional


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
