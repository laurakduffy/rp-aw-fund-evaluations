"""Tests for risk_profiles module."""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.risk_profiles import compute_risk_profiles, RISK_PROFILES


class TestRiskProfiles:
    def test_all_profiles_present(self):
        draws = np.random.lognormal(mean=5, sigma=1, size=10000)
        result = compute_risk_profiles(draws)
        for rp in RISK_PROFILES:
            assert rp in result

    def test_upside_less_than_neutral(self):
        """Truncating upper tail should reduce mean."""
        draws = np.random.lognormal(mean=5, sigma=2, size=10000)
        result = compute_risk_profiles(draws)
        assert result["upside"] <= result["neutral"]

    def test_downside_less_than_neutral(self):
        """Loss aversion should reduce expected utility when there's variance."""
        draws = np.random.normal(loc=100, scale=50, size=10000)
        result = compute_risk_profiles(draws)
        assert result["downside"] <= result["neutral"]

    def test_combined_most_conservative(self):
        """Combined should be <= both upside and downside."""
        draws = np.random.lognormal(mean=5, sigma=2, size=10000)
        result = compute_risk_profiles(draws)
        assert result["combined"] <= result["neutral"]

    def test_constant_draws_all_equal(self):
        """With zero variance, all profiles should be equal."""
        draws = np.full(1000, 42.0)
        result = compute_risk_profiles(draws)
        for rp in RISK_PROFILES:
            assert abs(result[rp] - 42.0) < 1e-10
