"""Export pipeline: write CSV, assumptions markdown, and sensitivity outputs."""

import csv
import os
from datetime import date

import numpy as np

from models.risk_profiles import RISK_PROFILES
from models.diminishing_returns import PERIOD_KEYS


def export_dataset(dataset, output_path, verbose=False):
    """Write the main CE dataset CSV.

    One row per effect with risk-adjusted totals and period-allocated values.
    """
    rows = dataset["rows"]
    if not rows:
        if verbose:
            print("No effect rows to export.")
        return

    fieldnames = list(rows[0].keys())

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            formatted = {}
            for k, v in row.items():
                if isinstance(v, float):
                    formatted[k] = f"{v:.4g}"
                else:
                    formatted[k] = v
            writer.writerow(formatted)

    if verbose:
        print(f"\nDataset CSV written to: {output_path}")
        print(f"  {len(rows)} effect rows, {len(fieldnames)} columns")


def export_assumptions(dataset, output_path, verbose=False):
    """Write the assumptions register as markdown."""
    fund = dataset["fund_config"]
    rows = dataset["rows"]
    dr = dataset["diminishing"]
    ccm_meta = dataset.get("ccm_metadata", {})

    lines = [
        "# AW Fund Marginal CE: Assumptions Register",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Fund Configuration",
        "",
        f"- **Project ID**: {fund['project_id']}",
        f"- **Display name**: {fund['display_name']}",
        f"- **Annual budget**: ${fund['annual_budget_M']}M/year",
        f"- **Room for more funding**: ${fund.get('room_for_more_M', 'unknown')}M",
        "",
        "## CE Source",
        "",
        f"- **Model**: Rethink Priorities Cross-Cause Cost-Effectiveness Model (CCM)",
        f"- **Source repo**: {ccm_meta.get('source', 'N/A')}",
        f"- **Unit**: {ccm_meta.get('unit', 'suffering-years averted per $1000')}",
        f"- **Samples**: {ccm_meta.get('n_samples', 'N/A')}",
        f"- **Note**: {ccm_meta.get('note', '')}",
        "",
        "## Diminishing Returns",
        "",
        f"- **20% CE threshold**: "
        f"{'$' + str(dr['threshold_20pct_M']) + 'M' if dr['threshold_20pct_M'] else 'not reached within scan range'}",
        f"- **Anchor points**: {fund.get('diminishing_anchors', 'N/A')}",
        "",
        "## Effect-Level Summary",
        "",
        "| Intervention | Species | Recipient | Split | "
        "Persistence | Fit | Neutral aDALYs/$1M |",
        "|---|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['effect_id']} | {row['species']} | {row['recipient_type']} "
            f"| {row['fund_split_pct']:.0%} "
            f"| {row['persistence_years']}yr | {row['fit_distribution']} "
            f"| {row['total_neutral']:,.0f} |"
        )

    lines.extend([
        "",
        "## Key Sources",
        "",
        "- CE estimates: Rethink Priorities CCM "
        "(github.com/rethinkpriorities/cross-cause-cost-effectiveness-model-public)",
        "- Chicken estimates: Laura Duffy direct override in CCM",
        "- Shrimp/Carp/BSF: CCM bottom-up models",
        "- Policy/Movement/Wild: Analyst priors derived from CCM chicken/shrimp baselines",
        "- Fund splits: EA AWF 2024 payout reports (forum.effectivealtruism.org)",
        "- Distribution fitting: rp-distribution-fitting (lowest fit-error selection)",
        "",
        "## Caveats",
        "",
        "- CCM estimates are pre-moral-weight (animal suffering-years, not human DALYs).",
        "- Policy advocacy, movement building, and wild animal estimates are analyst priors, "
        "not from the CCM's bottom-up models.",
        "- Shrimp and fish interventions have binary success models — ~50% of samples are zero, "
        "making distribution fitting less reliable for these.",
        "- Fund splits are estimated from public payout reports and may not reflect "
        "the fund's marginal allocation.",
        "- No time discounting is applied.",
        "",
    ])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    if verbose:
        print(f"Assumptions register written to: {output_path}")


def export_sensitivity(dataset, output_path, verbose=False):
    """Write one-way sensitivity analysis CSV.

    Varies fund_split_pct and persistence_years +/- 50% and reports
    change in neutral EV.
    """
    rows = dataset["rows"]
    if not rows:
        return

    sensitivity_rows = []
    header = [
        "effect_id", "parameter", "base_value",
        "low_value", "high_value",
        "base_neutral", "low_neutral", "high_neutral",
        "pct_change_low", "pct_change_high",
    ]

    params_to_vary = [
        ("fund_split_pct", 0.5, 1.5),
        ("persistence_years", 0.5, 1.5),
    ]

    for row in rows:
        base_neutral = row["total_neutral"]
        if base_neutral == 0:
            continue

        for param_name, low_mult, high_mult in params_to_vary:
            base_val = row.get(param_name, 0)
            if base_val == 0:
                continue

            low_neutral = base_neutral * low_mult
            high_neutral = base_neutral * high_mult

            sensitivity_rows.append({
                "effect_id": row["effect_id"],
                "parameter": param_name,
                "base_value": f"{base_val:.4g}",
                "low_value": f"{base_val * low_mult:.4g}",
                "high_value": f"{base_val * high_mult:.4g}",
                "base_neutral": f"{base_neutral:.4g}",
                "low_neutral": f"{low_neutral:.4g}",
                "high_neutral": f"{high_neutral:.4g}",
                "pct_change_low": f"{(low_mult - 1) * 100:+.0f}%",
                "pct_change_high": f"{(high_mult - 1) * 100:+.0f}%",
            })

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(sensitivity_rows)

    if verbose:
        print(f"Sensitivity CSV written to: {output_path}")
        print(f"  {len(sensitivity_rows)} rows across {len(rows)} effects")
