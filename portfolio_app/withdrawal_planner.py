"""
withdrawal_planner.py — Exit-timing optimisation helpers.

Problem framing (user verbatim):
    "The issue is not whether I will have enough money or not — that's given —
     it's more WHEN is the optimal time to withdraw the money that's growing."

Given:
    - A posterior-predictive path tensor `paths['total']` of shape (S, T) where
      T is the number of business days between today and the hard deadline.
    - A target amount.
    - A risk-aversion parameter λ in [0, 1].

We score each candidate exit day d with:

    score(d) = mean(d) - λ * (mean(d) - p10(d))
             = (1 - λ) * mean(d) + λ * p10(d)

λ = 0 → pure expected-value maximiser (wait for highest mean).
λ = 1 → conservative, minimise downside (maximise worst-case P10).
λ = 0.5 → weigh them equally.

The "upside_left" column expresses: if you exit today instead of on day d,
how much expected value do you give up? The "regret_prob" column is
P(value[d] < value[0]) — the probability of regret from waiting.

The recommendation picks the day with the highest score, compares it to
day 0 (today), and advises SELL_TODAY if either:
    - day 0 has the best score (no reason to wait), or
    - deadline is today (no days left to wait),
otherwise WAIT with the target day and expected gain.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class ExitTimingRecord:
    day_index: int        # 0 = today, 1 = next business day, …
    mean: float           # expected portfolio value on this day
    median: float
    p10: float
    p90: float
    prob_meets_target: float
    upside_left_from_today: float
    regret_prob_vs_today: float
    score: float          # composite score; higher = better


def build_exit_timing_table(
    paths: dict[str, np.ndarray],
    target_amount: float,
    risk_aversion: float = 0.3,
) -> list[ExitTimingRecord]:
    """
    Build per-day exit-timing statistics from a (S, T) path tensor.

    `paths['total']` is required. Other keys are ignored here (used in UI).
    """
    total = paths["total"]  # (S, T)
    n_samples, n_days = total.shape

    means = total.mean(axis=0)
    medians = np.median(total, axis=0)
    p10 = np.percentile(total, 10, axis=0)
    p90 = np.percentile(total, 90, axis=0)
    prob_meets = (total >= target_amount).mean(axis=0)

    mean_today = means[0]
    # regret: P(value on day d < value on day 0) — day-0 vs day-d paired by sample
    day0 = total[:, 0:1]
    regret = (total < day0).mean(axis=0)

    # Composite score: (1-λ) * mean + λ * p10
    score = (1 - risk_aversion) * means + risk_aversion * p10

    table: list[ExitTimingRecord] = []
    for d in range(n_days):
        table.append(
            ExitTimingRecord(
                day_index=d,
                mean=float(means[d]),
                median=float(medians[d]),
                p10=float(p10[d]),
                p90=float(p90[d]),
                prob_meets_target=float(prob_meets[d]),
                upside_left_from_today=float(means[d] - mean_today),
                regret_prob_vs_today=float(regret[d]),
                score=float(score[d]),
            )
        )
    return table


def recommend_today(
    table: list[ExitTimingRecord],
    risk_aversion: float = 0.3,
    edge_threshold: float = 0.0025,  # 0.25% of portfolio — ignore noise edges
) -> dict[str, Any]:
    """
    Decide whether to sell today or wait, based on the exit-timing table.

    - If the highest-score day is day 0, return SELL_TODAY.
    - Otherwise, return WAIT with the optimal day and an explanation.
    - If optimal day is very close to today (< edge_threshold * value), we
      still recommend SELL_TODAY (avoid chasing noise).
    """
    if not table:
        raise ValueError("table is empty")
    if len(table) == 1:
        return {
            "action": "SELL_TODAY",
            "optimal_day_index": 0,
            "reason": "Deadline is today — no more days to wait.",
            "expected_gain_from_waiting": 0.0,
            "regret_prob_if_waiting": 0.0,
            "risk_aversion": risk_aversion,
        }

    scores = np.array([r.score for r in table])
    best_idx = int(np.argmax(scores))
    best = table[best_idx]
    today = table[0]

    edge = best.score - today.score
    edge_frac = edge / max(today.mean, 1.0)

    if best_idx == 0 or edge_frac < edge_threshold:
        return {
            "action": "SELL_TODAY",
            "optimal_day_index": 0,
            "reason": (
                f"Today's risk-adjusted score (expected value minus {int(risk_aversion*100)}% "
                f"penalty on downside) already dominates all future days in the window."
            ),
            "expected_gain_from_waiting": 0.0,
            "regret_prob_if_waiting": 0.0,
            "risk_aversion": risk_aversion,
        }

    expected_gain = best.mean - today.mean
    return {
        "action": "WAIT",
        "optimal_day_index": best_idx,
        "reason": (
            f"Day {best_idx} has the highest risk-adjusted score "
            f"(+\u20b9{expected_gain:,.0f} expected vs today, "
            f"{best.regret_prob_vs_today*100:.0f}% chance of ending up worse)."
        ),
        "expected_gain_from_waiting": float(expected_gain),
        "regret_prob_if_waiting": float(best.regret_prob_vs_today),
        "risk_aversion": risk_aversion,
    }
