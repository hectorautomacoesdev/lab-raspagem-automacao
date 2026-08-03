"""Estatísticas descritivas dos multiplicadores.

IMPORTANTE: são estatísticas DESCRITIVAS. O Aviator é provably-fair — nada aqui
prevê o próximo resultado. Serve para estudar a distribuição empírica.
"""
from __future__ import annotations

import statistics as st


def compute_stats(multipliers) -> dict:
    xs = [float(x) for x in multipliers if x is not None]
    n = len(xs)
    if n == 0:
        return {"n": 0}

    def pct_at_least(x):
        return 100.0 * sum(1 for v in xs if v >= x) / n

    def pct_below(x):
        return 100.0 * sum(1 for v in xs if v < x) / n

    return {
        "n": n,
        "mean": st.fmean(xs),
        "median": st.median(xs),
        "min": min(xs),
        "max": max(xs),
        "pct_below_2x": pct_below(2.0),
        "pct_at_least_2x": pct_at_least(2.0),
        "pct_at_least_10x": pct_at_least(10.0),
        "longest_low_streak": longest_low_streak(xs, 2.0),
        "current_low_streak": current_low_streak(xs, 2.0),
    }


def longest_low_streak(xs, threshold=2.0) -> int:
    best = cur = 0
    for v in xs:
        if v < threshold:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def current_low_streak(xs, threshold=2.0) -> int:
    cur = 0
    for v in reversed(xs):
        if v < threshold:
            cur += 1
        else:
            break
    return cur


def histogram(multipliers,
              buckets=((1, 1.5), (1.5, 2), (2, 3), (3, 5), (5, 10), (10, 1e9))):
    xs = [float(x) for x in multipliers if x is not None]
    return [(lo, hi, sum(1 for v in xs if lo <= v < hi)) for lo, hi in buckets]
