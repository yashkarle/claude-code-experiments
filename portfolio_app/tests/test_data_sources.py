"""Tests for data_sources.py — NAV fetcher, cache, alignment."""
import datetime
import json
from pathlib import Path

import pandas as pd
import pytest

from data_sources import (
    CACHE_DIR,
    align_business_days,
    fetch_fund_nav,
    load_nav_from_fixture,
    nav_to_daily_returns,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_load_nav_from_fixture_returns_dataframe():
    df = load_nav_from_fixture(FIXTURE_DIR / "pp_flexi_cap.json")
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {"nav"}
    assert df.index.name == "date"
    assert isinstance(df.index, pd.DatetimeIndex)
    assert len(df) > 100
    assert df["nav"].dtype == float
    assert (df["nav"] > 0).all()


def test_load_nav_from_fixture_is_sorted_ascending():
    df = load_nav_from_fixture(FIXTURE_DIR / "pp_flexi_cap.json")
    assert df.index.is_monotonic_increasing


def test_nav_to_daily_returns_length_and_values():
    df = load_nav_from_fixture(FIXTURE_DIR / "pp_flexi_cap.json")
    returns = nav_to_daily_returns(df)
    assert len(returns) == len(df) - 1
    # Daily returns for equity funds are tiny
    assert returns.abs().max() < 0.25  # 25% daily move would be implausible
    assert returns.std() > 0.001       # but non-zero vol


def test_align_business_days_forward_fills_gaps():
    idx_a = pd.date_range("2024-01-01", "2024-01-10", freq="B")
    idx_b = pd.date_range("2024-01-03", "2024-01-10", freq="B")
    a = pd.Series(range(len(idx_a)), index=idx_a, name="a", dtype=float)
    b = pd.Series(range(len(idx_b)), index=idx_b, name="b", dtype=float)
    aligned = align_business_days([a, b], start="2024-01-01", end="2024-01-10")
    assert not aligned.isna().any().any()
    assert list(aligned.columns) == ["a", "b"]
    # b did not exist before 2024-01-03 → should be back-filled (or dropped)
    assert aligned.index.min() >= pd.Timestamp("2024-01-03")


def test_fetch_fund_nav_uses_cache(tmp_path, monkeypatch):
    """Second call should not hit the network."""
    monkeypatch.setattr("data_sources.CACHE_DIR", tmp_path)

    call_count = {"n": 0}

    def fake_get(url, timeout=10):
        call_count["n"] += 1
        fixture = json.loads((FIXTURE_DIR / "pp_flexi_cap.json").read_text())

        class FakeResponse:
            status_code = 200
            def json(self):
                return fixture
            def raise_for_status(self):
                pass
        return FakeResponse()

    monkeypatch.setattr("data_sources.requests.get", fake_get)

    df1 = fetch_fund_nav(scheme_code=122639, ttl_hours=24)
    df2 = fetch_fund_nav(scheme_code=122639, ttl_hours=24)

    assert call_count["n"] == 1  # Only first call hits network
    pd.testing.assert_frame_equal(df1, df2)
