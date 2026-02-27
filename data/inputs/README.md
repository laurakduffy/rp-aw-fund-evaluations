# Input Data

## Current Structure

```
data/inputs/
├── ccm_intervention_estimates.yaml   # CCM-derived CE percentiles
├── ccm_extract.py                    # Script that generated the YAML
├── funds/
│   ├── ea_awf.yaml                   # EA AWF (from 2024 payout reports)
│   ├── navigation_fund.yaml          # TNF combined (from TNF provided data)
│   ├── navigation_fund_general.yaml  # TNF general fund only
│   ├── navigation_fund_cagefree.yaml # TNF cage-free accountability fund
│   ├── TNF_README.md                 # Full TNF categorisation methodology
│   ├── coefficient_giving.yaml       # Template — awaiting Lewis
│   ├── aw_combined.yaml              # Budget-weighted aggregate
│   └── TEMPLATE.yaml                 # Instructions for new funds
└── README.md                         # This file
```

---

## Data Provenance Summary

### Real data (grounded in published sources or fund manager input)

| Data | Source | File |
|------|--------|------|
| Chicken CE distribution | Laura Duffy estimates via CCM repo | `ccm_intervention_estimates.yaml` |
| Shrimp CE distribution | CCM bottom-up model | `ccm_intervention_estimates.yaml` |
| Fish CE distribution (carp proxy) | CCM bottom-up model | `ccm_intervention_estimates.yaml` |
| Invertebrate CE distribution (BSF proxy) | CCM bottom-up model | `ccm_intervention_estimates.yaml` |
| EA AWF budget ($3.7M/yr, $6.3M RFMF) | [2024 review](https://forum.effectivealtruism.org/posts/pZhqWRiq9ubaMSnqx) | `ea_awf.yaml` |
| EA AWF grant-level amounts | [Apr-Oct payouts](https://forum.effectivealtruism.org/posts/dvPJZSK3bGooCi8CW), [Oct-Dec payouts](https://forum.effectivealtruism.org/posts/w5rXxuvxnZBv4ehvF) | `ea_awf.yaml` |
| TNF budget ($21M 2024, $24M 2025) | Jesse's RFMF doc (confidential, Feb 2026) | `navigation_fund*.yaml` |
| TNF line-item allocations | Jesse's "Summary of Grantmaking for RP" spreadsheet | `navigation_fund*.yaml` |
| TNF RFMF ($40M gen + $20M cage-free) | Jesse's RFMF doc | `navigation_fund*.yaml` |

### Analyst estimates (reasonable but involve judgement)

| Data | Method | Sensitivity | File |
|------|--------|-------------|------|
| Policy advocacy CE | 50% × (60% chicken + 40% shrimp) CCM blend | **High** | `ccm_extract.py` |
| Movement building CE | 25% of chicken CCM estimate | **High** | `ccm_extract.py` |
| Wild animal welfare CE | lognorm(1, 100) per $1000 | **Very high** | `ccm_extract.py` |
| EA AWF split categorisation | Named grants mapped to 7 intervention types | **Low** | `ea_awf.yaml` |
| TNF regional line splits (55/30/10/5) | Based on species lists + area descriptions | **Medium** | See `TNF_README.md` |
| All diminishing returns anchors | Narrative from docs, no numerical CE data | **High** | All fund YAMLs |
| Effect timing (start year, persistence) | CCM defaults | **Low-medium** | `ccm_intervention_estimates.yaml` |

### Placeholder (empty)

| Data | Status | File |
|------|--------|------|
| Coefficient Giving | **Empty template** — no data from Lewis | `coefficient_giving.yaml` |

### Missing entirely

| Data | Impact |
|------|--------|
| Coefficient Giving splits + budget | Can't model CG |
| Moral weight conversion | CCM values are animal suffering-years, not human-equivalent DALYs |
| Mammal intervention CE | CCM has no model; TNF funds pig welfare but we can't price it |
| Wild animal welfare model | Only analyst prior, not a real model |

---

## CCM Intervention Estimates

`ccm_intervention_estimates.yaml` contains percentiles (p10/p50/p90/mean) of **suffering-years averted per $1000** for each intervention, extracted from the Rethink Priorities Cross-Cause Model.

**Source**: `github.com/rethinkpriorities/cross-cause-cost-effectiveness-model-public`

**How it was generated**: `ccm_extract.py` replicates the CCM's distribution parameters using scipy/numpy, samples 100K draws, and computes percentiles. Run it to regenerate:

```bash
source ../../test_env/bin/activate
python ccm_extract.py
```

| Intervention | CCM Method | Key Parameter |
|---|---|---|
| chicken_corporate_campaigns | Direct override | norm(lo=160, hi=3630) per $1000 |
| shrimp_welfare | Bottom-up model | Binary success × scale × persistence |
| fish_welfare | Bottom-up (carp proxy) | Binary success × scale × persistence |
| invertebrate_welfare | Bottom-up (BSF proxy) | Binary success × scale × persistence |
| policy_advocacy_multi_species | Analyst blend | 50% × (60% chicken + 40% shrimp) |
| movement_building | Analyst estimate | 25% of chicken CE |
| wild_animal_welfare | Analyst prior | lognorm(lo=1, hi=100) — very uncertain |

**Important**: These are animal suffering-years, not human-equivalent DALYs. Moral weight conversion is not yet applied.

## Fund Split Files

Each fund YAML in `funds/` specifies:
- `annual_budget_M`: Annual budget in millions
- `splits`: Fraction of budget per intervention (should sum to ~1.0)
- `diminishing_anchors`: How CE changes with more funding

### EA AWF (`ea_awf.yaml`)

Estimated from the [2024 payout reports](https://forum.effectivealtruism.org/posts/dvPJZSK3bGooCi8CW) and [2024 review](https://forum.effectivealtruism.org/posts/pZhqWRiq9ubaMSnqx). Individual grants were categorised by intervention type. See inline comments in the file.

### Navigation Fund (`navigation_fund*.yaml`)

Derived from Jesse's grantmaking summary spreadsheet (line-item data for 2024-2025). Three files:
- `navigation_fund.yaml` — combined view (~$22.8M/yr)
- `navigation_fund_general.yaml` — general fund only (~$16.7M/yr)
- `navigation_fund_cagefree.yaml` — cage-free accountability (~$6.15M/yr)

Full methodology in `funds/TNF_README.md`.

### Coefficient Giving (`coefficient_giving.yaml`)

Empty template. Awaiting data from Lewis.

## Ingesting New Data

### When a fund manager sends splits:
1. Open the fund's YAML in `funds/`
2. Set `annual_budget_M` and fill in `splits`
3. Run `python run.py --fund <fund_id> --verbose`

### When CCM parameters update:
1. Update the distribution parameters in `ccm_extract.py`
2. Re-run `python ccm_extract.py`
3. Re-run `python run.py --verbose` for all funds

### Adding a new intervention:
1. Add the distribution parameters to `ccm_extract.py` and re-run
2. Add the intervention key to fund YAML splits
3. Pipeline will pick it up automatically
