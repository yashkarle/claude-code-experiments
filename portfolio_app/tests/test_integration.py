"""
Integration smoke test — exercises the full data → model → forecast pipeline
using synthetic data (no network). This is SLOW (~30s) because it actually
samples PyMC, but it catches wiring bugs that unit tests miss.

Run with: pytest portfolio_app/tests/test_integration.py -v
Skip in CI fast loops: pytest -m "not slow" ...
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data_sources import _parse_mfapi_payload, align_business_days
from factor_model import FACTOR_NAMES

pytestmark = pytest.mark.slow

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def synthetic_history():
    """Build 500 business days of synthetic NAV + factors."""
    rng = np.random.default_rng(0)
    n = 500
    idx = pd.date_range("2023-01-02", periods=n, freq="B")

    factor_data = {name: rng.normal(0, 0.01, n) for name in FACTOR_NAMES}
    # Convert returns to levels
    factors_lvl = pd.DataFrame({
        k: 100 * np.cumprod(1 + v) for k, v in factor_data.items()
    }, index=idx)

    nav = pd.DataFrame({
        "Fund A": 100 * np.cumprod(1 + 0.0003 + 0.8 * factor_data["nifty"] + rng.normal(0, 0.004, n)),
        "Fund B": 100 * np.cumprod(1 + 0.0002 + 0.6 * factor_data["nifty"] + rng.normal(0, 0.004, n)),
    }, index=idx)
    return nav, factors_lvl


def test_full_pipeline(synthetic_history):
    from factor_model import (
        build_factor_model,
        compute_percentile_bands,
        generate_factor_forecast,
        prepare_training_data,
        run_factor_inference,
    )
    from withdrawal_planner import build_exit_timing_table, recommend_today

    nav, factors = synthetic_history
    fund_returns, factor_returns = prepare_training_data(nav, factors)
    model = build_factor_model(
        fund_names=list(fund_returns.columns),
        fund_returns=fund_returns.values,
        factor_returns=factor_returns.values,
    )
    # tiny sampling for speed
    idata = run_factor_inference(
        model, n_draws=100, n_tune=100, n_chains=2, target_accept=0.85
    )

    paths = generate_factor_forecast(
        idata=idata,
        fund_names=list(fund_returns.columns),
        factor_returns_history=factor_returns.values,
        current_values=np.array([150.0, 120.0]),
        n_business_days=30,
        n_samples=500,
        block_size=5,
    )
    bands = compute_percentile_bands(paths)
    assert "total" in bands
    assert bands["total"]["p10"].shape == (30,)
    assert (bands["total"]["p10"] <= bands["total"]["p50"]).all()
    assert (bands["total"]["p50"] <= bands["total"]["p90"]).all()

    table = build_exit_timing_table(paths, target_amount=200.0, risk_aversion=0.3)
    assert len(table) == 30
    rec = recommend_today(table, risk_aversion=0.3)
    assert rec["action"] in {"SELL_TODAY", "WAIT"}
