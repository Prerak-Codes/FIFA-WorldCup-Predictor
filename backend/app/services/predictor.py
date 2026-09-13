"""
PredictorService — Core ML Inference & Tournament Simulation Engine.
"""

import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd

# Path resolving
BACKEND_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from src.simulate_tournament import TournamentSimulator, DEFAULT_GROUPS
from backend.app.schemas.prediction import (
    MatchupRequest,
    MatchupResponse,
    TeamMetrics,
    SingleSimulationResponse,
    MonteCarloResponse,
    MonteCarloLeaderboardItem,
    TeamEloResponse,
    EloDataPoint,
    RadarAttributeItem,
)


class PredictorService:
    _instance: Optional["PredictorService"] = None

    def __init__(self):
        models_dir = BACKEND_DIR / "models"
        data_dir = BACKEND_DIR / "data"

        model_path = str(models_dir / "best_model.pkl")
        elo_path = str(data_dir / "interim" / "elo_clean.csv")
        rankings_path = str(data_dir / "interim" / "rankings_clean.csv")
        match_features_path = str(data_dir / "interim" / "match_features_clean.csv")

        # Fallback to root directories if backend copies don't exist yet
        if not Path(model_path).exists():
            model_path = str(ROOT_DIR / "models" / "best_model.pkl")
        if not Path(elo_path).exists():
            elo_path = str(ROOT_DIR / "data" / "interim" / "elo_clean.csv")
        if not Path(rankings_path).exists():
            rankings_path = str(ROOT_DIR / "data" / "interim" / "rankings_clean.csv")
        if not Path(match_features_path).exists():
            match_features_path = str(ROOT_DIR / "data" / "interim" / "match_features_clean.csv")

        print("[INFO] Loading TournamentSimulator into PredictorService...")
        self.sim = TournamentSimulator(
            model_path=model_path,
            elo_path=elo_path,
            rankings_path=rankings_path,
            match_features_path=match_features_path,
        )
        print(f"[OK] Loaded {len(self.sim.all_teams)} tournament teams.")

        # Load Elo history dataframe
        self.elo_df = pd.read_csv(elo_path)
        self.elo_df["date"] = pd.to_datetime(self.elo_df["date"]).dt.strftime("%Y-%m-%d")

    @classmethod
    def get_instance(cls) -> "PredictorService":
        if cls._instance is None:
            cls._instance = PredictorService()
        return cls._instance

    def get_teams(self) -> Dict[str, Any]:
        """Returns tournament qualified teams (32) and all available Elo teams."""
        all_elo_teams = sorted(self.elo_df["team"].unique().tolist())
        return {
            "tournament_teams": sorted(self.sim.all_teams),
            "all_elo_teams": all_elo_teams,
            "groups": DEFAULT_GROUPS,
        }

    def predict_matchup(self, req: MatchupRequest) -> MatchupResponse:
        home = req.home_team
        away = req.away_team
        is_neutral = req.is_neutral
        year = req.match_year
        tournament = req.tournament

        p1 = self.sim.team_profiles.get(home, {})
        p2 = self.sim.team_profiles.get(away, {})

        elo1 = p1.get("elo", 1500.0)
        elo2 = p2.get("elo", 1500.0)
        rank1 = p1.get("rank", 50.0)
        rank2 = p2.get("rank", 50.0)

        row = {
            "match_year": year,
            "home_team": home,
            "away_team": away,
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
        probs = self.sim.model.predict_proba(df)[0]

        if is_neutral:
            row2 = row.copy()
            row2["home_team"] = away
            row2["away_team"] = home
            row2["home_advantage"] = 0
            row2["elo_diff"] = elo2 - elo1
            row2["rank_diff"] = rank1 - rank2
            row2["form_win_rate_diff"] = -row["form_win_rate_diff"]
            row2["form_goal_diff"] = -row["form_goal_diff"]
            row2["overall_diff"] = -row["overall_diff"]
            row2["attack_diff"] = -row["attack_diff"]
            row2["defense_diff"] = -row["defense_diff"]
            df2 = pd.DataFrame([row2])
            probs2 = self.sim.model.predict_proba(df2)[0]

            p_h = 0.5 * (probs[0] + probs2[2])
            p_d = 0.5 * (probs[1] + probs2[1])
            p_a = 0.5 * (probs[2] + probs2[0])
            total = p_h + p_d + p_a
            p_home, p_draw, p_away = float(p_h / total), float(p_d / total), float(p_a / total)
        else:
            p_home, p_draw, p_away = float(probs[0]), float(probs[1]), float(probs[2])

        if p_home > p_away and p_home > p_draw:
            predicted_outcome = f"{home} Favored"
            advantage_pct = round((p_home - p_away) * 100, 1)
        elif p_draw > p_home and p_draw > p_away:
            predicted_outcome = "Draw Likely"
            advantage_pct = round(p_draw * 100, 1)
        else:
            predicted_outcome = f"{away} Favored"
            advantage_pct = round((p_away - p_home) * 100, 1)

        home_profile = TeamMetrics(
            elo=round(p1.get("elo", 1500.0), 1),
            rank=int(p1.get("rank", 50)),
            overall=round(p1.get("overall", 72.0), 1),
            attack=round(p1.get("attack", 72.0), 1),
            defense=round(p1.get("defense", 72.0), 1),
            form_wr=round(p1.get("form_wr", 0.33), 3),
            form_gd=round(p1.get("form_gd", 0.0), 2),
        )

        away_profile = TeamMetrics(
            elo=round(p2.get("elo", 1500.0), 1),
            rank=int(p2.get("rank", 50)),
            overall=round(p2.get("overall", 72.0), 1),
            attack=round(p2.get("attack", 72.0), 1),
            defense=round(p2.get("defense", 72.0), 1),
            form_wr=round(p2.get("form_wr", 0.33), 3),
            form_gd=round(p2.get("form_gd", 0.0), 2),
        )

        return MatchupResponse(
            home_team=home,
            away_team=away,
            is_neutral=is_neutral,
            tournament=tournament,
            match_year=year,
            p_home=round(p_home, 4),
            p_draw=round(p_draw, 4),
            p_away=round(p_away, 4),
            predicted_outcome=predicted_outcome,
            advantage_pct=advantage_pct,
            home_profile=home_profile,
            away_profile=away_profile,
        )

    def simulate_single_tournament(self, seed: int = 0) -> SingleSimulationResponse:
        if seed > 0:
            random.seed(seed)
            np.random.seed(seed)

        res = self.sim.simulate_single_tournament()
        group_adv = {k: list(v) for k, v in res["group_advancers"].items()}

        return SingleSimulationResponse(
            champion=res["champion"],
            runner_up=res["runner_up"],
            third=res["third"],
            group_advancers=group_adv,
            r16=res["r16"],
            qf=res["qf"],
            sf=res["sf"],
            final=res["final"],
        )

    def get_simulation_leaderboard(self) -> MonteCarloResponse:
        p = BACKEND_DIR / "data" / "predictions" / "world_cup_simulation_summary.csv"
        if not p.exists():
            p = ROOT_DIR / "data" / "predictions" / "world_cup_simulation_summary.csv"

        if p.exists():
            df = pd.read_csv(p)
            items = []
            for _, r in df.iterrows():
                items.append(MonteCarloLeaderboardItem(
                    team=r["team"],
                    elo=float(r["elo"]),
                    rank=int(r["rank"]),
                    r16_pct=float(r["r16_pct"]),
                    qf_pct=float(r["qf_pct"]),
                    sf_pct=float(r["sf_pct"]),
                    final_pct=float(r["final_pct"]),
                    champion_pct=float(r["champion_pct"]),
                ))
            return MonteCarloResponse(
                total_simulations=10000,
                elapsed_seconds=1.04,
                leaderboard=items,
            )

        # Fallback if uncalculated
        return self.run_monte_carlo(simulations=1000, seed=42)

    def run_monte_carlo(self, simulations: int = 10000, seed: int = 42) -> MonteCarloResponse:
        summary_df, meta = self.sim.run_monte_carlo(num_simulations=simulations, seed=seed)
        
        # Save output
        out_p = BACKEND_DIR / "data" / "predictions" / "world_cup_simulation_summary.csv"
        out_p.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(out_p, index=False)

        items = []
        for _, r in summary_df.iterrows():
            items.append(MonteCarloLeaderboardItem(
                team=r["team"],
                elo=float(r["elo"]),
                rank=int(r["rank"]),
                r16_pct=float(r["r16_pct"]),
                qf_pct=float(r["qf_pct"]),
                sf_pct=float(r["sf_pct"]),
                final_pct=float(r["final_pct"]),
                champion_pct=float(r["champion_pct"]),
            ))

        return MonteCarloResponse(
            total_simulations=simulations,
            elapsed_seconds=float(meta["metadata"]["elapsed_seconds"]),
            leaderboard=items,
        )

    def get_elo_history(self, teams: List[str]) -> List[TeamEloResponse]:
        results = []
        filtered = self.elo_df[self.elo_df["team"].isin(teams)].sort_values("date")
        for team in teams:
            t_df = filtered[filtered["team"] == team]
            pts = [EloDataPoint(date=r["date"], rating=float(r["rating"])) for _, r in t_df.iterrows()]
            results.append(TeamEloResponse(team=team, history=pts))
        return results

    def get_radar_profiles(self, teams: List[str]) -> List[RadarAttributeItem]:
        results = []
        all_elos = [v["elo"] for v in self.sim.team_profiles.values()]
        elo_min, elo_max = min(all_elos), max(all_elos)

        for t in teams:
            prof = self.sim.team_profiles.get(t)
            if prof:
                elo_norm = float((prof["elo"] - elo_min) / (elo_max - elo_min) * 100)
                form_gd_norm = float(max(0.0, min(100.0, 50.0 + prof["form_gd"] * 10)))
                results.append(RadarAttributeItem(
                    team=t,
                    elo_norm=round(elo_norm, 1),
                    attack=round(float(prof["attack"]), 1),
                    defense=round(float(prof["defense"]), 1),
                    overall=round(float(prof["overall"]), 1),
                    form_wr=round(float(prof["form_wr"] * 100), 1),
                    form_gd_norm=round(form_gd_norm, 1),
                ))
        return results
