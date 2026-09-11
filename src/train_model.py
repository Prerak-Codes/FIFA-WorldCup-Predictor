import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
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


def train_and_evaluate():
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

    train_size = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    pipelines = build_model_pipeline()
    results = {}

    for name, pipeline in pipelines.items():
        print(f"\nTraining {name}...")
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Accuracy: {accuracy:.4f}")
        print(classification_report(y_test, predictions, target_names=[LABEL_MAP[i] for i in range(3)]))
        results[name] = {
            "accuracy": accuracy,
            "model": pipeline,
        }

    best_name, best_result = max(results.items(), key=lambda item: item[1]["accuracy"])
    best_model = best_result["model"]

    model_path = MODELS_DIR / "best_model.pkl"
    with open(model_path, "wb") as handle:
        pickle.dump(best_model, handle)

    print(f"\nBest model: {best_name} with accuracy {best_result['accuracy']:.4f}")
    print(f"Saved model to: {model_path}")

    return best_model, best_name, best_result["accuracy"]


if __name__ == "__main__":
    print("=" * 80)
    print("MODEL TRAINING PIPELINE")
    print("=" * 80)
    train_and_evaluate()
