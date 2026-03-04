"""Risk-adjusted expected value summaries.

Computes risk-neutral EV plus risk-averse variants from empirical draws.
Mirrors the informal adjustments from gcr-fund-evaluations/export_rp_csv.py
and the formal models from rp-distribution-fitting/risk_analysis.py.

Risk profiles:
  neutral  — risk-neutral EV (mean)
  upside   — truncate upper tail at p99, renormalize
  downside — loss-averse utility (lambda=2.5, reference=median)
  combined — truncation + loss aversion
"""

import math

import numpy as np

TRUNCATION_PERCENTILE = 0.99
LOSS_AVERSION_LAMBDA = 2.5

RISK_PROFILES = ["neutral", "upside", "downside", "combined"]


def compute_risk_profiles(draws):
    """Compute all risk-adjusted values from an empirical draw array.

    Args:
        draws: 1-D numpy array of outcome values (e.g. animal-DALYs/$1M).

    Returns:
        dict with keys: neutral, upside, downside, combined
    """
    draws = np.asarray(draws, dtype=float)

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

    return {
        "neutral": neutral,
        "upside": upside,
        "downside": downside,
        "combined": combined,
    }
