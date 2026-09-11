"""
Tests for the trained model pipeline.
Verifies inference shape, probability calibration, and expected label mappings.
"""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def best_model():
    model_path = REPO / "models" / "best_model.pkl"
    assert model_path.exists(), f"Model not found at {model_path}"
    with open(model_path, "rb") as f:
        return pickle.load(f)


@pytest.fixture(scope="module")
def sample_input():
    return pd.DataFrame([{
        "match_year": 2026,
        "home_team": "England",
        "away_team": "Spain",
        "tournament": "FIFA World Cup",
        "elo_diff": 100.0,
        "rank_diff": -2.0,
        "home_advantage": 0,
        "h2h_win_rate_diff": 0.05,
        "h2h_total_matches": 10,
        "form_win_rate_diff": 0.1,
        "form_goal_diff": 0.3,
        "overall_diff": 1.5,
        "attack_diff": 2.0,
        "defense_diff": -1.0,
        "is_world_cup": 1,
        "is_continental": 0,
    }])


class TestModelInference:
    def test_model_loads(self, best_model):
        assert best_model is not None

    def test_predict_returns_label(self, best_model, sample_input):
        preds = best_model.predict(sample_input)
        assert len(preds) == 1
        assert preds[0] in (0, 1, 2), f"Unexpected label: {preds[0]}"

    def test_predict_proba_shape(self, best_model, sample_input):
        probs = best_model.predict_proba(sample_input)
        assert probs.shape == (1, 3), f"Expected shape (1, 3), got {probs.shape}"

    def test_probabilities_sum_to_one(self, best_model, sample_input):
        probs = best_model.predict_proba(sample_input)
        total = probs[0].sum()
        assert abs(total - 1.0) < 1e-6, f"Probabilities sum to {total}, not 1.0"

    def test_probabilities_all_non_negative(self, best_model, sample_input):
        probs = best_model.predict_proba(sample_input)
        assert (probs >= 0).all(), "Some probabilities are negative"

    def test_batch_inference(self, best_model):
        """Test that the model handles batch input of 32 rows correctly."""
        rows = []
        teams = ["Spain", "England", "France", "Brazil", "Argentina",
                 "Germany", "Portugal", "Netherlands"]
        for i, t1 in enumerate(teams):
            for t2 in teams:
                if t1 != t2:
                    rows.append({
                        "match_year": 2026,
                        "home_team": t1,
                        "away_team": t2,
                        "tournament": "FIFA World Cup",
                        "elo_diff": float(i * 10 - 30),
                        "rank_diff": float(i - 4),
                        "home_advantage": 0,
                        "h2h_win_rate_diff": 0.0,
                        "h2h_total_matches": 5,
                        "form_win_rate_diff": 0.05,
                        "form_goal_diff": 0.1,
                        "overall_diff": 1.0,
                        "attack_diff": 0.5,
                        "defense_diff": -0.5,
                        "is_world_cup": 1,
                        "is_continental": 0,
                    })
        df = pd.DataFrame(rows)
        probs = best_model.predict_proba(df)
        assert probs.shape == (len(rows), 3)
        row_sums = probs.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6), "Batch probabilities do not sum to 1"

    def test_home_advantage_affects_predictions(self, best_model, sample_input):
        """Home advantage flag should shift probability mass (model is non-linear, so
        we only require that the prediction changes, not a strict direction)."""
        neutral = sample_input.copy()
        neutral["home_advantage"] = 0
        home = sample_input.copy()
        home["home_advantage"] = 1

        p_neutral = best_model.predict_proba(neutral)[0]
        p_home = best_model.predict_proba(home)[0]
        # Probabilities should differ when home_advantage changes
        assert not all(abs(p_neutral[i] - p_home[i]) < 1e-6 for i in range(3)), (
            "Home advantage flag had zero effect on predicted probabilities"
        )

    def test_all_models_exist(self, models_dir):
        expected = ["best_model.pkl", "xgboost.pkl", "lightgbm.pkl",
                    "random_forest.pkl", "logistic_regression.pkl"]
        for name in expected:
            assert (models_dir / name).exists(), f"Model file missing: {name}"
