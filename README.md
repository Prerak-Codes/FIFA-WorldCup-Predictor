# ⚽ FIFA World Cup Winner Prediction using Machine Learning

> Predict FIFA World Cup match outcomes and estimate each team's probability of winning the tournament using Machine Learning, Feature Engineering, and Monte Carlo Simulation.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?logo=scikitlearn)
![XGBoost](https://img.shields.io/badge/XGBoost-Gradient%20Boosting-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-In%20Progress-red)

---

# 📌 Project Overview

This project aims to build a machine learning system capable of:

- Predicting international football match outcomes.
- Estimating match win/draw/loss probabilities.
- Simulating an entire FIFA World Cup tournament.
- Calculating each team's probability of becoming World Cup Champion.

Instead of directly predicting the tournament winner, the model predicts **individual match outcomes**, which are then used in **Monte Carlo simulations** to estimate championship probabilities.

---

# 🎯 Objectives

- Collect historical international football data.
- Organize multiple football datasets.
- Perform exploratory data analysis (EDA).
- Clean and preprocess datasets.
- Engineer meaningful football features.
- Train and compare multiple ML models.
- Simulate the FIFA World Cup.
- Build a web application for predictions.

---

# 📂 Project Structure

```text
FIFA-WorldCup-Predictor/
│
├── app/                                    # Web application (Flask/Streamlit)
│
├── data/
│   ├── raw/                               # ✅ Raw datasets (11 CSV files)
│   │   ├── international_results/
│   │   │   ├── results.csv
│   │   │   ├── goalscorers.csv
│   │   │   ├── shootouts.csv
│   │   │   └── former_names.csv
│   │   ├── elo_ratings/
│   │   │   └── eloratings.csv
│   │   ├── fifa_rankings/
│   │   │   ├── fifa_ranking.csv
│   │   │   ├── fifa_matches.csv
│   │   │   └── fifa_teams.csv
│   │   └── match_features/
│   │       ├── player_aggregates.csv
│   │       ├── teams_form.csv
│   │       └── teams_match_features.csv
│   │
│   ├── interim/                           # ✅ Cleaned datasets
│   │   ├── results_clean.csv
│   │   ├── elo_clean.csv
│   │   ├── rankings_clean.csv
│   │   └── match_features_clean.csv
│   │
│   ├── processed/                         # ✅ Engineered features
│   │   └── training_data.csv              # 49,501 matches × 11 features
│   │
│   └── predictions/                       # Tournament simulation results
│
├── models/                                 # Trained ML models
│   ├── baseline_model.pkl
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   └── best_model.pkl
│
├── notebooks/                              # Jupyter notebooks
│   ├── 01_dataset_exploration.ipynb        # ✅ EDA
│   ├── 02_clean_results.ipynb              # ✅ Clean results
│   ├── 03_clean_elo.ipynb                  # ✅ Clean Elo ratings
│   ├── 04_clean_rankings.ipynb             # ✅ Clean FIFA rankings
│   ├── 05_clean_match_features.ipynb       # ✅ Clean match features
│   ├── 06_dataset_merging.ipynb            # ✅ Merge datasets
│   ├── 07_feature_engineering.ipynb        # ✅ Feature engineering
│   ├── 08_model_training.ipynb             # 🚧 Model training
│   ├── 09_model_evaluation.ipynb           # Model evaluation
│   └── 10_tournament_simulation.ipynb      # Tournament simulation
│
├── reports/                                # Analysis reports
│   └── figures/                            # Visualizations
│
├── src/                                    # Source code modules
│   ├── load_data.py                        # ✅ Data loading (11 loaders)
│   ├── clean_results.py                    # ✅ Clean results
│   ├── clean_elo.py                        # ✅ Clean Elo
│   ├── clean_rankings.py                   # ✅ Clean rankings
│   ├── clean_match_features.py             # ✅ Clean match features
│   ├── merge_data.py                       # ✅ Merge datasets
│   ├── feature_engineering.py              # ✅ Feature engineering pipeline
│   ├── train_model.py                      # Model training module
│   ├── evaluate_model.py                   # Model evaluation module
│   └── simulate_tournament.py              # Monte Carlo simulation
│
├── tests/                                  # Unit tests
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

# 📊 Datasets

This project combines multiple football datasets.

| Dataset | Purpose |
|----------|----------|
| International Results | Historical international match results |
| FIFA Rankings | Official FIFA rankings |
| Elo Ratings | Team strength ratings |
| Match Features | Team and player feature datasets |

Current raw datasets include:

- results.csv
- goalscorers.csv
- shootouts.csv
- former_names.csv
- eloratings.csv
- fifa_ranking.csv
- fifa_matches.csv
- fifa_teams.csv
- player_aggregates.csv
- teams_form.csv
- teams_match_features.csv

---

# 📊 Exploratory Data Analysis (Completed)

The initial EDA has been completed for all datasets.

The exploration includes:

- Dataset dimensions
- Column inspection
- Data types
- Missing value analysis
- Duplicate detection
- Statistical summaries
- Team distribution
- Tournament distribution
- Date range analysis

This analysis provides the foundation for the upcoming data cleaning pipeline.

---

# ⚙️ Current Data Pipeline

```
Raw Datasets
      │
      ▼
Load Data ✅
      │
      ▼
Exploratory Data Analysis ✅
      │
      ▼
Data Cleaning ✅
      │
      ▼
Dataset Merging ✅
      │
      ▼
Feature Engineering ✅ (49,501 matches engineered)
      │
      ▼
Model Training 🚧
      │
      ▼
World Cup Simulation
```

---

# 🧠 Machine Learning Pipeline

```text
Raw Datasets
      │
      ▼
Data Cleaning
      │
      ▼
Dataset Merging
      │
      ▼
Feature Engineering
      │
      ▼
Train/Test Split
      │
      ▼
Model Training
      │
      ▼
Model Evaluation
      │
      ▼
Match Prediction
      │
      ▼
Monte Carlo Simulation
      │
      ▼
World Cup Winner Probabilities
```

---

# 🛠️ Current Progress

## ✅ Completed

- Project structure created
- Raw datasets organized (11 CSV files)
- Data loading module implemented (11 loader functions)
- Exploratory Data Analysis completed
- Data cleaning completed (results, elo, rankings, match_features)
- Dataset merging completed
- Feature engineering completed (src/feature_engineering.py)
- Training dataset generated (49,501 matches × 11 features)
- GitHub project initialized

## 🚧 In Progress

- Model training pipeline (Notebook 08)
- Multiple ML model implementation

## ⏳ Upcoming

- Model evaluation & comparison
- World Cup simulation
- Web application

---

# � Feature Engineering (Completed)

Successfully engineered features from 49,501 international football matches spanning 155 years (1872-2026).

## Generated Training Dataset: `data/processed/training_data.csv`

| Feature | Type | Description |
|---------|------|-------------|
| `date` | DateTime | Match date |
| `home_team` | String | Home team name |
| `away_team` | String | Away team name |
| `tournament` | String | Tournament name |
| `home_score` | Int | Goals scored by home team |
| `away_score` | Int | Goals scored by away team |
| `match_result` | String | Match outcome (Home Win/Draw/Away Win) |
| `elo_diff` | Float | Elo rating difference |
| `rank_diff` | Float | FIFA ranking difference |
| `home_advantage` | Int | Binary indicator (1=home) |
| `match_result_encoded` | Int | Encoded target (0=Home Win, 1=Draw, 2=Away Win) |

## Feature Engineering Module: `src/feature_engineering.py`

Provides reusable functions:
- `load_interim_datasets()` - Loads all cleaned data
- `engineer_features_optimized()` - Creates features from raw data
- `preprocess_features()` - Handles feature preprocessing
- `save_processed_data()` - Exports to CSV
- `create_training_pipeline()` - Complete end-to-end pipeline

## Related Notebook

**`notebooks/07_feature_engineering.ipynb`** - Interactive notebook demonstrating:
- Data loading and exploration
- Feature engineering workflow
- Feature analysis and correlation
- Dataset statistics

---

# 📈 Engineered Features

The following features have been created for model training:

- ✅ Date and team information (home/away teams)
- ✅ Match outcome (target variable)
- ✅ Elo rating difference
- ✅ FIFA ranking difference  
- ✅ Home advantage indicator
- ✅ Score information

## Planned Feature Enhancements

Future versions will include:

- Last 5 match form
- Last 10 match goal difference
- Average goals scored/conceded
- Head-to-head record
- Tournament importance
- Neutral venue indicator

---

# 🤖 Planned Machine Learning Models

The following models will be implemented and compared.

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- LightGBM
- CatBoost

The best-performing model will be selected based on evaluation metrics.

---

# 📊 Planned Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- Log Loss

---

# 🌍 Planned World Cup Simulation

After training the best model:

- Predict every tournament match.
- Simulate the FIFA World Cup thousands of times.
- Estimate each team's probability of becoming champion.

---

# 🚀 Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-Learn
- XGBoost
- LightGBM
- CatBoost
- Jupyter Notebook
- Git
- GitHub

---

# 📅 Development Roadmap

## Phase 1 – Project Initialization
- [x] Project structure
- [x] Dataset collection
- [x] Raw dataset organization
- [x] Data loading module

## Phase 2 – Data Understanding
- [x] Exploratory Data Analysis (EDA)
- [x] Data cleaning
- [x] Data validation

## Phase 3 – Data Engineering
- [x] Dataset merging
- [x] Feature engineering
- [x] Processed dataset creation (training_data.csv)

## Phase 4 – Machine Learning (Current)
- [ ] Train/Test split
- [ ] Baseline model (Logistic Regression)
- [ ] Model evaluation

## Phase 5 – Advanced Models
- [ ] Random Forest
- [ ] XGBoost
- [ ] LightGBM
- [ ] CatBoost

## Phase 6 – Model Comparison
- [ ] Compare all models
- [ ] Hyperparameter tuning
- [ ] Select best model

## Phase 7 – Tournament Simulation
- [ ] Monte Carlo simulation
- [ ] World Cup winner prediction

## Phase 8 – Deployment
- [ ] Streamlit/Flask web app
- [ ] Deployment

---

# 📌 Future Improvements

- Player-level statistics
- Injury reports
- Team market values
- Live FIFA rankings
- Betting odds integration
- Explainable AI (SHAP)
- Automated data pipeline

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and create a pull request.

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.
