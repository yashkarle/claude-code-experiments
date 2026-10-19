"""Tests for the Multi-FY withdrawal optimizer (portfolio.optimize_multi_fy_withdrawal)."""
from __future__ import annotations

import datetime

import numpy as np
import pytest

from portfolio import (
    Portfolio,
    TaxState,
    fy_anchor_months,
    fy_label_for_date,
    optimize_multi_fy_withdrawal,
)


# ---------------------------------------------------------------------------
# Test 1: single-FY target within zero-tax capacity → one tranche, zero tax
# ---------------------------------------------------------------------------

def test_single_fy_within_capacity_zero_tax(sample_portfolio, mock_projected_paths):
    # Blended gain ratio at month 1 ~= 0.3431
    # Zero-tax capacity ≈ 1,25,000 / 0.3431 ≈ ₹3,64,341
    sched = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=300_000.0,
        horizon_months=11,  # < 12, stays inside FY 26-27
        projected_paths=mock_projected_paths,
        strategy="tax_minimizing",
    )
    assert len(sched.tranches) == 1
    assert sched.tranches[0].fy_label == "FY 2026-27"
    assert sched.total_tax == pytest.approx(0.0, abs=1.0)
    assert sched.total_withdrawal == pytest.approx(300_000.0, abs=1.0)
    assert sched.shortfall == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Test 2: target exactly equal to first-FY zero-tax capacity
# ---------------------------------------------------------------------------

def test_target_equals_zero_tax_capacity(sample_portfolio, mock_projected_paths):
    # Compute the exact zero-tax capacity for FY 26-27 month 1.
    fund_pp = sample_portfolio.funds[0]
    fund_ic = sample_portfolio.funds[1]
    pv_pp = fund_pp.current_value * 1.01
    pv_ic = fund_ic.current_value * 1.01
    total_pv = pv_pp + pv_ic
    total_cost = fund_pp.invested + fund_ic.invested
    blended_gr = (total_pv - total_cost) / total_pv
    capacity = 125_000.0 / blended_gr

    sched = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=capacity,
        horizon_months=11,
        projected_paths=mock_projected_paths,
        strategy="tax_minimizing",
    )
    assert len(sched.tranches) == 1
    # The tranche should fill exactly the exemption (tax ≈ 0).
    assert sched.total_tax == pytest.approx(0.0, abs=1.0)
    assert sched.tranches[0].total_amount == pytest.approx(capacity, rel=1e-6)


# ---------------------------------------------------------------------------
# Test 3: target = 2x single-FY capacity over 24 months → two tranches, zero tax
# ---------------------------------------------------------------------------

def test_two_fy_split_zero_tax(sample_portfolio, mock_projected_paths):
    # Use a conservative target known to fit inside two FY zero-tax windows.
    target = 600_000.0
    sched = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=target,
        horizon_months=24,  # spans FY 26-27 and FY 27-28
        projected_paths=mock_projected_paths,
        strategy="tax_minimizing",
    )
    assert len(sched.tranches) == 2
    fy_labels = [t.fy_label for t in sched.tranches]
    assert fy_labels == ["FY 2026-27", "FY 2027-28"]
    assert sched.total_tax == pytest.approx(0.0, abs=1.0)
    assert sched.total_withdrawal == pytest.approx(target, abs=1.0)
    # First tranche fills FY26-27 capacity exactly; second carries the remainder.
    assert sched.tranches[0].total_amount > 0
    assert sched.tranches[1].total_amount > 0


# ---------------------------------------------------------------------------
# Test 4: target exceeding all-FY zero-tax capacity → overflow taxed in last FY
# ---------------------------------------------------------------------------

def test_overflow_into_last_fy(sample_portfolio, mock_projected_paths):
    # ₹50L target across 36 months — far above 3 × per-FY capacity.
    target = 5_000_000.0
    sched = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=target,
        horizon_months=36,
        projected_paths=mock_projected_paths,
        strategy="tax_minimizing",
    )
    # Expect 3 tranches (FY 26-27, 27-28, 28-29) with overflow on the last.
    assert len(sched.tranches) == 3
    assert sched.total_withdrawal == pytest.approx(target, abs=1.0)
    # Tax must be > 0 because target far exceeds 3 × zero-tax capacity.
    assert sched.total_tax > 0
    # The first two tranches should still be zero-tax (exemption-filled).
    assert sched.tranches[0].tax == pytest.approx(0.0, abs=1.0)
    assert sched.tranches[1].tax == pytest.approx(0.0, abs=1.0)
    # Last tranche carries all the tax.
    assert sched.tranches[2].tax > 0


# ---------------------------------------------------------------------------
# Test 5: gain-ratio growth — tranche amount shrinks per FY
# ---------------------------------------------------------------------------

def test_gain_ratio_growth_shrinks_zero_tax_window(sample_portfolio, mock_projected_paths):
    # When the optimizer cannot consume target in FY 26-27, the FY 27-28
    # tranche must be smaller than the FY 26-27 tranche because the blended
    # gain ratio has grown over the year.
    sched = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=1_500_000.0,
        horizon_months=36,
        projected_paths=mock_projected_paths,
        strategy="tax_minimizing",
    )
    # Need at least two tranches to compare.
    assert len(sched.tranches) >= 2
    # FY26-27 capacity > FY27-28 capacity strictly (gain ratio rose).
    assert sched.tranches[0].total_amount > sched.tranches[1].total_amount


# ---------------------------------------------------------------------------
# Test 6: equal_split divides exactly evenly
# ---------------------------------------------------------------------------

def test_equal_split_strategy(sample_portfolio, mock_projected_paths):
    target = 900_000.0
    sched = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=target,
        horizon_months=36,
        projected_paths=mock_projected_paths,
        strategy="equal_split",
    )
    assert len(sched.tranches) == 3
    expected = target / 3
    for t in sched.tranches:
        assert t.total_amount == pytest.approx(expected, abs=1.0)


# ---------------------------------------------------------------------------
# Test 7: risk_aware=True uses lower projected values → smaller zero-tax window
# ---------------------------------------------------------------------------

def test_risk_aware_uses_lower_projection(sample_portfolio):
    # Build paths where p10 is materially lower than p50.
    n_samples, n_months = 200, 60
    paths: dict[str, np.ndarray] = {}
    total = np.zeros((n_samples, n_months))
    rng = np.random.default_rng(7)
    for f in sample_portfolio.funds:
        # Geometric Brownian-ish: lognormal monthly multiplier.
        log_returns = rng.normal(loc=0.01, scale=0.04, size=(n_samples, n_months))
        traj = f.current_value * np.cumprod(1.0 + log_returns, axis=1)
        paths[f.name] = traj
        total += traj
    paths["total"] = total

    sched_p50 = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=600_000.0,
        horizon_months=24,
        projected_paths=paths,
        strategy="tax_minimizing",
        risk_aware=False,
    )
    sched_p10 = optimize_multi_fy_withdrawal(
        portfolio=sample_portfolio,
        target_amount=600_000.0,
        horizon_months=24,
        projected_paths=paths,
        strategy="tax_minimizing",
        risk_aware=True,
    )
    # p10 has lower projected values → lower gain ratio → LARGER zero-tax window
    # for FY 26-27.  That means tranche[0] absorbs more, leaving LESS for
    # tranche[1].  Verify the first tranche is bigger under p10.
    assert len(sched_p50.tranches) >= 2
    assert len(sched_p10.tranches) >= 2
    assert sched_p10.tranches[0].total_amount >= sched_p50.tranches[0].total_amount


# ---------------------------------------------------------------------------
# Helper tests for FY label / anchor utilities
# ---------------------------------------------------------------------------

def test_fy_label_boundary_cases():
    assert fy_label_for_date(datetime.date(2026, 4, 1)) == "FY 2026-27"
    assert fy_label_for_date(datetime.date(2026, 3, 31)) == "FY 2025-26"
    assert fy_label_for_date(datetime.date(2027, 1, 1)) == "FY 2026-27"


def test_fy_anchor_months_count(sample_portfolio):
    # 36 months from 12 Apr 2026 spans FYs 26-27, 27-28, 28-29 (3 anchors).
    anchors = fy_anchor_months(sample_portfolio, 36)
    labels = [a[0] for a in anchors]
    assert labels == ["FY 2026-27", "FY 2027-28", "FY 2028-29"]
