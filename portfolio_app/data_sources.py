"""
data_sources.py — Historical NAV and market-factor fetchers for the
Bayesian factor model.

Data sources:
- Mutual fund NAV:     https://api.mfapi.in/mf/{scheme_code}  (free, no auth)
- Market indices:      yfinance (Yahoo)
  - ^NSEI     NIFTY 50
  - ^BSESN    SENSEX
  - ^INDIAVIX India VIX (regime proxy — also see "Future Stretch" section)
  - GC=F      Gold futures
  - INR=X     USD/INR
  - CL=F      Crude oil

Cache: parquet files under portfolio_app/.cache/ keyed by source+symbol, with
a TTL check — avoids refetching on every Streamlit rerun.

Future stretch (NOT in MVP): plug in a news sentiment score from GDELT or
NewsAPI as an additional factor. We document the regime-proxy trade-off:
using India VIX alone captures market-implied uncertainty but misses
idiosyncratic headline shocks (e.g., RBI surprises, geopolitical events).
See `TODO-future-stretch.md` in the repo for design notes.
"""
from __future__ import annotations

import datetime
import json
import time
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import requests

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

MFAPI_BASE = "https://api.mfapi.in/mf"

# Recorded fixture files used as offline fallback when mfapi.in is unreachable
# and no parquet cache exists yet. Keys are scheme codes.
_FIXTURE_DIR = Path(__file__).parent / "tests" / "fixtures"
_OFFLINE_FIXTURES: dict[int, str] = {
    122639: "pp_flexi_cap.json",
    120586: "icici_large_cap.json",
}

# Yahoo tickers — kept as module constants so tests can patch them
INDEX_TICKERS = {
    "nifty": "^NSEI",
    "sensex": "^BSESN",
    "vix": "^INDIAVIX",
    "gold": "GC=F",
    "usdinr": "INR=X",
    "crude": "CL=F",
}


# ---------------------------------------------------------------------------
# Mutual fund NAV
# ---------------------------------------------------------------------------

def _parse_mfapi_payload(payload: dict) -> pd.DataFrame:
    """Convert mfapi.in JSON payload into a sorted DataFrame indexed by date."""
    rows = payload.get("data", [])
    if not rows:
        raise ValueError("mfapi payload has no 'data' rows")
    records = [
        {
            "date": datetime.datetime.strptime(r["date"], "%d-%m-%Y").date(),
            "nav": float(r["nav"]),
        }
        for r in rows
    ]
    df = pd.DataFrame.from_records(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df[["nav"]]


def load_nav_from_fixture(path: Path) -> pd.DataFrame:
    """Test helper — load a recorded mfapi payload from disk."""
    payload = json.loads(Path(path).read_text())
    return _parse_mfapi_payload(payload)


def fetch_fund_nav(scheme_code: int, ttl_hours: int = 24) -> pd.DataFrame:
    """
    Fetch NAV history for a mutual fund scheme, with a parquet cache keyed by
    scheme code. Returns a DataFrame with ['nav'] column, DatetimeIndex.

    If the cache file exists and is younger than `ttl_hours`, it is returned
    without a network call.
    """
    import warnings

    cache_path = CACHE_DIR / f"mf_{scheme_code}.parquet"
    if cache_path.exists():
        age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_hours < ttl_hours:
            return pd.read_parquet(cache_path)

    url = f"{MFAPI_BASE}/{scheme_code}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        df = _parse_mfapi_payload(payload)
        df.to_parquet(cache_path)
        return df
    except Exception as exc:
        # Priority 1: stale parquet cache (any age)
        if cache_path.exists():
            warnings.warn(
                f"mfapi.in request failed for scheme {scheme_code} ({exc}); "
                "serving stale parquet cache.",
                stacklevel=2,
            )
            return pd.read_parquet(cache_path)

        # Priority 2: bundled fixture file (offline cold-start fallback)
        fixture_name = _OFFLINE_FIXTURES.get(scheme_code)
        if fixture_name:
            fixture_path = _FIXTURE_DIR / fixture_name
            if fixture_path.exists():
                warnings.warn(
                    f"mfapi.in unreachable for scheme {scheme_code}; "
                    "loading bundled fixture as offline fallback. "
                    "Data is synthetic — re-run when the API recovers.",
                    stacklevel=2,
                )
                df = load_nav_from_fixture(fixture_path)
                df.to_parquet(cache_path)   # seed cache so next run is instant
                return df

        raise RuntimeError(
            f"mfapi.in unavailable for scheme {scheme_code}, no parquet cache, "
            f"and no bundled fixture. Original error: {exc}"
        ) from exc


def nav_to_daily_returns(nav_df: pd.DataFrame) -> pd.Series:
    """Compute daily simple returns: (nav_t / nav_{t-1}) - 1."""
    return nav_df["nav"].pct_change().dropna()


# ---------------------------------------------------------------------------
# Market factors (yfinance)
# ---------------------------------------------------------------------------

def fetch_index(
    ticker: str,
    start: str = "2019-01-01",
    end: Optional[str] = None,
    ttl_hours: int = 12,
) -> pd.Series:
    """
    Fetch Close price for a Yahoo ticker, with a parquet cache.
    Returns a Series indexed by date.
    """
    import yfinance as yf  # imported lazily — heavy import

    cache_path = CACHE_DIR / f"yf_{ticker.replace('^','').replace('=','')}.parquet"
    if cache_path.exists():
        age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_hours < ttl_hours:
            cached = pd.read_parquet(cache_path)
            return cached["close"]

    df = yf.download(
        ticker,
        start=start,
        end=end or datetime.date.today().isoformat(),
        progress=False,
        auto_adjust=True,
    )
    if df.empty:
        raise RuntimeError(f"yfinance returned no data for {ticker}")

    # yfinance returns a multi-column frame; pick Close
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.rename("close").astype(float)

    close.to_frame().to_parquet(cache_path)
    return close


def fetch_all_factors(
    start: str = "2019-01-01",
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch all market factors, forward-fill missing business days, return a
    wide DataFrame with one column per factor.
    """
    series = []
    for name, ticker in INDEX_TICKERS.items():
        s = fetch_index(ticker, start=start, end=end).rename(name)
        series.append(s)
    return align_business_days(series, start=start, end=end)


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------

def align_business_days(
    series_list: Iterable[pd.Series],
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Align a list of time series to a common business-day index, forward-fill
    missing days, and clip to the intersection (so no leading NaN rows).
    """
    frame = pd.concat(list(series_list), axis=1)

    # Clip to user window first
    if start is not None:
        frame = frame[frame.index >= pd.Timestamp(start)]
    if end is not None:
        frame = frame[frame.index <= pd.Timestamp(end)]

    # Build a business-day calendar over the actual span
    if frame.empty:
        return frame
    bday_idx = pd.date_range(frame.index.min(), frame.index.max(), freq="B")
    frame = frame.reindex(bday_idx).ffill()

    # Drop any leading rows where any column is still NaN (first obs before
    # one of the series existed)
    frame = frame.dropna(how="any")
    frame.index.name = "date"
    return frame


# ---------------------------------------------------------------------------
# Combined loader — everything the factor model needs
# ---------------------------------------------------------------------------

def load_history_for_funds(
    scheme_codes: dict[str, int],
    lookback_years: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load NAV + factor histories aligned to a common business-day index.

    Returns:
      nav_df       : DataFrame, columns = fund names, DatetimeIndex
      factors_df   : DataFrame, columns = factor names, DatetimeIndex
    Both are aligned to the same business-day index (intersection of windows).
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=365 * lookback_years + 30)
    start_iso = start.isoformat()
    end_iso = end.isoformat()

    nav_series = []
    for name, code in scheme_codes.items():
        nav_df = fetch_fund_nav(code)
        s = nav_df["nav"].rename(name)
        nav_series.append(s)

    factors = fetch_all_factors(start=start_iso, end=end_iso)

    combined = pd.concat(nav_series + [factors], axis=1)
    combined = combined[
        (combined.index >= pd.Timestamp(start_iso))
        & (combined.index <= pd.Timestamp(end_iso))
    ]
    bday_idx = pd.date_range(combined.index.min(), combined.index.max(), freq="B")
    combined = combined.reindex(bday_idx).ffill().dropna(how="any")
    combined.index.name = "date"

    nav_cols = list(scheme_codes.keys())
    factor_cols = list(INDEX_TICKERS.keys())
    return combined[nav_cols], combined[factor_cols]
