import pandas as pd
from pathlib import Path

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = BASE_DIR / "data" / "raw" / "elo_ratings"
INTERIM_DATA = BASE_DIR / "data" / "interim"


def clean_elo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Elo ratings dataset.
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
    # Convert date column
    # -----------------------------
    df["date"] = pd.to_datetime(
    df["date"],
    format="mixed",
    errors="coerce"
    )

    # -----------------------------
    # Remove extra spaces from team names
    # -----------------------------
    df["team"] = df["team"].str.strip()

    # -----------------------------
    # Convert numeric columns
    # -----------------------------
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["change"] = pd.to_numeric(df["change"], errors="coerce")

    # -----------------------------
    # Remove rows with missing ratings
    # -----------------------------
    df.dropna(subset=["rating"], inplace=True)

    # -----------------------------
    # Reset index
    # -----------------------------
    df.reset_index(drop=True, inplace=True)

    return df


def save_clean_elo(df: pd.DataFrame):
    """
    Save cleaned Elo ratings dataset.
    """

    INTERIM_DATA.mkdir(parents=True, exist_ok=True)

    output_path = INTERIM_DATA / "elo_clean.csv"

    df.to_csv(output_path, index=False)

    print(f"Cleaned dataset saved to:\n{output_path}")


if __name__ == "__main__":

    input_path = RAW_DATA / "eloratings.csv"

    elo = pd.read_csv(input_path)

    cleaned_elo = clean_elo(elo)

    save_clean_elo(cleaned_elo)

    print("\nCleaning completed successfully.")
    print(cleaned_elo.head())