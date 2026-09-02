import pandas as pd
import numpy as np
from pathlib import Path

# Project Paths
BASE_DIR = Path(__file__).resolve().parents[1]
INTERIM_DATA = BASE_DIR / "data" / "interim"
PROCESSED_DATA = BASE_DIR / "data" / "processed"

# Create processed directory if it doesn't exist
PROCESSED_DATA.mkdir(exist_ok=True)


def load_interim_datasets():
    """Load all cleaned interim datasets."""
    results = pd.read_csv(INTERIM_DATA / "results_clean.csv")
    elo = pd.read_csv(INTERIM_DATA / "elo_clean.csv")
    rankings = pd.read_csv(INTERIM_DATA / "rankings_clean.csv")
    match_features = pd.read_csv(INTERIM_DATA / "match_features_clean.csv")
    
    return results, elo, rankings, match_features


def engineer_features_optimized(results: pd.DataFrame, elo: pd.DataFrame, 
                                rankings: pd.DataFrame, match_features: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer meaningful betting-style match features using historical Elo and ranking data.
    """
    results = results.copy()
    results['date'] = pd.to_datetime(results['date'])
    results = results.sort_values('date').reset_index(drop=True)

    print("   ✓ Creating target variable...")
    def get_result(row):
        if row['home_score'] > row['away_score']:
            return 'Home Win'
        elif row['home_score'] < row['away_score']:
            return 'Away Win'
        else:
            return 'Draw'

    results['match_result'] = results.apply(get_result, axis=1)

    print("   ✓ Calculating Elo features...")
    elo = elo.copy()
    elo['date'] = pd.to_datetime(elo['date'])
    elo_home = elo.rename(columns={'team': 'home_team', 'rating': 'home_elo'})[['home_team', 'date', 'home_elo']]
    elo_away = elo.rename(columns={'team': 'away_team', 'rating': 'away_elo'})[['away_team', 'date', 'away_elo']]

    results_home = pd.merge_asof(
        results.sort_values(['home_team', 'date']).reset_index(drop=True),
        elo_home.sort_values(['home_team', 'date']).reset_index(drop=True),
        by='home_team',
        left_on='date',
        right_on='date',
        direction='backward'
    )
    results_merged = pd.merge_asof(
        results_home.sort_values(['away_team', 'date']).reset_index(drop=True),
        elo_away.sort_values(['away_team', 'date']).reset_index(drop=True),
        by='away_team',
        left_on='date',
        right_on='date',
        direction='backward'
    )

    print("   ✓ Calculating FIFA ranking features...")
    rankings = rankings.copy()
    rankings['rank_date'] = pd.to_datetime(rankings['rank_date'])
    ranking_home = rankings.rename(columns={'team': 'home_team', 'rank': 'home_rank'})[['home_team', 'rank_date', 'home_rank']]
    ranking_away = rankings.rename(columns={'team': 'away_team', 'rank': 'away_rank'})[['away_team', 'rank_date', 'away_rank']]

    results_merged = pd.merge_asof(
        results_merged.sort_values(['home_team', 'date']).reset_index(drop=True),
        ranking_home.sort_values(['home_team', 'rank_date']).reset_index(drop=True),
        by='home_team',
        left_on='date',
        right_on='rank_date',
        direction='backward'
    )
    results_merged = pd.merge_asof(
        results_merged.sort_values(['away_team', 'date']).reset_index(drop=True),
        ranking_away.sort_values(['away_team', 'rank_date']).reset_index(drop=True),
        by='away_team',
        left_on='date',
        right_on='rank_date',
        direction='backward'
    )

    results_merged['elo_diff'] = results_merged['home_elo'] - results_merged['away_elo']
    results_merged['rank_diff'] = results_merged['away_rank'] - results_merged['home_rank']
    results_merged['home_advantage'] = 1
    results_merged['match_result_encoded'] = results_merged['match_result'].map({
        'Home Win': 0,
        'Draw': 1,
        'Away Win': 2
    })

    engineered = results_merged[[
        'date', 'home_team', 'away_team', 'tournament',
        'home_score', 'away_score', 'match_result',
        'home_elo', 'away_elo', 'elo_diff',
        'home_rank', 'away_rank', 'rank_diff',
        'home_advantage', 'match_result_encoded'
    ]].copy()

    return engineered



def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess engineered features."""
    df = df.copy()
    return df


def save_processed_data(df: pd.DataFrame, filename: str = 'training_data.csv'):
    """Save processed training data to CSV."""
    output_path = PROCESSED_DATA / filename
    df.to_csv(output_path, index=False)
    print(f"✓ Processed data saved to: {output_path}")
    return output_path


def create_training_pipeline():
    """Complete pipeline: Load, engineer features, preprocess, and save."""
    print("=" * 60)
    print("FEATURE ENGINEERING PIPELINE")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading interim datasets...")
    results, elo, rankings, match_features = load_interim_datasets()
    print(f"   ✓ Results: {len(results)} matches")
    print(f"   ✓ Elo: {len(elo)} records")
    print(f"   ✓ Rankings: {len(rankings)} records")
    
    # Engineer features
    print("\n2. Engineering features...")
    engineered = engineer_features_optimized(results, elo, rankings, match_features)
    print(f"   ✓ Features engineered: {engineered.shape}")
    
    # Preprocess features
    print("\n3. Preprocessing features...")
    processed = preprocess_features(engineered)
    print(f"   ✓ Features processed: {processed.shape}")
    
    # Save data
    print("\n4. Saving processed data...")
    save_processed_data(processed)
    
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETE!")
    print("=" * 60)
    print(f"\nDataset Summary:")
    print(f"  • Total Matches: {len(processed)}")
    print(f"  • Total Features: {len(processed.columns)}")
    print(f"  • Date Range: {processed['date'].min()} to {processed['date'].max()}")
    
    return processed


if __name__ == "__main__":
    training_data = create_training_pipeline()
    print("\nFirst few rows:")
    print(training_data.head(10).to_string())

    print("\n" + training_data.head())
