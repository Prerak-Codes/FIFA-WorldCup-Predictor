"""
Tournament Simulation Engine for FIFA World Cup Predictor.
Uses trained ML models and Monte Carlo simulations to simulate
group stages, knockout brackets, and tournament outcomes.
"""

import argparse
import json
import logging
import pickle
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_GROUPS = {
    "A": ["Qatar", "Ecuador", "Senegal", "Netherlands"],
    "B": ["England", "Iran", "United States", "Wales"],
    "C": ["Argentina", "Saudi Arabia", "Mexico", "Poland"],
    "D": ["France", "Australia", "Denmark", "Tunisia"],
    "E": ["Spain", "Costa Rica", "Germany", "Japan"],
    "F": ["Belgium", "Canada", "Morocco", "Croatia"],
    "G": ["Brazil", "Serbia", "Switzerland", "Cameroon"],
    "H": ["Portugal", "Ghana", "Uruguay", "South Korea"],
}


class TournamentSimulator:
    """Monte Carlo Tournament Simulator driven by predictive ML models."""

    def __init__(
        self,
        model_path: str = "models/best_model.pkl",
        elo_path: str = "data/interim/elo_clean.csv",
        rankings_path: str = "data/interim/rankings_clean.csv",
        match_features_path: str = "data/interim/match_features_clean.csv",
        groups: Optional[Dict[str, List[str]]] = None,
    ):
        self.model_path = Path(model_path)
        self.elo_path = Path(elo_path)
        self.rankings_path = Path(rankings_path)
        self.match_features_path = Path(match_features_path)
        self.groups = groups or DEFAULT_GROUPS
        self.all_teams = [team for grp in self.groups.values() for team in grp]

        self.model = None
        self.team_profiles: Dict[str, Dict[str, float]] = {}
        self.symmetric_probs: Dict[Tuple[str, str], Tuple[float, float, float]] = {}

        self._load_assets()
        self._build_team_profiles()
        self.compute_pairwise_probabilities()

    def _load_assets(self):
        """Loads trained model checkpoint and interim team data."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at {self.model_path}")
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)

        self.elo_df = pd.read_csv(self.elo_path)
        self.rankings_df = pd.read_csv(self.rankings_path)
        self.mf_df = pd.read_csv(self.match_features_path)

        self.elo_df["date"] = pd.to_datetime(self.elo_df["date"])
        self.rankings_df["rank_date"] = pd.to_datetime(self.rankings_df["rank_date"])
        self.mf_df["_date"] = pd.to_datetime(self.mf_df["_date"])

    def _build_team_profiles(self):
        """Extracts the most recent Elo ratings, FIFA rankings, and FIFA attributes."""
        latest_elo = self.elo_df.sort_values("date").groupby("team")["rating"].last().to_dict()
        latest_rank = self.rankings_df.sort_values("rank_date").groupby("team")["rank"].last().to_dict()
        latest_mf = self.mf_df.sort_values("_date").groupby("_home_team").last()

        for team in self.all_teams:
            elo_val = float(latest_elo.get(team, 1500.0))
            rank_val = float(latest_rank.get(team, 50.0))

            if team in latest_mf.index:
                row = latest_mf.loc[team]
                overall = float(row.get("home_avg_overall", 72.0))
                attack = float(row.get("home_avg_attack", 72.0))
                defense = float(row.get("home_avg_defense", 72.0))
                form_wr = float(row.get("home_form_win_rate", 0.33))
                form_sc = float(row.get("home_form_scored", 1.2))
                form_co = float(row.get("home_form_conceded", 1.2))
            else:
                overall, attack, defense, form_wr, form_sc, form_co = 72.0, 72.0, 72.0, 0.33, 1.2, 1.2

            self.team_profiles[team] = {
                "elo": elo_val,
                "rank": rank_val,
                "overall": overall,
                "attack": attack,
                "defense": defense,
                "form_wr": form_wr,
                "form_gd": float(form_sc - form_co),
            }

    def compute_pairwise_probabilities(self):
        """
        Precomputes symmetric win/draw/loss probabilities for all pairwise matchups
        in a single batch call to optimize Monte Carlo throughput.
        """
        pairs = []
        pair_keys = []
        for t1 in self.all_teams:
            for t2 in self.all_teams:
                if t1 != t2:
                    p1 = self.team_profiles[t1]
                    p2 = self.team_profiles[t2]
                    pairs.append({
                        "match_year": 2026,
                        "home_team": t1,
                        "away_team": t2,
                        "tournament": "FIFA World Cup",
                        "elo_diff": p1["elo"] - p2["elo"],
                        "rank_diff": p2["rank"] - p1["rank"],
                        "home_advantage": 0,
                        "h2h_win_rate_diff": 0.0,
                        "h2h_total_matches": 0,
                        "form_win_rate_diff": p1["form_wr"] - p2["form_wr"],
                        "form_goal_diff": p1["form_gd"] - p2["form_gd"],
                        "overall_diff": p1["overall"] - p2["overall"],
                        "attack_diff": p1["attack"] - p2["attack"],
                        "defense_diff": p1["defense"] - p2["defense"],
                        "is_world_cup": 1,
                        "is_continental": 0,
                    })
                    pair_keys.append((t1, t2))

        pairs_df = pd.DataFrame(pairs)
        probs_matrix = self.model.predict_proba(pairs_df)

        raw_probs = {}
        for i, (t1, t2) in enumerate(pair_keys):
            raw_probs[(t1, t2)] = probs_matrix[i]

        # Neutral venue symmetrization
        for t1 in self.all_teams:
            for t2 in self.all_teams:
                if t1 != t2:
                    p_t1_as_home = raw_probs[(t1, t2)]  # [P(win t1), P(draw), P(win t2)]
                    p_t2_as_home = raw_probs[(t2, t1)]  # [P(win t2), P(draw), P(win t1)]

                    p1 = 0.5 * (p_t1_as_home[0] + p_t2_as_home[2])
                    draw = 0.5 * (p_t1_as_home[1] + p_t2_as_home[1])
                    p2 = 0.5 * (p_t1_as_home[2] + p_t2_as_home[0])
                    total = p1 + draw + p2
                    self.symmetric_probs[(t1, t2)] = (p1 / total, draw / total, p2 / total)

    def get_matchup_probability(self, team1: str, team2: str) -> Tuple[float, float, float]:
        """Returns (P(team1 win), P(draw), P(team2 win))."""
        if (team1, team2) in self.symmetric_probs:
            return self.symmetric_probs[(team1, team2)]
        if (team2, team1) in self.symmetric_probs:
            p2, draw, p1 = self.symmetric_probs[(team2, team1)]
            return (p1, draw, p2)
        # Fallback if uncomputed
        return (0.333, 0.334, 0.333)

    def simulate_match(
        self, team1: str, team2: str, knockout: bool = False
    ) -> Tuple[str, str, int, int, Optional[str]]:
        """
        Simulates a single match between two teams.
        Returns: (team1, team2, score1, score2, winner).
        In knockout mode, winner is guaranteed (resolved via penalty shootout if tied).
        """
        p1, pdraw, p2 = self.get_matchup_probability(team1, team2)
        r = random.random()

        if r < p1:
            s1 = random.choice([1, 2, 3])
            s2 = random.choice([0, 1]) if s1 > 1 else 0
            return team1, team2, s1, s2, team1
        elif r < p1 + pdraw:
            score = random.choice([0, 1, 2])
            s1, s2 = score, score
            if knockout:
                diff = self.team_profiles[team1]["elo"] - self.team_profiles[team2]["elo"]
                p_pens1 = 0.5 + 0.1 * np.tanh(diff / 200.0)
                winner = team1 if random.random() < p_pens1 else team2
                return team1, team2, s1, s2, winner
            return team1, team2, s1, s2, None
        else:
            s2 = random.choice([1, 2, 3])
            s1 = random.choice([0, 1]) if s2 > 1 else 0
            return team1, team2, s1, s2, team2

    def simulate_group_stage(self) -> Dict[str, Tuple[str, str]]:
        """
        Simulates the group stage (round robin within each group).
        Returns top 2 advancing teams per group.
        """
        advancing = {}
        for grp_name, teams in self.groups.items():
            points = {t: 0 for t in teams}
            gd = {t: 0 for t in teams}
            gf = {t: 0 for t in teams}

            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    t1, t2 = teams[i], teams[j]
                    _, _, s1, s2, winner = self.simulate_match(t1, t2, knockout=False)
                    gf[t1] += s1
                    gf[t2] += s2
                    gd[t1] += (s1 - s2)
                    gd[t2] += (s2 - s1)
                    if winner == t1:
                        points[t1] += 3
                    elif winner == t2:
                        points[t2] += 3
                    else:
                        points[t1] += 1
                        points[t2] += 1

            ranked = sorted(
                teams,
                key=lambda t: (points[t], gd[t], gf[t], random.random()),
                reverse=True,
            )
            advancing[grp_name] = (ranked[0], ranked[1])
        return advancing

    def simulate_knockout_stage(self, advancing: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """
        Simulates standard World Cup 16-team knockout bracket:
        R16 -> QF -> SF -> Final & 3rd place match.
        """
        # Round of 16 bracket structure
        r16_matchups = [
            (advancing["A"][0], advancing["B"][1]),
            (advancing["C"][0], advancing["D"][1]),
            (advancing["E"][0], advancing["F"][1]),
            (advancing["G"][0], advancing["H"][1]),
            (advancing["B"][0], advancing["A"][1]),
            (advancing["D"][0], advancing["C"][1]),
            (advancing["F"][0], advancing["E"][1]),
            (advancing["H"][0], advancing["G"][1]),
        ]

        qf_teams = []
        for t1, t2 in r16_matchups:
            _, _, _, _, winner = self.simulate_match(t1, t2, knockout=True)
            qf_teams.append(winner)

        # Quarterfinals
        qf_matchups = [
            (qf_teams[0], qf_teams[1]),
            (qf_teams[2], qf_teams[3]),
            (qf_teams[4], qf_teams[5]),
            (qf_teams[6], qf_teams[7]),
        ]
        sf_teams = []
        for t1, t2 in qf_matchups:
            _, _, _, _, winner = self.simulate_match(t1, t2, knockout=True)
            sf_teams.append(winner)

        # Semifinals
        sf_matchups = [
            (sf_teams[0], sf_teams[1]),
            (sf_teams[2], sf_teams[3]),
        ]
        finalists = []
        third_place_match = []
        for t1, t2 in sf_matchups:
            _, _, _, _, winner = self.simulate_match(t1, t2, knockout=True)
            finalists.append(winner)
            loser = t2 if winner == t1 else t1
            third_place_match.append(loser)

        # Final & 3rd place
        _, _, _, _, champion = self.simulate_match(finalists[0], finalists[1], knockout=True)
        runner_up = finalists[1] if champion == finalists[0] else finalists[0]
        _, _, _, _, third = self.simulate_match(third_place_match[0], third_place_match[1], knockout=True)

        return {
            "r16": [t for m in r16_matchups for t in m],
            "qf": qf_teams,
            "sf": sf_teams,
            "final": finalists,
            "champion": champion,
            "runner_up": runner_up,
            "third": third,
        }

    def simulate_single_tournament(self) -> Dict[str, Any]:
        """Runs a complete tournament from group stage to final."""
        advancing = self.simulate_group_stage()
        knockout_res = self.simulate_knockout_stage(advancing)
        return {
            "group_advancers": advancing,
            **knockout_res
        }

    def run_monte_carlo(
        self, num_simulations: int = 10000, seed: Optional[int] = 42
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes N full tournament simulations and aggregates progression probabilities.
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        stats = {
            t: {"r16": 0, "qf": 0, "sf": 0, "final": 0, "champion": 0}
            for t in self.all_teams
        }

        t0 = time.time()
        logger.info(f"Starting Monte Carlo simulation ({num_simulations:,} iterations)...")

        for _ in range(num_simulations):
            adv = self.simulate_group_stage()
            ko = self.simulate_knockout_stage(adv)

            for t in ko["r16"]:
                stats[t]["r16"] += 1
            for t in ko["qf"]:
                stats[t]["qf"] += 1
            for t in ko["sf"]:
                stats[t]["sf"] += 1
            for t in ko["final"]:
                stats[t]["final"] += 1
            stats[ko["champion"]]["champion"] += 1

        elapsed = time.time() - t0
        logger.info(f"Completed {num_simulations:,} simulations in {elapsed:.2f} seconds ({num_simulations/elapsed:.0f} sims/sec).")

        rows = []
        for t, st in stats.items():
            prof = self.team_profiles[t]
            rows.append({
                "team": t,
                "elo": prof["elo"],
                "rank": int(prof["rank"]),
                "r16_pct": round(st["r16"] / num_simulations * 100, 2),
                "qf_pct": round(st["qf"] / num_simulations * 100, 2),
                "sf_pct": round(st["sf"] / num_simulations * 100, 2),
                "final_pct": round(st["final"] / num_simulations * 100, 2),
                "champion_pct": round(st["champion"] / num_simulations * 100, 2),
                "raw_champion_count": st["champion"],
            })

        summary_df = pd.DataFrame(rows).sort_values("champion_pct", ascending=False).reset_index(drop=True)

        meta = {
            "num_simulations": num_simulations,
            "elapsed_seconds": round(elapsed, 2),
            "simulations_per_second": round(num_simulations / elapsed, 0),
            "seed": seed,
            "teams_simulated": len(self.all_teams),
            "top_contenders": summary_df.head(10)[["team", "champion_pct", "final_pct", "elo", "rank"]].to_dict(orient="records"),
        }

        return summary_df, {"metadata": meta, "team_stats": stats}

    def export_results(
        self,
        summary_df: pd.DataFrame,
        results_meta: Dict[str, Any],
        output_csv: str = "data/predictions/world_cup_simulation_summary.csv",
        output_json: str = "data/predictions/world_cup_simulation_results.json",
    ):
        """Exports simulation summary tables and JSON metadata."""
        out_csv_path = Path(output_csv)
        out_json_path = Path(output_json)
        out_csv_path.parent.mkdir(parents=True, exist_ok=True)

        summary_df.to_csv(out_csv_path, index=False)
        logger.info(f"Saved simulation summary to {out_csv_path}")

        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(results_meta, f, indent=2)
        logger.info(f"Saved simulation metadata to {out_json_path}")


def main():
    parser = argparse.ArgumentParser(description="Monte Carlo FIFA World Cup Tournament Simulator")
    parser.add_argument("--simulations", type=int, default=10000, help="Number of Monte Carlo iterations")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--model", type=str, default="models/best_model.pkl", help="Path to best model pickle")
    parser.add_argument("--out-dir", type=str, default="data/predictions", help="Output directory")
    args = parser.parse_args()

    simulator = TournamentSimulator(model_path=args.model)
    summary_df, results_meta = simulator.run_monte_carlo(num_simulations=args.simulations, seed=args.seed)

    out_csv = Path(args.out_dir) / "world_cup_simulation_summary.csv"
    out_json = Path(args.out_dir) / "world_cup_simulation_results.json"
    simulator.export_results(summary_df, results_meta, output_csv=str(out_csv), output_json=str(out_json))

    print("\n========================================================")
    print(f"   FIFA WORLD CUP PREDICTIONS ({args.simulations:,} Monte Carlo Runs)")
    print("========================================================")
    print(
        summary_df[["team", "elo", "rank", "r16_pct", "qf_pct", "sf_pct", "final_pct", "champion_pct"]]
        .head(12)
        .to_string(index=False)
    )
    print("========================================================\n")


if __name__ == "__main__":
    main()
