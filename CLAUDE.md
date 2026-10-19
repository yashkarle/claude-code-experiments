# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Layout

This repo hosts **two independent projects** that share no code:

1. **`gmail_monitor.py`** (repo root) — Gmail API + Twilio phone-call alerter. Uses its own `requirements.txt` at the repo root and its own venv at `venv/`.
2. **`portfolio_app/`** — Streamlit + PyMC NRI mutual-fund withdrawal planner. Has its own `portfolio_app/requirements.txt` and venv at `venv_portfolio_app/`.

When working on one project, do not touch the other's files, venv, or requirements.

---

## Project 1 — Gmail Monitor (`gmail_monitor.py`)

Single-file Python script that polls Gmail for emails from configured senders and triggers a Twilio voice call. State is persisted to `notified_emails.json` (tracks which message IDs have already alerted) and `token.pickle` (Gmail OAuth refresh token).

**Run**
```bash
pip install -r requirements.txt         # root requirements.txt
python3 gmail_monitor.py
```

Configuration is environment-driven via `.env` (see `.env.example`). First run opens a browser for Gmail OAuth consent and writes `token.pickle`. See `SETUP.md` for the Gmail API + Twilio credential bootstrap and `DEPLOYMENT.md` for 24/7 hosting options.

---

## Project 2 — Portfolio Withdrawal Planner (`portfolio_app/`)

Streamlit web app that gives an NRI user probabilistic guidance on when and how much to withdraw from an Indian equity mutual fund portfolio, with LTCG tax impact.

### Commands

```bash
# Install (use the dedicated venv to avoid clashing with gmail_monitor deps)
python3 -m venv venv_portfolio_app
source venv_portfolio_app/bin/activate
pip install -r portfolio_app/requirements.txt

# Run
streamlit run portfolio_app/app.py
```

There are no tests, linters, or build steps configured. First page load takes ~20–30 s while MCMC samples; subsequent reruns use Streamlit's cache.

### Architecture

Four-module layering. `app.py` imports `portfolio`, `data_sources`,
`factor_model`, and `withdrawal_planner` as top-level modules, so
`streamlit run` must be invoked from the repo root with the file path
`portfolio_app/app.py` (Streamlit adds the script's directory to `sys.path`).

```
portfolio.py ────────┐
data_sources.py ─────┤
factor_model.py ─────┼──► app.py  (Streamlit UI, Plotly charts, caching)
withdrawal_planner.py ┘
```

**`portfolio.py`** — Pure-Python dataclasses (`FundHolding`, `TaxState`, `Portfolio`)
and tax math. `FundHolding` carries `invested`, `current_value`, and an
mfapi.in `scheme_code` for NAV fetch. All holdings are treated as LTCG
(₹1.25L exemption per FY, 12.5% above). The `is_long_term` flag and `xirr`
field from earlier versions have been removed — LTCG is the only tax path
supported, and returns are calibrated from NAV history directly.

**`data_sources.py`** — NAV fetcher (mfapi.in) and market factor fetcher
(yfinance: NIFTY, SENSEX, India VIX, gold, USD/INR, crude), both backed
by a parquet cache under `portfolio_app/.cache/` with a TTL check.
`load_history_for_funds` returns NAV + factor DataFrames aligned to a
common business-day index with forward-fill. News/sentiment is **not**
included in MVP — India VIX serves as a regime proxy.

**`factor_model.py`** — Bayesian linear factor model (PyMC v5). Per-fund
daily returns are regressed on 6 market factors with hierarchical
non-centered coefficients across the 2 funds:

    r_i[t] ~ Normal(alpha_i + X[t] @ beta_i, sigma_i)
    alpha_i = group_alpha + group_alpha_sd * alpha_offset_i
    beta_i  = group_beta  + group_beta_sd  * beta_offset_i

Non-centered parameterisation is mandatory (Neal's funnel with few groups).
`run_factor_inference` must use `cores=1` — Streamlit runs in a web-server
process context, and `pm.sample`'s default multi-core forking deadlocks
there. 4 chains sequentially for r_hat / ESS diagnostics. Expected first
load ~60–120s.

Posterior predictive is **pure numpy**, not `pm.sample_posterior_predictive`.
`generate_factor_forecast` composes posterior draws with a **block
bootstrap of historical factor returns** (block_size parameter) to
preserve short-horizon autocorrelation, and returns a `(n_samples,
n_business_days, n_funds)` tensor per fund plus a `'total'` sum.

**`withdrawal_planner.py`** — Pure-numpy helpers to turn a `(samples, days)`
path tensor into an exit-timing table of per-day statistics
(mean/P10/P50/P90/regret prob/composite score) and a sell-today-vs-wait
recommendation. The composite score is
`(1-λ)·mean + λ·P10` where λ is the user's risk aversion.

**`app.py`** — Streamlit UI with 4 tabs (Trajectory, Withdrawal Planner,
Tax Impact, Scenarios). Non-obvious pieces:

- **Three-layer caching**: `@st.cache_resource` on `get_history` persists
  the parquet-cached DataFrames; `@st.cache_resource` on `get_factor_idata`
  persists the `InferenceData`; `@st.cache_data` on `get_long_forecast` /
  `get_short_forecast` caches the numpy forecast tensors. The first
  argument of each `@st.cache_data` helper that would break hashing is
  prefixed with `_`.
- **Two forecast horizons**: long (`N_BDAYS_LONG = 756 ≈ 3 years`) for
  Trajectory/Tax/Scenarios tabs, and short (variable, capped at ~180 days)
  for the Withdrawal Planner tab. Both share the same posterior; only the
  `n_business_days` and `block_size` arguments differ.
- **FY-boundary tax logic** (Tab 2 tax expander): withdrawal tax at the
  optimal exit day is computed against the appropriate `TaxState` depending
  on whether the exit date falls in the current or a future FY.
- **Plotly `add_vline` is unsafe on categorical (string) x-axes** — it
  tries to compute `mean()` of the strings and crashes. All FY-boundary
  markers and the "Optimal exit" marker on the Withdrawal Planner fan
  chart use `fig.add_shape()` + `fig.add_annotation()` explicitly. Do
  NOT "clean up" the shape-based markers back to `add_vline`.
- **`numpy.int64` vs `datetime.timedelta`** — month/day indices from
  `np.arange` must be cast to `int()` before passing to
  `timedelta(days=...)`.

### Dependency notes

`portfolio_app/requirements.txt` intentionally uses flexible ranges (e.g. `pymc>=5.16,<6`) because `pytensor` pins do not exist for every Python minor version. On Python 3.11, pinned versions cause "No matching distribution" errors. If you update pins, verify against the target Python version first.

---

## CI

GitHub Actions in `.github/workflows/`:
- **`claude.yml`** — `@claude` mention handler for issues and PR comments.
- **`claude-code-review.yml`** — Auto-runs Claude code review on every PR open/sync/reopen.

Both workflows apply to the whole repo. A PR touching `portfolio_app/` will still trigger review, and vice-versa.
