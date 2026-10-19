"""Pytest configuration for portfolio_app.

Adds the parent directory to sys.path so tests can `import portfolio` as a
top-level module (matching the way `app.py` imports it under `streamlit run`).
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import numpy as np
import pytest

# Make `portfolio` and `models` importable as top-level modules.
PORTFOLIO_APP_DIR = Path(__file__).resolve().parent.parent
if str(PORTFOLIO_APP_DIR) not in sys.path:
    sys.path.insert(0, str(PORTFOLIO_APP_DIR))

from portfolio import FundHolding, Portfolio, TaxState  # noqa: E402


@pytest.fixture
def sample_portfolio() -> Portfolio:
    """A two-fund portfolio anchored at 12 Apr 2026 (FY 26-27, fresh start).

    Total invested: 15,78,521  Total current value: 23,72,671
    Blended gain ratio: ~0.3431  (8,94,150 / 23,72,671)
    """
    return Portfolio(
        funds=[
            FundHolding(
                name="Parag Parikh Flexi Cap",
                invested=903_555.0,
                current_value=1_396_100.0,
                scheme_code=122639,
            ),
            FundHolding(
                name="ICICI Pru Large Cap",
                invested=674_966.0,
                current_value=976_571.0,
                scheme_code=120586,
            ),
        ],
        tax_state=TaxState(fy_exemption_limit=125_000.0, already_realized=0.0),
        as_of_date=datetime.date(2026, 4, 12),
    )


@pytest.fixture
def mock_projected_paths(sample_portfolio: Portfolio) -> dict[str, np.ndarray]:
    """Deterministic linear-growth paths covering 60 months.

    Each fund grows by 1% per month from its current value (compounded
    geometrically). Returns shape (n_samples=200, n_months=60) so that
    ``np.percentile(paths, 50, axis=0)`` exactly equals the deterministic line.
    """
    n_samples = 200
    n_months = 60
    monthly_factor = 1.01  # 1% per month, deterministic

    paths: dict[str, np.ndarray] = {}
    total = np.zeros((n_samples, n_months))
    for fund in sample_portfolio.funds:
        traj = fund.current_value * (monthly_factor ** np.arange(1, n_months + 1))
        arr = np.tile(traj, (n_samples, 1))
        paths[fund.name] = arr
        total += arr
    paths["total"] = total
    return paths
