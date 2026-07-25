"""Alert rule evaluation: target price, percentage drop, historical low."""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from . import db

DEFAULT_DROP_PCT = float(os.environ.get("DEFAULT_DROP_PCT", "10"))
HISTORICAL_LOW_WINDOW_DAYS = int(os.environ.get("HISTORICAL_LOW_WINDOW_DAYS", "90"))
MIN_HISTORY_DAYS_FOR_LOW_RULE = 30


@dataclass
class FiredRule:
    rule: str
    message: str


def _previous_price(product_id: int, before_history_id: int | None = None) -> float | None:
    history = db.get_price_history(product_id)
    if before_history_id is not None:
        history = [h for h in history if h["id"] < before_history_id]
    if len(history) < 1:
        return None
    return history[-1]["price"]


def _history_span_days(history: list) -> float:
    if len(history) < 2:
        return 0.0
    first = datetime.fromisoformat(history[0]["checked_at"])
    last = datetime.fromisoformat(history[-1]["checked_at"])
    return (last - first).total_seconds() / 86400.0


def evaluate(product: "db.sqlite3.Row", new_price_row_id: int, new_price: float) -> list[FiredRule]:
    """Evaluate all rules for a product after a new price has been recorded.

    `new_price_row_id` is the id of the just-inserted price_history row, so we
    can compare against everything recorded *before* it.
    """
    fired: list[FiredRule] = []
    full_history = [h for h in db.get_price_history(product["id"]) if h["id"] <= new_price_row_id]
    prior_history = [h for h in full_history if h["id"] < new_price_row_id]

    # --- Rule 1: target price ---
    target_price = product["target_price"]
    if target_price is not None and new_price <= target_price:
        fired.append(FiredRule(
            rule="target_price",
            message=f"Price €{new_price:.2f} is at or below your target of €{target_price:.2f}.",
        ))

    # --- Rule 2: percentage drop vs previous check ---
    prev_price = prior_history[-1]["price"] if prior_history else None
    if prev_price is not None and prev_price > 0:
        drop_pct = product["drop_pct"] if product["drop_pct"] is not None else DEFAULT_DROP_PCT
        actual_drop = (prev_price - new_price) / prev_price * 100
        if actual_drop >= drop_pct:
            fired.append(FiredRule(
                rule="drop_pct",
                message=f"Price dropped {actual_drop:.1f}% (from €{prev_price:.2f} to €{new_price:.2f}), "
                        f"meeting your {drop_pct:.0f}% alert threshold.",
            ))

    # --- Rule 3: historical low (only once enough history exists) ---
    if _history_span_days(full_history) >= MIN_HISTORY_DAYS_FOR_LOW_RULE:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=HISTORICAL_LOW_WINDOW_DAYS)).isoformat()
        window = [h for h in prior_history if h["checked_at"] >= cutoff]
        if window:
            window_min = min(h["price"] for h in window)
            if new_price < window_min:
                fired.append(FiredRule(
                    rule="historical_low",
                    message=f"€{new_price:.2f} is the lowest price in the last "
                            f"{HISTORICAL_LOW_WINDOW_DAYS} days (previous low was €{window_min:.2f}).",
                ))

    return fired


def should_send(product_id: int, rule: "FiredRule") -> bool:
    """Suppress repeat alerts for the same rule while the condition persists
    (i.e. only alert again if the price has changed since the last alert for
    this rule)."""
    last = db.get_last_alert(product_id, rule.rule)
    if last is None:
        return True
    latest_price = db.get_latest_price(product_id)
    return latest_price is None or latest_price["price"] != last["price"]
