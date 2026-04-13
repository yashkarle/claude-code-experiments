"""Tests for factor_model.py — model build sanity, NOT posterior correctness."""
import numpy as np
import pandas as pd
import pytest

from factor_model import (
    FACTOR_NAMES,
    build_factor_model,
    prepare_training_data,
)


def _synthetic_history(n_days: int = 500, seed: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-01", periods=n_days, freq="B")

    factor_data = {name: rng.normal(0, 0.01, n_days) for name in FACTOR_NAMES}
    factors = pd.DataFrame(factor_data, index=idx)

    # Two synthetic funds with known betas
    nav_a = 100 * np.cumprod(1 + 0.0003 + 0.8 * factors["nifty"] + rng.normal(0, 0.003, n_days))
    nav_b = 100 * np.cumprod(1 + 0.0002 + 0.6 * factors["nifty"] + rng.normal(0, 0.003, n_days))
    nav = pd.DataFrame({"Fund A": nav_a, "Fund B": nav_b}, index=idx)
    return nav, factors


def test_prepare_training_data_shapes():
    nav, factors = _synthetic_history()
    fund_returns, factor_returns = prepare_training_data(nav, factors)
    assert fund_returns.shape[0] == factor_returns.shape[0]
    assert fund_returns.shape[1] == 2
    assert factor_returns.shape[1] == len(FACTOR_NAMES)
    # returns are tiny
    assert fund_returns.abs().max().max() < 0.5


def test_build_factor_model_creates_pymc_model():
    import pymc as pm
    nav, factors = _synthetic_history()
    fund_returns, factor_returns = prepare_training_data(nav, factors)

    model = build_factor_model(
        fund_names=list(fund_returns.columns),
        fund_returns=fund_returns.values,
        factor_returns=factor_returns.values,
    )
    assert isinstance(model, pm.Model)
    rv_names = {rv.name for rv in model.free_RVs}
    # Expect hyperpriors + fund-level non-centered offsets
    assert "alpha_offset" in rv_names
    assert "beta_offset" in rv_names
    assert "sigma_fund" in rv_names
    assert "group_alpha" in rv_names
    assert "group_beta" in rv_names


def test_model_build_respects_coords():
    nav, factors = _synthetic_history()
    fund_returns, factor_returns = prepare_training_data(nav, factors)
    model = build_factor_model(
        fund_names=["Fund A", "Fund B"],
        fund_returns=fund_returns.values,
        factor_returns=factor_returns.values,
    )
    assert model.coords["fund"] == ("Fund A", "Fund B")
    assert model.coords["factor"] == tuple(FACTOR_NAMES)


def test_simulate_factor_paths_shape():
    """Block-bootstrap should return shape (n_sims, n_days, n_factors)."""
    from factor_model import simulate_factor_paths

    nav, factors = _synthetic_history(n_days=500)
    _, factor_returns = prepare_training_data(nav, factors)
    sims = simulate_factor_paths(
        factor_returns.values, n_sims=50, n_days=30, block_size=5, seed=7
    )
    assert sims.shape == (50, 30, len(FACTOR_NAMES))


def test_generate_factor_forecast_shapes():
    from factor_model import (
        build_factor_model,
        generate_factor_forecast,
        prepare_training_data,
        run_factor_inference,
    )

    nav, factors = _synthetic_history(n_days=300)
    fund_returns, factor_returns = prepare_training_data(nav, factors)
    model = build_factor_model(
        fund_names=list(fund_returns.columns),
        fund_returns=fund_returns.values,
        factor_returns=factor_returns.values,
    )
    # Sample VERY cheaply — this is a smoke test, not a correctness test
    idata = run_factor_inference(
        model, n_draws=50, n_tune=50, n_chains=2, target_accept=0.8
    )

    paths = generate_factor_forecast(
        idata=idata,
        fund_names=list(fund_returns.columns),
        factor_returns_history=factor_returns.values,
        current_values=np.array([100.0, 200.0]),
        n_business_days=15,
        n_samples=100,
        block_size=5,
        random_seed=3,
    )
    assert set(paths.keys()) == {"Fund A", "Fund B", "total"}
    assert paths["Fund A"].shape == (100, 15)
    assert paths["total"].shape == (100, 15)
    # total = sum of funds
    np.testing.assert_allclose(
        paths["total"], paths["Fund A"] + paths["Fund B"], rtol=1e-10
    )


def test_current_factor_regime_returns_dict():
    from factor_model import current_factor_regime

    nav, factors = _synthetic_history(n_days=200)
    summary = current_factor_regime(factors, window=20)
    assert "nifty_trailing_vol_20d" in summary
    assert "vix_level" in summary
    assert "usdinr_mom_20d" in summary
    assert all(isinstance(v, float) for v in summary.values())
