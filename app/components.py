"""
UI Components and Country Flags for FIFA World Cup Predictor.
100% structured native components — zero raw HTML leakage.
"""

TEAM_FLAGS = {
    "Qatar": "🇶🇦", "Ecuador": "🇪🇨", "Senegal": "🇸🇳", "Netherlands": "🇳🇱",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Iran": "🇮🇷", "United States": "🇺🇸", "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "Argentina": "🇦🇷", "Saudi Arabia": "🇸🇦", "Mexico": "🇲🇽", "Poland": "🇵🇱",
    "France": "🇫🇷", "Australia": "🇦🇺", "Denmark": "🇩🇰", "Tunisia": "🇹🇳",
    "Spain": "🇪🇸", "Costa Rica": "🇨🇷", "Germany": "🇩🇪", "Japan": "🇯🇵",
    "Belgium": "🇧🇪", "Canada": "🇨🇦", "Morocco": "🇲🇦", "Croatia": "🇭🇷",
    "Brazil": "🇧🇷", "Serbia": "🇷🇸", "Switzerland": "🇨🇭", "Cameroon": "🇨🇲",
    "Portugal": "🇵🇹", "Ghana": "🇬🇭", "Uruguay": "🇺🇾", "South Korea": "🇰🇷",
    "Italy": "🇮🇹", "Colombia": "🇨🇴", "Chile": "🇨🇱", "Nigeria": "🇳🇬",
    "Egypt": "🇪🇬", "Algeria": "🇩🇿", "Ivory Coast": "🇨🇮", "Peru": "🇵🇪",
    "Sweden": "🇸🇪", "Norway": "🇳🇴", "Austria": "🇦🇹", "Ukraine": "🇺🇦",
    "Czech Republic": "🇨🇿", "Turkey": "🇹🇷", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Hungary": "🇭🇺", "Paraguay": "🇵🇾", "Venezuela": "🇻🇪",
    "South Africa": "🇿🇦", "New Zealand": "🇳🇿",
}


def get_flag(team: str) -> str:
    """Returns country flag emoji or football icon fallback."""
    return TEAM_FLAGS.get(team, "⚽")


def get_team_label(team: str) -> str:
    """Returns '🇪🇸 Spain' formatted label."""
    return f"{get_flag(team)} {team}"


CSS_THEME = """
<style>
/* Hide Streamlit deploy button & toolbar */
#MainMenu { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
header [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* Modern font and tabs */
.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
</style>
"""
