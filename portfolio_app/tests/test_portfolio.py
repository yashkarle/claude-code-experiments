"""Tests for portfolio.py tax math and dataclass invariants."""
import datetime

import pytest

from portfolio import (
    DEFAULT_PORTFOLIO,
    FundHolding,
    Portfolio,
    TaxState,
    compute_portfolio_withdrawal_tax,
    projected_gain_ratio,
    suggest_proportional_split,
)


def test_fund_holding_gain_and_ratio():
    f = FundHolding(name="Test", invested=100_000.0, current_value=150_000.0)
    assert f.unrealized_gain == pytest.approx(50_000.0)
    assert f.gain_ratio == pytest.approx(1 / 3)


def test_fund_holding_no_long_term_flag():
    """is_long_term was removed — all holdings are LTCG by construction."""
    f = FundHolding(name="X", invested=100.0, current_value=120.0)
    assert not hasattr(f, "is_long_term")


def test_tax_state_exemption_and_headroom():
    ts = TaxState(fy_exemption_limit=125_000.0, already_realized=40_000.0)
    assert ts.remaining_exemption == pytest.approx(85_000.0)


def test_tax_on_gain_within_exemption_is_zero():
    ts = TaxState(fy_exemption_limit=125_000.0, already_realized=0.0)
    assert ts.tax_on_gain(100_000.0) == pytest.approx(0.0)


def test_tax_on_gain_above_exemption_is_12_5_percent():
    ts = TaxState(fy_exemption_limit=125_000.0, already_realized=0.0)
    # Gain of 225,000: 125,000 exempt, 100,000 taxed at 12.5% = 12,500
    assert ts.tax_on_gain(225_000.0) == pytest.approx(12_500.0)


def test_projected_gain_ratio_grows_with_value():
    f = FundHolding(name="X", invested=100_000.0, current_value=150_000.0)
    gr_now = projected_gain_ratio(f, 150_000.0)
    gr_future = projected_gain_ratio(f, 200_000.0)
    assert gr_future > gr_now
    assert gr_future == pytest.approx(0.5)


def test_portfolio_aggregates():
    p = Portfolio(
        funds=[
            FundHolding("A", 100_000.0, 150_000.0),
            FundHolding("B", 200_000.0, 250_000.0),
        ],
        tax_state=TaxState(),
        as_of_date=datetime.date(2026, 4, 11),
    )
    assert p.total_invested == pytest.approx(300_000.0)
    assert p.total_current_value == pytest.approx(400_000.0)
    assert p.total_unrealized_gain == pytest.approx(100_000.0)
    assert p.blended_gain_ratio == pytest.approx(0.25)


def test_months_to_next_fy_from_april():
    p = Portfolio(
        funds=[FundHolding("A", 1.0, 1.0)],
        tax_state=TaxState(),
        as_of_date=datetime.date(2026, 4, 11),
    )
    # Apr 11 2026 → next FY starts Apr 1 2027 → ~355 days → 12 months
    assert 11 <= p.months_to_next_fy() <= 12


def test_proportional_split_sums_to_target():
    p = DEFAULT_PORTFOLIO
    alloc = suggest_proportional_split(p, 1_000_000.0)
    assert sum(alloc.values()) == pytest.approx(1_000_000.0)


def test_portfolio_withdrawal_tax_zero_below_exemption():
    p = Portfolio(
        funds=[FundHolding("A", 100_000.0, 200_000.0)],
        tax_state=TaxState(already_realized=0.0),
        as_of_date=datetime.date(2026, 4, 11),
    )
    # Withdraw 100k at current value 200k → gain ratio 0.5 → realised gain 50k < 125k exemption
    result = compute_portfolio_withdrawal_tax(
        p, {"A": 100_000.0}, {"A": 200_000.0}
    )
    assert result["total_tax"] == pytest.approx(0.0)
    assert result["exemption_used"] == pytest.approx(50_000.0)


def test_portfolio_withdrawal_tax_above_exemption():
    p = Portfolio(
        funds=[FundHolding("A", 100_000.0, 400_000.0)],  # 75% gain ratio
        tax_state=TaxState(already_realized=0.0),
        as_of_date=datetime.date(2026, 4, 11),
    )
    # Withdraw 400k at 400k → gain 300k; 125k exempt, 175k taxed @ 12.5% = 21,875
    result = compute_portfolio_withdrawal_tax(
        p, {"A": 400_000.0}, {"A": 400_000.0}
    )
    assert result["total_realized_gain"] == pytest.approx(300_000.0)
    assert result["total_tax"] == pytest.approx(21_875.0)
