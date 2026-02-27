# Navigation Fund (TNF) — Data and Categorisation Decisions

## Sources

1. **"TNF - Summary of Grantmaking for RP"** — spreadsheet from Jesse (Feb 2026) with line-by-line grant allocations for 2024 and 2025, broken down by region, species, and area.
2. **TNF RFMF document** — confidential Room For More Funding rationale shared Feb 2026, covering budget structure, team capacity, absorption arguments, and the Cage-Free Accountability Fund.

## Raw data

From the grantmaking summary (all figures are 2024+2025 cumulative):

| Region | Species | Area | Amount |
|--------|---------|------|--------|
| Global | Layer hens (Broilers, Fish, Shrimp) | Multinational cage-free corporate campaigns and accountability | $6,720,000 |
| EU & UK | Layer hens, Broilers, Fish, Shrimp, Crustaceans, Pigs | Corporate and political animal welfare reforms | $9,810,000 |
| Latin America | Layer hens, Fish, Broilers, Pigs | Corporate welfare and political power building | $1,745,000 |
| Asia | Layer hens, Fish, Broilers, Pigs | Corporate welfare and political power building | $4,570,000 |
| US & Canada | Layer hens, Broilers, Pigs | Holding food companies accountable to welfare commitments | $5,571,000 |
| US & Canada | Layer hens, Pigs, other species | Building political power and protecting state progress | $3,936,000 |
| Asia & EU | Shrimp, Tilapia, Catfish, Lobsters, Crabs | Farmer training and technical solutions for aquatic animals | $1,204,000 |
| US | Insects and wild animals | Insects and Wild Animals | $239,000 |
| Global | Indirect (invertebrates, wild, hens, fish, broilers) | Operational support for EA-aligned regrantors | $565,000 |
| US | Indirect (invertebrates, wild, hens, fish, broilers) | Unrestricted research grants | $600,000 |
| Global | Indirect | Innovation and experimentation with new tech | $594,000 |
| US and Europe | Indirect | Targeted media and communications | $3,673,000 |
| US | Indirect | Influencing youth and elites | $2,180,000 |
| Global | Indirect | Movement fundraising for EAA-aligned projects | $1,803,000 |
| Global | Indirect | Capacity building, leadership development, events | $2,331,000 |
| Global | Institutional meat reduction | Misc bridging grant | $100,000 |
| **Total** | | | **$45,641,000** |

This matches the RFMF doc's statement: "$21M in 2024 and $24M in 2025."

## Mapping to pipeline intervention categories

Our pipeline uses 7 intervention categories drawn from the CCM. Each TNF line item was mapped as follows.

### Unambiguous lines

| CSV line | Amount | Pipeline category | Rationale |
|----------|--------|-------------------|-----------|
| Multinational cage-free corporate | $6,720K | chicken_corporate_campaigns | Directly described as cage-free corporate campaigns |
| US & Canada accountability | $5,571K | chicken_corporate_campaigns | Holding food companies to welfare commitments = corporate accountability |
| US & Canada political | $3,936K | policy_advocacy_multi_species | "Building political power" = policy advocacy |
| Aquatic: shrimp | $914K | shrimp_welfare | Explicitly broken out in CSV notes |
| Aquatic: fish (Asia) | $150K | fish_welfare | Explicitly broken out |
| Aquatic: crabs & lobsters | $140K | invertebrate_welfare | Crustaceans mapped to invertebrate |
| Insects & wild animals | $239K | 50% invertebrate, 50% wild | CSV groups both; split evenly |
| EA regrantors | $565K | movement_building | Meta/infrastructure |
| Research grants | $600K | movement_building | Movement infrastructure |
| Innovation & experimentation | $594K | movement_building | R&D, not direct intervention |
| Media & communications | $3,673K | movement_building | Awareness/narrative building |
| Youth & elites | $2,180K | movement_building | Attitude change, long-term |
| Movement fundraising | $1,803K | movement_building | Meta/fundraising capacity |
| Capacity building & events | $2,331K | movement_building | Movement infrastructure |
| Misc bridging | $100K | movement_building | Small, uncategorisable |

### Regional lines requiring judgement

Three regional lines describe blended work ("corporate and political welfare reforms") affecting multiple species. These are the hardest to categorise.

**EU & UK — $9,810K**

Description: "Advancing corporate and political animal welfare reforms." Species listed: Layer hens, Broilers, Fish, Shrimp, Other Crustaceans, Pigs.

This line covers both corporate cage-free campaigns (securing and enforcing commitments from European companies) and policy work (EU-level anti-confinement legislation). Layer hens are listed first and are described as the dominant species across TNF. The RFMF doc highlights EU policy coordination as a major strategic area.

Allocation:
- 55% → chicken_corporate_campaigns ($5,396K): corporate outreach and compliance
- 30% → policy_advocacy_multi_species ($2,943K): EU legislative advocacy
- 10% → fish_welfare ($981K): fish mentioned as significant secondary species
- 5% → shrimp_welfare ($491K): shrimp and crustaceans mentioned

**Latin America — $1,745K**

Description: "Corporate animal welfare and political power building." Species: Layer hens, Fish, Broilers, Pigs.

Allocation:
- 55% → chicken_corporate_campaigns ($960K): corporate outreach
- 35% → policy_advocacy_multi_species ($611K): political power building
- 10% → fish_welfare ($175K): fish mentioned second

**Asia — $4,570K**

Description: "Corporate animal welfare and political power building." Species: Layer hens, Fish, Broilers, Pigs. Note says <10% experimental.

Allocation:
- 55% → chicken_corporate_campaigns ($2,514K): corporate outreach
- 35% → policy_advocacy_multi_species ($1,600K): political work
- 10% → fish_welfare ($457K): fish mentioned second

### Rationale for the 55/30-35/10/5 split on regional lines

- **55% chicken**: Layer hens are listed first for every regional line. The 2024 review and RFMF doc both describe cage-free corporate campaigns as TNF's core business. "In most cases, the first species listed is likely the most significant spend" (CSV header).
- **30-35% policy**: Described as "political power building" or "political reforms" — this is a stated strategic priority in the RFMF doc.
- **10% fish**: Fish are listed second for EU, LatAm, and Asia. Aquatic welfare is a growing area but clearly secondary to chicken.
- **5% shrimp** (EU only): Shrimp and crustaceans are mentioned only for EU. LatAm and Asia don't list them, so 0% there.
- **0% other**: Wild animals, invertebrates, and movement building are handled by dedicated lines.

These ratios are the main judgement call in the analysis. If Jesse disagrees with 55/30/10/5, the fix is to update these ratios and re-run.

## Resulting splits

| Category | 2yr Total | Annual (~) | Split |
|----------|-----------|-----------|-------|
| chicken_corporate_campaigns | $21,161K | $10,580K | 46.4% |
| movement_building | $11,846K | $5,923K | 26.0% |
| policy_advocacy_multi_species | $9,090K | $4,545K | 19.9% |
| fish_welfare | $1,763K | $882K | 3.9% |
| shrimp_welfare | $1,405K | $703K | 3.1% |
| invertebrate_welfare | $260K | $130K | 0.6% |
| wild_animal_welfare | $120K | $60K | 0.3% |
| **Total** | **$45,645K** | **$22,823K** | **100%** |

## General vs Cage-Free Fund split

The RFMF doc presents the Cage-Free Accountability Fund as a distinct sub-fund with its own RFMF ($20M in 2026, $40M in 2027). We model it separately.

**Cage-Free Accountability Fund** (`navigation_fund_cagefree.yaml`): The two lines most closely matching the fund description — "Multinational cage-free corporate campaigns" ($6.72M) and "US & Canada accountability" ($5.57M) — total $12.29M/2yr = ~$6.15M/yr. This maps 100% to `chicken_corporate_campaigns`.

**General Fund** (`navigation_fund_general.yaml`): Everything else. $33.35M/2yr = ~$16.7M/yr. The RFMF doc states a 2026 general budget of $20M (trending up), consistent with this being an average of the lower 2024 figure.

**Combined** (`navigation_fund.yaml`): Budget-weighted merge of both. Use this for a single TNF cost-effectiveness estimate.

## Diminishing returns

The RFMF doc doesn't give numerical CE multipliers but describes thresholds in narrative form. Our anchors are analyst estimates:

**General fund**: TNF argues they can scale from $20M to $40M per year with minimal CE decline (scale grant sizes, hire one more PO). Above $60M they'd need more hires and may exhaust strong pipeline. We model: 0.95 at $17M, 0.85 at $35M, 0.65 at $57M, 0.45 at $100M.

**Cage-free fund**: Clearer thresholds from the doc. First $10M additional goes to Ahold (high CE). Next $10M preps next retailer (still high, slightly deferred). Above $20M additional requires geographic expansion (lower marginal CE). We model: 0.95 at $6M, 0.85 at $16M, 0.70 at $26M, 0.45 at $50M.

## What could change these estimates

- **Jesse confirms or corrects regional splits**: The 55/30/10/5 allocation on EU/LatAm/Asia lines is the biggest assumption. Even shifting chicken from 55% to 45% or 65% would meaningfully change the overall split.
- **Cage-free fund budget clarified**: We inferred ~$6.15M/yr from the two most relevant CSV lines, but the RFMF doc doesn't state the current cage-free budget explicitly.
- **2026 budget differs from 2024-2025 average**: The RFMF doc says $20M general for 2026. If TNF is shifting allocation significantly (e.g. more policy, less movement building), these splits would need updating.
- **New interventions**: The RFMF doc mentions incubating projects in emerging fields. If TNF enters wild animal welfare or invertebrate welfare more seriously, those tiny allocations would grow.
