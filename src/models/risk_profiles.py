"""Risk-adjusted expected value summaries.

Computes risk-neutral EV plus risk-averse variants from empirical draws.
Mirrors the informal adjustments from gcr-fund-evaluations/export_rp_csv.py
and the formal models from rp-distribution-fitting/risk_analysis.py.

Risk profiles:
  Informal adjustments:
    neutral  — risk-neutral EV (mean)
    upside   — truncate upper tail at p99, renormalize
    downside — loss-averse utility (lambda=2.5, reference=median)
    combined — truncation + loss aversion

  Formal models (Duffy 2023):
    dmreu    — Difference-Making Risk-Weighted EU (p=0.05, moderate aversion)
    wlu      — Weighted Linear Utility (c=0.05, low-moderate concavity)
    ambiguity — Ambiguity Aversion (k=4.0, mild)
"""

import numpy as np

from risk_analysis import (
    compute_dmreu,
    compute_wlu,
    compute_ambiguity_aversion,
)

TRUNCATION_PERCENTILE = 0.99
LOSS_AVERSION_LAMBDA = 2.5

# Formal model defaults (Duffy 2023, matching GCR fund evaluations).
DMREU_P = 0.05       # thought-experiment probability → exponent a = -2/log10(p)
WLU_L = 0.01 
WLU_M = 0.05         # concavity; 0=neutral, 0.05=low-moderate
WLU_H = 0.1
AMBIGUITY_K = 4.0    # cubic coefficient; 0=neutral, 4=mild (1.5x weight-to-worst)

RISK_PROFILES = [
    "neutral", "upside", "downside", "combined",
    "dmreu", "wlu - low", "wlu - moderate", "wlu - high", "ambiguity",
]


def compute_risk_profiles(draws):
    """Compute all risk-adjusted values from an empirical draw array.

    Args:
        draws: 1-D numpy array of outcome values (e.g. animal-DALYs/$1M).

    Returns:
        dict with keys for all 9 risk profiles.
    """
    draws = np.asarray(draws, dtype=float)

    # ── Informal adjustments ──

    neutral = float(np.mean(draws))

    # Upside skepticism: truncate at p99
    trunc_val = np.percentile(draws, TRUNCATION_PERCENTILE * 100)
    mask = draws <= trunc_val
    upside = float(np.mean(draws[mask]))

    # Downside protection: loss-averse utility around median
    ref = float(np.median(draws))
    gains = draws - ref
    utilities = np.where(gains >= 0, gains, LOSS_AVERSION_LAMBDA * gains)
    downside = float(np.mean(utilities) + ref)

    # Combined: truncation + loss aversion
    truncated = draws[mask]
    gains_t = truncated - ref
    utilities_t = np.where(gains_t >= 0, gains_t, LOSS_AVERSION_LAMBDA * gains_t)
    combined = float(np.mean(utilities_t) + ref)

    # ── Formal models (Duffy 2023) ──

    dmreu = compute_dmreu(fit=None, p=DMREU_P, samples=draws)
    wlu_low = compute_wlu(fit=None, c=WLU_L, samples=draws)
    wlu_moderate = compute_wlu(fit=None, c=WLU_M, samples=draws)
    wlu_high = compute_wlu(fit=None, c=WLU_H, samples=draws)
    ambiguity = compute_ambiguity_aversion(fit=None, k=AMBIGUITY_K, samples=draws)

    return {
        "neutral": neutral,
        "upside": upside,
        "downside": downside,
        "combined": combined,
        "dmreu": dmreu,
        "wlu - low": wlu_low,
        "wlu - moderate": wlu_moderate,
        "wlu - high": wlu_high,
        "ambiguity": ambiguity,
    }
