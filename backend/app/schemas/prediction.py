"""
Pydantic Schemas for Match Prediction and Tournament Simulation API.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MatchupRequest(BaseModel):
    home_team: str = Field(..., example="Spain")
    away_team: str = Field(..., example="England")
    is_neutral: bool = Field(True, example=True)
    tournament: str = Field("FIFA World Cup", example="FIFA World Cup")
    match_year: int = Field(2026, example=2026)


class TeamMetrics(BaseModel):
    elo: float
    rank: int
    overall: float
    attack: float
    defense: float
    form_wr: float
    form_gd: float


class MatchupResponse(BaseModel):
    home_team: str
    away_team: str
    is_neutral: bool
    tournament: str
    match_year: int
    p_home: float
    p_draw: float
    p_away: float
    predicted_outcome: str
    advantage_pct: float
    home_profile: TeamMetrics
    away_profile: TeamMetrics


class SingleSimulationRequest(BaseModel):
    seed: int = Field(0, example=42)


class SingleSimulationResponse(BaseModel):
    champion: str
    runner_up: str
    third: str
    group_advancers: Dict[str, List[str]]
    r16: List[str]
    qf: List[str]
    sf: List[str]
    final: List[str]


class MonteCarloLeaderboardItem(BaseModel):
    team: str
    elo: float
    rank: int
    r16_pct: float
    qf_pct: float
    sf_pct: float
    final_pct: float
    champion_pct: float


class MonteCarloResponse(BaseModel):
    total_simulations: int
    elapsed_seconds: float
    leaderboard: List[MonteCarloLeaderboardItem]


class EloDataPoint(BaseModel):
    date: str
    rating: float


class TeamEloResponse(BaseModel):
    team: str
    history: List[EloDataPoint]


class RadarAttributeItem(BaseModel):
    team: str
    elo_norm: float
    attack: float
    defense: float
    overall: float
    form_wr: float
    form_gd_norm: float
