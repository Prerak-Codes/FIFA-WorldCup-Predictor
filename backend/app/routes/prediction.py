"""
Prediction & Tournament API Routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from backend.app.schemas.prediction import (
    MatchupRequest,
    MatchupResponse,
    SingleSimulationRequest,
    SingleSimulationResponse,
    MonteCarloResponse,
    TeamEloResponse,
    RadarAttributeItem,
)
from backend.app.services.predictor import PredictorService

router = APIRouter(prefix="/api", tags=["Predictions & Tournament"])


@router.get("/teams")
def get_teams():
    """Returns qualified 32 World Cup nations, all historical Elo teams, and tournament groups."""
    service = PredictorService.get_instance()
    return service.get_teams()


@router.post("/predict", response_model=MatchupResponse)
def predict_matchup(req: MatchupRequest):
    """Calculates win/draw/loss probabilities for two competing nations."""
    service = PredictorService.get_instance()
    if req.home_team == req.away_team:
        raise HTTPException(status_code=400, detail="Home team and away team must be distinct.")
    return service.predict_matchup(req)


@router.post("/simulate/single", response_model=SingleSimulationResponse)
def simulate_single(req: SingleSimulationRequest):
    """Simulates one complete 32-team World Cup tournament from groups to final."""
    service = PredictorService.get_instance()
    return service.simulate_single_tournament(seed=req.seed)


@router.get("/simulate/leaderboard", response_model=MonteCarloResponse)
def get_leaderboard():
    """Returns stage advancement and championship probabilities across 10,000 simulations."""
    service = PredictorService.get_instance()
    return service.get_simulation_leaderboard()


@router.post("/simulate/monte-carlo", response_model=MonteCarloResponse)
def run_monte_carlo(simulations: int = Query(10000, ge=100, le=50000), seed: int = 42):
    """Executes a fresh batch of Monte Carlo tournament simulations."""
    service = PredictorService.get_instance()
    return service.run_monte_carlo(simulations=simulations, seed=seed)


@router.get("/analytics/elo-history", response_model=List[TeamEloResponse])
def get_elo_history(teams: str = Query("Spain,England,France,Brazil,Argentina")):
    """Returns historical Elo rating trajectory for requested teams."""
    service = PredictorService.get_instance()
    team_list = [t.strip() for t in teams.split(",") if t.strip()]
    return service.get_elo_history(team_list)


@router.get("/analytics/radar", response_model=List[RadarAttributeItem])
def get_radar_profiles(teams: str = Query("Spain,England,France,Brazil,Argentina")):
    """Returns normalized multidimensional radar attributes (Attack, Defense, Elo, Form)."""
    service = PredictorService.get_instance()
    team_list = [t.strip() for t in teams.split(",") if t.strip()]
    return service.get_radar_profiles(team_list)
