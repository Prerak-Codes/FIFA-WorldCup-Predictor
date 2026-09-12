"""
FIFA World Cup Predictor — Modern Football Analytics Platform
=============================================================
Tabs:
  1. Head-to-Head Match Predictor
  2. World Cup Bracket Simulator
  3. Team Analytics & Historical Explorer
"""

import random
import sys
from pathlib import Path

import numpy as np
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
from app.components import (
    CSS_THEME,
    get_flag,
    get_team_label,
)
from src.simulate_tournament import DEFAULT_GROUPS

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA World Cup Analytics & Match Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Clean Styles (Hides deploy button and chrome)
st.markdown(CSS_THEME, unsafe_allow_html=True)

# ── Initialize Prediction Engine ──────────────────────────────────────────────
sim = load_simulator()
ALL_TEAMS = sorted(sim.all_teams)

elo_df = load_elo_history()
ELO_TEAMS = sorted(elo_df["team"].unique().tolist())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏆 FIFA World Cup")
    st.subheader("2026 Analytics Platform")
    st.caption("Calibrated Machine Learning Match & Tournament Forecasting")

    st.divider()

    with st.container(border=True):
        st.markdown("**ENGINE BENCHMARKS**")
        col_b1, col_b2 = st.columns(2)
        col_b1.metric("Holdout Acc", "62.71%")
        col_b2.metric("Log Loss", "0.8219")
        st.caption("Trained on 49,500+ international matches (1872–2026). Tested on holdout fixtures.")

    st.divider()

    with st.container(border=True):
        st.markdown("**PLATFORM MODULES**")
        st.markdown("⚔️ **Match Predictor**: Pairwise Win/Draw/Loss probabilities")
        st.markdown("🏆 **Tournament Engine**: 32-team World Cup simulation")
        st.markdown("📊 **Team Explorer**: Historical Elo ratings & squad radar profiles")

    st.caption("Production Edition · 2026 World Cup")

# ── Top Hero Header ───────────────────────────────────────────────────────────
st.title("⚽ FIFA World Cup Prediction Platform")
st.caption("AI-Powered International Football Analytics & Tournament Monte Carlo Simulation")

# ── Primary Navigation Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "⚔️ Head-to-Head Predictor",
    "🏆 World Cup Bracket Simulator",
    "📊 Team Analytics Explorer",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: Head-to-Head Match Predictor
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("Select two national teams to evaluate match outcome probabilities using our calibrated XGBoost model.")

    # Team Selection Section
    col1, col_vs, col2 = st.columns([5, 2, 5])

    with col1:
        home_idx = ALL_TEAMS.index("Spain") if "Spain" in ALL_TEAMS else 0
        home_team = st.selectbox(
            "Team A (Home / Selected)",
            options=ALL_TEAMS,
            index=home_idx,
            format_func=get_team_label,
            key="h2h_home",
        )
        home_profile = sim.team_profiles.get(home_team, {})
        with st.container(border=True):
            st.markdown(f"### {get_flag(home_team)} {home_team}")
            st.caption("TEAM A · HOME / SELECTED")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Elo", f"{home_profile.get('elo', 1500):.0f}")
            m2.metric("FIFA Rank", f"#{int(home_profile.get('rank', 50))}")
            m3.metric("Attack", f"{home_profile.get('attack', 72):.1f}")
            m4.metric("Defense", f"{home_profile.get('defense', 72):.1f}")

    with col_vs:
        st.markdown("<br><br><h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)

    with col2:
        away_options = [t for t in ALL_TEAMS if t != home_team]
        away_idx = away_options.index("England") if "England" in away_options else 0
        away_team = st.selectbox(
            "Team B (Away / Opponent)",
            options=away_options,
            index=away_idx,
            format_func=get_team_label,
            key="h2h_away",
        )
        away_profile = sim.team_profiles.get(away_team, {})
        with st.container(border=True):
            st.markdown(f"### {get_flag(away_team)} {away_team}")
            st.caption("TEAM B · AWAY / OPPONENT")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Elo", f"{away_profile.get('elo', 1500):.0f}")
            m2.metric("FIFA Rank", f"#{int(away_profile.get('rank', 50))}")
            m3.metric("Attack", f"{away_profile.get('attack', 72):.1f}")
            m4.metric("Defense", f"{away_profile.get('defense', 72):.1f}")

    # Match Parameters Box
    with st.container(border=True):
        st.markdown("**MATCH CONTEXT & VENUE SETTINGS**")
        col_opt1, col_opt2, col_opt3 = st.columns([1, 1.5, 1])
        with col_opt1:
            is_neutral = st.toggle("⚖️ Neutral Ground", value=True, help="Neutral venues eliminate arbitrary home-field scoring advantage.")
        with col_opt2:
            tournament = st.selectbox(
                "Tournament Competition",
                ["FIFA World Cup", "UEFA Euro", "Copa America", "Friendly", "AFC Asian Cup"],
            )
        with col_opt3:
            match_year = st.number_input("Match Year", min_value=2020, max_value=2030, value=2026, step=1)

    predict_btn = st.button("⚡ Calculate Match Forecast", type="primary", use_container_width=True)

    # State & Prediction Computation
    calc_key = (home_team, away_team, is_neutral, tournament, match_year)

    if predict_btn or "last_forecast" not in st.session_state:
        with st.spinner(f"Evaluating XGBoost match dynamics for {home_team} vs {away_team}…"):
            p_h, p_d, p_a = predict_matchup(sim, home_team, away_team, is_neutral, tournament, match_year)
            st.session_state["last_forecast"] = {
                "key": calc_key,
                "probs": (p_h, p_d, p_a),
            }
        if predict_btn:
            st.toast(f"Forecast updated: {home_team} vs {away_team}", icon="⚽")
    else:
        if st.session_state["last_forecast"]["key"] != calc_key:
            p_h, p_d, p_a = predict_matchup(sim, home_team, away_team, is_neutral, tournament, match_year)
            st.session_state["last_forecast"] = {
                "key": calc_key,
                "probs": (p_h, p_d, p_a),
            }
        else:
            p_h, p_d, p_a = st.session_state["last_forecast"]["probs"]

    p_home, p_draw, p_away = st.session_state["last_forecast"]["probs"]

    st.divider()

    # ── 1. Verdict Banner ──
    home_flag = get_flag(home_team)
    away_flag = get_flag(away_team)
    venue_tag = "Neutral Venue" if is_neutral else f"Home Field: {home_team}"

    if p_home > p_away and p_home > p_draw:
        diff_pct = (p_home - p_away) * 100
        st.success(f"""### ★ FORECAST: {home_flag} {home_team.upper()} FAVORED TO WIN

Model predicts **{home_team}** has a **{p_home:.1%}** win probability ({diff_pct:+.1f}% advantage over {away_team}) on {venue_tag}.""")
    elif p_draw > p_home and p_draw > p_away:
        st.info(f"""### ★ FORECAST: ⚖️ DRAW / BALANCED MATCH EXPECTED

Both teams project closely matched. Draw outcome probability is **{p_draw:.1%}** on {venue_tag}.""")
    else:
        diff_pct = (p_away - p_home) * 100
        st.error(f"""### ★ FORECAST: {away_flag} {away_team.upper()} FAVORED TO WIN

Model predicts **{away_team}** has a **{p_away:.1%}** win probability ({diff_pct:+.1f}% advantage over {home_team}) on {venue_tag}.""")

    # ── 2. Structured Probability Metric Cards (Zero HTML Leakage) ──
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        with st.container(border=True):
            st.caption(f"{home_flag} {home_team.upper()} WIN")
            st.metric(label="Win Probability", value=f"{p_home:.1%}")
            st.progress(min(max(p_home, 0.0), 1.0))

    with col_p2:
        with st.container(border=True):
            st.caption("⚖️ DRAW OUTCOME")
            st.metric(label="Draw Probability", value=f"{p_draw:.1%}")
            st.progress(min(max(p_draw, 0.0), 1.0))

    with col_p3:
        with st.container(border=True):
            st.caption(f"{away_flag} {away_team.upper()} WIN")
            st.metric(label="Win Probability", value=f"{p_away:.1%}")
            st.progress(min(max(p_away, 0.0), 1.0))

    # ── 3. Visual Probability Bar Chart ──
    st.plotly_chart(prob_bar_chart(home_team, away_team, p_home, p_draw, p_away), use_container_width=True)

    # ── 4. Metric Comparison Matrix ──
    st.subheader("📊 Head-to-Head Metric Comparison")

    p1 = sim.team_profiles.get(home_team, {})
    p2 = sim.team_profiles.get(away_team, {})

    elo_diff = p1.get("elo", 1500) - p2.get("elo", 1500)
    rank_diff = int(p2.get("rank", 50)) - int(p1.get("rank", 50))
    ovr_diff = p1.get("overall", 72) - p2.get("overall", 72)
    att_diff = p1.get("attack", 72) - p2.get("attack", 72)
    def_diff = p1.get("defense", 72) - p2.get("defense", 72)
    wr_diff = (p1.get("form_wr", 0.33) - p2.get("form_wr", 0.33)) * 100

    comp_df = pd.DataFrame({
        "Performance Metric": [
            "Elo Rating",
            "FIFA World Ranking",
            "Squad Overall Rating",
            "Attack Rating",
            "Defense Rating",
            "Recent Form Win Rate",
            "Form Goal Differential",
        ],
        f"{get_flag(home_team)} {home_team}": [
            f"{p1.get('elo', 0):.0f}",
            f"#{int(p1.get('rank', 0))}",
            f"{p1.get('overall', 72):.1f}",
            f"{p1.get('attack', 72):.1f}",
            f"{p1.get('defense', 72):.1f}",
            f"{p1.get('form_wr', 0.33):.1%}",
            f"{p1.get('form_gd', 0):+.2f}",
        ],
        f"{get_flag(away_team)} {away_team}": [
            f"{p2.get('elo', 0):.0f}",
            f"#{int(p2.get('rank', 0))}",
            f"{p2.get('overall', 72):.1f}",
            f"{p2.get('attack', 72):.1f}",
            f"{p2.get('defense', 72):.1f}",
            f"{p2.get('form_wr', 0.33):.1%}",
            f"{p2.get('form_gd', 0):+.2f}",
        ],
        "Differential Advantage": [
            f"{elo_diff:+.0f} ({home_team if elo_diff > 0 else away_team})",
            f"{rank_diff:+d} ranks ({home_team if rank_diff > 0 else away_team})",
            f"{ovr_diff:+.1f} OVR",
            f"{att_diff:+.1f} ATT",
            f"{def_diff:+.1f} DEF",
            f"{wr_diff:+.1f}%",
            f"{p1.get('form_gd', 0) - p2.get('form_gd', 0):+.2f}",
        ],
    })
    st.dataframe(comp_df.set_index("Performance Metric"), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: World Cup Bracket Simulator
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("Simulate the entire 32-team FIFA World Cup tournament using calibrated match win probabilities, group tiebreakers, and knockout penalty shootout models.")

    sub1, sub2 = st.tabs(["🎲 Single Tournament Simulation", "📈 Monte Carlo Leaderboard (10,000 Runs)"])

    # ── Sub-tab 1: Single Tournament Simulation ──
    with sub1:
        col_s1, col_s2 = st.columns([2, 4])
        with col_s1:
            seed_val = st.number_input(
                "Random Seed (0 = Random outcome every run)",
                min_value=0,
                max_value=9999,
                value=0,
                help="Set a seed > 0 for deterministic replayability.",
            )
        with col_s2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_btn = st.button("▶ Run World Cup Tournament Simulation", type="primary")

        if run_btn:
            if seed_val > 0:
                random.seed(int(seed_val))
                np.random.seed(int(seed_val))
            result = sim.simulate_single_tournament()
            st.session_state["bracket_result"] = result

        if "bracket_result" in st.session_state:
            res = st.session_state["bracket_result"]

            # Champion Spotlight Card
            with st.container(border=True):
                st.header(f"🏆 Champion: {get_flag(res['champion'])} {res['champion']}")
                c_run, c_3rd = st.columns(2)
                c_run.subheader(f"🥈 Runner-Up: {get_flag(res['runner_up'])} {res['runner_up']}")
                c_3rd.subheader(f"🥉 3rd Place: {get_flag(res['third'])} {res['third']}")

            st.divider()

            # Group Stage Standings
            st.subheader("🔵 Group Stage Qualifiers")
            grp_cols = st.columns(4)
            for idx, (grp, (first, second)) in enumerate(res["group_advancers"].items()):
                with grp_cols[idx % 4]:
                    with st.container(border=True):
                        st.markdown(f"**Group {grp}**")
                        for t in DEFAULT_GROUPS[grp]:
                            flag = get_flag(t)
                            if t == first:
                                st.success(f"🥇 {flag} {t}")
                            elif t == second:
                                st.info(f"🥈 {flag} {t}")
                            else:
                                st.caption(f"❌ {flag} {t}")

            st.divider()

            # Knockout Bracket
            st.subheader("⚔️ Knockout Stage Progression")
            kn_cols = st.columns(4)
            r16 = res["r16"]

            with kn_cols[0]:
                st.markdown("**ROUND OF 16**")
                for i in range(0, len(r16), 2):
                    t1, t2 = r16[i], r16[i + 1]
                    winner = t1 if t1 in res["qf"] else t2
                    with st.container(border=True):
                        st.markdown(f"**{'🟢' if winner==t1 else '⚪'} {get_flag(t1)} {t1}**")
                        st.markdown(f"**{'🟢' if winner==t2 else '⚪'} {get_flag(t2)} {t2}**")

            with kn_cols[1]:
                st.markdown("**QUARTER-FINALS**")
                qf = res["qf"]
                for i in range(0, len(qf), 2):
                    t1, t2 = qf[i], qf[i + 1]
                    winner = t1 if t1 in res["sf"] else t2
                    with st.container(border=True):
                        st.markdown(f"**{'🟢' if winner==t1 else '⚪'} {get_flag(t1)} {t1}**")
                        st.markdown(f"**{'🟢' if winner==t2 else '⚪'} {get_flag(t2)} {t2}**")

            with kn_cols[2]:
                st.markdown("**SEMI-FINALS**")
                sf = res["sf"]
                for i in range(0, len(sf), 2):
                    t1, t2 = sf[i], sf[i + 1]
                    winner = t1 if t1 in res["final"] else t2
                    with st.container(border=True):
                        st.markdown(f"**{'🟢' if winner==t1 else '⚪'} {get_flag(t1)} {t1}**")
                        st.markdown(f"**{'🟢' if winner==t2 else '⚪'} {get_flag(t2)} {t2}**")

            with kn_cols[3]:
                st.markdown("**WORLD CUP FINAL**")
                t1, t2 = res["final"]
                champ = res["champion"]
                with st.container(border=True):
                    st.markdown(f"### {'🏆' if champ==t1 else ''} {get_flag(t1)} {t1}")
                    st.markdown(f"### {'🏆' if champ==t2 else ''} {get_flag(t2)} {t2}")

                st.markdown("**3RD PLACE PLAYOFF**")
                with st.container(border=True):
                    st.markdown(f"🥉 **{get_flag(res['third'])} {res['third']}**")

    # ── Sub-tab 2: Monte Carlo Leaderboard ──
    with sub2:
        st.markdown("Aggregated stage advancement and championship probabilities derived from **10,000 full Monte Carlo tournament simulations**.")

        sim_csv = load_simulation_csv()

        recalc = st.button("🔄 Re-run 10,000 Monte Carlo Iterations (~1.0s)", type="secondary")
        if recalc:
            with st.spinner("Executing 10,000 tournament simulations…"):
                summary_df, meta = sim.run_monte_carlo(num_simulations=10000, seed=42)
                summary_df.to_csv(
                    BASE_DIR / "data" / "predictions" / "world_cup_simulation_summary.csv",
                    index=False,
                )
                st.session_state["sim_df"] = summary_df
                st.success(f"Simulation completed in {meta['metadata']['elapsed_seconds']:.2f} seconds ({meta['metadata']['simulations_per_second']:.0f} tournaments/sec).")

        display_df = st.session_state.get("sim_df", sim_csv)

        if display_df is not None:
            st.subheader("🏆 Top 16 Championship Favorites")
            top16 = display_df.head(16).copy()
            top16["formatted_team"] = top16["team"].apply(lambda t: f"{get_flag(t)} {t}")

            fig_bar = px.bar(
                top16,
                x="formatted_team",
                y="champion_pct",
                color="champion_pct",
                color_continuous_scale=["#1E293B", "#059669", "#10B981", "#34D399"],
                labels={"formatted_team": "Country", "champion_pct": "Championship Probability (%)"},
                text="champion_pct",
            )
            fig_bar.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_line_color="rgba(255,255,255,0.15)",
                marker_line_width=1,
            )
            fig_bar.update_layout(
                template="plotly_dark",
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="Champion Probability (%)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=40),
                height=380,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("📊 Stage-by-Stage Progression Matrix (%)")
            heatmap_cols = ["r16_pct", "qf_pct", "sf_pct", "final_pct", "champion_pct"]
            heatmap_df = display_df[["team"] + heatmap_cols].copy()
            heatmap_df["team"] = heatmap_df["team"].apply(lambda t: f"{get_flag(t)} {t}")
            heatmap_df = heatmap_df.set_index("team")
            heatmap_df.columns = ["Round of 16", "Quarter-Final", "Semi-Final", "Final", "Champion"]

            fig_hm = px.imshow(
                heatmap_df.values,
                x=heatmap_df.columns.tolist(),
                y=heatmap_df.index.tolist(),
                color_continuous_scale="Viridis",
                text_auto=".1f",
                aspect="auto",
                labels={"color": "Probability (%)"},
            )
            fig_hm.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=720,
                margin=dict(l=10, r=10, t=30, b=20),
            )
            st.plotly_chart(fig_hm, use_container_width=True)

            st.subheader("📋 Complete Tournament Leaderboard (All 32 Nations)")
            table_df = display_df.copy()
            table_df["Nation"] = table_df["team"].apply(lambda t: f"{get_flag(t)} {t}")
            table_df = table_df[[
                "Nation", "elo", "rank", "r16_pct", "qf_pct", "sf_pct", "final_pct", "champion_pct"
            ]]
            table_df.columns = [
                "Nation", "Elo Rating", "FIFA Rank", "R16 %", "QF %", "SF %", "Final %", "Champion %"
            ]
            st.dataframe(table_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No precomputed simulation data found. Click 'Re-run Monte Carlo' to generate.")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: Team Analytics & Historical Explorer
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("Inspect historical Elo trajectory over football history (1872–2026) and analyze multidimensional radar attributes for international squads.")

    selected_teams = st.multiselect(
        "Select National Teams for Comparative Analysis",
        options=ELO_TEAMS,
        default=["Spain", "England", "France", "Brazil", "Argentina"],
        format_func=get_team_label,
        max_selections=8,
    )

    if not selected_teams:
        st.info("Please select at least one team from the dropdown above.")
    else:
        st.subheader("📈 Historical Elo Rating Progression")
        elo_filtered = elo_df[elo_df["team"].isin(selected_teams)].sort_values("date")
        fig_elo = px.line(
            elo_filtered,
            x="date",
            y="rating",
            color="team",
            labels={"date": "Date", "rating": "Elo Rating", "team": "Country"},
            color_discrete_sequence=["#10B981", "#38BDF8", "#F59E0B", "#F43F5E", "#A855F7", "#EC4899", "#14B8A6", "#E2E8F0"],
        )
        fig_elo.update_traces(line=dict(width=2.5))
        fig_elo.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            margin=dict(l=10, r=10, t=20, b=30),
            height=400,
        )
        st.plotly_chart(fig_elo, use_container_width=True)

        st.divider()

        st.subheader("🕸️ Squad Attribute Radar Profile (Current Season)")
        radar_teams = [t for t in selected_teams if t in sim.team_profiles]
        if radar_teams:
            categories = ["Elo (Norm)", "Attack Index", "Defense Index", "Overall Squad", "Form Win Rate", "Form Goal Edge"]
            all_elo_vals = [v["elo"] for v in sim.team_profiles.values()]
            elo_min, elo_max = min(all_elo_vals), max(all_elo_vals)

            palette = ["#10B981", "#38BDF8", "#F59E0B", "#F43F5E", "#A855F7", "#EC4899", "#14B8A6", "#E2E8F0"]
            fig_radar = go.Figure()

            for idx, team in enumerate(radar_teams):
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
                team_color = palette[idx % len(palette)]

                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=cats_closed,
                    fill="toself",
                    name=f"{get_flag(team)} {team}",
                    line=dict(color=team_color, width=2),
                    opacity=0.35,
                ))

            fig_radar.update_layout(
                template="plotly_dark",
                polar=dict(
                    bgcolor="rgba(17, 24, 39, 0.6)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.08)"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                ),
                showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=30, t=30, b=30),
                height=450,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        st.divider()

        st.subheader("📋 Current Squad Performance Specifications")
        stats_rows = []
        for team in selected_teams:
            prof = sim.team_profiles.get(team, {})
            stats_rows.append({
                "Nation": f"{get_flag(team)} {team}",
                "Elo Rating": f"{prof.get('elo', 0):.0f}",
                "FIFA World Rank": f"#{int(prof.get('rank', 0))}",
                "Squad Overall": f"{prof.get('overall', 72):.1f}",
                "Attack Rating": f"{prof.get('attack', 72):.1f}",
                "Defense Rating": f"{prof.get('defense', 72):.1f}",
                "Form Win Rate": f"{prof.get('form_wr', 0.33):.1%}",
                "Form Goal Differential": f"{prof.get('form_gd', 0):+.2f}",
            })

        stats_df = pd.DataFrame(stats_rows)
        st.dataframe(stats_df.set_index("Nation"), use_container_width=True)
