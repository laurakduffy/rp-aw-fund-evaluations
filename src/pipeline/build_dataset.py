"""Build the full effect dataset for the AW fund marginal CE pipeline.

Orchestrates: effects computation -> uncertainty fitting -> risk profiles ->
diminishing returns -> time allocation -> assembled dataset.
"""

import numpy as np

from models.effects import compute_all_effects
from models.uncertainty import fit_and_draw
from models.risk_profiles import compute_risk_profiles, RISK_PROFILES
from models.diminishing_returns import (
    compute_diminishing_row,
    find_20pct_threshold,
    allocate_to_periods,
    PERIOD_KEYS,
)

def build_all_effects(fund_key="aw_combined", verbose=False):
    """Build the complete effect dataset.

    Returns:
        dict with:
            fund_config: fund-level metadata
            rows: list of enriched effect dicts (one per effect)
            diminishing: diminishing returns data for the fund
            ccm_metadata: source metadata from CCM extraction
    """
    raw = compute_all_effects(fund_key=fund_key, verbose=verbose)
    fund_config = raw["fund_config"]
    effects = raw["effects"]

    if verbose:
        print("\n" + "=" * 70)
        print("FITTING DISTRIBUTIONS AND COMPUTING RISK PROFILES")
        print("=" * 70)

    rows = []
    for effect in effects:
        pct_dict = effect["animal_dalys_per_M"]

        if verbose:
            print(f"\n  {effect['effect_id']}:")

        # Separate mean from percentiles for fitting
        ccm_mean = pct_dict.pop("mean", None)
        fit_pcts = {k: v for k, v in pct_dict.items() if k in ("p1", "p5", "p10", "p50", "p90", "p95", "p99")}

        # If p10 is zero (binary-success interventions like shrimp/fish/invertebrates),
        # distribution fitting struggles with the zero mass. Use CCM mean directly.
        zero_heavy = fit_pcts.get("p10", 0) == 0
        if zero_heavy and ccm_mean and ccm_mean > 0:
            if verbose:
                print(f"    Zero-heavy distribution (p10=p50=0). Using CCM mean={ccm_mean:,.0f}")
            draws = np.array([ccm_mean] * 100)
            fit = None
        else:
            try:
                fit, draws = fit_and_draw(fit_pcts, n_samples=10000, verbose=verbose)
            except (ValueError, Exception) as e:
                if verbose:
                    print(f"    Fitting failed: {e}. Using point estimates.")
                mid = fit_pcts.get("p50", ccm_mean or 0)
                draws = np.array([mid] * 100)
                fit = None

        risk = compute_risk_profiles(draws)

        period_fracs = allocate_to_periods(
            effect["effect_start_year"],
            effect["persistence_years"],
        )

        row = {
            "project_id": fund_config["project_id"],
            "effect_id": effect["effect_id"],
            "intervention": effect["intervention"],
            "species": effect["species"],
            "recipient_type": effect["recipient_type"],
            "fund_split_pct": effect["fund_split_pct"],
            "effect_start_year": effect["effect_start_year"],
            "persistence_years": effect["persistence_years"],
            "fit_distribution": fit.name if fit else "point_estimate",
            "fit_error": fit.error if fit else 0.0,
        }

        for pk, pv in fit_pcts.items():
            row[f"animal_dalys_per_M_{pk}"] = pv
        if ccm_mean is not None:
            row["animal_dalys_per_M_mean"] = ccm_mean

        for rp in RISK_PROFILES:
            row[f"total_{rp}"] = risk[rp]

        for period_key in PERIOD_KEYS:
            frac = period_fracs[period_key]
            for rp in RISK_PROFILES:
                row[f"{rp}_{period_key}"] = risk[rp] * frac

        if verbose:
            print(f"    Neutral: {risk['neutral']:,.0f}  "
                  f"Upside: {risk['upside']:,.0f}  "
                  f"Downside: {risk['downside']:,.0f}  "
                  f"Combined: {risk['combined']:,.0f}")

        rows.append(row)

    # Fund-level diminishing returns
    budget_m = fund_config["annual_budget_M"]
    anchors = fund_config.get("diminishing_anchors", [[1, 1.0]])
    dr_values, dr_spend_points = compute_diminishing_row(budget_m, anchors)
    threshold_20pct = find_20pct_threshold(budget_m, anchors)

    if verbose:
        print(f"\n{'=' * 70}")
        print("DIMINISHING RETURNS")
        print(f"  Budget: ${budget_m}M")
        print(f"  20% CE threshold: "
              f"{'$' + str(threshold_20pct) + 'M' if threshold_20pct else 'not reached'}")

    return {
        "fund_config": fund_config,
        "rows": rows,
        "diminishing": {
            "values": dr_values,
            "spend_points": dr_spend_points,
            "threshold_20pct_M": threshold_20pct,
        },
        "ccm_metadata": raw.get("ccm_metadata", {}),
    }
