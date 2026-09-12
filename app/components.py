"""
UI Components and Design System for FIFA World Cup Predictor.
Provides modern football analytics styling, custom cards, and layout helpers.
"""

import re
from typing import Dict, Any, List

def clean_html(html: str) -> str:
    """
    Removes HTML comments, strips leading/trailing spaces from each line,
    and collapses newlines so Streamlit never interprets indented HTML as markdown code blocks.
    """
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    lines = [line.strip() for line in html.strip().splitlines() if line.strip()]
    return "".join(lines)


# ── Country Flag Mapping ──────────────────────────────────────────────────────
TEAM_FLAGS = {
    # 2022 / 2026 World Cup Qualified Nations
    "Qatar": "🇶🇦",
    "Ecuador": "🇪🇨",
    "Senegal": "🇸🇳",
    "Netherlands": "🇳🇱",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Iran": "🇮🇷",
    "United States": "🇺🇸",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "Argentina": "🇦🇷",
    "Saudi Arabia": "🇸🇦",
    "Mexico": "🇲🇽",
    "Poland": "🇵🇱",
    "France": "🇫🇷",
    "Australia": "🇦🇺",
    "Denmark": "🇩🇰",
    "Tunisia": "🇹🇳",
    "Spain": "🇪🇸",
    "Costa Rica": "🇨🇷",
    "Germany": "🇩🇪",
    "Japan": "🇯🇵",
    "Belgium": "🇧🇪",
    "Canada": "🇨🇦",
    "Morocco": "🇲🇦",
    "Croatia": "🇭🇷",
    "Brazil": "🇧🇷",
    "Serbia": "🇷🇸",
    "Switzerland": "🇨🇭",
    "Cameroon": "🇨🇲",
    "Portugal": "🇵🇹",
    "Ghana": "🇬🇭",
    "Uruguay": "🇺🇾",
    "South Korea": "🇰🇷",
    # Notable international teams
    "Italy": "🇮🇹",
    "Colombia": "🇨🇴",
    "Chile": "🇨🇱",
    "Nigeria": "🇳🇬",
    "Egypt": "🇪🇬",
    "Algeria": "🇩🇿",
    "Ivory Coast": "🇨🇮",
    "Peru": "🇵🇪",
    "Sweden": "🇸🇪",
    "Norway": "🇳🇴",
    "Austria": "🇦🇹",
    "Ukraine": "🇺🇦",
    "Czech Republic": "🇨🇿",
    "Turkey": "🇹🇷",
    "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Hungary": "🇭🇺",
    "Paraguay": "🇵🇾",
    "Venezuela": "🇻🇪",
    "South Africa": "🇿🇦",
    "New Zealand": "🇳🇿",
}


def get_flag(team: str) -> str:
    """Returns country flag emoji or football icon fallback."""
    return TEAM_FLAGS.get(team, "⚽")


def get_team_label(team: str) -> str:
    """Returns '🇪🇸 Spain' formatted label."""
    return f"{get_flag(team)} {team}"


# ── CSS Design System ─────────────────────────────────────────────────────────
CSS_THEME = clean_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: #0A0E17 !important;
    color: #F3F4F6 !important;
}

#MainMenu { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
header[data-testid="stHeader"] {
    background: rgba(10, 14, 23, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}
[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stSidebar"] {
    background-color: #0D131F !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.08) !important;
    margin: 1.2rem 0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background-color: #111827 !important;
    padding: 6px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin-bottom: 24px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
}
.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    white-space: pre-wrap !important;
    background-color: transparent !important;
    border-radius: 10px !important;
    color: #94A3B8 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 0 20px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
    background-color: rgba(255, 255, 255, 0.04) !important;
}
.stTabs [aria-selected="true"] {
    background: #1E293B !important;
    color: #10B981 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

div[data-testid="stMetric"] {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 16px 20px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
}
div[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
}

div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    color: #F3F4F6 !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25) !important;
}
div[data-baseweb="input"] > div {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(16, 185, 129, 0.5) !important;
}
.stButton > button[kind="secondary"] {
    background-color: #1E293B !important;
    color: #F1F5F9 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #334155 !important;
    border-color: rgba(255, 255, 255, 0.22) !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background-color: #111827 !important;
}
</style>
""")


# ── Sidebar Components ────────────────────────────────────────────────────────
def render_sidebar_header() -> str:
    html = """
    <div style="padding: 10px 4px 20px 4px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <span style="font-size: 2rem;">🏆</span>
            <div>
                <div style="font-size: 1.15rem; font-weight: 800; letter-spacing: 0.05em; color: #F8FAFC; text-transform: uppercase; line-height: 1.1;">
                    FIFA World Cup
                </div>
                <div style="font-size: 0.78rem; font-weight: 600; color: #10B981; letter-spacing: 0.12em; text-transform: uppercase;">
                    Analytics Platform
                </div>
            </div>
        </div>
        <div style="display: inline-block; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); color: #34D399; font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.04em;">
            ● Model Active · Calibrated XGBoost
        </div>
    </div>
    """
    return clean_html(html)


def render_sidebar_model_specs() -> str:
    html = """
    <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 12px;">
            Engine Benchmarks
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="font-size: 0.84rem; color: #CBD5E1;">Holdout Accuracy</span>
            <span style="font-size: 0.88rem; font-weight: 700; color: #10B981;">62.71%</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="font-size: 0.84rem; color: #CBD5E1;">Holdout Log-Loss</span>
            <span style="font-size: 0.88rem; font-weight: 700; color: #38BDF8;">0.8219</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="font-size: 0.84rem; color: #CBD5E1;">Historical Matches</span>
            <span style="font-size: 0.88rem; font-weight: 600; color: #F1F5F9;">49,500+</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0;">
            <span style="font-size: 0.84rem; color: #CBD5E1;">Monte Carlo Runs</span>
            <span style="font-size: 0.88rem; font-weight: 600; color: #F59E0B;">10,000</span>
        </div>
    </div>
    """
    return clean_html(html)


# ── Prediction Hero Components ────────────────────────────────────────────────
def render_prediction_hero(
    home_team: str,
    away_team: str,
    p_home: float,
    p_draw: float,
    p_away: float,
    is_neutral: bool,
) -> str:
    """High-impact prediction outcome banner."""
    home_flag = get_flag(home_team)
    away_flag = get_flag(away_team)

    if p_home > p_away and p_home > p_draw:
        status_color = "#10B981"
        bg_gradient = "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(17, 24, 39, 0.95) 100%)"
        border_color = "rgba(16, 185, 129, 0.4)"
        outcome_title = f"{home_flag} {home_team.upper()} FAVORED TO WIN"
        diff_pct = (p_home - p_away) * 100
        desc = f"Model assigns <strong>{home_team}</strong> a {p_home:.1%} win chance ({diff_pct:+.1f}% advantage over {away_team})."
    elif p_draw > p_home and p_draw > p_away:
        status_color = "#94A3B8"
        bg_gradient = "linear-gradient(135deg, rgba(148, 163, 184, 0.15) 0%, rgba(17, 24, 39, 0.95) 100%)"
        border_color = "rgba(148, 163, 184, 0.35)"
        outcome_title = "⚖️ DRAW / BALANCED MATCH EXPECTED"
        desc = f"Both nations project closely matched on neutral ground. Draw probability: {p_draw:.1%}."
    else:
        status_color = "#F43F5E"
        bg_gradient = "linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(17, 24, 39, 0.95) 100%)"
        border_color = "rgba(244, 63, 94, 0.4)"
        outcome_title = f"{away_flag} {away_team.upper()} FAVORED TO WIN"
        diff_pct = (p_away - p_home) * 100
        desc = f"Model assigns <strong>{away_team}</strong> a {p_away:.1%} win chance ({diff_pct:+.1f}% advantage over {home_team})."

    venue_text = "Neutral Ground Matchup" if is_neutral else f"Home Field: {home_team}"

    html = f"""
    <div style="background: {bg_gradient}; border: 1px solid {border_color}; border-radius: 16px; padding: 22px 26px; margin: 20px 0 24px 0; box-shadow: 0 8px 30px rgba(0,0,0,0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-size: 0.76rem; font-weight: 700; color: {status_color}; letter-spacing: 0.1em; text-transform: uppercase;">
                ★ MATCH FORECAST VERDICT
            </div>
            <div style="font-size: 0.74rem; font-weight: 500; color: #94A3B8; background: rgba(255,255,255,0.06); padding: 3px 10px; border-radius: 20px;">
                {venue_text}
            </div>
        </div>
        <div style="font-size: 1.55rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.01em; margin-bottom: 6px;">
            {outcome_title}
        </div>
        <div style="font-size: 0.95rem; color: #CBD5E1; line-height: 1.4;">
            {desc}
        </div>
    </div>
    """
    return clean_html(html)


def render_probability_cards(
    home_team: str, away_team: str, p_home: float, p_draw: float, p_away: float
) -> str:
    """3 sleek cards displaying Win/Draw/Loss probabilities without any raw markdown text."""
    home_flag = get_flag(home_team)
    away_flag = get_flag(away_team)

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div style="background: #111827; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; padding: 20px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="font-size: 0.8rem; font-weight: 700; color: #34D399; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px;">
                {home_flag} {home_team} Win
            </div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #F8FAFC; margin-bottom: 10px; line-height: 1;">
                {p_home:.1%}
            </div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 10px; height: 6px; overflow: hidden;">
                <div style="background: #10B981; width: {p_home*100:.1f}%; height: 100%;"></div>
            </div>
        </div>
        <div style="background: #111827; border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 14px; padding: 20px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px;">
                ⚖️ Draw Outcome
            </div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #F8FAFC; margin-bottom: 10px; line-height: 1;">
                {p_draw:.1%}
            </div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 10px; height: 6px; overflow: hidden;">
                <div style="background: #64748B; width: {p_draw*100:.1f}%; height: 100%;"></div>
            </div>
        </div>
        <div style="background: #111827; border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 14px; padding: 20px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="font-size: 0.8rem; font-weight: 700; color: #FB7185; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px;">
                {away_flag} {away_team} Win
            </div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #F8FAFC; margin-bottom: 10px; line-height: 1;">
                {p_away:.1%}
            </div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 10px; height: 6px; overflow: hidden;">
                <div style="background: #F43F5E; width: {p_away*100:.1f}%; height: 100%;"></div>
            </div>
        </div>
    </div>
    """
    return clean_html(html)


# ── Team Profile Preview Cards ────────────────────────────────────────────────
def render_team_preview_card(team: str, profile: Dict[str, Any], is_home: bool) -> str:
    """Card displaying team name, flag, Elo, FIFA rank, and attack/defense ratings."""
    flag = get_flag(team)
    elo_val = profile.get("elo", 1500.0)
    rank_val = int(profile.get("rank", 50))
    overall = profile.get("overall", 72.0)
    attack = profile.get("attack", 72.0)
    defense = profile.get("defense", 72.0)
    badge_label = "TEAM A (HOME)" if is_home else "TEAM B (AWAY)"
    badge_color = "#10B981" if is_home else "#38BDF8"

    html = f"""
    <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 18px; margin-top: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 0.72rem; font-weight: 700; color: {badge_color}; letter-spacing: 0.08em; text-transform: uppercase;">
                {badge_label}
            </div>
            <div style="font-size: 0.74rem; font-weight: 600; color: #94A3B8; background: rgba(255,255,255,0.06); padding: 2px 8px; border-radius: 12px;">
                FIFA #{rank_val}
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
            <span style="font-size: 2rem;">{flag}</span>
            <span style="font-size: 1.35rem; font-weight: 800; color: #F8FAFC;">{team}</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center;">
            <div style="background: rgba(255,255,255,0.04); padding: 6px; border-radius: 8px;">
                <div style="font-size: 0.68rem; color: #94A3B8; font-weight: 600;">ELO</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #F1F5F9;">{elo_val:.0f}</div>
            </div>
            <div style="background: rgba(255,255,255,0.04); padding: 6px; border-radius: 8px;">
                <div style="font-size: 0.68rem; color: #94A3B8; font-weight: 600;">OVR</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #F1F5F9;">{overall:.1f}</div>
            </div>
            <div style="background: rgba(255,255,255,0.04); padding: 6px; border-radius: 8px;">
                <div style="font-size: 0.68rem; color: #94A3B8; font-weight: 600;">ATT</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #10B981;">{attack:.1f}</div>
            </div>
            <div style="background: rgba(255,255,255,0.04); padding: 6px; border-radius: 8px;">
                <div style="font-size: 0.68rem; color: #94A3B8; font-weight: 600;">DEF</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #38BDF8;">{defense:.1f}</div>
            </div>
        </div>
    </div>
    """
    return clean_html(html)


# ── Tournament & Bracket Helpers ──────────────────────────────────────────────
def render_champion_banner(champion: str, runner_up: str, third: str) -> str:
    """Championship trophy banner."""
    champ_flag = get_flag(champion)
    run_flag = get_flag(runner_up)
    third_flag = get_flag(third)

    html = f"""
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(17, 24, 39, 0.95) 100%); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 16px; padding: 24px; margin: 24px 0; text-align: center; box-shadow: 0 8px 32px rgba(245, 158, 11, 0.2);">
        <div style="font-size: 0.8rem; font-weight: 700; color: #F59E0B; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 6px;">
            🏆 WORLD CUP CHAMPION
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 8px;">
            {champ_flag} {champion}
        </div>
        <div style="display: flex; justify-content: center; gap: 24px; font-size: 0.92rem; color: #CBD5E1; margin-top: 12px;">
            <div>🥈 <strong>Runner-Up:</strong> {run_flag} {runner_up}</div>
            <div>🥉 <strong>3rd Place:</strong> {third_flag} {third}</div>
        </div>
    </div>
    """
    return clean_html(html)
