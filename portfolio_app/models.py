"""
models.py — Bayesian hierarchical model (PyMC v5) for portfolio growth forecasting.

Model overview
--------------
We have 2 funds, each with a known XIRR (annualised return).  We treat the XIRR
as a near-exact observation of the fund's *true* long-run monthly mean return,
and use a hierarchical model to share statistical strength across the two funds.

Non-centered parameterisation is used for the fund-level means to avoid the
classic "Neal's funnel" geometry that plagues hierarchical models with few groups.

Posterior predictive paths are generated via pure numpy (not pm.sample_posterior_predictive)
for speed and to avoid Streamlit/multiprocessing conflicts.
"""
from __future__ import annotations

import warnings
from typing import Optional

import arviz as az
import numpy as np
import pymc as pm

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------

def build_hierarchical_model(
    fund_names: list[str],
    observed_monthly_returns: np.ndarray,   # shape (n_funds,)
    observation_noise: float = 0.0008,      # ~0.1% monthly — XIRR is near-exact
) -> pm.Model:
    """
    Build (but do not sample) a hierarchical PyMC model.

    Generative process
    ------------------
    group_mu    ~ Normal(obs_mean, 0.003)
    group_sigma ~ HalfNormal(0.002)

    For each fund i (non-centered):
      mu_offset[i] ~ Normal(0, 1)
      mu_fund[i]   = group_mu + group_sigma * mu_offset[i]   [Deterministic]
      sigma_fund[i] ~ HalfNormal(0.045)    ← monthly vol prior (~15% annual)

    Likelihood:
      obs[i] ~ Normal(mu_fund[i], observation_noise, observed=observed_monthly_returns)
    """
    n_funds = len(fund_names)
    obs_mean = float(observed_monthly_returns.mean())

    with pm.Model(coords={"fund": fund_names}) as model:
        # --- Hyper-priors ---
        group_mu = pm.Normal("group_mu", mu=obs_mean, sigma=0.003)
        group_sigma = pm.HalfNormal("group_sigma", sigma=0.002)

        # --- Non-centered fund-level means ---
        mu_offset = pm.Normal("mu_offset", mu=0, sigma=1, dims="fund")
        mu_fund = pm.Deterministic(
            "mu_fund", group_mu + group_sigma * mu_offset, dims="fund"
        )

        # --- Fund-level volatility ---
        sigma_fund = pm.HalfNormal("sigma_fund", sigma=0.045, dims="fund")

        # --- Likelihood (XIRR treated as near-exact observation) ---
        pm.Normal(
            "obs",
            mu=mu_fund,
            sigma=observation_noise,
            observed=observed_monthly_returns,
            dims="fund",
        )

    return model


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def run_inference(
    model: pm.Model,
    n_draws: int = 1000,
    n_tune: int = 500,
    n_chains: int = 2,
    cores: int = 1,         # MUST be 1 for Streamlit (avoids multiprocessing fork)
    random_seed: int = 42,
    progressbar: bool = False,
) -> az.InferenceData:
    """
    Run NUTS sampling on the provided model.

    With cores=1, chains run sequentially (~15-25s for this model size).
    progressbar=False suppresses terminal output in Streamlit context.
    """
    with model:
        idata = pm.sample(
            draws=n_draws,
            tune=n_tune,
            chains=n_chains,
            cores=cores,
            random_seed=random_seed,
            progressbar=progressbar,
            target_accept=0.9,
        )
    return idata


# ---------------------------------------------------------------------------
# Posterior predictive path generation (pure numpy)
# ---------------------------------------------------------------------------

def generate_posterior_predictive(
    idata: az.InferenceData,
    fund_names: list[str],
    current_values: np.ndarray,   # shape (n_funds,)
    n_months: int = 36,
    n_samples: int = 2000,
    random_seed: int = 42,
) -> dict[str, np.ndarray]:
    """
    Draw n_samples trajectories per fund from the posterior predictive.

    Steps:
      1. Extract mu_fund and sigma_fund posterior arrays (chains × draws × funds).
      2. Flatten chains, subsample to n_samples.
      3. Simulate monthly compounding: value[t] = value[t-1] * (1 + r[t])
         where r[t] ~ Normal(mu_fund_s, sigma_fund_s) independently.

    Returns:
      dict mapping fund_name → ndarray(n_samples, n_months)
              and 'total'    → ndarray(n_samples, n_months)  (sum across funds)
    """
    rng = np.random.default_rng(random_seed)

    # --- Extract posterior samples ---
    # Shape: (n_chains, n_draws, n_funds)
    mu_raw = idata.posterior["mu_fund"].values
    sigma_raw = idata.posterior["sigma_fund"].values

    # Flatten chains → (n_chains*n_draws, n_funds)
    n_chains_post, n_draws_post, _ = mu_raw.shape
    mu_flat = mu_raw.reshape(n_chains_post * n_draws_post, len(fund_names))
    sigma_flat = sigma_raw.reshape(n_chains_post * n_draws_post, len(fund_names))

    # Subsample
    total_post = len(mu_flat)
    idx = rng.choice(total_post, size=min(n_samples, total_post), replace=False)
    mu_s = mu_flat[idx]      # (n_samples, n_funds)
    sigma_s = sigma_flat[idx]

    # --- Simulate monthly returns: (n_samples, n_funds, n_months) ---
    monthly_r = rng.normal(
        loc=mu_s[:, :, np.newaxis],
        scale=sigma_s[:, :, np.newaxis],
        size=(len(idx), len(fund_names), n_months),
    )

    # Compound growth: value_paths[s, i, t] = current_value[i] * prod(1+r[s,i,0:t+1])
    growth_factors = np.cumprod(1.0 + monthly_r, axis=2)
    value_paths = current_values[np.newaxis, :, np.newaxis] * growth_factors
    # shape: (n_samples, n_funds, n_months)

    result: dict[str, np.ndarray] = {}
    for k, name in enumerate(fund_names):
        result[name] = value_paths[:, k, :]  # (n_samples, n_months)
    result["total"] = value_paths.sum(axis=1)  # (n_samples, n_months)

    return result


# ---------------------------------------------------------------------------
# Percentile bands
# ---------------------------------------------------------------------------

def compute_percentile_bands(
    paths: dict[str, np.ndarray],
    percentiles: tuple[int, int, int] = (10, 50, 90),
) -> dict[str, dict[str, np.ndarray]]:
    """
    For each key in `paths`, compute percentile bands along axis=0 (samples).

    Returns:
      {name: {'p10': ndarray(n_months), 'p50': ..., 'p90': ...}}
    """
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
# Scenario paths (Bull / Base / Bear)
# ---------------------------------------------------------------------------

def generate_scenario_paths(
    idata: az.InferenceData,
    fund_names: list[str],
    current_values: np.ndarray,
    n_months: int = 36,
    n_path_samples: int = 300,
    random_seed: int = 99,
) -> dict[str, dict[str, np.ndarray]]:
    """
    Stratify posterior samples by the sum of mu_fund across funds, then
    compute the median trajectory for each stratum.

    Bull  = top 25% of sum(mu_fund)
    Base  = middle 40-60th percentile
    Bear  = bottom 25% of sum(mu_fund)

    Returns: {scenario: {'total': ndarray(n_months), fund_name: ndarray(n_months), ...}}
    """
    rng = np.random.default_rng(random_seed)

    mu_raw = idata.posterior["mu_fund"].values
    sigma_raw = idata.posterior["sigma_fund"].values
    n_chains_post, n_draws_post, _ = mu_raw.shape
    mu_flat = mu_raw.reshape(n_chains_post * n_draws_post, len(fund_names))
    sigma_flat = sigma_raw.reshape(n_chains_post * n_draws_post, len(fund_names))

    mu_sum = mu_flat.sum(axis=1)  # scalar score per posterior sample
    p25, p40, p60, p75 = np.percentile(mu_sum, [25, 40, 60, 75])

    strata = {
        "bull": np.where(mu_sum >= p75)[0],
        "base": np.where((mu_sum >= p40) & (mu_sum <= p60))[0],
        "bear": np.where(mu_sum <= p25)[0],
    }

    scenarios: dict[str, dict[str, np.ndarray]] = {}

    for scenario_name, indices in strata.items():
        # Subsample within stratum
        pick = rng.choice(indices, size=min(n_path_samples, len(indices)), replace=False)
        mu_s = mu_flat[pick]
        sigma_s = sigma_flat[pick]

        monthly_r = rng.normal(
            loc=mu_s[:, :, np.newaxis],
            scale=sigma_s[:, :, np.newaxis],
            size=(len(pick), len(fund_names), n_months),
        )
        growth = np.cumprod(1.0 + monthly_r, axis=2)
        value_paths = current_values[np.newaxis, :, np.newaxis] * growth

        result: dict[str, np.ndarray] = {}
        for k, name in enumerate(fund_names):
            result[name] = np.median(value_paths[:, k, :], axis=0)
        result["total"] = np.median(value_paths.sum(axis=1), axis=0)

        scenarios[scenario_name] = result

    return scenarios


# ---------------------------------------------------------------------------
# Withdrawal probability
# ---------------------------------------------------------------------------

def compute_withdrawal_probability(
    paths: dict[str, np.ndarray],
    target_amount: float,
    threshold: float = 0.80,
) -> tuple[np.ndarray, int]:
    """
    At each future month, compute P(portfolio_total >= target_amount).

    Returns:
      p_sufficient : ndarray(n_months) — probability at each month
      first_month  : int — first month (1-indexed) where p >= threshold, or -1
    """
    total_paths = paths["total"]  # (n_samples, n_months)
    p_sufficient = (total_paths >= target_amount).mean(axis=0)

    passing = np.where(p_sufficient >= threshold)[0]
    first_month = int(passing[0]) + 1 if len(passing) > 0 else -1

    return p_sufficient, first_month
