import pandas as pd
from pathlib import Path

# ---------------------------------------
# Project Paths
# ---------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = BASE_DIR / "data" / "raw" / "match_features"
INTERIM_DATA = BASE_DIR / "data" / "interim"


def clean_match_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean teams_match_features dataset.
    """

    df = df.copy()

    # ---------------------------------------
    # Standardize column names
    # ---------------------------------------
    df.columns = df.columns.str.strip().str.lower()

    # ---------------------------------------
    # Remove duplicates
    # ---------------------------------------
    df.drop_duplicates(inplace=True)

    # ---------------------------------------
    # Convert date
    # ---------------------------------------
    df["_date"] = pd.to_datetime(
        df["_date"],
        errors="coerce"
    )

    # ---------------------------------------
    # Strip whitespace
    # ---------------------------------------
    df["_home_team"] = df["_home_team"].str.strip()

    df["_away_team"] = df["_away_team"].str.strip()

    df["_tournament"] = df["_tournament"].str.strip()

    # ---------------------------------------
    # Fill numeric missing values
    # ---------------------------------------
    numeric_cols = df.select_dtypes(include="number").columns

    df[numeric_cols] = df[numeric_cols].fillna(
        df[numeric_cols].median()
    )

    # ---------------------------------------
    # Remove rows with invalid dates
    # ---------------------------------------
    df.dropna(subset=["_date"], inplace=True)

    # ---------------------------------------
    # Reset index
    # ---------------------------------------
    df.reset_index(drop=True, inplace=True)

    return df


def save_clean_match_features(df: pd.DataFrame):

    INTERIM_DATA.mkdir(parents=True, exist_ok=True)

    output_path = INTERIM_DATA / "match_features_clean.csv"

    df.to_csv(output_path, index=False)

    print(f"Saved cleaned dataset to:\n{output_path}")


if __name__ == "__main__":

    input_path = RAW_DATA / "teams_match_features.csv"

    df = pd.read_csv(input_path)

    cleaned = clean_match_features(df)

    save_clean_match_features(cleaned)

    print("\nCleaning completed successfully.")

    print(cleaned.head())