"""
FIFA World Cup Predictor — Interactive Streamlit Dashboard
Tabs:
  1. Head-to-Head Match Predictor
  2. World Cup Bracket Simulator
  3. Team Analytics & Historical Explorer
"""

import random
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
sys.path.insert(0, str(BASE_DIR))

from app.utils import (
    load_simulator,
    load_elo_history,
    load_simulation_csv,
    predict_matchup,
    prob_bar_chart,
)
from src.simulate_tournament import DEFAULT_GROUPS

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA World Cup Predictor",
    page_icon="\u26bd",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load shared resources ─────────────────────────────────────────────────────
sim = load_simulator()
ALL_TEAMS = sorted(sim.all_teams)

elo_df = load_elo_history()
ELO_TEAMS = sorted(elo_df["team"].unique().tolist())

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("\u26bd FIFA World Cup Predictor")
st.sidebar.markdown(
    """
    **Model**: XGBoost (62.7% Accuracy)  
    **Log Loss**: 0.8219 on 2021\u20132026 matches  
    **Training**: 43,722 historical matches  
    **Simulation**: 10,000 Monte Carlo runs
    """
)
st.sidebar.divider()
st.sidebar.caption("Built with Streamlit \u00b7 Powered by XGBoost \u00b7 Data: FIFA/Elo ratings")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "\U0001f19a Head-to-Head Predictor",
    "\U0001f3c6 World Cup Bracket Simulator",
    "\U0001f4ca Team Analytics Explorer",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: Head-to-Head Match Predictor
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("\U0001f19a Head-to-Head Match Predictor")
    st.markdown(
        "Select two international teams and predict match outcome probabilities "
        "using our XGBoost model trained on 43,722+ historical matches."
    )

    col1, col_vs, col2 = st.columns([5, 1, 5])

    with col1:
        home_idx = ALL_TEAMS.index("England") if "England" in ALL_TEAMS else 0
        home_team = st.selectbox("\U0001f3e0 Home Team / Team A", options=ALL_TEAMS, index=home_idx, key="h2h_home")

    with col_vs:
        st.markdown("<br><br><h2 style='text-align:center'>VS</h2>", unsafe_allow_html=True)

    with col2:
        away_options = [t for t in ALL_TEAMS if t != home_team]
        away_idx = away_options.index("Spain") if "Spain" in away_options else 0
        away_team = st.selectbox("\u2708\ufe0f Away Team / Team B", options=away_options, index=away_idx, key="h2h_away")

    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        is_neutral = st.toggle("\u2696\ufe0f Neutral Venue", value=True)
    with col_opt2:
        tournament = st.selectbox(
            "\U0001f3df\ufe0f Tournament",
            ["FIFA World Cup", "UEFA Euro", "Copa America", "Friendly", "AFC Asian Cup"],
        )
    with col_opt3:
        match_year = st.number_input("\U0001f4c5 Year", min_value=2020, max_value=2030, value=2026, step=1)

    p_home, p_draw, p_away = predict_matchup(sim, home_team, away_team, is_neutral, tournament, match_year)

    st.divider()

    if p_home > p_away and p_home > p_draw:
        outcome_label = "\U0001f7e2 " + home_team + " FAVORED"
    elif p_draw > p_home and p_draw > p_away:
        outcome_label = "\u2696\ufe0f DRAW LIKELY"
    else:
        outcome_label = "\U0001f534 " + away_team + " FAVORED"

    st.subheader("Prediction: " + outcome_label)

    st.plotly_chart(prob_bar_chart(home_team, away_team, p_home, p_draw, p_away), use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("\U0001f7e2 " + home_team + " Win", f"{p_home:.1%}")
    m2.metric("\u2696\ufe0f Draw", f"{p_draw:.1%}")
    m3.metric("\U0001f534 " + away_team + " Win", f"{p_away:.1%}")

    st.divider()
    st.subheader("\U0001f4cb Team Comparison")
    p1 = sim.team_profiles.get(home_team, {})
    p2 = sim.team_profiles.get(away_team, {})
    comp_df = pd.DataFrame({
        "Attribute": ["Elo Rating", "FIFA Rank", "Overall Rating", "Attack Rating", "Defense Rating", "Form Win Rate", "Form Goal Diff"],
        home_team: [
            f"{p1.get('elo', 0):.0f}",
            str(int(p1.get("rank", 0))),
            f"{p1.get('overall', 72):.1f}",
            f"{p1.get('attack', 72):.1f}",
            f"{p1.get('defense', 72):.1f}",
            f"{p1.get('form_wr', 0.33):.1%}",
            f"{p1.get('form_gd', 0):+.2f}",
        ],
        away_team: [
            f"{p2.get('elo', 0):.0f}",
            str(int(p2.get("rank", 0))),
            f"{p2.get('overall', 72):.1f}",
            f"{p2.get('attack', 72):.1f}",
            f"{p2.get('defense', 72):.1f}",
            f"{p2.get('form_wr', 0.33):.1%}",
            f"{p2.get('form_gd', 0):+.2f}",
        ],
    })
    st.dataframe(comp_df.set_index("Attribute"), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: World Cup Bracket Simulator
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("\U0001f3c6 World Cup 2026 Bracket Simulator")

    sub1, sub2 = st.tabs(["\U0001f3b2 Simulate Tournament", "\U0001f4c8 Monte Carlo Leaderboard"])

    with sub1:
        st.markdown("Click **Run Simulation** to play out one full World Cup bracket using ML model probabilities.")
        seed_val = st.number_input("\U0001f3b2 Random Seed (0 = random each run)", min_value=0, max_value=9999, value=0)
        run_btn = st.button("\u25b6\ufe0f Run Tournament Simulation", type="primary")

        if run_btn:
            if seed_val > 0:
                random.seed(int(seed_val))
            result = sim.simulate_single_tournament()
            st.session_state["bracket_result"] = result

        if "bracket_result" in st.session_state:
            res = st.session_state["bracket_result"]

            st.subheader("\U0001f535 Group Stage \u2014 Qualifiers")
            grp_cols = st.columns(4)
            for idx, (grp, (first, second)) in enumerate(res["group_advancers"].items()):
                with grp_cols[idx % 4]:
                    st.markdown("**Group " + grp + "**")
                    for t in DEFAULT_GROUPS[grp]:
                        if t == first:
                            st.success("\U0001f947 " + t)
                        elif t == second:
                            st.info("\U0001f948 " + t)
                        else:
                            st.markdown("\u274c " + t)

            st.divider()
            st.subheader("\u2694\ufe0f Knockout Bracket")

            kn_cols = st.columns(4)
            r16 = res["r16"]

            with kn_cols[0]:
                st.markdown("**Round of 16**")
                for i in range(0, len(r16), 2):
                    t1, t2 = r16[i], r16[i + 1]
                    w1 = "\U0001f7e2" if t1 in res["qf"] else "\u26aa"
                    w2 = "\U0001f7e2" if t2 in res["qf"] else "\u26aa"
                    st.markdown(w1 + " " + t1)
                    st.markdown(w2 + " " + t2)
                    st.markdown("---")

            with kn_cols[1]:
                st.markdown("**Quarter-Finals**")
                qf = res["qf"]
                for i in range(0, len(qf), 2):
                    t1, t2 = qf[i], qf[i + 1]
                    w1 = "\U0001f7e2" if t1 in res["sf"] else "\u26aa"
                    w2 = "\U0001f7e2" if t2 in res["sf"] else "\u26aa"
                    st.markdown(w1 + " " + t1)
                    st.markdown(w2 + " " + t2)
                    st.markdown("---")

            with kn_cols[2]:
                st.markdown("**Semi-Finals**")
                sf = res["sf"]
                for i in range(0, len(sf), 2):
                    t1, t2 = sf[i], sf[i + 1]
                    w1 = "\U0001f7e2" if t1 in res["final"] else "\u26aa"
                    w2 = "\U0001f7e2" if t2 in res["final"] else "\u26aa"
                    st.markdown(w1 + " " + t1)
                    st.markdown(w2 + " " + t2)
                    st.markdown("---")

            with kn_cols[3]:
                st.markdown("**Final**")
                t1, t2 = res["final"]
                w1 = "\U0001f7e2" if t1 == res["champion"] else "\u26aa"
                w2 = "\U0001f7e2" if t2 == res["champion"] else "\u26aa"
                st.markdown(w1 + " " + t1)
                st.markdown(w2 + " " + t2)
                st.divider()
                st.markdown("**3rd Place**")
                st.markdown("\U0001f949 " + res["third"])

            st.divider()
            st.markdown("## \U0001f3c6 Champion: **" + res["champion"] + "**")
            st.markdown(
                "\U0001f948 Runner-Up: " + res["runner_up"] +
                "  |  \U0001f949 3rd Place: " + res["third"]
            )

    with sub2:
        st.markdown("Championship probabilities from **10,000 Monte Carlo tournament simulations**.")

        sim_csv = load_simulation_csv()

        recalc = st.button("\U0001f504 Re-run 10,000 Simulations (~2 seconds)", type="secondary")
        if recalc:
            with st.spinner("Running 10,000 Monte Carlo simulations\u2026"):
                summary_df, meta = sim.run_monte_carlo(num_simulations=10000, seed=42)
                summary_df.to_csv(
                    BASE_DIR / "data" / "predictions" / "world_cup_simulation_summary.csv",
                    index=False,
                )
                st.session_state["sim_df"] = summary_df
                st.success("Done in " + str(meta["metadata"]["elapsed_seconds"]) + "s!")

        display_df = st.session_state.get("sim_df", sim_csv)

        if display_df is not None:
            fig = px.bar(
                display_df.head(16),
                x="team",
                y="champion_pct",
                color="champion_pct",
                color_continuous_scale="RdYlGn",
                labels={"team": "Country", "champion_pct": "Champion Probability (%)"},
                title="\U0001f3c6 FIFA World Cup 2026 \u2014 Championship Probability (Monte Carlo, N=10,000)",
                text="champion_pct",
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(
                template="plotly_white",
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="Champion Probability (%)",
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("\U0001f4ca Stage-by-Stage Progression Probabilities")
            heatmap_cols = ["r16_pct", "qf_pct", "sf_pct", "final_pct", "champion_pct"]
            heatmap_df = display_df[["team"] + heatmap_cols].set_index("team")
            heatmap_df.columns = ["Round of 16", "Quarter-Final", "Semi-Final", "Final", "Champion"]
            fig2 = px.imshow(
                heatmap_df.values,
                x=heatmap_df.columns.tolist(),
                y=heatmap_df.index.tolist(),
                color_continuous_scale="YlOrRd",
                text_auto=".1f",
                aspect="auto",
                title="Stage Progression Probability Heatmap (%)",
                labels={"color": "Probability (%)"},
            )
            fig2.update_layout(template="plotly_white", height=700)
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("\U0001f4cb Full Leaderboard")
            styled_df = display_df.copy()
            styled_df.columns = [c.replace("_pct", " %").replace("_", " ").title() for c in styled_df.columns]
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No simulation results found. Click Re-run Simulations above.")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: Team Analytics & Historical Explorer
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("\U0001f4ca Team Analytics & Historical Explorer")

    selected_teams = st.multiselect(
        "Select teams to compare (max 8)",
        options=ELO_TEAMS,
        default=["Spain", "England", "France", "Brazil", "Argentina"],
        max_selections=8,
    )

    if not selected_teams:
        st.info("Please select at least one team.")
    else:
        st.subheader("\U0001f4c8 Elo Rating History")
        elo_filtered = elo_df[elo_df["team"].isin(selected_teams)].sort_values("date")
        fig_elo = px.line(
            elo_filtered,
            x="date",
            y="rating",
            color="team",
            title="Historical Elo Ratings Over Time",
            labels={"date": "Date", "rating": "Elo Rating", "team": "Country"},
            template="plotly_white",
        )
        fig_elo.update_traces(line_width=2)
        fig_elo.update_layout(hovermode="x unified")
        st.plotly_chart(fig_elo, use_container_width=True)

        st.divider()

        st.subheader("\U0001f578\ufe0f Team Profile Radar (Current Season)")
        radar_teams = [t for t in selected_teams if t in sim.team_profiles]
        if radar_teams:
            categories = ["Elo (norm)", "Attack", "Defense", "Overall", "Form WR%", "Form GD"]
            all_elo_vals = [v["elo"] for v in sim.team_profiles.values()]
            elo_min, elo_max = min(all_elo_vals), max(all_elo_vals)

            fig_radar = go.Figure()
            for team in radar_teams:
                prof = sim.team_profiles[team]
                elo_norm = (prof["elo"] - elo_min) / (elo_max - elo_min) * 100
                form_gd_norm = max(0.0, min(100.0, 50.0 + prof["form_gd"] * 10))
                values = [
                    elo_norm,
                    prof["attack"],
                    prof["defense"],
                    prof["overall"],
                    prof["form_wr"] * 100,
                    form_gd_norm,
                ]
                values_closed = values + [values[0]]
                cats_closed = categories + [categories[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=cats_closed,
                    fill="toself",
                    name=team,
                    opacity=0.5,
                ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Team Attribute Radar Chart",
                template="plotly_white",
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        st.divider()

        st.subheader("\U0001f4cb Current Team Stats")
        stats_rows = []
        for team in selected_teams:
            prof = sim.team_profiles.get(team, {})
            stats_rows.append({
                "Team": team,
                "Elo Rating": f"{prof.get('elo', 0):.0f}",
                "FIFA Rank": int(prof.get("rank", 0)),
                "Overall": f"{prof.get('overall', 72):.1f}",
                "Attack": f"{prof.get('attack', 72):.1f}",
                "Defense": f"{prof.get('defense', 72):.1f}",
                "Form Win Rate": f"{prof.get('form_wr', 0.33):.1%}",
                "Form Goal Diff": f"{prof.get('form_gd', 0):+.2f}",
            })
        stats_df = pd.DataFrame(stats_rows)
        st.dataframe(stats_df.set_index("Team"), use_container_width=True)
