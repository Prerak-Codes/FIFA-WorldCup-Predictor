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
import re

def clean_html(html: str) -> str:
    """Removes HTML comments, strips whitespace, and collapses newlines."""
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    lines = [line.strip() for line in html.strip().splitlines() if line.strip()]
    return "".join(lines)

from app.components import (
    CSS_THEME,
    get_flag,
    get_team_label,
    render_sidebar_header,
    render_sidebar_model_specs,
    render_prediction_hero,
    render_probability_cards,
    render_team_preview_card,
    render_champion_banner,
)
from src.simulate_tournament import DEFAULT_GROUPS

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA World Cup Analytics & Match Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Modern Sports Analytics Theme
st.markdown(CSS_THEME, unsafe_allow_html=True)

# ── Initialize Prediction Engine ──────────────────────────────────────────────
sim = load_simulator()
ALL_TEAMS = sorted(sim.all_teams)

elo_df = load_elo_history()
ELO_TEAMS = sorted(elo_df["team"].unique().tolist())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(render_sidebar_header(), unsafe_allow_html=True)
    st.markdown(render_sidebar_model_specs(), unsafe_allow_html=True)

    st.markdown(
        clean_html("""
        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                Platform Modules
            </div>
            <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.6;">
                <div>⚔️ <strong>Match Forecaster:</strong> Win/Draw/Loss probabilities calibrated by international Elo & FIFA rankings.</div>
                <div style="margin-top: 6px;">🏆 <strong>Tournament Engine:</strong> Full 32-team World Cup simulation with Monte Carlo depth.</div>
                <div style="margin-top: 6px;">📊 <strong>Team Explorer:</strong> Historical Elo progression & squad attribute profiles.</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.caption("FIFA World Cup Analytics Platform · 2026 Edition")


# ── Top Hero Header ───────────────────────────────────────────────────────────
st.markdown(
    clean_html("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="background: rgba(16,185,129,0.15); color: #34D399; font-size: 0.72rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.08em; text-transform: uppercase;">
                Tournament Forecast Engine
            </span>
            <span style="color: #64748B; font-size: 0.8rem;">·</span>
            <span style="color: #94A3B8; font-size: 0.8rem;">49,500+ Matches Analyzed</span>
        </div>
        <div style="font-size: 2rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">
            FIFA World Cup Prediction Platform
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

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
    st.markdown(
        clean_html("""
        <div style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 18px;">
            Select two competing national teams to calculate match outcome probabilities based on Elo differentials, FIFA squad ratings, and recent international form.
        </div>
        """),
        unsafe_allow_html=True,
    )

    # Team Selection Section
    col1, col_vs, col2 = st.columns([5, 2, 5])

    with col1:
        home_idx = ALL_TEAMS.index("Spain") if "Spain" in ALL_TEAMS else 0
        home_team = st.selectbox(
            "Select Team A (Home / Selected)",
            options=ALL_TEAMS,
            index=home_idx,
            format_func=get_team_label,
            key="h2h_home",
        )
        home_profile = sim.team_profiles.get(home_team, {})
        st.markdown(render_team_preview_card(home_team, home_profile, is_home=True), unsafe_allow_html=True)

    with col_vs:
        st.markdown(
            clean_html("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding-top: 50px;">
                <div style="background: linear-gradient(135deg, #1E293B 0%, #111827 100%); border: 2px solid rgba(255,255,255,0.12); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                    <span style="font-size: 1.25rem; font-weight: 800; color: #F8FAFC; letter-spacing: 0.05em;">VS</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with col2:
        away_options = [t for t in ALL_TEAMS if t != home_team]
        away_idx = away_options.index("England") if "England" in away_options else 0
        away_team = st.selectbox(
            "Select Team B (Away / Opponent)",
            options=away_options,
            index=away_idx,
            format_func=get_team_label,
            key="h2h_away",
        )
        away_profile = sim.team_profiles.get(away_team, {})
        st.markdown(render_team_preview_card(away_team, away_profile, is_home=False), unsafe_allow_html=True)

    # Match Parameters Card
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            clean_html("""
            <div style="font-size: 0.76rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                Match Context & Venue Settings
            </div>
            """),
            unsafe_allow_html=True,
        )
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

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    predict_btn = st.button("⚡ Calculate Match Forecast", type="primary", use_container_width=True)

    # ── Calculation State & Execution ──
    calc_key = (home_team, away_team, is_neutral, tournament, match_year)

    if predict_btn or "last_forecast" not in st.session_state:
        with st.spinner(f"Evaluating XGBoost match dynamics for {home_team} vs {away_team}…"):
            p_h, p_d, p_a = predict_matchup(sim, home_team, away_team, is_neutral, tournament, match_year)
            st.session_state["last_forecast"] = {
                "key": calc_key,
                "probs": (p_h, p_d, p_a),
            }
        if predict_btn:
            st.toast(f"Forecast updated: {home_team} vs {away_team}", icon="⚡")
    else:
        # If user altered selections without clicking button yet, keep reactive update
        if st.session_state["last_forecast"]["key"] != calc_key:
            p_h, p_d, p_a = predict_matchup(sim, home_team, away_team, is_neutral, tournament, match_year)
            st.session_state["last_forecast"] = {
                "key": calc_key,
                "probs": (p_h, p_d, p_a),
            }
        else:
            p_h, p_d, p_a = st.session_state["last_forecast"]["probs"]

    p_home, p_draw, p_away = st.session_state["last_forecast"]["probs"]

    # ── High-Impact Prediction Results ────────────────────────────────────────
    st.markdown(render_prediction_hero(home_team, away_team, p_home, p_draw, p_away, is_neutral), unsafe_allow_html=True)

    # Probability Metric Cards
    st.markdown(render_probability_cards(home_team, away_team, p_home, p_draw, p_away), unsafe_allow_html=True)

    # Probability Distribution Meter
    st.markdown(
        clean_html("""
        <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px;">
            Probability Distribution Breakdown
        </div>
        """),
        unsafe_allow_html=True,
    )
    st.plotly_chart(prob_bar_chart(home_team, away_team, p_home, p_draw, p_away), use_container_width=True)

    # Head-to-Head Comparison Matrix
    st.markdown(
        clean_html("""
        <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC; margin: 28px 0 12px 0;">
            📊 Head-to-Head Metric Comparison
        </div>
        """),
        unsafe_allow_html=True,
    )

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
    st.markdown(
        clean_html("""
        <div style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 18px;">
            Simulate the entire 32-team FIFA World Cup tournament using calibrated match win probabilities, group tiebreaker rules, and knockout penalty shootout models.
        </div>
        """),
        unsafe_allow_html=True,
    )

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

            # Champion Spotlight Banner
            st.markdown(
                render_champion_banner(res["champion"], res["runner_up"], res["third"]),
                unsafe_allow_html=True,
            )

            # Group Stage Standings
            st.markdown(
                clean_html("""
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 24px 0 12px 0;">
                    🔵 Group Stage Qualifiers
                </div>
                """),
                unsafe_allow_html=True,
            )

            grp_cols = st.columns(4)
            for idx, (grp, (first, second)) in enumerate(res["group_advancers"].items()):
                with grp_cols[idx % 4]:
                    group_teams = DEFAULT_GROUPS[grp]
                    items_html = []
                    for t in group_teams:
                        flag = get_flag(t)
                        if t == first:
                            items_html.append(f"<div style='color: #F59E0B; font-weight: 700; padding: 3px 0;'>🥇 {flag} {t}</div>")
                        elif t == second:
                            items_html.append(f"<div style='color: #38BDF8; font-weight: 600; padding: 3px 0;'>🥈 {flag} {t}</div>")
                        else:
                            items_html.append(f"<div style='color: #64748B; padding: 3px 0; text-decoration: line-through;'>{flag} {t}</div>")

                    st.markdown(
                        clean_html(f"""
                        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px; margin-bottom: 16px;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #10B981; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                                Group {grp}
                            </div>
                            {''.join(items_html)}
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )

            st.divider()

            # Knockout Bracket
            st.markdown(
                clean_html("""
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 16px 0 16px 0;">
                    ⚔️ Knockout Stage Progression
                </div>
                """),
                unsafe_allow_html=True,
            )

            kn_cols = st.columns(4)
            r16 = res["r16"]

            with kn_cols[0]:
                st.markdown(clean_html("<div style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 12px;'>Round of 16</div>"), unsafe_allow_html=True)
                for i in range(0, len(r16), 2):
                    t1, t2 = r16[i], r16[i + 1]
                    winner = t1 if t1 in res["qf"] else t2
                    c1 = "#10B981" if winner == t1 else "#64748B"
                    c2 = "#10B981" if winner == t2 else "#64748B"
                    w1_mark = "✔" if winner == t1 else ""
                    w2_mark = "✔" if winner == t2 else ""
                    st.markdown(
                        clean_html(f"""
                        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 12px; margin-bottom: 12px;">
                            <div style="color: {c1}; font-weight: {'700' if winner==t1 else '500'}; display: flex; justify-content: space-between;">
                                <span>{get_flag(t1)} {t1}</span><span>{w1_mark}</span>
                            </div>
                            <div style="color: {c2}; font-weight: {'700' if winner==t2 else '500'}; display: flex; justify-content: space-between; margin-top: 4px;">
                                <span>{get_flag(t2)} {t2}</span><span>{w2_mark}</span>
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )

            with kn_cols[1]:
                st.markdown(clean_html("<div style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 12px;'>Quarter-Finals</div>"), unsafe_allow_html=True)
                qf = res["qf"]
                for i in range(0, len(qf), 2):
                    t1, t2 = qf[i], qf[i + 1]
                    winner = t1 if t1 in res["sf"] else t2
                    c1 = "#10B981" if winner == t1 else "#64748B"
                    c2 = "#10B981" if winner == t2 else "#64748B"
                    w1_mark = "✔" if winner == t1 else ""
                    w2_mark = "✔" if winner == t2 else ""
                    st.markdown(
                        clean_html(f"""
                        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; margin-bottom: 24px;">
                            <div style="color: {c1}; font-weight: {'700' if winner==t1 else '500'}; display: flex; justify-content: space-between;">
                                <span>{get_flag(t1)} {t1}</span><span>{w1_mark}</span>
                            </div>
                            <div style="color: {c2}; font-weight: {'700' if winner==t2 else '500'}; display: flex; justify-content: space-between; margin-top: 6px;">
                                <span>{get_flag(t2)} {t2}</span><span>{w2_mark}</span>
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )

            with kn_cols[2]:
                st.markdown(clean_html("<div style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 12px;'>Semi-Finals</div>"), unsafe_allow_html=True)
                sf = res["sf"]
                for i in range(0, len(sf), 2):
                    t1, t2 = sf[i], sf[i + 1]
                    winner = t1 if t1 in res["final"] else t2
                    c1 = "#10B981" if winner == t1 else "#64748B"
                    c2 = "#10B981" if winner == t2 else "#64748B"
                    w1_mark = "✔" if winner == t1 else ""
                    w2_mark = "✔" if winner == t2 else ""
                    st.markdown(
                        clean_html(f"""
                        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; margin-bottom: 48px;">
                            <div style="color: {c1}; font-weight: {'700' if winner==t1 else '500'}; display: flex; justify-content: space-between;">
                                <span>{get_flag(t1)} {t1}</span><span>{w1_mark}</span>
                            </div>
                            <div style="color: {c2}; font-weight: {'700' if winner==t2 else '500'}; display: flex; justify-content: space-between; margin-top: 8px;">
                                <span>{get_flag(t2)} {t2}</span><span>{w2_mark}</span>
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )

            with kn_cols[3]:
                st.markdown(clean_html("<div style='font-size: 0.85rem; font-weight: 700; color: #F59E0B; text-transform: uppercase; margin-bottom: 12px;'>World Cup Final</div>"), unsafe_allow_html=True)
                t1, t2 = res["final"]
                champ = res["champion"]
                c1 = "#10B981" if champ == t1 else "#64748B"
                c2 = "#10B981" if champ == t2 else "#64748B"
                st.markdown(
                    clean_html(f"""
                    <div style="background: linear-gradient(135deg, rgba(245,158,11,0.1) 0%, #111827 100%); border: 1px solid rgba(245,158,11,0.35); border-radius: 12px; padding: 16px; margin-bottom: 24px;">
                        <div style="color: {c1}; font-weight: {'800' if champ==t1 else '500'}; display: flex; justify-content: space-between; font-size: 1.05rem;">
                            <span>{get_flag(t1)} {t1}</span><span>{'🏆' if champ==t1 else ''}</span>
                        </div>
                        <div style="color: {c2}; font-weight: {'800' if champ==t2 else '500'}; display: flex; justify-content: space-between; font-size: 1.05rem; margin-top: 8px;">
                            <span>{get_flag(t2)} {t2}</span><span>{'🏆' if champ==t2 else ''}</span>
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

                st.markdown(clean_html("<div style='font-size: 0.85rem; font-weight: 700; color: #D97706; text-transform: uppercase; margin-bottom: 8px;'>3rd Place Playoff</div>"), unsafe_allow_html=True)
                st.markdown(
                    clean_html(f"""
                    <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px;">
                        <div style="color: #F8FAFC; font-weight: 600;">🥉 {get_flag(res['third'])} {res['third']}</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

    # ── Sub-tab 2: Monte Carlo Leaderboard ──
    with sub2:
        st.markdown(
            clean_html("""
            <div style="color: #94A3B8; font-size: 0.92rem; margin-bottom: 16px;">
                Aggregated stage advancement and championship probabilities derived from <strong>10,000 full Monte Carlo tournament simulations</strong>.
            </div>
            """),
            unsafe_allow_html=True,
        )

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
            # Championship Probability Bar Chart
            st.markdown(
                clean_html("""
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 18px 0 8px 0;">
                    🏆 Top 16 Championship Favorites
                </div>
                """),
                unsafe_allow_html=True,
            )

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

            # Stage Progression Heatmap
            st.markdown(
                clean_html("""
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 28px 0 8px 0;">
                    📊 Stage-by-Stage Progression Matrix (%)
                </div>
                """),
                unsafe_allow_html=True,
            )

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

            # Full Leaderboard Table
            st.markdown(
                clean_html("""
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 24px 0 8px 0;">
                    📋 Complete Tournament Leaderboard (All 32 Nations)
                </div>
                """),
                unsafe_allow_html=True,
            )
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
    st.markdown(
        clean_html("""
        <div style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 18px;">
            Inspect historical Elo trajectory over football history (1872–2026) and analyze multidimensional radar attributes for international squads.
        </div>
        """),
        unsafe_allow_html=True,
    )

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
        # Elo Rating Progression Line Chart
        st.markdown(
            clean_html("""
            <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 18px 0 8px 0;">
                📈 Historical Elo Rating Progression
            </div>
            """),
            unsafe_allow_html=True,
        )

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

        # Team Radar Profile (Current Season)
        st.markdown(
            clean_html("""
            <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 18px 0 8px 0;">
                🕸️ Squad Attribute Radar Profile (Current Season)
            </div>
            """),
            unsafe_allow_html=True,
        )

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

        # Current Squad Metric Table
        st.markdown(
            clean_html("""
            <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 18px 0 8px 0;">
                📋 Current Squad Performance Specifications
            </div>
            """),
            unsafe_allow_html=True,
        )

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
