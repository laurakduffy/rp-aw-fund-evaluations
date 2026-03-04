"""Effect engine: CCM intervention estimates + fund allocation splits.

Loads pre-computed cost-effectiveness distributions from the CCM extraction
(ccm_intervention_estimates.yaml) and fund-specific budget splits from
per-fund YAML files (data/inputs/funds/<fund_id>.yaml).

For each intervention in the fund's split, produces an effect dict with
suffering-years-per-$1M percentiles ready for distribution fitting.
"""

import os
import yaml

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "inputs")


def load_ccm_estimates(path=None):
    """Load CCM intervention estimates YAML."""
    if path is None:
        path = os.path.join(_DATA_DIR, "ccm_intervention_estimates.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def load_fund(fund_id, path=None):
    """Load a per-fund YAML file by fund_id.

    Looks in data/inputs/funds/<fund_id>.yaml unless path is given.
    """
    if path is None:
        path = os.path.join(_DATA_DIR, "funds", f"{fund_id}.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def compute_all_effects(fund_key="aw_combined", verbose=False):
    """Compute effect rows for all interventions in the given fund.

    For each intervention:
      - Look up CCM percentiles (suffering-years averted per $1000)
      - Convert to per-$1M (multiply by 1000)
      - Attach fund split weight, timing, and DR anchors

    Returns dict with fund_config, effects list, ccm_metadata.
    """
    ccm_data = load_ccm_estimates()
    fund_data = load_fund(fund_key)
    fund_config = fund_data["fund"]
    ccm_interventions = ccm_data["interventions"]

    splits = fund_config["splits"]
    total_split = sum(v for v in splits.values() if v and v > 0)

    if verbose:
        print(f"\nFund: {fund_config['display_name']}")
        print(f"Annual budget: ${fund_config['annual_budget_M']}M")
        print(f"Room for more: ${fund_config['room_for_more_M']}M")
        print(f"Split sum: {total_split:.2f}")
        print()

    all_effects = []
    for intervention_key, split_pct in splits.items():
        if not split_pct or split_pct <= 0:
            continue

        if intervention_key not in ccm_interventions:
            if verbose:
                print(f"  Warning: {intervention_key} not in CCM estimates, skipping")
            continue

        ccm = ccm_interventions[intervention_key]
        pct_per_1000 = ccm["percentiles_per_1000"]

        if pct_per_1000 is None:
            if verbose:
                print(f"  Warning: {intervention_key} has no CCM percentiles, skipping")
            continue

        # Convert from per-$1000 to per-$1M
        animal_dalys_per_M = {
            k: v * 1000
            for k, v in pct_per_1000.items()
            if k in ("p1", "p5", "p10", "p50", "p90", "p95", "p99", "mean")
        }

        effect = {
            "effect_id": intervention_key,
            "intervention": intervention_key,
            "species": ccm.get("species", "unknown"),
            "recipient_type": ccm.get("recipient_type", "unknown"),
            "description": ccm.get("description", ""),
            "ccm_method": ccm.get("ccm_method", ""),
            "fund_split_pct": split_pct,
            "animal_dalys_per_M": animal_dalys_per_M,
            "effect_start_year": ccm.get("effect_start_year", 1),
            "persistence_years": ccm.get("persistence_years", 5),
        }

        if verbose:
            mid = animal_dalys_per_M.get("p50", 0)
            print(f"  {intervention_key}: p50 = {mid:,.0f} suffering-years/$1M "
                  f"(split={split_pct:.0%})")

        all_effects.append(effect)

    if verbose:
        print(f"\nTotal effects: {len(all_effects)}")

    return {
        "fund_config": fund_config,
        "effects": all_effects,
        "ccm_metadata": ccm_data.get("metadata", {}),
    }
