"""Tests for withdrawal_planner.py — exit-timing scoring."""
import numpy as np
import pytest

from withdrawal_planner import (
    ExitTimingRecord,
    build_exit_timing_table,
    recommend_today,
)


def _synthetic_paths(n_samples: int = 1000, n_days: int = 40) -> dict:
    rng = np.random.default_rng(0)
    drift = np.linspace(0, 0.02, n_days)            # trending up
    noise = rng.normal(0, 0.01, (n_samples, n_days))
    series = 1_000_000 * np.exp(drift[None, :] + noise.cumsum(axis=1))
    return {"total": series, "A": series * 0.6, "B": series * 0.4}


def test_build_exit_timing_table_shapes_and_monotonicity():
    paths = _synthetic_paths()
    table = build_exit_timing_table(paths, target_amount=1_000_000)
    assert len(table) == 40
    for row in table:
        assert isinstance(row, ExitTimingRecord)
        assert row.p10 <= row.median <= row.p90
        assert 0.0 <= row.prob_meets_target <= 1.0


def test_build_exit_timing_table_expected_value_increases_on_trend():
    paths = _synthetic_paths()
    table = build_exit_timing_table(paths, target_amount=1_000_000)
    # Trending up → later days have higher expected value
    assert table[-1].mean > table[0].mean


def test_recommend_today_wait_when_upside_outweighs_downside():
    paths = _synthetic_paths()
    table = build_exit_timing_table(paths, target_amount=1_000_000)
    rec = recommend_today(table, risk_aversion=0.5)
    assert rec["action"] in {"SELL_TODAY", "WAIT"}
    assert "reason" in rec
    assert "optimal_day_index" in rec
    assert 0 <= rec["optimal_day_index"] < len(table)


def test_recommend_today_sell_when_deadline_is_today():
    paths = _synthetic_paths(n_days=1)
    table = build_exit_timing_table(paths, target_amount=500_000)
    rec = recommend_today(table, risk_aversion=0.5)
    assert rec["action"] == "SELL_TODAY"
    assert rec["optimal_day_index"] == 0
