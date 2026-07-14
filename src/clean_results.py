import pandas as pd
from pathlib import Path

# Project Paths
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = BASE_DIR / "data" / "raw" / "international_results"
INTERIM_DATA = BASE_DIR / "data" / "interim"


def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the international football results dataset.
    """

    df = df.copy()

    # -----------------------------
    # Standardize column names
    # -----------------------------
    df.columns = df.columns.str.strip().str.lower()

    # -----------------------------
    # Remove duplicate matches
    # -----------------------------
    df.drop_duplicates(inplace=True)

    # -----------------------------
    # Convert date column
    # -----------------------------
    df["date"] = pd.to_datetime(df["date"])

    # -----------------------------
    # Remove extra spaces
    # -----------------------------
    text_columns = [
        "home_team",
        "away_team",
        "tournament",
        "city",
        "country",
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].str.strip()

    # -----------------------------
    # Convert score columns
    # -----------------------------
    score_columns = ["home_score", "away_score"]

    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # -----------------------------
    # Remove rows with missing
    # essential values
    # -----------------------------
    essential_columns = [
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
    ]

    df.dropna(subset=essential_columns, inplace=True)

    # -----------------------------
    # Remove impossible scores
    # -----------------------------
    df = df[
        (df["home_score"] >= 0) &
        (df["away_score"] >= 0)
    ]

    # -----------------------------
    # Reset index
    # -----------------------------
    df.reset_index(drop=True, inplace=True)

    return df


def save_clean_results(df: pd.DataFrame):
    """
    Save cleaned dataset.
    """

    INTERIM_DATA.mkdir(parents=True, exist_ok=True)

    output_path = INTERIM_DATA / "results_clean.csv"

    df.to_csv(output_path, index=False)

    print(f"Cleaned dataset saved to:\n{output_path}")


if __name__ == "__main__":

    input_path = RAW_DATA / "results.csv"

    results = pd.read_csv(input_path)

    cleaned_results = clean_results(results)

    save_clean_results(cleaned_results)

    print("\nCleaning completed successfully.")
    print(cleaned_results.head())