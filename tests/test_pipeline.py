"""Integration tests for the full pipeline."""

import os
import sys
import pytest
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pipeline.build_dataset import build_all_effects
from pipeline.export import export_dataset, export_assumptions, export_sensitivity
from models.risk_profiles import RISK_PROFILES
from models.diminishing_returns import PERIOD_KEYS

_CACHED_DATASET = None


def _get_dataset():
    """Cache dataset across all test classes to avoid repeated slow fitting."""
    global _CACHED_DATASET
    if _CACHED_DATASET is None:
        _CACHED_DATASET = build_all_effects(fund_key="aw_combined", verbose=False)
    return _CACHED_DATASET


class TestBuildDataset:
    @pytest.fixture(scope="class")
    def dataset(self):
        return _get_dataset()

    def test_has_rows(self, dataset):
        assert len(dataset["rows"]) > 0

    def test_has_fund_config(self, dataset):
        assert "project_id" in dataset["fund_config"]

    def test_has_diminishing(self, dataset):
        assert "values" in dataset["diminishing"]
        assert "threshold_20pct_M" in dataset["diminishing"]

    def test_all_rows_have_required_fields(self, dataset):
        required = [
            "project_id", "effect_id", "recipient_type",
            "fund_split_pct",
            "fit_distribution", "total_neutral",
        ]
        for row in dataset["rows"]:
            for field in required:
                assert field in row, f"Missing {field} in {row['effect_id']}"

    def test_all_risk_profiles_present(self, dataset):
        for row in dataset["rows"]:
            for rp in RISK_PROFILES:
                assert f"total_{rp}" in row

    def test_all_period_allocations_present(self, dataset):
        for row in dataset["rows"]:
            for pk in PERIOD_KEYS:
                for rp in RISK_PROFILES:
                    key = f"{rp}_{pk}"
                    assert key in row, f"Missing {key} in {row['effect_id']}"

    def test_neutral_non_negative(self, dataset):
        for row in dataset["rows"]:
            assert row["total_neutral"] >= 0, f"{row['effect_id']} has negative neutral"

    def test_expected_interventions_present(self, dataset):
        effect_ids = {row["effect_id"] for row in dataset["rows"]}
        expected = {
            "chicken_corporate_campaigns",
            "fish_welfare",
            "shrimp_welfare",
            "policy_advocacy_multi_species",
            "movement_building",
            "wild_animal_welfare",
        }
        for e in expected:
            assert e in effect_ids, f"Missing intervention: {e}"


class TestExport:
    @pytest.fixture(scope="class")
    def dataset(self):
        return _get_dataset()

    def test_csv_export(self, dataset, tmp_path):
        csv_path = str(tmp_path / "test_output.csv")
        export_dataset(dataset, csv_path)
        assert os.path.exists(csv_path)
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == len(dataset["rows"])

    def test_assumptions_export(self, dataset, tmp_path):
        md_path = str(tmp_path / "test_assumptions.md")
        export_assumptions(dataset, md_path)
        assert os.path.exists(md_path)
        with open(md_path) as f:
            content = f.read()
        assert "Assumptions Register" in content
        assert "CCM" in content

    def test_sensitivity_export(self, dataset, tmp_path):
        csv_path = str(tmp_path / "test_sensitivity.csv")
        export_sensitivity(dataset, csv_path)
        assert os.path.exists(csv_path)
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) > 0
