import pandas as pd


def clean_elo(df):

    df = df.copy()

    df.columns = df.columns.str.lower().str.strip()

    df.drop_duplicates(inplace=True)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    df.dropna(inplace=True)

    return df