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


def calculate_head_to_head_features(results: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate historical head-to-head records strictly prior to each match (no future leak).
    """
    df = results.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    team1 = np.minimum(df['home_team'].values, df['away_team'].values)
    team2 = np.maximum(df['home_team'].values, df['away_team'].values)
    pair_key = team1 + '__vs__' + team2

    home_h2h_win_rate = np.zeros(len(df), dtype=float)
    away_h2h_win_rate = np.zeros(len(df), dtype=float)
    h2h_total_matches = np.zeros(len(df), dtype=int)

    pair_stats = {}

    for i in range(len(df)):
        pk = pair_key[i]
        ht = df['home_team'].iloc[i]
        at = df['away_team'].iloc[i]
        hs = df['home_score'].iloc[i]
        as_ = df['away_score'].iloc[i]

        if pk in pair_stats:
            st = pair_stats[pk]
            tot = st['total']
            h2h_total_matches[i] = tot
            if tot > 0:
                home_h2h_win_rate[i] = st.get(ht, 0) / tot
                away_h2h_win_rate[i] = st.get(at, 0) / tot
        else:
            pair_stats[pk] = {'total': 0}

        st = pair_stats[pk]
        st['total'] += 1
        if hs > as_:
            st[ht] = st.get(ht, 0) + 1
        elif as_ > hs:
            st[at] = st.get(at, 0) + 1
        else:
            st['draws'] = st.get('draws', 0) + 1

    df['h2h_total_matches'] = h2h_total_matches
    df['home_h2h_win_rate'] = home_h2h_win_rate
    df['away_h2h_win_rate'] = away_h2h_win_rate
    df['h2h_win_rate_diff'] = home_h2h_win_rate - away_h2h_win_rate

    return df


def engineer_features_optimized(results: pd.DataFrame, elo: pd.DataFrame, 
                                rankings: pd.DataFrame, match_features: pd.DataFrame = None) -> pd.DataFrame:
    """
    Engineer meaningful betting-style match features using historical Elo, ranking, 
    head-to-head records, and match form data.
    Performs temporal as-of joins to ensure no future data leakage.
    """
    results = results.copy()
    results['date'] = pd.to_datetime(results['date'])
    results = results.sort_values('date').reset_index(drop=True)

    print("   [OK] Calculating Head-to-Head historical records...")
    results = calculate_head_to_head_features(results)

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

    # Merge match features (form, player attributes, tournament indicators)
    if match_features is not None and not match_features.empty:
        print("   [OK] Merging form and player aggregate features (match_features)...")
        mf = match_features.drop_duplicates(subset=['_date', '_home_team', '_away_team'], keep='first').copy()
        mf['_date'] = pd.to_datetime(mf['_date'])
        mf_renamed = mf.rename(columns={
            '_date': 'date',
            '_home_team': 'home_team',
            '_away_team': 'away_team'
        })

        keep_mf_cols = [
            'date', 'home_team', 'away_team',
            'home_form_scored', 'home_form_conceded', 'home_form_win_rate',
            'away_form_scored', 'away_form_conceded', 'away_form_win_rate',
            'home_avg_overall', 'away_avg_overall', 'overall_diff',
            'home_avg_attack', 'away_avg_attack', 'attack_diff',
            'home_avg_defense', 'away_avg_defense', 'defense_diff',
            'is_world_cup', 'is_continental'
        ]
        results_merged = pd.merge(
            results_merged,
            mf_renamed[keep_mf_cols],
            on=['date', 'home_team', 'away_team'],
            how='left'
        )

        # Impute missing values for matches without video game aggregates
        results_merged['home_form_win_rate'] = results_merged['home_form_win_rate'].fillna(0.33)
        results_merged['away_form_win_rate'] = results_merged['away_form_win_rate'].fillna(0.33)
        results_merged['form_win_rate_diff'] = results_merged['home_form_win_rate'] - results_merged['away_form_win_rate']

        results_merged['home_form_scored'] = results_merged['home_form_scored'].fillna(1.2)
        results_merged['home_form_conceded'] = results_merged['home_form_conceded'].fillna(1.2)
        results_merged['away_form_scored'] = results_merged['away_form_scored'].fillna(1.2)
        results_merged['away_form_conceded'] = results_merged['away_form_conceded'].fillna(1.2)
        results_merged['form_goal_diff'] = (
            (results_merged['home_form_scored'] - results_merged['home_form_conceded']) - 
            (results_merged['away_form_scored'] - results_merged['away_form_conceded'])
        )

        results_merged['overall_diff'] = results_merged['overall_diff'].fillna(0.0)
        results_merged['attack_diff'] = results_merged['attack_diff'].fillna(0.0)
        results_merged['defense_diff'] = results_merged['defense_diff'].fillna(0.0)
        results_merged['is_world_cup'] = results_merged['is_world_cup'].fillna(0).astype(int)
        results_merged['is_continental'] = results_merged['is_continental'].fillna(0).astype(int)

    feature_cols = [
        'date', 'home_team', 'away_team', 'tournament',
        'home_score', 'away_score', 'match_result',
        'home_elo', 'away_elo', 'elo_diff',
        'home_rank', 'away_rank', 'rank_diff',
        'home_advantage',
        'h2h_total_matches', 'home_h2h_win_rate', 'away_h2h_win_rate', 'h2h_win_rate_diff',
        'home_form_win_rate', 'away_form_win_rate', 'form_win_rate_diff',
        'home_form_scored', 'home_form_conceded', 'away_form_scored', 'away_form_conceded', 'form_goal_diff',
        'overall_diff', 'attack_diff', 'defense_diff',
        'is_world_cup', 'is_continental',
        'match_result_encoded'
    ]

    # Keep available feature columns
    final_cols = [col for col in feature_cols if col in results_merged.columns]
    engineered = results_merged[final_cols].copy()

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
    print(f"   [OK] Match features: {len(match_features)} records")
    
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
    print(f"  * Prior H2H matches available: {(processed['h2h_total_matches'] > 0).sum()} matches")
    print(f"  * Neutral matches (home_advantage=0): {(processed['home_advantage'] == 0).sum()} matches")
    
    return processed


if __name__ == "__main__":
    training_data = create_training_pipeline()
    print("\nFirst few rows:")
    print(training_data.head(5).to_string())
