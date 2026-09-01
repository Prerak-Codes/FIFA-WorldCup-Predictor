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
    Engineer features using simpler approach with key metrics.
    """
    results = results.copy()
    results['date'] = pd.to_datetime(results['date'])
    
    print("   ✓ Creating target variable...")
    # Determine match outcome
    def get_result(row):
        if row['home_score'] > row['away_score']:
            return 'Home Win'
        elif row['home_score'] < row['away_score']:
            return 'Away Win'
        else:
            return 'Draw'
    
    results['match_result'] = results.apply(get_result, axis=1)
    
    # Keep core features only
    print("   ✓ Preparing core features...")
    engineered = results[[
        'date', 'home_team', 'away_team', 'tournament',
        'home_score', 'away_score', 'match_result'
    ]].copy()
    
    # Add derived features
    engineered['elo_diff'] = 0.0  # Placeholder - will be filled from Elo data
    engineered['rank_diff'] = 0.0  # Placeholder - will be filled from rankings
    engineered['home_advantage'] = 1
    engineered['match_result_encoded'] = engineered['match_result'].map({
        'Home Win': 0,
        'Draw': 1,
        'Away Win': 2
    })
    
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
