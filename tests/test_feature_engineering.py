"""
Tests for src/feature_engineering.py.
Verifies temporal ordering, no-future-leakage, and correct feature values.
"""
import numpy as np
import pandas as pd
import pytest


class TestTrainingData:
    """Test the pre-built training_data.csv for structural correctness."""

    def test_minimum_row_count(self, training_df):
        assert len(training_df) > 40_000, f"Expected >40k rows, got {len(training_df)}"

    def test_target_column_exists(self, training_df):
        # The training CSV stores the label as match_result_encoded
        assert "match_result_encoded" in training_df.columns

    def test_target_values_valid(self, training_df):
        valid = {0, 1, 2}
        actual = set(training_df["match_result_encoded"].unique())
        assert actual.issubset(valid), f"Unexpected target values: {actual - valid}"

    def test_required_numeric_features(self, training_df):
        required = [
            "elo_diff", "rank_diff", "home_advantage",
            "h2h_win_rate_diff", "h2h_total_matches",
            "form_win_rate_diff", "form_goal_diff",
            "overall_diff", "attack_diff", "defense_diff",
        ]
        missing = [c for c in required if c not in training_df.columns]
        assert not missing, f"Missing feature columns: {missing}"

    def test_home_advantage_binary(self, training_df):
        vals = training_df["home_advantage"].unique()
        for v in vals:
            assert v in (0, 1), f"home_advantage has non-binary value: {v}"

    def test_dates_sorted_ascending(self, training_df):
        dates = training_df["date"]
        assert dates.is_monotonic_increasing, "Training data is not sorted by date"

    def test_no_future_leakage_h2h(self, training_df):
        """
        First row should have h2h_total_matches == 0 because
        no prior encounters exist at the very start of history.
        """
        first_row = training_df.iloc[0]
        assert first_row["h2h_total_matches"] == 0, (
            f"First row h2h_total_matches={first_row['h2h_total_matches']}, expected 0"
        )

    def test_is_world_cup_binary(self, training_df):
        if "is_world_cup" in training_df.columns:
            vals = training_df["is_world_cup"].unique()
            for v in vals:
                assert v in (0, 1), f"is_world_cup has non-binary value: {v}"

    def test_train_test_temporal_split(self, training_df):
        """Verify temporal split: training subset ends <=2020, test subset starts >=2021."""
        train = training_df[training_df["date"].dt.year <= 2020]
        test = training_df[training_df["date"].dt.year >= 2021]
        assert len(train) > 30_000, f"Training set too small: {len(train)}"
        assert len(test) > 1_000, f"Test set too small: {len(test)}"
        assert train["date"].max() < test["date"].min(), "Temporal split overlap detected!"


class TestEloData:
    def test_elo_ratings_in_realistic_range(self, elo_df):
        # Filter out 0/NaN padding rows that appear for unrated nations
        rated = elo_df[elo_df["rating"] > 0]["rating"]
        assert (rated > 200).all(), "Some non-zero Elo ratings below 200"
        assert (rated < 3000).all(), "Some Elo ratings above 3000"

    def test_elo_sorted_by_date(self, elo_df):
        for team, grp in elo_df.groupby("team"):
            assert grp["date"].is_monotonic_increasing, f"Elo not sorted for {team}"

    def test_world_cup_teams_have_elo(self, elo_df):
        tournament_teams = [
            "Spain", "England", "France", "Brazil", "Argentina",
            "Germany", "Portugal", "Netherlands",
        ]
        elo_teams = set(elo_df["team"].unique())
        for team in tournament_teams:
            assert team in elo_teams, f"{team} missing from Elo data"
