import pandas as pd


def clean_results(df: pd.DataFrame):

    df = df.copy()

    df.columns = df.columns.str.strip().str.lower()

    df.drop_duplicates(inplace=True)

    df["date"] = pd.to_datetime(df["date"])

    df["home_team"] = df["home_team"].str.strip()

    df["away_team"] = df["away_team"].str.strip()

    df.dropna(inplace=True)

    return df


if __name__ == "__main__":

    from load_data import load_results

    results = load_results()

    cleaned = clean_results(results)

    print(cleaned.head())