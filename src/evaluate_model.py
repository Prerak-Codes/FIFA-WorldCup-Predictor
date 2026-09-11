import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
)

from train_model import LABEL_MAP, load_training_data

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def evaluate_saved_model():
    df = load_training_data()
    df = df.dropna(subset=["elo_diff", "rank_diff", "home_advantage"]).copy()
    df["match_year"] = df["date"].dt.year

    feature_columns = [
        "match_year",
        "home_team",
        "away_team",
        "tournament",
        "elo_diff",
        "rank_diff",
        "home_advantage",
        "h2h_win_rate_diff",
        "h2h_total_matches",
        "form_win_rate_diff",
        "form_goal_diff",
        "overall_diff",
        "attack_diff",
        "defense_diff",
        "is_world_cup",
        "is_continental",
    ]
    X = df[feature_columns]
    y = df["match_result_encoded"]

    train_size = int(len(df) * 0.8)
    X_test = X.iloc[train_size:]
    y_test = y.iloc[train_size:]

    model_path = MODELS_DIR / "best_model.pkl"
    with open(model_path, "rb") as handle:
        model = pickle.load(handle)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    labels = [LABEL_MAP[index] for index in range(3)]

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1, 2],
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1, 2]).tolist()

    metrics = {
        "model": str(model_path.name),
        "test_matches": int(len(y_test)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "log_loss": float(log_loss(y_test, probabilities, labels=[0, 1, 2])),
        "confusion_matrix": {
            "labels": labels,
            "rows_actual_columns_predicted": matrix,
        },
        "classification_report": report,
    }

    report_path = REPORTS_DIR / "model_evaluation.json"
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model: {metrics['model']}")
    print(f"Test matches: {metrics['test_matches']}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"Log loss: {metrics['log_loss']:.4f}")
    print("\nConfusion matrix (actual rows, predicted columns):")
    print(pd.DataFrame(matrix, index=labels, columns=labels))
    print(f"\nEvaluation report saved to: {report_path}")

    return metrics


if __name__ == "__main__":
    evaluate_saved_model()
