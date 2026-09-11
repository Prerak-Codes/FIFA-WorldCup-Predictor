# ⚽ FIFA World Cup Predictor — ML-Powered Match & Tournament Forecaster

> Predict international match outcomes and simulate the FIFA World Cup using Machine Learning, Feature Engineering, and Monte Carlo Simulation.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?logo=scikitlearn)
![XGBoost](https://img.shields.io/badge/XGBoost-62.7%25_Accuracy-green)
![LightGBM](https://img.shields.io/badge/LightGBM-0.8219_LogLoss-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63-red?logo=streamlit)
![Tests](https://img.shields.io/badge/Tests-56%20passed-brightgreen)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

## 🏆 Project Overview

This project builds a **complete end-to-end football prediction system** capable of:

- **Predicting international match outcomes** (Win / Draw / Loss probabilities)
- **Simulating entire FIFA World Cup tournaments** from group stages to the final
- **Estimating championship probability** for all 32 qualified nations via 10,000 Monte Carlo runs
- **Serving predictions interactively** through a Streamlit dashboard

**Key results on the 2021–2026 holdout test set:**

| Model | Accuracy | Log Loss |
|---|---|---|
| Logistic Regression | 58.6% | 0.892 |
| Random Forest | 59.4% | 0.896 |
| Gradient Boosting | 61.1% | 0.851 |
| **XGBoost ⭐ (Champion)** | **62.71%** | **0.832** |
| LightGBM | 62.3% | **0.822** |

---

## 🗂️ Project Structure

```text
FIFA-WorldCup-Predictor/
│
├── app/                            # Streamlit web application
│   ├── __init__.py
│   ├── main.py                     # 3-tab interactive dashboard
│   └── utils.py                    # Shared loaders, predictors, charts
│
├── data/
│   ├── raw/                        # Original datasets (11 CSV files)
│   │   ├── international_results/  # Results, goalscorers, shootouts
│   │   ├── elo_ratings/            # Club Elo ratings
│   │   ├── fifa_rankings/          # FIFA world rankings
│   │   └── match_features/         # FIFA player attributes
│   ├── interim/                    # Cleaned intermediate data
│   └── processed/                  # Final training_data.csv (49,501 matches)
│
├── models/                         # Serialized model checkpoints
│   ├── best_model.pkl              # XGBoost (champion)
│   ├── xgboost.pkl
│   ├── lightgbm.pkl
│   ├── random_forest.pkl
│   └── logistic_regression.pkl
│
├── notebooks/                      # Jupyter analysis notebooks
│   ├── 01–06_*.ipynb               # EDA, cleaning, merging
│   ├── 07_feature_engineering.ipynb
│   ├── 08_model_training.ipynb
│   ├── 09_model_evaluation.ipynb
│   └── 10_tournament_simulation.ipynb
│
├── reports/
│   └── model_evaluation.json       # Benchmark metrics (all 5 models)
│
├── src/                            # Core Python modules
│   ├── load_data.py                # Raw data loaders
│   ├── clean_elo.py                # Elo data cleaning
│   ├── feature_engineering.py      # Temporal feature pipeline
│   ├── train_model.py              # Model training & checkpointing
│   ├── evaluate_model.py           # Evaluation & reporting
│   └── simulate_tournament.py      # Monte Carlo tournament engine
│
├── tests/                          # Automated test suite (56 tests)
│   ├── conftest.py                 # Shared pytest fixtures
│   ├── test_load_data.py
│   ├── test_feature_engineering.py
│   ├── test_model.py
│   └── test_simulation.py
│
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Install

```powershell
git clone https://github.com/Prerak-Codes/FIFA-WorldCup-Predictor.git
cd FIFA-WorldCup-Predictor

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Interactive Dashboard

```powershell
.venv\Scripts\streamlit run app/main.py
# Opens at http://localhost:8501
```

### 3. Run Simulations from CLI

```powershell
# Run 10,000 Monte Carlo simulations and export results
.venv\Scripts\python src/simulate_tournament.py --simulations 10000 --seed 42

# View results
Get-Content data/predictions/world_cup_simulation_summary.csv | Select-Object -First 12
```

### 4. Re-train Models

```powershell
.venv\Scripts\python src/feature_engineering.py  # Rebuild training data
.venv\Scripts\python src/train_model.py           # Train all 5 models
.venv\Scripts\python src/evaluate_model.py        # Print benchmark table
```

### 5. Run Tests

```powershell
.venv\Scripts\python -m pytest tests/ -v
# Expected: 56 passed in ~4 seconds
```

---

## 🌐 Streamlit Dashboard

Launch with `.venv\Scripts\streamlit run app/main.py`, then navigate to `http://localhost:8501`.

### Tab 1 — 🆚 Head-to-Head Match Predictor
- Choose any two of the 32 World Cup 2026 nations
- Toggle **Neutral Venue** on/off
- Select tournament type (World Cup / Euro / Copa / Friendly)
- Instantly see **Win / Draw / Loss probabilities** as a colour-coded stacked bar
- Compare both teams' Elo ratings, FIFA rank, attack, defense, and form

### Tab 2 — 🏆 World Cup Bracket Simulator
- **Single Simulation**: Click one button to play out a full bracket — see group standings with 🥇/🥈/❌ and knockout rounds with green/grey highlights
- **Monte Carlo Leaderboard**: Championship probability bar chart + stage progression heatmap for all 32 nations + full sortable table

### Tab 3 — 📊 Team Analytics Explorer
- Select up to **8 teams** simultaneously
- **Elo history line chart** spanning the full history of international football (270 nations)
- **Radar/spider chart** comparing Attack, Defense, Overall, Form WR, and Elo across selected teams

---

## 🔬 Model Features (13 numeric + 3 categorical)

| Feature | Description |
|---|---|
| `elo_diff` | Elo rating difference (home − away) |
| `rank_diff` | FIFA ranking difference (away − home, lower = better) |
| `home_advantage` | 1 if true home venue, 0 if neutral |
| `h2h_win_rate_diff` | Historical head-to-head win rate advantage |
| `h2h_total_matches` | Prior meetings between the two teams |
| `form_win_rate_diff` | Recent 5-match form win rate differential |
| `form_goal_diff` | Recent 5-match average goal difference |
| `overall_diff` | FIFA squad overall rating gap |
| `attack_diff` | FIFA attack rating gap |
| `defense_diff` | FIFA defense rating gap |
| `is_world_cup` | 1 if World Cup match |
| `is_continental` | 1 if continental championship (Euro/Copa/etc.) |
| `match_year` | Year of the match |
| `home_team` | Home team (one-hot encoded) |
| `away_team` | Away team (one-hot encoded) |
| `tournament` | Tournament name (one-hot encoded) |

---

## 🏅 World Cup 2026 Predictions (10,000 Monte Carlo Simulations)

| Rank | Team | Elo | FIFA Rank | R16% | QF% | SF% | Final% | Champion% |
|---|---|---|---|---|---|---|---|---|
| 1 | **Spain** | 2171 | 7 | 76.1% | 51.4% | 34.1% | 22.1% | **13.85%** |
| 2 | **England** | 2042 | 5 | 82.3% | 54.0% | 32.7% | 19.0% | **11.48%** |
| 3 | **France** | 2062 | 4 | 68.3% | 43.6% | 25.9% | 14.8% | **8.57%** |
| 4 | **Brazil** | 1979 | 1 | 70.0% | 43.7% | 24.1% | 13.8% | **7.32%** |
| 5 | **Argentina** | 2113 | 3 | 76.1% | 41.7% | 23.5% | 12.3% | **6.56%** |
| 6 | Netherlands | 1959 | 8 | 70.6% | 40.2% | 22.6% | 11.4% | 5.49% |
| 7 | Germany | 1910 | 11 | 62.0% | 33.0% | 18.7% | 9.9% | 4.80% |
| 8 | Belgium | 1849 | 2 | 61.8% | 30.4% | 16.8% | 8.8% | 4.52% |

---

## 🚀 Implementation Roadmap

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Data pipeline fixes, Elo cleaning, `requirements.txt` | ✅ Complete |
| **Phase 2** | Head-to-head features, FIFA squad features, `StandardScaler` | ✅ Complete |
| **Phase 3** | Temporal validation split, sample weighting, model checkpoints | ✅ Complete |
| **Phase 4** | XGBoost & LightGBM integration, hyperparameter tuning | ✅ Complete |
| **Phase 5** | Monte Carlo simulation engine, prediction exports | ✅ Complete |
| **Phase 6** | Streamlit interactive dashboard (3 tabs) | ✅ Complete |
| **Phase 7** | Automated test suite (56 tests), README documentation | ✅ Complete |

---

## 🧪 Tests

56 automated tests across 4 modules:

```
tests/
  test_load_data.py           — Raw CSV loader integrity (14 tests)
  test_feature_engineering.py — Temporal ordering, no-leakage, feature validity (12 tests)
  test_model.py               — Inference shape, probability calibration, batch API (8 tests)
  test_simulation.py          — Group stage, knockout bracket, Monte Carlo correctness (22 tests)
```

Run with:
```powershell
.venv\Scripts\python -m pytest tests/ -v
```

---

## 📦 Dependencies

```
pandas>=2.2.0        numpy>=1.26.0        scikit-learn>=1.4.0
xgboost>=2.0.0       lightgbm>=4.0.0      plotly>=5.20.0
streamlit>=1.35.0    pytest>=8.0.0        scipy>=1.12.0
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
