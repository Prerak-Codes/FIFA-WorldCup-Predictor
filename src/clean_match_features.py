import pandas as pd


def clean_team_form(df):

    df = df.copy()

    df.columns = df.columns.str.lower().str.strip()

    df.drop_duplicates(inplace=True)

    df.dropna(inplace=True)

    return df


def clean_match_features(df):

    df = df.copy()

    df.columns = df.columns.str.lower().str.strip()

    df.drop_duplicates(inplace=True)

    df.dropna(inplace=True)

    return df