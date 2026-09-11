"""Tests for src/load_data.py — verify all raw data loaders work correctly."""
import pandas as pd
import pytest
from src.load_data import (
    load_results,
    load_shootouts,
    load_goalscorers,
    load_elo,
    load_rankings,
    load_fifa_matches,
    load_fifa_teams,
    load_match_features,
)


class TestLoadResults:
    def test_returns_dataframe(self):
        df = load_results()
        assert isinstance(df, pd.DataFrame)

    def test_not_empty(self):
        df = load_results()
        assert len(df) > 10_000, f"Expected >10k rows, got {len(df)}"

    def test_required_columns(self):
        df = load_results()
        required = {"date", "home_team", "away_team", "home_score", "away_score"}
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_scores_are_non_negative(self):
        df = load_results().dropna(subset=["home_score", "away_score"])
        assert (df["home_score"] >= 0).all()
        assert (df["away_score"] >= 0).all()

    def test_date_parseable(self):
        df = load_results()
        dates = pd.to_datetime(df["date"], errors="coerce")
        assert dates.isna().sum() == 0, "Some dates failed to parse"


class TestLoadElo:
    def test_returns_dataframe(self):
        df = load_elo()
        assert isinstance(df, pd.DataFrame)

    def test_not_empty(self):
        df = load_elo()
        assert len(df) > 1000

    def test_required_columns(self):
        df = load_elo()
        required = {"date", "team", "rating"}
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"


class TestLoadRankings:
    def test_returns_dataframe(self):
        df = load_rankings()
        assert isinstance(df, pd.DataFrame)

    def test_not_empty(self):
        df = load_rankings()
        assert len(df) > 100

    def test_rank_column_positive(self):
        df = load_rankings()
        assert "rank" in df.columns
        assert (df["rank"] > 0).all()


class TestLoadMatchFeatures:
    def test_returns_dataframe(self):
        df = load_match_features()
        assert isinstance(df, pd.DataFrame)

    def test_not_empty(self):
        df = load_match_features()
        assert len(df) > 100
