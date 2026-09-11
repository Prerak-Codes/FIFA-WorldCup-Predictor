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
                                rankings: pd.DataFrame, match_features: pd.DataFrame = None) -> pd.DataFrame:
    """
    Engineer meaningful betting-style match features using historical Elo and ranking data.
    Performs temporal as-of joins to ensure no future data leakage.
    """
    results = results.copy()
    results['date'] = pd.to_datetime(results['date'])
    results = results.sort_values('date').reset_index(drop=True)

    print("   [OK] Creating target variable and match outcomes...")
    def get_result(row):
        if row['home_score'] > row['away_score']:
            return 'Home Win'
        elif row['home_score'] < row['away_score']:
            return 'Away Win'
        else:
            return 'Draw'

    results['match_result'] = results.apply(get_result, axis=1)

    # Home advantage: 1 if true home match, 0 if neutral venue
    if 'neutral' in results.columns:
        results['home_advantage'] = (~results['neutral'].fillna(False).astype(bool)).astype(int)
    else:
        results['home_advantage'] = 1

    print("   [OK] Calculating Elo features (as-of temporal join)...")
    elo = elo.copy()
    elo['date'] = pd.to_datetime(elo['date'])
    elo_home = elo.rename(columns={'team': 'home_team', 'rating': 'home_elo'})[['home_team', 'date', 'home_elo']].sort_values('date').reset_index(drop=True)
    elo_away = elo.rename(columns={'team': 'away_team', 'rating': 'away_elo'})[['away_team', 'date', 'away_elo']].sort_values('date').reset_index(drop=True)

    results_merged = pd.merge_asof(
        results.sort_values('date').reset_index(drop=True),
        elo_home,
        by='home_team',
        on='date',
        direction='backward'
    )
    results_merged = pd.merge_asof(
        results_merged.sort_values('date').reset_index(drop=True),
        elo_away,
        by='away_team',
        on='date',
        direction='backward'
    )

    print("   [OK] Calculating FIFA ranking features (as-of temporal join)...")
    rankings = rankings.copy()
    rankings['rank_date'] = pd.to_datetime(rankings['rank_date'])
    ranking_home = rankings.rename(columns={'team': 'home_team', 'rank': 'home_rank'})[['home_team', 'rank_date', 'home_rank']].sort_values('rank_date').reset_index(drop=True)
    ranking_away = rankings.rename(columns={'team': 'away_team', 'rank': 'away_rank'})[['away_team', 'rank_date', 'away_rank']].sort_values('rank_date').reset_index(drop=True)

    results_merged = pd.merge_asof(
        results_merged.sort_values('date').reset_index(drop=True),
        ranking_home,
        by='home_team',
        left_on='date',
        right_on='rank_date',
        direction='backward'
    )
    results_merged = pd.merge_asof(
        results_merged.sort_values('date').reset_index(drop=True),
        ranking_away,
        by='away_team',
        left_on='date',
        right_on='rank_date',
        direction='backward'
    )

    # Derived rating differences with standard baseline imputation
    home_elo_filled = results_merged['home_elo'].fillna(1500.0)
    away_elo_filled = results_merged['away_elo'].fillna(1500.0)
    results_merged['elo_diff'] = home_elo_filled - away_elo_filled

    home_rank_filled = results_merged['home_rank'].fillna(215.0)
    away_rank_filled = results_merged['away_rank'].fillna(215.0)
    results_merged['rank_diff'] = away_rank_filled - home_rank_filled

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
    print(f"[OK] Processed data saved to: {output_path}")
    return output_path


def create_training_pipeline():
    """Complete pipeline: Load, engineer features, preprocess, and save."""
    print("=" * 60)
    print("FEATURE ENGINEERING PIPELINE")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading interim datasets...")
    results, elo, rankings, match_features = load_interim_datasets()
    print(f"   [OK] Results: {len(results)} matches")
    print(f"   [OK] Elo: {len(elo)} records")
    print(f"   [OK] Rankings: {len(rankings)} records")
    
    # Engineer features
    print("\n2. Engineering features...")
    engineered = engineer_features_optimized(results, elo, rankings, match_features)
    print(f"   [OK] Features engineered: {engineered.shape}")
    
    # Preprocess features
    print("\n3. Preprocessing features...")
    processed = preprocess_features(engineered)
    print(f"   [OK] Features processed: {processed.shape}")
    
    # Save data
    print("\n4. Saving processed data...")
    save_processed_data(processed)
    
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETE!")
    print("=" * 60)
    print(f"\nDataset Summary:")
    print(f"  * Total Matches: {len(processed)}")
    print(f"  * Total Features: {len(processed.columns)}")
    print(f"  * Date Range: {processed['date'].min()} to {processed['date'].max()}")
    print(f"  * Non-zero elo_diff: {(processed['elo_diff'] != 0).sum()} matches")
    print(f"  * Non-zero rank_diff: {(processed['rank_diff'] != 0).sum()} matches")
    print(f"  * Neutral matches (home_advantage=0): {(processed['home_advantage'] == 0).sum()} matches")
    
    return processed


if __name__ == "__main__":
    training_data = create_training_pipeline()
    print("\nFirst few rows:")
    print(training_data.head(5).to_string())
