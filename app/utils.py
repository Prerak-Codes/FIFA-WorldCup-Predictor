"""
Shared utilities for the FIFA World Cup Predictor Streamlit App.
"""

import pickle
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Resolve paths relative to repository root ────────────────────────────────
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
sys.path.insert(0, str(BASE_DIR))

from src.simulate_tournament import TournamentSimulator, DEFAULT_GROUPS

import re

def clean_html(html: str) -> str:
    """Removes HTML comments, strips whitespace, and collapses newlines."""
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    lines = [line.strip() for line in html.strip().splitlines() if line.strip()]
    return "".join(lines)

# ── Cached resource loaders ──────────────────────────────────────────────────

@st.cache_resource(show_spinner="Initializing prediction engine…")
def load_simulator() -> TournamentSimulator:
    sim = TournamentSimulator(
        model_path=str(BASE_DIR / "models" / "best_model.pkl"),
        elo_path=str(BASE_DIR / "data" / "interim" / "elo_clean.csv"),
        rankings_path=str(BASE_DIR / "data" / "interim" / "rankings_clean.csv"),
        match_features_path=str(BASE_DIR / "data" / "interim" / "match_features_clean.csv"),
    )
    return sim


@st.cache_data(show_spinner="Loading Elo ratings…")
def load_elo_history() -> pd.DataFrame:
    df = pd.read_csv(BASE_DIR / "data" / "interim" / "elo_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(show_spinner="Loading match database…")
def load_results() -> pd.DataFrame:
    df = pd.read_csv(BASE_DIR / "data" / "interim" / "results_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(show_spinner="Loading simulation models…")
def load_simulation_csv() -> Optional[pd.DataFrame]:
    p = BASE_DIR / "data" / "predictions" / "world_cup_simulation_summary.csv"
    if p.exists():
        return pd.read_csv(p)
    return None


# ── Matchup Inference Engine ──────────────────────────────────────────────────

def predict_matchup(
    sim: TournamentSimulator,
    home_team: str,
    away_team: str,
    is_neutral: bool,
    tournament: str,
    year: int,
) -> Tuple[float, float, float]:
    """
    Returns (P_home_win, P_draw, P_away_win) for a custom matchup.
    Builds a fresh single-row DataFrame and calls the model pipeline.
    """
    if home_team == away_team:
        return (0.333, 0.334, 0.333)

    p1 = sim.team_profiles.get(home_team, {})
    p2 = sim.team_profiles.get(away_team, {})

    elo1 = p1.get("elo", 1500.0)
    elo2 = p2.get("elo", 1500.0)
    rank1 = p1.get("rank", 50.0)
    rank2 = p2.get("rank", 50.0)

    row = {
        "match_year": year,
        "home_team": home_team,
        "away_team": away_team,
        "tournament": tournament,
        "elo_diff": elo1 - elo2,
        "rank_diff": rank2 - rank1,
        "home_advantage": 0 if is_neutral else 1,
        "h2h_win_rate_diff": 0.0,
        "h2h_total_matches": 0,
        "form_win_rate_diff": p1.get("form_wr", 0.33) - p2.get("form_wr", 0.33),
        "form_goal_diff": p1.get("form_gd", 0.0) - p2.get("form_gd", 0.0),
        "overall_diff": p1.get("overall", 72.0) - p2.get("overall", 72.0),
        "attack_diff": p1.get("attack", 72.0) - p2.get("attack", 72.0),
        "defense_diff": p1.get("defense", 72.0) - p2.get("defense", 72.0),
        "is_world_cup": 1 if "World Cup" in tournament else 0,
        "is_continental": 1 if any(x in tournament for x in ["Euro", "Copa", "AFCON", "Asian"]) else 0,
    }

    df = pd.DataFrame([row])
    probs = sim.model.predict_proba(df)[0]

    if is_neutral:
        # Symmetrize for neutral venue
        row2 = row.copy()
        row2["home_team"] = away_team
        row2["away_team"] = home_team
        row2["home_advantage"] = 0
        row2["elo_diff"] = elo2 - elo1
        row2["rank_diff"] = rank1 - rank2
        row2["form_win_rate_diff"] = -row["form_win_rate_diff"]
        row2["form_goal_diff"] = -row["form_goal_diff"]
        row2["overall_diff"] = -row["overall_diff"]
        row2["attack_diff"] = -row["attack_diff"]
        row2["defense_diff"] = -row["defense_diff"]
        df2 = pd.DataFrame([row2])
        probs2 = sim.model.predict_proba(df2)[0]

        p_home = 0.5 * (probs[0] + probs2[2])
        p_draw = 0.5 * (probs[1] + probs2[1])
        p_away = 0.5 * (probs[2] + probs2[0])
        total = p_home + p_draw + p_away
        return (p_home / total, p_draw / total, p_away / total)

    return (float(probs[0]), float(probs[1]), float(probs[2]))


def prob_bar_chart(home: str, away: str, p_home: float, p_draw: float, p_away: float) -> go.Figure:
    """Modern dark-themed horizontal stacked bar chart of Win/Draw/Loss probabilities."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name=f"{home} Win",
        x=[round(p_home * 100, 1)],
        y=["Probability"],
        orientation="h",
        marker=dict(color="#10B981", line=dict(color="rgba(255,255,255,0.15)", width=1)),
        text=[f"{p_home:.1%}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=13, family="Inter, sans-serif"),
        hovertemplate=f"<b>{home} Win</b>: {p_home:.1%}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Draw",
        x=[round(p_draw * 100, 1)],
        y=["Probability"],
        orientation="h",
        marker=dict(color="#64748B", line=dict(color="rgba(255,255,255,0.15)", width=1)),
        text=[f"{p_draw:.1%}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=13, family="Inter, sans-serif"),
        hovertemplate=f"<b>Draw</b>: {p_draw:.1%}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name=f"{away} Win",
        x=[round(p_away * 100, 1)],
        y=["Probability"],
        orientation="h",
        marker=dict(color="#F43F5E", line=dict(color="rgba(255,255,255,0.15)", width=1)),
        text=[f"{p_away:.1%}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=13, family="Inter, sans-serif"),
        hovertemplate=f"<b>{away} Win</b>: {p_away:.1%}<extra></extra>",
    ))

    fig.update_layout(
        template="plotly_dark",
        barmode="stack",
        height=85,
        margin=dict(l=0, r=0, t=10, b=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=12),
        ),
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            fixedrange=True,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
