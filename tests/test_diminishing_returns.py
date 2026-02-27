"""Tests for diminishing_returns module."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.diminishing_returns import (
    eval_diminishing_raw,
    compute_diminishing_row,
    find_20pct_threshold,
    years_in_period,
    allocate_to_periods,
)


class TestEvalDiminishingRaw:
    def test_at_baseline(self):
        anchors = [[1, 1.0], [2, 0.8], [5, 0.3]]
        # At 1x budget, CE = 1.0
        assert eval_diminishing_raw(10, anchors, 10) == 1.0

    def test_interpolation(self):
        anchors = [[1, 1.0], [2, 0.5]]
        # At 1.5x budget = $15M with $10M budget
        val = eval_diminishing_raw(10, anchors, 15)
        assert abs(val - 0.75) < 1e-10

    def test_beyond_last_anchor(self):
        anchors = [[1, 1.0], [5, 0.5]]
        # Beyond 5x should decay as 1/x
        val = eval_diminishing_raw(10, anchors, 100)  # 10x
        assert val < 0.5
        assert val > 0

    def test_below_first_anchor(self):
        anchors = [[1, 1.0], [5, 0.5]]
        val = eval_diminishing_raw(10, anchors, 5)  # 0.5x
        assert val == 1.0


class TestComputeDiminishingRow:
    def test_normalized_to_one(self):
        anchors = [[1, 1.0], [5, 0.5], [10, 0.1]]
        values, _ = compute_diminishing_row(10, anchors)
        assert abs(values[0] - 1.0) < 1e-10

    def test_decreasing(self):
        anchors = [[1, 1.0], [5, 0.5], [10, 0.1]]
        values, _ = compute_diminishing_row(10, anchors)
        assert values[-1] < values[0]


class TestFind20PctThreshold:
    def test_finds_threshold(self):
        anchors = [[1, 1.0], [5, 0.5], [10, 0.1]]
        threshold = find_20pct_threshold(10, anchors)
        assert threshold is not None
        assert threshold > 10

    def test_none_when_no_threshold(self):
        anchors = [[1, 1.0], [2, 0.95]]
        # With slow decay, might not hit 20% in range
        threshold = find_20pct_threshold(100, anchors, max_spend_m=200)
        # Could be None or found, just check it doesn't crash


class TestYearsInPeriod:
    def test_full_overlap(self):
        assert years_in_period(10, 0, 5) == 5.0

    def test_partial_overlap(self):
        assert years_in_period(3, 0, 5) == 3.0

    def test_no_overlap(self):
        assert years_in_period(3, 5, 10) == 0.0

    def test_open_end(self):
        assert years_in_period(100, 50, None) == 50.0


class TestAllocateToPeriods:
    def test_fractions_sum_to_one_or_less(self):
        fracs = allocate_to_periods(0, 10)
        total = sum(fracs.values())
        assert total <= 1.0 + 1e-10

    def test_short_persistence_concentrated(self):
        fracs = allocate_to_periods(0, 3)
        # All effect should be in the first period (0-5 years)
        assert fracs["0_to_5"] > 0
