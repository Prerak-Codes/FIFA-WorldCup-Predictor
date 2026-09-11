"""
Tests for src/simulate_tournament.py.
Verifies group standings logic, knockout bracket integrity, and Monte Carlo outputs.
"""
import random

import numpy as np
import pytest

from src.simulate_tournament import DEFAULT_GROUPS, TournamentSimulator


class TestTournamentSimulatorSetup:
    def test_loads_32_teams(self, simulator):
        assert len(simulator.all_teams) == 32

    def test_has_8_groups(self, simulator):
        assert len(simulator.groups) == 8

    def test_all_group_teams_have_profiles(self, simulator):
        for team in simulator.all_teams:
            assert team in simulator.team_profiles, f"{team} missing from team_profiles"

    def test_pairwise_probs_computed(self, simulator):
        n = len(simulator.all_teams)
        expected = n * (n - 1)  # n*(n-1) ordered pairs
        assert len(simulator.symmetric_probs) == expected

    def test_symmetric_probs_sum_to_one(self, simulator):
        for (t1, t2), (p1, draw, p2) in simulator.symmetric_probs.items():
            total = p1 + draw + p2
            assert abs(total - 1.0) < 1e-6, f"Probs for {t1} vs {t2} sum to {total}"

    def test_symmetric_probs_are_symmetric(self, simulator):
        """P(A wins vs B) == P(B loses vs A), within float32 tolerance."""
        for t1 in simulator.all_teams[:4]:
            for t2 in simulator.all_teams:
                if t1 != t2:
                    p1, d1, p2 = simulator.symmetric_probs[(t1, t2)]
                    q2, d2, q1 = simulator.symmetric_probs[(t2, t1)]
                    assert abs(p1 - q1) < 1e-7, f"Asymmetry detected for {t1} vs {t2}"
                    assert abs(d1 - d2) < 1e-7, f"Draw asymmetry for {t1} vs {t2}"

    def test_elo_ratings_reasonable(self, simulator):
        for team, prof in simulator.team_profiles.items():
            assert 500 <= prof["elo"] <= 3000, f"Unreasonable Elo for {team}: {prof['elo']}"

    def test_rank_values_positive(self, simulator):
        for team, prof in simulator.team_profiles.items():
            assert prof["rank"] > 0, f"Non-positive rank for {team}"


class TestSimulateMatch:
    def test_knockout_always_has_winner(self, simulator):
        random.seed(42)
        for _ in range(100):
            _, _, _, _, winner = simulator.simulate_match("Spain", "England", knockout=True)
            assert winner in ("Spain", "England"), f"Unexpected winner: {winner}"

    def test_group_match_can_draw(self, simulator):
        """Group matches can produce None (draw) winners."""
        random.seed(0)
        draw_seen = False
        for _ in range(500):
            _, _, _, _, winner = simulator.simulate_match("Spain", "England", knockout=False)
            if winner is None:
                draw_seen = True
                break
        assert draw_seen, "No draws produced in 500 group stage match simulations"

    def test_match_returns_non_negative_scores(self, simulator):
        random.seed(7)
        for _ in range(50):
            _, _, s1, s2, _ = simulator.simulate_match("Brazil", "Argentina", knockout=False)
            assert s1 >= 0 and s2 >= 0


class TestGroupStage:
    def test_advances_exactly_2_per_group(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        assert len(advancing) == 8
        for grp, (first, second) in advancing.items():
            assert first != second, f"Group {grp}: same team advanced twice"
            assert first in DEFAULT_GROUPS[grp], f"{first} not in group {grp}"
            assert second in DEFAULT_GROUPS[grp], f"{second} not in group {grp}"

    def test_total_advancing_teams_is_16(self, simulator):
        random.seed(1)
        advancing = simulator.simulate_group_stage()
        all_advancing = [t for pair in advancing.values() for t in pair]
        assert len(all_advancing) == 16
        assert len(set(all_advancing)) == 16, "Duplicate teams advanced!"


class TestKnockoutStage:
    def test_produces_unique_champion(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        ko = simulator.simulate_knockout_stage(advancing)
        assert ko["champion"] in simulator.all_teams

    def test_champion_not_runner_up(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        ko = simulator.simulate_knockout_stage(advancing)
        assert ko["champion"] != ko["runner_up"]

    def test_third_place_not_finalist(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        ko = simulator.simulate_knockout_stage(advancing)
        assert ko["third"] not in ko["final"]

    def test_qf_has_8_teams(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        ko = simulator.simulate_knockout_stage(advancing)
        assert len(ko["qf"]) == 8

    def test_sf_has_4_teams(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        ko = simulator.simulate_knockout_stage(advancing)
        assert len(ko["sf"]) == 4

    def test_final_has_2_teams(self, simulator):
        random.seed(42)
        advancing = simulator.simulate_group_stage()
        ko = simulator.simulate_knockout_stage(advancing)
        assert len(ko["final"]) == 2


class TestMonteCarlo:
    def test_champion_probabilities_sum_to_100(self, simulator):
        random.seed(42)
        np.random.seed(42)
        summary_df, meta = simulator.run_monte_carlo(num_simulations=500, seed=42)
        total_champ_pct = summary_df["champion_pct"].sum()
        # Each simulation produces exactly 1 champion, so total % should be ~100
        assert abs(total_champ_pct - 100.0) < 2.0, (
            f"Champion probabilities sum to {total_champ_pct:.2f}%, expected ~100%"
        )

    def test_all_teams_in_summary(self, simulator):
        random.seed(99)
        summary_df, _ = simulator.run_monte_carlo(num_simulations=200, seed=99)
        assert len(summary_df) == len(simulator.all_teams)

    def test_summary_sorted_by_champion_pct(self, simulator):
        summary_df, _ = simulator.run_monte_carlo(num_simulations=200, seed=7)
        vals = summary_df["champion_pct"].tolist()
        assert vals == sorted(vals, reverse=True), "Summary not sorted by champion_pct"

    def test_strong_teams_top_favorites(self, simulator):
        """Spain, England, France, or Brazil should be in top 4 over 5000 sims."""
        summary_df, _ = simulator.run_monte_carlo(num_simulations=5000, seed=42)
        top4 = set(summary_df.head(4)["team"].tolist())
        elite = {"Spain", "England", "France", "Brazil", "Argentina"}
        overlap = top4 & elite
        assert len(overlap) >= 2, f"Expected elite teams in top 4, got: {top4}"
