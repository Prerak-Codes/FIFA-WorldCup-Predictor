import pandas as pd
from pathlib import Path

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = BASE_DIR / "data" / "raw" / "fifa_rankings"
INTERIM_DATA = BASE_DIR / "data" / "interim"


def clean_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean FIFA Rankings dataset.
    """

    df = df.copy()

    # -----------------------------
    # Standardize column names
    # -----------------------------
    df.columns = df.columns.str.strip().str.lower()

    # -----------------------------
    # Remove duplicate rows
    # -----------------------------
    df.drop_duplicates(inplace=True)

    # -----------------------------
    # Convert rank_date
    # -----------------------------
    df["rank_date"] = pd.to_datetime(
        df["rank_date"],
        errors="coerce"
    )

    # -----------------------------
    # Remove whitespace
    # -----------------------------
    df["team"] = df["team"].str.strip()

    df["country_abrv"] = df["country_abrv"].str.strip()

    df["confederation"] = df["confederation"].str.strip()

    # -----------------------------
    # Convert numeric columns
    # -----------------------------
    numeric_columns = [
        "rank",
        "total_points",
        "previous_points",
        "rank_change"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # -----------------------------
    # Remove invalid rows
    # -----------------------------
    df.dropna(inplace=True)

    # -----------------------------
    # Reset index
    # -----------------------------
    df.reset_index(drop=True, inplace=True)

    return df


def save_clean_rankings(df: pd.DataFrame):
    """
    Save cleaned rankings dataset.
    """

    INTERIM_DATA.mkdir(parents=True, exist_ok=True)

    output_path = INTERIM_DATA / "rankings_clean.csv"

    df.to_csv(output_path, index=False)

    print(f"Cleaned dataset saved to:\n{output_path}")


if __name__ == "__main__":

    input_path = RAW_DATA / "fifa_rankings.csv"

    rankings = pd.read_csv(input_path)

    cleaned_rankings = clean_rankings(rankings)

    save_clean_rankings(cleaned_rankings)

    print("\nCleaning completed successfully.")
    print(cleaned_rankings.head())