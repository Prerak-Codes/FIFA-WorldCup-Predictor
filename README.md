# ⚽ FIFA World Cup Predictor — ML-Powered Match & Tournament Forecaster

> Decoupled Full-Stack Machine Learning System predicting international match outcomes and simulating the 2026 FIFA World Cup using XGBoost, Monte Carlo Simulation, FastAPI, and React.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?logo=tailwind-css)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![XGBoost](https://img.shields.io/badge/XGBoost-62.7%25_Accuracy-green)
![Tests](https://img.shields.io/badge/Tests-56%20passed-brightgreen)

---

## 🏆 Project Overview

This project builds a **complete production-grade, decoupled full-stack sports analytics & prediction system**:

- **Decoupled Architecture**: High-performance **FastAPI REST API** backend serving machine learning inference alongside a modern **React + Vite + Tailwind CSS** interactive frontend dashboard.
- **Predicting International Match Outcomes**: Win / Draw / Loss calibrated probabilities computed using an ensemble XGBoost model trained on 49,500+ historical international matches (1872–2026).
- **Simulating the 2026 FIFA World Cup**: Interactive tournament bracket simulation from group stages through knockout rounds to the final with extra time and penalty shootouts.
- **10,000 Monte Carlo Simulations**: Statistical championship probability distributions for all 32 qualified nations.
- **Interactive Team Analytics & Historical Elo Engine**: Historical Elo rating progression curves (1990–2026) and multi-attribute tactical comparisons.

**Key results on the 2021–2026 holdout test set:**

| Model | Accuracy | Log Loss |
|---|---|---|
| Logistic Regression | 58.6% | 0.892 |
| Random Forest | 59.4% | 0.896 |
| Gradient Boosting | 61.1% | 0.851 |
| **XGBoost ⭐ (Champion)** | **62.71%** | **0.832** |
| LightGBM | 62.3% | **0.822** |

---

## 🗂️ Modern Decoupled Project Architecture

```text
FIFA-WorldCup-Predictor/
│
├── frontend/                       # Modern React + Vite + Tailwind CSS Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Brand header, tabs, live API status
│   │   │   ├── PredictorTab.jsx    # H2H selector, verdict, probability meters, stats
│   │   │   ├── BracketSimulatorTab.jsx # Interactive bracket & Monte Carlo leaderboard
│   │   │   └── AnalyticsTab.jsx    # Historical Elo charts (Recharts) & team metrics
│   │   ├── services/
│   │   │   └── api.js              # Frontend REST API client
│   │   ├── utils/
│   │   │   └── teams.js            # Country code mappings & flags
│   │   ├── App.jsx                 # Master application controller
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile                  # Multi-stage Nginx container build
│
├── backend/                        # High-Performance FastAPI REST Service
│   ├── app/
│   │   ├── routes/
│   │   │   └── prediction.py       # REST endpoints (/predict, /simulate, /analytics)
│   │   ├── services/
│   │   │   └── predictor.py        # ML model runner & tournament simulator engine
│   │   ├── schemas/
│   │   │   └── prediction.py       # Pydantic request / response schemas
│   │   └── main.py                 # FastAPI application & CORS configuration
│   ├── models/
│   │   └── best_model.pkl          # Serialized production XGBoost model
│   ├── requirements.txt            # Backend service dependencies
│   └── Dockerfile                  # FastAPI containerfile
│
├── docker-compose.yml              # One-command full-stack container orchestration
│
├── data/
│   ├── raw/                        # Original historical datasets (11 CSVs)
│   ├── interim/                    # Cleaned intermediate Elo & match data
│   ├── processed/                  # Final training_data.csv (49,501 matches)
│   └── predictions/                # 10,000-run Monte Carlo simulation exports
│
├── src/                            # Model training & feature engineering pipelines
│   ├── feature_engineering.py      # Temporal feature pipeline & leak prevention
│   ├── train_model.py              # Multi-model training & checkpointing
│   ├── evaluate_model.py           # Benchmark metrics & reporting
│   └── simulate_tournament.py      # Standalone Monte Carlo tournament CLI
│
├── tests/                          # Automated Pytest suite (56 tests)
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

### Option 1: Docker Compose (Recommended)

Run the entire full-stack application (FastAPI backend + React frontend) with a single command:

```bash
docker compose up --build
```

- **Frontend Dashboard**: Open [http://localhost:3000](http://localhost:3000)
- **FastAPI Interactive Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Local Development

#### 1. Start the FastAPI Backend

```powershell
# In root directory:
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Run FastAPI backend with hot-reload
uvicorn backend.app.main:app --reload --port 8000
```
- API health check: [http://localhost:8000/health](http://localhost:8000/health)
- Swagger Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 2. Start the React Frontend

```powershell
# In a new terminal:
cd frontend
npm install
npm run dev
```
- Interactive Frontend: [http://localhost:5173](http://localhost:5173)

---

## 📡 Backend REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health and version status |
| `GET` | `/api/teams` | List of 32 qualified tournament nations |
| `POST` | `/api/predict` | Predict single head-to-head match outcome & goal difference |
| `POST` | `/api/simulate/single` | Run full tournament simulation (Groups -> Knockouts -> Champion) |
| `GET` | `/api/simulate/leaderboard` | Retrieve 10,000 Monte Carlo simulation championship odds |
| `POST` | `/api/simulate/monte-carlo` | Trigger custom Monte Carlo tournament run |
| `GET` | `/api/analytics/elo-history` | Fetch historical Elo rating time series (1990–2026) |
| `GET` | `/api/analytics/radar` | Fetch comparative team attack, defense, rank, and win rates |

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

## 🧪 Automated Testing

56 comprehensive automated tests verify data integrity, leak-free feature pipelines, calibrated inference, and simulation correctness:

```powershell
.venv\Scripts\python -m pytest tests/ -v
# Output: 56 passed in ~3.5 seconds
```

---

## 📄 License

MIT License &mdash; see [LICENSE](LICENSE) for details.
