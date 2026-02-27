"""Extract CCM intervention estimates into percentile summaries.

Replicates the distribution parameters from the CCM repo
(rethinkpriorities/cross-cause-cost-effectiveness-model-public)
at ccm/interventions/animal/animal_interventions.py and
ccm/interventions/animal/animal_intervention_params.py

This script samples those distributions and writes p10/p50/p90 percentiles
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
    """Return p10, p50, p90 as floats."""
    p10, p50, p90 = np.percentile(arr, [10, 50, 90])
    return {"p10": float(p10), "p50": float(p50), "p90": float(p90),
            "mean": float(np.mean(arr))}


# ── Chicken (corporate campaigns) ──
# Direct override from Laura Duffy's estimates
# suffering_years_per_$1000 ~ norm(lo=160, hi=3630, lclip=16, credibility=90)
# Source: ccm/interventions/animal/animal_interventions.py DEFAULT_CHICKEN_PARAMS

chicken_sy_per_1000 = sample_norm_ci(160, 3630, lclip=16, rclip=100_000, credibility=90)
chicken_stats = pcts(chicken_sy_per_1000)

# ── Shrimp ──
# Source: ccm/interventions/animal/animal_interventions.py DEFAULT_SHRIMP_PARAMS
# + ccm/interventions/animal/animal_intervention_params.py for num_animals_born_per_year

shrimp_num_born = sample_lognorm_ci(300e9, 610e9, lclip=50e9, rclip=2000e9, credibility=90)
shrimp_prop_affected = sample_lognorm_ci(5e-5, 1e-3, lclip=1e-6, rclip=5e-3)
shrimp_hours_suffering = sample_norm_ci(0.0072, 0.62, lclip=0, rclip=0.95)
shrimp_prop_reduced = sample_beta(9, 4)
shrimp_prob_success = sample_beta(3, 3)
shrimp_cost = sample_lognorm_ci(150_000, 1_000_000, lclip=100_000, rclip=1_000_000)
shrimp_persistence = sample_lognorm_ci(5, 20, lclip=1, credibility=90)

shrimp_successes = (shrimp_prob_success >= np.random.uniform(0, 1, N)).astype(float)
shrimp_annual_averted = (
    shrimp_num_born * shrimp_prop_affected
    * (shrimp_hours_suffering / HOURS_PER_YEAR)
    * shrimp_prop_reduced
) * shrimp_successes
shrimp_sy_per_dollar = shrimp_annual_averted * shrimp_persistence / shrimp_cost
shrimp_sy_per_1000 = shrimp_sy_per_dollar * 1000
shrimp_stats = pcts(shrimp_sy_per_1000)

# ── Carp (proxy for farmed fish) ──
# Source: DEFAULT_CARP_PARAMS

carp_num_born = sample_norm_ci(8.34e9, 16.7e9, lclip=2e9, rclip=50e9)
carp_prop_affected = sample_lognorm_ci(5e-5, 1e-3, lclip=1e-6, rclip=5e-3)
# Culture cycle ~383 days; suffering as 1/20 to 1/5 of a DALY
carp_hours_suffering = sample_norm_ci(24 * 345 / 20, 24 * 421 / 5, lclip=300, rclip=500)
carp_prop_reduced = sample_beta(1.6, 19)
carp_prob_success = sample_beta(3, 3)
carp_cost = sample_lognorm_ci(150_000, 1_000_000, lclip=100_000, rclip=1_000_000)
carp_persistence = sample_lognorm_ci(5, 20, lclip=1, credibility=90)

carp_successes = (carp_prob_success >= np.random.uniform(0, 1, N)).astype(float)
carp_annual_averted = (
    carp_num_born * carp_prop_affected
    * (carp_hours_suffering / HOURS_PER_YEAR)
    * carp_prop_reduced
) * carp_successes
carp_sy_per_dollar = carp_annual_averted * carp_persistence / carp_cost
carp_sy_per_1000 = carp_sy_per_dollar * 1000
carp_stats = pcts(carp_sy_per_1000)

# ── BSF (Black Soldier Fly, proxy for invertebrates) ──
# Source: DEFAULT_BSF_PARAMS

bsf_num_born = sample_norm_ci(200e9, 300e9, lclip=20e9, rclip=1000e9)
bsf_prop_affected = sample_lognorm_ci(5e-5, 1e-3, lclip=1e-6, rclip=5e-3)
# 22-24 day larval stage; suffering as 1/20 to 1/5 a DALY
bsf_hours_suffering = sample_norm_ci(24 * 22 / 20, 24 * 24 / 5, lclip=20, rclip=26)
bsf_prop_reduced = sample_beta(9, 4)
bsf_prob_success = sample_beta(3, 3)
bsf_cost = sample_lognorm_ci(150_000, 1_000_000, lclip=100_000, rclip=1_000_000)
bsf_persistence = sample_lognorm_ci(5, 20, lclip=1, credibility=90)

bsf_successes = (bsf_prob_success >= np.random.uniform(0, 1, N)).astype(float)
bsf_annual_averted = (
    bsf_num_born * bsf_prop_affected
    * (bsf_hours_suffering / HOURS_PER_YEAR)
    * bsf_prop_reduced
) * bsf_successes
bsf_sy_per_dollar = bsf_annual_averted * bsf_persistence / bsf_cost
bsf_sy_per_1000 = bsf_sy_per_dollar * 1000
bsf_stats = pcts(bsf_sy_per_1000)


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
            "ccm_distribution": "norm(lo=160, hi=3630, lclip=16, credibility=90)",
            "recipient_type": "birds",
            "species": "chicken",
            "effect_start_year": 1,
            "persistence_years": 8,
            "percentiles_per_1000": chicken_stats,
        },
        "shrimp_welfare": {
            "description": "Shrimp slaughter and welfare interventions",
            "ccm_method": "Bottom-up model (prop_affected * hours * reduction * success * persistence / cost)",
            "recipient_type": "shrimp",
            "species": "shrimp",
            "effect_start_year": 2,
            "persistence_years": 5,
            "percentiles_per_1000": shrimp_stats,
        },
        "fish_welfare": {
            "description": "Farmed fish welfare interventions (carp as CCM proxy)",
            "ccm_method": "Bottom-up model using carp parameters",
            "recipient_type": "fish",
            "species": "carp",
            "effect_start_year": 2,
            "persistence_years": 5,
            "percentiles_per_1000": carp_stats,
        },
        "invertebrate_welfare": {
            "description": "Invertebrate welfare interventions (BSF as CCM proxy)",
            "ccm_method": "Bottom-up model using BSF parameters",
            "recipient_type": "non_shrimp_invertebrates",
            "species": "bsf",
            "effect_start_year": 3,
            "persistence_years": 5,
            "percentiles_per_1000": bsf_stats,
        },
        "policy_advocacy_multi_species": {
            "description": "Policy advocacy affecting multiple farmed species",
            "ccm_method": "Analyst estimate: weighted average of chicken (60%) and shrimp (40%) CCM estimates at 50% effectiveness discount",
            "recipient_type": "multiple",
            "species": "multiple",
            "effect_start_year": 2,
            "persistence_years": 8,
            "percentiles_per_1000": None,  # computed below
        },
        "movement_building": {
            "description": "Movement capacity building, infrastructure, mobilization",
            "ccm_method": "Analyst estimate: 25% of chicken CCM estimate as indirect multiplier",
            "recipient_type": "multiple",
            "species": "multiple",
            "effect_start_year": 3,
            "persistence_years": 10,
            "percentiles_per_1000": None,  # computed below
        },
        "wild_animal_welfare": {
            "description": "Wild animal welfare research and field-building",
            "ccm_method": "No CCM model available. Analyst prior: very uncertain, low but potentially large scale.",
            "recipient_type": "multiple",
            "species": "wild",
            "effect_start_year": 5,
            "persistence_years": 15,
            "percentiles_per_1000": None,  # computed below
        },
    },
}

# ── Compute derived interventions ──

# Policy advocacy: weighted blend of chicken and shrimp at 50% discount
policy_blend = 0.5 * (0.6 * chicken_sy_per_1000 + 0.4 * shrimp_sy_per_1000)
output["interventions"]["policy_advocacy_multi_species"]["percentiles_per_1000"] = pcts(policy_blend)

# Movement building: 25% of chicken estimate as indirect multiplier
movement = 0.25 * chicken_sy_per_1000
output["interventions"]["movement_building"]["percentiles_per_1000"] = pcts(movement)

# Wild animal welfare: very rough analyst prior
wild = sample_lognorm_ci(1, 100, lclip=0.01, rclip=10000, credibility=90)
output["interventions"]["wild_animal_welfare"]["percentiles_per_1000"] = pcts(wild)


# ── Write YAML ──

def represent_float(dumper, value):
    if abs(value) < 0.01 or abs(value) > 1e6:
        return dumper.represent_scalar("tag:yaml.org,2002:float", f"{value:.4g}")
    return dumper.represent_scalar("tag:yaml.org,2002:float", f"{value:.2f}")

yaml.add_representer(float, represent_float)

output_path = "ccm_intervention_estimates.yaml"
with open(output_path, "w") as f:
    yaml.dump(output, f, default_flow_style=False, sort_keys=False, width=120)

print(f"Wrote {output_path}")
print()
for name, data in output["interventions"].items():
    p = data["percentiles_per_1000"]
    if p:
        print(f"  {name}: p10={p['p10']:.2f}, p50={p['p50']:.2f}, p90={p['p90']:.2f}, mean={p['mean']:.2f}")
