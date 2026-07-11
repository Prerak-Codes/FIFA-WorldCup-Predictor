import pandas as pd


def clean_rankings(df):

    df = df.copy()

    df.columns = df.columns.str.lower().str.strip()

    df.drop_duplicates(inplace=True)

    if "rank_date" in df.columns:
        df["rank_date"] = pd.to_datetime(df["rank_date"])

    df.dropna(inplace=True)

    return df