# AW Fund Marginal CE: Assumptions Register

Generated: 2026-02-27

## Fund Configuration

- **Project ID**: navigation_fund
- **Display name**: Navigation Fund (Combined)
- **Annual budget**: $22.8M/year
- **Room for more funding**: $60.0M

## CE Source

- **Model**: Rethink Priorities Cross-Cause Cost-Effectiveness Model (CCM)
- **Source repo**: rethinkpriorities/cross-cause-cost-effectiveness-model-public
- **Unit**: suffering-years averted per $1000 (pre-moral-weight)
- **Samples**: 100000
- **Note**: These are animal suffering-years, not human-equivalent DALYs. The CCM applies moral weight adjustments downstream. For this pipeline we use these values directly as 'animal-DALYs' pending confirmation on which moral weights to apply.

## Diminishing Returns

- **20% CE threshold**: not reached within scan range
- **Anchor points**: [[10.0, 1.0], [23.0, 0.95], [45.0, 0.85], [80.0, 0.65], [120.0, 0.45]]

## Effect-Level Summary

| Intervention | Species | Recipient | Split | Persistence | Fit | Neutral aDALYs/$1M |
|---|---|---|---|---|---|---|
| chicken_corporate_campaigns | chicken | birds | 46% | 8yr | gev | 1,893,257 |
| policy_advocacy_multi_species | multiple | multiple | 20% | 8yr | gev | 580,029 |
| movement_building | multiple | multiple | 26% | 10yr | gev | 473,316 |
| fish_welfare | carp | fish | 4% | 5yr | point_estimate | 303,100 |
| shrimp_welfare | shrimp | shrimp | 3% | 5yr | point_estimate | 61,480 |
| invertebrate_welfare | bsf | non_shrimp_invertebrates | 1% | 5yr | point_estimate | 2,846,800 |
| wild_animal_welfare | wild | multiple | 0% | 15yr | lognormal | 26,639 |

## Key Sources

- CE estimates: Rethink Priorities CCM (github.com/rethinkpriorities/cross-cause-cost-effectiveness-model-public)
- Chicken estimates: Laura Duffy direct override in CCM
- Shrimp/Carp/BSF: CCM bottom-up models
- Policy/Movement/Wild: Analyst priors derived from CCM chicken/shrimp baselines
- Fund splits: EA AWF 2024 payout reports (forum.effectivealtruism.org)
- Distribution fitting: rp-distribution-fitting (lowest fit-error selection)

## Caveats

- CCM estimates are pre-moral-weight (animal suffering-years, not human DALYs).
- Policy advocacy, movement building, and wild animal estimates are analyst priors, not from the CCM's bottom-up models.
- Shrimp and fish interventions have binary success models — ~50% of samples are zero, making distribution fitting less reliable for these.
- Fund splits are estimated from public payout reports and may not reflect the fund's marginal allocation.
- No time discounting is applied.
