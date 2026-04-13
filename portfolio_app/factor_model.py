"""
factor_model.py — Historical-NAV-calibrated Bayesian factor model.

Replaces the XIRR-as-observation model in models.py. Fits per-fund daily
returns against 5 market factors (NIFTY, gold, USD/INR, VIX, crude) using
a hierarchical linear model with non-centered parameterisation.

Generative process (for each fund i, each trading day t):

    r_i[t] ~ Normal(
        alpha_i
      + beta_i   * f_nifty[t]
      + gamma_i  * f_gold[t]
      + delta_i  * f_usdinr[t]
      + eta_i    * f_vix[t]
      + zeta_i   * f_crude[t],
        sigma_i
    )

Coefficients are hierarchical across the 2 funds: each fund's coefficient
is drawn from a shared group prior (group_mean + group_sd * offset), with
`offset ~ Normal(0, 1)` for the non-centered parameterisation.

Priors are chosen small because daily excess returns are tiny (~0.05% typical
magnitude). See each `pm.Normal(..., sigma=...)` for the justification.

Sampling:
- cores=1 MANDATORY (Streamlit deadlock — see CLAUDE.md)
- 4 chains sequentially (convergence diagnostics)
- target_accept=0.95 (divergence suppression)

Expected runtime on a MacBook: ~60–120s for first load, cached thereafter
via @st.cache_resource on the caller side.
"""
from __future__ import annotations

import warnings
from typing import Optional

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Factor column order — MUST match data_sources.INDEX_TICKERS insertion order.
# Duplicated here instead of importing because factor_model must be unit-testable
# without touching the network-coupled data_sources module.
FACTOR_NAMES: tuple[str, ...] = (
    "nifty", "sensex", "vix", "gold", "usdinr", "crude",
)


def prepare_training_data(
    nav_df: pd.DataFrame,
    factors_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert aligned NAV and factor level DataFrames into daily return DataFrames
    suitable for the factor model.

    Returns:
      fund_returns   : DataFrame, shape (T-1, n_funds)
      factor_returns : DataFrame, shape (T-1, n_factors)

    VIX is handled specially: we use daily *level* change (differenced) rather
    than log return, because VIX is already a volatility measure and its %
    changes are heavy-tailed. All other factors use simple pct_change.
    """
    if not nav_df.index.equals(factors_df.index):
        raise ValueError("nav_df and factors_df must share the same index")

    fund_returns = nav_df.pct_change().dropna()

    # Keep all factors as pct_change except VIX which we first-difference then scale
    factor_returns = factors_df.pct_change()
    if "vix" in factor_returns.columns:
        # VIX: normalised first difference (Δ / rolling std so it's O(1))
        vix_diff = factors_df["vix"].diff()
        factor_returns["vix"] = vix_diff / vix_diff.rolling(60, min_periods=10).std()
    factor_returns = factor_returns.dropna()

    # Inner-join on index (first row of NAV dropped by pct_change, same for factors)
    common = fund_returns.index.intersection(factor_returns.index)
    return fund_returns.loc[common], factor_returns.loc[common]


def build_factor_model(
    fund_names: list[str],
    fund_returns: np.ndarray,      # shape (T, n_funds)
    factor_returns: np.ndarray,    # shape (T, n_factors)
) -> pm.Model:
    """
    Build the Bayesian factor model. Does not sample.

    Hierarchical structure:
      group_alpha   ~ Normal(0, 0.001)      # daily excess return, tiny
      group_alpha_sd ~ HalfNormal(0.0005)
      group_beta    ~ Normal(0, 0.5)        # factor loadings, centred near 0
      group_beta_sd ~ HalfNormal(0.5)

      alpha_i = group_alpha + group_alpha_sd * alpha_offset[i]
      beta_i[k] = group_beta[k] + group_beta_sd[k] * beta_offset[i, k]

      sigma_i ~ HalfNormal(0.02)            # ~2% daily idiosyncratic vol prior
    """
    n_funds = len(fund_names)
    n_factors = len(FACTOR_NAMES)
    if fund_returns.shape[1] != n_funds:
        raise ValueError(f"fund_returns has {fund_returns.shape[1]} cols, expected {n_funds}")
    if factor_returns.shape[1] != n_factors:
        raise ValueError(f"factor_returns has {factor_returns.shape[1]} cols, expected {n_factors}")
    if fund_returns.shape[0] != factor_returns.shape[0]:
        raise ValueError("fund_returns and factor_returns must have equal row counts")

    coords = {
        "fund": tuple(fund_names),
        "factor": FACTOR_NAMES,
        "obs": np.arange(fund_returns.shape[0]),
    }

    with pm.Model(coords=coords) as model:
        # --- Factor-observation tensor ---
        X = pm.Data("X", factor_returns, dims=("obs", "factor"))
        Y = pm.Data("Y", fund_returns, dims=("obs", "fund"))

        # --- Hyperpriors on alpha (per-fund intercept) ---
        #   Daily equity alpha is ~0.02% — sigma of 0.001 = 0.1% daily is
        #   ~3σ loose enough to let data drive the mean.
        group_alpha = pm.Normal("group_alpha", mu=0.0, sigma=0.001)
        group_alpha_sd = pm.HalfNormal("group_alpha_sd", sigma=0.0005)

        # --- Hyperpriors on beta (per-factor group mean + sd) ---
        #   Beta to NIFTY for a flexi-cap is typically 0.8–1.1; beta to gold is
        #   usually near 0. A group prior centred at 0 with sigma 0.5 is wide
        #   enough for any of these. The hierarchy pulls fund betas toward
        #   the group mean with strength 1/group_beta_sd^2.
        group_beta = pm.Normal("group_beta", mu=0.0, sigma=0.5, dims="factor")
        group_beta_sd = pm.HalfNormal("group_beta_sd", sigma=0.5, dims="factor")

        # --- Non-centered offsets ---
        alpha_offset = pm.Normal("alpha_offset", mu=0.0, sigma=1.0, dims="fund")
        beta_offset = pm.Normal(
            "beta_offset", mu=0.0, sigma=1.0, dims=("fund", "factor")
        )

        alpha = pm.Deterministic(
            "alpha", group_alpha + group_alpha_sd * alpha_offset, dims="fund"
        )
        beta = pm.Deterministic(
            "beta", group_beta + group_beta_sd * beta_offset, dims=("fund", "factor")
        )

        # --- Per-fund idiosyncratic volatility ---
        #   Expected daily residual vol ~1% for an equity fund after the
        #   market factor is accounted for. HalfNormal(sigma=0.02) puts
        #   most mass below 3%.
        sigma_fund = pm.HalfNormal("sigma_fund", sigma=0.02, dims="fund")

        # --- Likelihood: mu[obs, fund] = alpha[fund] + X[obs] @ beta[fund].T
        # X: (obs, factor)   beta: (fund, factor)   ⇒  X @ beta.T: (obs, fund)
        mu = alpha[None, :] + pm.math.dot(X, beta.T)

        pm.Normal(
            "r_obs",
            mu=mu,
            sigma=sigma_fund[None, :],
            observed=Y,
            dims=("obs", "fund"),
        )

    return model


def run_factor_inference(
    model: pm.Model,
    n_draws: int = 800,
    n_tune: int = 800,
    n_chains: int = 4,
    cores: int = 1,          # MUST be 1 — see CLAUDE.md Streamlit deadlock note
    random_seed: int = 42,
    progressbar: bool = False,
    target_accept: float = 0.95,
) -> az.InferenceData:
    """Run NUTS on the factor model. Sequential chains (cores=1 Streamlit-safe)."""
    with model:
        idata = pm.sample(
            draws=n_draws,
            tune=n_tune,
            chains=n_chains,
            cores=cores,
            random_seed=random_seed,
            progressbar=progressbar,
            target_accept=target_accept,
        )
    return idata


# ---------------------------------------------------------------------------
# Factor path simulation (historical block bootstrap)
# ---------------------------------------------------------------------------

def simulate_factor_paths(
    factor_returns_history: np.ndarray,  # (T_hist, n_factors)
    n_sims: int,
    n_days: int,
    block_size: int = 10,
    seed: int = 0,
) -> np.ndarray:
    """
    Historical block bootstrap of factor return sequences.

    We slice `n_days`-long paths by concatenating random `block_size`-long
    blocks from history. Block bootstrap preserves short-horizon autocorrelation
    (momentum, vol clustering) that an IID sample would destroy.

    Returns: ndarray of shape (n_sims, n_days, n_factors).
    """
    rng = np.random.default_rng(seed)
    T_hist, n_factors = factor_returns_history.shape
    if T_hist <= block_size:
        raise ValueError("history shorter than block_size")

    n_blocks = int(np.ceil(n_days / block_size))
    out = np.empty((n_sims, n_blocks * block_size, n_factors))

    for s in range(n_sims):
        starts = rng.integers(0, T_hist - block_size + 1, size=n_blocks)
        for b, start in enumerate(starts):
            out[s, b * block_size : (b + 1) * block_size, :] = factor_returns_history[
                start : start + block_size, :
            ]

    return out[:, :n_days, :]


# ---------------------------------------------------------------------------
# Forecast propagation: posterior × simulated factors → fund value paths
# ---------------------------------------------------------------------------

def generate_factor_forecast(
    idata: az.InferenceData,
    fund_names: list[str],
    factor_returns_history: np.ndarray,  # (T_hist, n_factors) — for bootstrap
    current_values: np.ndarray,          # (n_funds,)
    n_business_days: int = 45,
    n_samples: int = 1500,
    block_size: int = 10,
    random_seed: int = 42,
) -> dict[str, np.ndarray]:
    """
    Propagate posterior samples × bootstrapped factor paths through the factor
    model to produce forecast distributions on fund values per business day.

    Pipeline (all pure numpy — no second pm.sample_posterior_predictive call):
      1. Flatten posterior: shape (chains*draws, n_funds) for alpha and sigma;
         (chains*draws, n_funds, n_factors) for beta.
      2. Subsample n_samples posterior draws.
      3. Bootstrap n_samples factor paths, shape (n_samples, n_days, n_factors).
      4. For each sample s, day t, fund i:
           r[s, t, i] = alpha[s, i] + beta[s, i, :] @ factor_path[s, t, :]
                        + eps[s, t, i],   eps ~ Normal(0, sigma[s, i])
      5. Compound: value[s, t, i] = current_values[i] * prod(1+r[s, :t+1, i])
      6. total[s, t] = sum_i value[s, t, i]

    Returns: dict {fund_name: (n_samples, n_days), 'total': (n_samples, n_days)}
    """
    rng = np.random.default_rng(random_seed)

    alpha_raw = idata.posterior["alpha"].values          # (ch, draw, fund)
    beta_raw = idata.posterior["beta"].values            # (ch, draw, fund, factor)
    sigma_raw = idata.posterior["sigma_fund"].values     # (ch, draw, fund)

    n_ch, n_dr, n_f = alpha_raw.shape
    _, _, _, n_k = beta_raw.shape
    n_post = n_ch * n_dr

    alpha_flat = alpha_raw.reshape(n_post, n_f)
    beta_flat = beta_raw.reshape(n_post, n_f, n_k)
    sigma_flat = sigma_raw.reshape(n_post, n_f)

    take = min(n_samples, n_post)
    idx = rng.choice(n_post, size=take, replace=False)
    alpha_s = alpha_flat[idx]    # (S, F)
    beta_s = beta_flat[idx]      # (S, F, K)
    sigma_s = sigma_flat[idx]    # (S, F)

    factor_paths = simulate_factor_paths(
        factor_returns_history,
        n_sims=take,
        n_days=n_business_days,
        block_size=block_size,
        seed=random_seed + 1,
    )  # (S, T, K)

    # mu[s, t, i] = alpha[s, i] + sum_k beta[s, i, k] * factor_paths[s, t, k]
    # einsum: (S,F,K) × (S,T,K) → (S,T,F)
    mu = alpha_s[:, None, :] + np.einsum("sfk,stk->stf", beta_s, factor_paths)

    # Add idiosyncratic noise
    eps = rng.normal(
        loc=0.0,
        scale=sigma_s[:, None, :],  # broadcast over days
        size=(take, n_business_days, n_f),
    )
    daily_returns = mu + eps   # (S, T, F)

    # Compound per fund
    growth = np.cumprod(1.0 + daily_returns, axis=1)  # (S, T, F)
    values = current_values[None, None, :] * growth   # (S, T, F)

    result: dict[str, np.ndarray] = {}
    for i, name in enumerate(fund_names):
        result[name] = values[:, :, i]  # (S, T)
    result["total"] = values.sum(axis=2)  # (S, T)
    return result


def compute_percentile_bands(
    paths: dict[str, np.ndarray],
    percentiles: tuple[int, int, int] = (10, 50, 90),
) -> dict[str, dict[str, np.ndarray]]:
    """For each key, compute per-day percentile bands along the sample axis."""
    p_low, p_mid, p_high = percentiles
    bands: dict[str, dict[str, np.ndarray]] = {}
    for name, arr in paths.items():
        bands[name] = {
            f"p{p_low}": np.percentile(arr, p_low, axis=0),
            f"p{p_mid}": np.percentile(arr, p_mid, axis=0),
            f"p{p_high}": np.percentile(arr, p_high, axis=0),
        }
    return bands


# ---------------------------------------------------------------------------
# Regime summary (for UI)
# ---------------------------------------------------------------------------

def current_factor_regime(
    factors_df: pd.DataFrame,
    window: int = 20,
) -> dict[str, float]:
    """
    Compute a one-shot summary of 'what the market looks like right now'.

    Returns a dict suitable for displaying as metrics in the Scenarios tab:
      - nifty_trailing_vol_20d : realised daily vol of NIFTY returns (annualised)
      - vix_level              : latest VIX close
      - usdinr_mom_20d         : 20-day % change in USD/INR
      - gold_mom_20d           : 20-day % change in gold
      - crude_mom_20d          : 20-day % change in crude
    """
    tail = factors_df.tail(window + 1)
    out: dict[str, float] = {}

    nifty_ret = tail["nifty"].pct_change().dropna()
    out["nifty_trailing_vol_20d"] = float(nifty_ret.std() * np.sqrt(252))

    out["vix_level"] = float(tail["vix"].iloc[-1])

    for k in ("usdinr", "gold", "crude"):
        if k in factors_df.columns:
            start, end = tail[k].iloc[0], tail[k].iloc[-1]
            out[f"{k}_mom_{window}d"] = float((end / start) - 1.0)

    return out
