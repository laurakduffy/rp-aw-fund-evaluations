"""Extract CCM intervention estimates into percentile summaries.

Partially replicates the distribution parameters from the CCM repo
(rethinkpriorities/cross-cause-cost-effectiveness-model-public)
at ccm/interventions/animal/animal_interventions.py and
ccm/interventions/animal/animal_intervention_params.py. 

Other distributions are based on analyst estimates, with documentation found here:
https://docs.google.com/document/d/1Kuu08LFYpjG-wGzt7_QmBLkFTzsv4FaQHYRQKn9p3A8/edit?usp=sharing

This script samples those distributions and writes p1/p5/p10/p50/p90/p95/p99 percentiles
of suffering-years-averted per $1000 into ccm_intervention_estimates.yaml.

The CCM outputs are in "suffering-years averted per $1000" which is the
pre-moral-weight unit. Moral weight conversion happens downstream.

Run:
    source ../../test_env/bin/activate  (or ../test_env depending on cwd)
    python ccm_extract.py
"""

import numpy as np
import yaml
from scipy import stats

N = 100_000
HOURS_PER_YEAR = 24 * 365.25
np.random.seed(42)


def clip(arr, lo=None, hi=None):
    if lo is not None:
        arr = np.maximum(arr, lo)
    if hi is not None:
        arr = np.minimum(arr, hi)
    return arr


def sample_lognorm_ci(lo, hi, n=N, lclip=None, rclip=None, credibility=90):
    """Sample lognormal from confidence interval (lo=p5, hi=p95 by default)."""
    tail = (100 - credibility) / 2 / 100
    log_lo, log_hi = np.log(lo), np.log(hi)
    mu = (log_lo + log_hi) / 2
    z = stats.norm.ppf(1 - tail)
    sigma = (log_hi - log_lo) / (2 * z)
    samples = np.exp(np.random.normal(mu, sigma, n))
    return clip(samples, lclip, rclip)


def sample_norm_ci(lo, hi, n=N, lclip=None, rclip=None, credibility=90):
    """Sample normal from confidence interval."""
    tail = (100 - credibility) / 2 / 100
    mu = (lo + hi) / 2
    z = stats.norm.ppf(1 - tail)
    sigma = (hi - lo) / (2 * z)
    samples = np.random.normal(mu, sigma, n)
    return clip(samples, lclip, rclip)


def sample_beta(a, b, n=N):
    return np.random.beta(a, b, n)


def pcts(arr):
    """Return p1, p5, p10, p50, p90, p95, p99 as floats."""
    p1, p5, p10, p50, p90, p95, p99 = np.percentile(arr, [1, 5, 10, 50, 90, 95, 99])
    return {"p1": float(p1), "p5": float(p5), "p10": float(p10), "p50": float(p50), "p90": float(p90), "p95": float(p95), "p99": float(p99),
            "mean": float(np.mean(arr))}


# ── Chicken (corporate campaigns) ──
# Direct override from Laura Duffy's estimates - updated 3/2/2026 by Laura Duffy 
# suffering_years_per_$1000 from https://docs.google.com/document/d/1Kuu08LFYpjG-wGzt7_QmBLkFTzsv4FaQHYRQKn9p3A8/edit?usp=sharing

chicken_dalys_per_1000 = sample_lognorm_ci(177, 3600, lclip=50, rclip=10000, credibility=90) # mean around 1200 DALYs per $1000
chicken_sy_per_1000 = chicken_dalys_per_1000 
chicken_stats = pcts(chicken_sy_per_1000)

# ── Shrimp ──
# Source: https://docs.google.com/document/d/1Kuu08LFYpjG-wGzt7_QmBLkFTzsv4FaQHYRQKn9p3A8/edit?tab=t.0

## Humane Slaughter Intervention
shrimp_per_dollar_per_yr_slaughter = sample_lognorm_ci(800, 2200, lclip=100, rclip = 10e4, credibility=90) # mean around 1400
shrimp_slaughter_persistence = sample_lognorm_ci(6, 15, lclip=1, credibility=90) # mean around 10 years
shrimp_per_dollar_slaughter = shrimp_per_dollar_per_yr_slaughter * shrimp_slaughter_persistence
shrimp_hrs_suffering_per_shrimp_conventional_slaughter = sample_lognorm_ci(0.28, 6.4, lclip=0.1, rclip=24, credibility=90) # mean around 2 hours
shrimp_dalys_suffering_per_shrimp_conventional_slaughter = shrimp_hrs_suffering_per_shrimp_conventional_slaughter / HOURS_PER_YEAR
shrimp_hsi_percent_suffering_reduced = sample_beta(7,3) # 70% pain reduction on average

shrimp_dalys_reduced_per_dollar_slaughter = shrimp_per_dollar_slaughter * shrimp_dalys_suffering_per_shrimp_conventional_slaughter * shrimp_hsi_percent_suffering_reduced
shrimp_slaughter_pct_funding = sample_beta(18, 2) # mean around 90%

## Sludge removal and stocking density interventions
shrimp_affected_sludge = sample_lognorm_ci(50e6, 90e6, lclip=10e6, rclip=200e6, credibility=90) # mean around 70 million
shrimp_cost_sludge = 71342
shrimp_per_dollar_sludge = shrimp_affected_sludge / shrimp_cost_sludge
shrimp_per_dollar_density = shrimp_per_dollar_sludge

shrimp_sludge_hrs_suffering_per_shrimp_conventional = sample_lognorm_ci(32, 180, lclip=5, rclip=1000, credibility=90) # mean around 85 hours
shrimp_sludge_dalys_suffering_per_shrimp_conventional = shrimp_sludge_hrs_suffering_per_shrimp_conventional / HOURS_PER_YEAR
shrimp_sludge_percent_suffering_reduced = sample_beta(4, 4)
shrimp_sludge_dalys_reduced_per_dollar = shrimp_per_dollar_sludge * shrimp_sludge_dalys_suffering_per_shrimp_conventional * shrimp_sludge_percent_suffering_reduced

shrimp_density_hrs_suffering_per_shrimp_conventional = sample_lognorm_ci(50, 150, lclip=10, rclip=1000, credibility=90) # mean around 50 hours
shrimp_density_dalys_suffering_per_shrimp_conventional = shrimp_density_hrs_suffering_per_shrimp_conventional / HOURS_PER_YEAR
shrimp_density_percent_suffering_reduced = sample_beta(3, 12) # mean around 20%
shrimp_density_dalys_reduced_per_dollar = shrimp_per_dollar_density * shrimp_density_dalys_suffering_per_shrimp_conventional * shrimp_density_percent_suffering_reduced

shrimp_total_stocking_and_sludge_dalys_reduced_per_dollar = shrimp_sludge_dalys_reduced_per_dollar + shrimp_density_dalys_reduced_per_dollar

## weighted average estimate
shrimp_avg_dalys_reduced_per_dollar = (shrimp_slaughter_pct_funding * shrimp_dalys_reduced_per_dollar_slaughter
    + (1 - shrimp_slaughter_pct_funding) * shrimp_total_stocking_and_sludge_dalys_reduced_per_dollar
)

shrimp_sy_per_dollar = shrimp_avg_dalys_reduced_per_dollar

shrimp_sy_per_1000 = shrimp_sy_per_dollar * 1000

shrimp_stats = pcts(shrimp_sy_per_1000)

# ── Carp (proxy for farmed fish) ──
# Source: https://docs.google.com/document/d/1Kuu08LFYpjG-wGzt7_QmBLkFTzsv4FaQHYRQKn9p3A8/edit?tab=t.0

carp_affected_per_dollar = sample_lognorm_ci(0.5, 15, lclip=0.2, rclip=50, credibility=90) 
# Culture cycle ~383 days; suffering as 1/6 to 1/3 of a DALY
carp_hours_suffering = sample_norm_ci(24 * 383 / 6, 24 * 383 / 3, lclip=300, rclip=2/3*24*383)
carp_prop_reduced = sample_beta(3, 17) # about 15% reduction on average

carp_dalys_reduced_per_dollar = carp_affected_per_dollar * (carp_hours_suffering / HOURS_PER_YEAR) * carp_prop_reduced
carp_sy_per_dollar = carp_dalys_reduced_per_dollar #* carp_sentience
carp_sy_per_1000 = carp_sy_per_dollar * 1000
carp_stats = pcts(carp_sy_per_1000)

# ── BSF (Black Soldier Fly, proxy for invertebrates) ──
# Source: DEFAULT_BSF_PARAMS except for probability of success 

bsf_num_born = sample_norm_ci(200e9, 300e9, lclip=20e9, rclip=1000e9)
bsf_prop_affected = sample_lognorm_ci(5e-5, 1e-3, lclip=1e-6, rclip=5e-3)
# 22-24 day larval stage; suffering as 1/20 to 1/5 a DALY
bsf_hours_suffering = sample_norm_ci(24 * 22 / 20, 24 * 24 / 5, lclip=20, rclip=24*24*2/3)
bsf_prop_reduced = sample_beta(9, 4)
bsf_prob_success = sample_beta(4, 16) # mean around 20% chance of success
bsf_cost = sample_lognorm_ci(150_000, 1_000_000, lclip=100_000, rclip=1_000_000)
bsf_persistence = sample_lognorm_ci(5, 20, lclip=1, credibility=90)

bsf_annual_averted = (
    bsf_num_born * bsf_prop_affected
    * (bsf_hours_suffering / HOURS_PER_YEAR)
    * bsf_prop_reduced
) * bsf_prob_success
bsf_sy_per_dollar = bsf_annual_averted * bsf_persistence / bsf_cost
bsf_sy_per_1000 = bsf_sy_per_dollar * 1000
bsf_stats = pcts(bsf_sy_per_1000)


## Wild Mammals - Rodent example. See: https://docs.google.com/document/d/1Kuu08LFYpjG-wGzt7_QmBLkFTzsv4FaQHYRQKn9p3A8/edit?usp=sharing
wild_mammal_target_pop = sample_lognorm_ci(4100, 56000, lclip=1000, rclip=200000) # mean around 20,000 wild mammals affected
wild_mammal_suffering_hrs_per_rat = sample_lognorm_ci(60, 330, lclip=1, rclip=1000) # mean around 160 hours of suffering reduced per affected mammal
wild_mammal_p_success = sample_beta(4, 16) # mean around 20% chance of success
wild_mammal_percent_deaths_averted_if_success = sample_beta(2, 2) 
wild_mammal_years_impact = sample_lognorm_ci(5, 20, lclip=1, credibility=90) # mean around 10 years of impact if successful
wild_mammal_cost = sample_lognorm_ci(1e5, 10e6, lclip=1e4, rclip=15e6) # mean around $1 million

wild_mammal_success = (wild_mammal_p_success >= np.random.uniform(0, 1, N)).astype(float)
wild_mammal_sy_per_dollar = (
    wild_mammal_target_pop
    * (wild_mammal_suffering_hrs_per_rat / HOURS_PER_YEAR)
    * wild_mammal_percent_deaths_averted_if_success
    * wild_mammal_years_impact
    * wild_mammal_success
) / wild_mammal_cost
wild_mammal_sy_per_1000 = wild_mammal_sy_per_dollar * 1000
wild_mammal_stats = pcts(wild_mammal_sy_per_1000)

## Wild Invertebrates - Same inputs as BSF interventions, but different assumptions about probability of success
# Source: DEFAULT_BSF_PARAMS 

wild_invert_num_born = bsf_num_born
wild_invert_prop_affected = bsf_prop_affected
# 22-24 day larval stage; suffering as 1/20 to 1/5 a DALY
wild_invert_hours_suffering = sample_norm_ci(24 * 22 / 20, 24 * 24 / 5, lclip=20, rclip=24*24*2/3)
wild_invert_prop_reduced = sample_beta(9, 4)
wild_invert_prob_success = sample_beta(1, 9) # mean around 10% chance of success
wild_invert_cost = sample_lognorm_ci(150_000, 1_000_000, lclip=100_000, rclip=1_000_000)
wild_invert_persistence = sample_lognorm_ci(5, 20, lclip=1, credibility=90)

wild_invert_annual_averted = (
    wild_invert_num_born * wild_invert_prop_affected
    * (wild_invert_hours_suffering / HOURS_PER_YEAR)
    * wild_invert_prop_reduced
) * wild_invert_prob_success
wild_invert_sy_per_dollar = wild_invert_annual_averted * wild_invert_persistence / wild_invert_cost
wild_invert_sy_per_1000 = wild_invert_sy_per_dollar * 1000
wild_invert_stats = pcts(wild_invert_sy_per_1000)

## Wild animals overall
wild_share_mammals = sample_beta(1, 1) # mean around 50% of wild animal welfare spending on mammals, highly uncertain
wild_sy_per_1000_mixture_distribution = (wild_share_mammals * wild_mammal_sy_per_1000 + (1 - wild_share_mammals) * wild_invert_sy_per_1000)
wild_sy_per_1000 = wild_sy_per_1000_mixture_distribution
wild_stats = pcts(wild_sy_per_1000)
# ── Write output ──

output = {
    "metadata": {
        "source": "rethinkpriorities/cross-cause-cost-effectiveness-model-public",
        "source_files": [
            "ccm/interventions/animal/animal_interventions.py",
            "ccm/interventions/animal/animal_intervention_params.py",
        ],
        "unit": "suffering-years averted per $1000 (pre-moral-weight)",
        "n_samples": N,
        "seed": 42,
        "note": (
            "These are animal suffering-years, not human-equivalent DALYs. "
            "The CCM applies moral weight adjustments downstream. "
            "For this pipeline we use these values directly as 'animal-DALYs' "
            "pending confirmation on which moral weights to apply."
        ),
    },
    "interventions": {
        "chicken_corporate_campaigns": {
            "description": "Corporate cage-free and welfare campaigns for chickens",
            "ccm_method": "Direct override from Laura Duffy estimates",
            "ccm_distribution": "None",
            "recipient_type": "birds",
            "species": "chicken",
            "effect_start_year": 1,
            "persistence_years": 15,
            "percentiles_per_1000": chicken_stats,
        },
        "shrimp_welfare": {
            "description": "Shrimp slaughter and welfare interventions",
            "ccm_method": "Combination of McKay estimates and SWP estimates for shrimp slaughter, stocking density, and sludge removal interventions",
            "recipient_type": "shrimp",
            "species": "shrimp",
            "effect_start_year": 1,
            "persistence_years": 10,
            "percentiles_per_1000": shrimp_stats,
        },
        "fish_welfare": {
            "description": "Farmed fish welfare interventions (carp as CCM proxy)",
            "ccm_method": "Carp/$ from FWI, suffering stats from CCM carp parameters",
            "recipient_type": "fish",
            "species": "carp",
            "effect_start_year": 1,
            "persistence_years": 10,
            "percentiles_per_1000": carp_stats,
        },
        "invertebrate_welfare": {
            "description": "Invertebrate welfare interventions (BSF as CCM proxy)",
            "ccm_method": "Bottom-up model using BSF parameters",
            "recipient_type": "non_shrimp_invertebrates",
            "species": "bsf",
            "effect_start_year": 10,
            "persistence_years": 10,
            "percentiles_per_1000": bsf_stats,
        },
        "policy_advocacy_multi_species": {
            "description": "Policy advocacy affecting multiple farmed species",
            "ccm_method": "Analyst estimate: weighted average of chicken (60%) and shrimp (40%) CCM estimates at 50% effectiveness discount",
            "recipient_type": "multiple",
            "species": "multiple",
            "effect_start_year": 4,
            "persistence_years": 15,
            "percentiles_per_1000": None,  # computed below
        },
        "movement_building": {
            "description": "Movement capacity building, infrastructure, mobilization",
            "ccm_method": "Analyst estimate: 25% of blend of chicken (60%) and shrimp (40%) as indirect multiplier",
            "recipient_type": "multiple",
            "species": "multiple",
            "effect_start_year": 4,
            "persistence_years": 10,
            "percentiles_per_1000": None,  # computed below
        },
        "wild_animal_welfare": {
            "description": "Wild animal welfare research and field-building",
            "ccm_method": "No CCM model available. Roughly modeled as mixture of a wild mammal-focused intervention and a wild insect-focused intervention.",
            "recipient_type": "multiple",
            "species": "wild",
            "effect_start_year": 10,
            "persistence_years": 10,
            "percentiles_per_1000": wild_stats,  
        },
    },
}

# ── Compute derived interventions ──

# Policy advocacy: weighted blend of chicken and shrimp at 50% discount
policy_blend = 0.5 * (0.6 * chicken_sy_per_1000 + 0.4 * shrimp_sy_per_1000)
output["interventions"]["policy_advocacy_multi_species"]["percentiles_per_1000"] = pcts(policy_blend)

# Movement building: 25% of chicken estimate as indirect multiplier
movement = 0.25 * (0.6* chicken_sy_per_1000 + 0.4 * shrimp_sy_per_1000)
output["interventions"]["movement_building"]["percentiles_per_1000"] = pcts(movement)

# ── Write YAML ──

def represent_float(dumper, value):
    if abs(value) < 0.01 or abs(value) > 1e6:
        return dumper.represent_scalar("tag:yaml.org,2002:float", f"{value:.4g}")
    return dumper.represent_scalar("tag:yaml.org,2002:float", f"{value:.2f}")

yaml.add_representer(float, represent_float)

import os
output_path = os.path.join(os.path.dirname(__file__), "ccm_intervention_estimates.yaml")
with open(output_path, "w") as f:
    yaml.dump(output, f, default_flow_style=False, sort_keys=False, width=120)

print(f"Wrote {output_path}")
print()
for name, data in output["interventions"].items():
    p = data["percentiles_per_1000"]
    if p:
        print(f"  {name}: p1={p['p1']:.2f}, p5={p['p5']:.2f}, p10={p['p10']:.2f}, p50={p['p50']:.2f}, p90={p['p90']:.2f}, p95={p['p95']:.2f}, p99={p['p99']:.2f}, mean={p['mean']:.2f}")
