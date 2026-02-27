"""Tests for uncertainty module."""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.uncertainty import (
    percentiles_to_quantile_spec,
    fit_best,
    generate_draws,
    fit_and_draw,
)


class TestPercentileConversion:
    def test_string_keys(self):
        spec = percentiles_to_quantile_spec({"p10": 5, "p50": 20, "p90": 100})
        assert spec == {0.10: 5.0, 0.50: 20.0, 0.90: 100.0}

    def test_numeric_keys(self):
        spec = percentiles_to_quantile_spec({10: 5, 50: 20, 90: 100})
        assert spec == {0.10: 5.0, 0.50: 20.0, 0.90: 100.0}


class TestFitBest:
    def test_lognormal_inputs(self):
        """Lognormal-shaped inputs should fit well."""
        fit = fit_best({"p10": 5, "p50": 20, "p90": 80})
        assert fit is not None
        assert fit.error < 1.0
        assert fit.median() > 0

    def test_symmetric_inputs(self):
        """Symmetric inputs should fit normal or similar."""
        fit = fit_best({"p10": 10, "p50": 50, "p90": 90})
        assert fit is not None
        assert fit.error < 1.0

    def test_tiebreaker_prefers_lighter_tails(self):
        """When errors are tied, should pick least heavy-tailed distribution."""
        fit = fit_best({"p10": 1000, "p50": 5000, "p90": 25000})
        assert fit.name != "log_students_t"


class TestDrawGeneration:
    def test_draw_count(self):
        fit = fit_best({"p10": 10, "p50": 50, "p90": 200})
        draws = generate_draws(fit, n_samples=1000)
        assert len(draws) == 1000

    def test_draws_sorted(self):
        """Quantile-spaced draws should be monotonically increasing."""
        fit = fit_best({"p10": 10, "p50": 50, "p90": 200})
        draws = generate_draws(fit, n_samples=100)
        assert np.all(np.diff(draws) >= 0)

    def test_fit_and_draw_convenience(self):
        fit, draws = fit_and_draw({"p10": 5, "p50": 20, "p90": 80}, n_samples=500)
        assert fit is not None
        assert len(draws) == 500
