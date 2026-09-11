import pandas as pd
from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = BASE_DIR / "data" / "raw" 


def load_results():
    return pd.read_csv(RAW_DATA / "international_results" / "results.csv")


def load_shootouts():
    return pd.read_csv(RAW_DATA / "international_results" / "shootouts.csv")


def load_goalscorers():
    return pd.read_csv(RAW_DATA / "international_results" / "goalscorers.csv")


def load_former_names():
    return pd.read_csv(RAW_DATA / "international_results" / "former_names.csv")


def load_elo():
    return pd.read_csv(RAW_DATA / "elo_ratings" / "eloratings.csv")


def load_rankings():
    return pd.read_csv(RAW_DATA / "fifa_rankings" / "fifa_rankings.csv")


def load_fifa_matches():
    return pd.read_csv(RAW_DATA / "fifa_rankings" / "fifa_matches.csv")


def load_fifa_teams():
    return pd.read_csv(RAW_DATA / "fifa_rankings" / "fifa_teams.csv")


def load_team_form():
    return pd.read_csv(RAW_DATA / "match_features" / "teams_form.csv")


def load_match_features():
    return pd.read_csv(RAW_DATA / "match_features" / "teams_match_features.csv")


def load_player_aggregates():
    return pd.read_csv(RAW_DATA / "match_features" / "player_aggregates.csv")