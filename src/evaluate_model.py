import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
)

from train_model import LABEL_MAP, load_training_data

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def evaluate_saved_model(split_strategy: str = "temporal"):
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

    if split_strategy == "temporal":
        test_mask = df["match_year"] >= 2021
        X_test = X[test_mask]
        y_test = y[test_mask]
        split_info = "Temporal (2021-2026 test set)"
    else:
        train_size = int(len(df) * 0.8)
        X_test = X.iloc[train_size:]
        y_test = y.iloc[train_size:]
        split_info = "Chronological 80/20 test set"

    labels = [LABEL_MAP[index] for index in range(3)]
    evaluation_summary = {
        "split_strategy": split_strategy,
        "split_info": split_info,
        "test_matches": int(len(y_test)),
        "models": {}
    }

    model_files = sorted(list(MODELS_DIR.glob("*.pkl")))
    print(f"\n============================================================")
    print(f"BENCHMARKING SAVED MODELS: {split_info}")
    print(f"============================================================")

    for model_path in model_files:
        model_name = model_path.stem
        with open(model_path, "rb") as handle:
            model = pickle.load(handle)

        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)

        acc = float(accuracy_score(y_test, predictions))
        bal_acc = float(balanced_accuracy_score(y_test, predictions))
        ll = float(log_loss(y_test, probabilities, labels=[0, 1, 2]))
        macro_f1 = float(f1_score(y_test, predictions, average="macro"))

        report = classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2],
            target_names=labels,
            output_dict=True,
            zero_division=0,
        )
        matrix = confusion_matrix(y_test, predictions, labels=[0, 1, 2]).tolist()

        evaluation_summary["models"][model_name] = {
            "file": model_path.name,
            "accuracy": acc,
            "balanced_accuracy": bal_acc,
            "log_loss": ll,
            "macro_f1": macro_f1,
            "confusion_matrix": {
                "labels": labels,
                "rows_actual_columns_predicted": matrix,
            },
            "classification_report": report,
        }
        print(f"  * {model_name:22} | Acc: {acc:.4f} | BalAcc: {bal_acc:.4f} | LogLoss: {ll:.4f} | MacroF1: {macro_f1:.4f}")

    report_path = REPORTS_DIR / "model_evaluation.json"
    report_path.write_text(json.dumps(evaluation_summary, indent=2), encoding="utf-8")
    print(f"\n[OK] Model evaluation report saved to: {report_path}")

    return evaluation_summary


if __name__ == "__main__":
    evaluate_saved_model(split_strategy="temporal")
