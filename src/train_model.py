import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)


LABEL_MAP = {
    0: "Home Win",
    1: "Draw",
    2: "Away Win",
}


def load_training_data():
    df = pd.read_csv(PROCESSED_DATA / "training_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def build_model_pipeline():
    numeric_features = [
        "match_year",
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
    categorical_features = ["home_team", "away_team", "tournament"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numeric_features,
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
        ]
    )

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=150,
            random_state=42
        ),
        "xgboost": XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="mlogloss",
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            num_leaves=31,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1,
        ),
    }

    pipelines = {}
    for name, estimator in models.items():
        pipelines[name] = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", estimator),
            ]
        )

    return pipelines


def train_and_evaluate(split_strategy: str = "temporal"):
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
    target_column = "match_result_encoded"

    X = df[feature_columns]
    y = df[target_column]

    if split_strategy == "temporal":
        train_mask = df["match_year"] <= 2020
        test_mask = df["match_year"] >= 2021
        X_train, X_test = X[train_mask], X[test_mask]
        y_train, y_test = y[train_mask], y[test_mask]
        print(f"Split Strategy: Temporal (Train <= 2020: {len(X_train)} matches, Test >= 2021: {len(X_test)} matches)")
    else:
        train_size = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        print(f"Split Strategy: Chronological 80/20 (Train: {len(X_train)} matches, Test: {len(X_test)} matches)")

    sample_weights = compute_sample_weight("balanced", y_train)
    pipelines = build_model_pipeline()
    results = {}

    for name, pipeline in pipelines.items():
        print(f"\nTraining {name}...")
        if name == "gradient_boosting":
            pipeline.fit(X_train, y_train, model__sample_weight=sample_weights)
        else:
            pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)
        probabilities = pipeline.predict_proba(X_test)

        acc = accuracy_score(y_test, predictions)
        bal_acc = balanced_accuracy_score(y_test, predictions)
        macro_f1 = f1_score(y_test, predictions, average="macro")
        ll = log_loss(y_test, probabilities, labels=[0, 1, 2])

        print(f"Accuracy: {acc:.4f} | Balanced Accuracy: {bal_acc:.4f} | Log Loss: {ll:.4f} | Macro F1: {macro_f1:.4f}")
        print(classification_report(y_test, predictions, target_names=[LABEL_MAP[i] for i in range(3)]))

        # Save individual model checkpoint
        checkpoint_path = MODELS_DIR / f"{name}.pkl"
        with open(checkpoint_path, "wb") as f:
            pickle.dump(pipeline, f)

        results[name] = {
            "accuracy": float(acc),
            "balanced_accuracy": float(bal_acc),
            "log_loss": float(ll),
            "macro_f1": float(macro_f1),
            "model": pipeline,
            "checkpoint": str(checkpoint_path.name)
        }

    best_name, best_result = max(results.items(), key=lambda item: item[1]["accuracy"])
    best_model = best_result["model"]

    best_model_path = MODELS_DIR / "best_model.pkl"
    with open(best_model_path, "wb") as handle:
        pickle.dump(best_model, handle)

    print(f"\nBest model selected: {best_name} with accuracy {best_result['accuracy']:.4f}")
    print(f"Saved best model to: {best_model_path}")

    return results


if __name__ == "__main__":
    print("=" * 80)
    print("MODEL TRAINING & BASELINE BENCHMARKING PIPELINE")
    print("=" * 80)
    train_and_evaluate(split_strategy="temporal")
