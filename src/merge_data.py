import pandas as pd


def merge_results_elo(results, elo):

    merged = pd.merge(
        results,
        elo,
        on="date",
        how="left"
    )

    return merged


if __name__ == "__main__":

    from load_data import load_results, load_elo

    results = load_results()

    elo = load_elo()

    merged = merge_results_elo(results, elo)

    print(merged.head())