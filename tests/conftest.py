"""Shared pytest fixtures for the FIFA World Cup Predictor test suite."""
import sys
from pathlib import Path

import pandas as pd
import pytest

# Make src/ importable without installing the package
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


@pytest.fixture(scope="session")
def repo_dir():
    return REPO


@pytest.fixture(scope="session")
def interim_dir(repo_dir):
    return repo_dir / "data" / "interim"


@pytest.fixture(scope="session")
def processed_dir(repo_dir):
    return repo_dir / "data" / "processed"


@pytest.fixture(scope="session")
def models_dir(repo_dir):
    return repo_dir / "models"


@pytest.fixture(scope="session")
def raw_results_df(repo_dir):
    return pd.read_csv(repo_dir / "data" / "raw" / "international_results" / "results.csv")


@pytest.fixture(scope="session")
def elo_df(interim_dir):
    df = pd.read_csv(interim_dir / "elo_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@pytest.fixture(scope="session")
def rankings_df(interim_dir):
    df = pd.read_csv(interim_dir / "rankings_clean.csv")
    df["rank_date"] = pd.to_datetime(df["rank_date"])
    return df


@pytest.fixture(scope="session")
def training_df(processed_dir):
    df = pd.read_csv(processed_dir / "training_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@pytest.fixture(scope="session")
def simulator(repo_dir):
    from src.simulate_tournament import TournamentSimulator
    return TournamentSimulator(
        model_path=str(repo_dir / "models" / "best_model.pkl"),
        elo_path=str(repo_dir / "data" / "interim" / "elo_clean.csv"),
        rankings_path=str(repo_dir / "data" / "interim" / "rankings_clean.csv"),
        match_features_path=str(repo_dir / "data" / "interim" / "match_features_clean.csv"),
    )
