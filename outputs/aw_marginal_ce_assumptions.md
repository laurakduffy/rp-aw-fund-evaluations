# AW Fund Marginal CE: Assumptions Register

Generated: 2026-03-04

## Fund Configuration

- **Project ID**: aw_combined
- **Display name**: Combined AW Funds (Marginal)
- **Annual budget**: $26.5M/year
- **Room for more funding**: $79.3M

## CE Source

- **Model**: Rethink Priorities Cross-Cause Cost-Effectiveness Model (CCM)
- **Source repo**: rethinkpriorities/cross-cause-cost-effectiveness-model-public
- **Unit**: suffering-years averted per $1000 (pre-moral-weight)
- **Samples**: 100000
- **Note**: These are animal suffering-years, not human-equivalent DALYs. The CCM applies moral weight adjustments downstream. For this pipeline we use these values directly as 'animal-DALYs' pending confirmation on which moral weights to apply.

## Diminishing Returns

- **20% CE threshold**: not reached within scan range
- **Anchor points**: [[10.0, 1.0], [26.5, 0.95], [55.0, 0.82], [100.0, 0.55], [160.0, 0.35]]

## Effect-Level Summary

| Intervention | Species | Recipient | Split | Persistence | Fit | Neutral aDALYs/$1M |
|---|---|---|---|---|---|---|
| chicken_corporate_campaigns | chicken | birds | 51% | 15yr | lognormal | 1,214,870 |
| movement_building | multiple | multiple | 23% | 10yr | lognormal | 456,094 |
| policy_advocacy_multi_species | multiple | multiple | 12% | 15yr | lognormal | 912,189 |
| fish_welfare | carp | fish | 4% | 10yr | lognormal | 182,950 |
| shrimp_welfare | shrimp | shrimp | 2% | 10yr | gev | 2,728,516 |
| wild_animal_welfare | wild | multiple | 2% | 10yr | lognormal | 795,145 |
| invertebrate_welfare | bsf | non_shrimp_invertebrates | 1% | 10yr | lognormal | 3,127,201 |

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
