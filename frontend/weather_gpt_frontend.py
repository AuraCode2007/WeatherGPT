"""
frontend/weather_gpt_frontend.py
WeatherGPT — AI-powered weather intelligence platform.

Features:
  • Real-time weather dashboard with live metrics
  • Conversational AI chat (Gemini) with multilingual support
  • IMD-style extreme weather alerts & early warnings
  • Domain-specific advisory modes (Agriculture, Aviation, Flood, Urban, Marine, Research)
  • Climate trend analysis with historical data
  • Voice input support (browser speech-to-text via HTML5)
  • Mobile-responsive, dark-mode premium UI
"""

import streamlit as st
import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WeatherGPT — AI Weather Intelligence",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND = "http://localhost:8000"

# ─────────────────────────────────────────────────────────────────────────────
# CSS — Premium dark glassmorphism UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root & Reset ─────────────────────────────────────────────────────────── */
:root {
    --bg-primary:    #060b17;
    --bg-card:       rgba(13, 25, 50, 0.75);
    --bg-glass:      rgba(255, 255, 255, 0.04);
    --accent-blue:   #3b82f6;
    --accent-cyan:   #06b6d4;
    --accent-green:  #10b981;
    --accent-yellow: #f59e0b;
    --accent-red:    #ef4444;
    --accent-purple: #8b5cf6;
    --text-primary:  #f1f5f9;
    --text-muted:    #64748b;
    --border:        rgba(255,255,255,0.08);
    --glow-blue:     0 0 40px rgba(59,130,246,0.15);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background: rgba(6, 11, 23, 0.95) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hero Header ──────────────────────────────────────────────────────────── */
.hero-header {
    background: linear-gradient(135deg,
        rgba(59,130,246,0.15) 0%,
        rgba(6,182,212,0.10) 40%,
        rgba(139,92,246,0.10) 100%);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f1f5f9 0%, #06b6d4 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.5rem;
    font-weight: 400;
}
.badge-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.badge {
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93c5fd;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Weather Cards ────────────────────────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s, border-color 0.2s;
    position: relative;
    overflow: hidden;
}
.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(59,130,246,0.4);
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
    opacity: 0;
    transition: opacity 0.2s;
}
.metric-card:hover::after { opacity: 1; }
.metric-icon  { font-size: 1.6rem; margin-bottom: 0.4rem; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }
.metric-label { font-size: 0.72rem; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.2rem; }

/* ── Alert Banner ─────────────────────────────────────────────────────────── */
.alert-extreme { background: rgba(239,68,68,0.12);  border-left: 4px solid #ef4444; }
.alert-severe  { background: rgba(245,158,11,0.12); border-left: 4px solid #f59e0b; }
.alert-moderate{ background: rgba(59,130,246,0.12); border-left: 4px solid #3b82f6; }
.alert-minor   { background: rgba(16,185,129,0.12); border-left: 4px solid #10b981; }
.alert-box {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.88rem;
    line-height: 1.6;
    color: var(--text-primary);
}
.alert-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.3rem; }

/* ── Forecast Strip ───────────────────────────────────────────────────────── */
.forecast-strip {
    display: flex;
    gap: 0.8rem;
    overflow-x: auto;
    padding: 0.5rem 0 0.8rem;
    scrollbar-width: thin;
    scrollbar-color: #3b82f6 transparent;
}
.forecast-day {
    flex: 0 0 110px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 0.7rem;
    text-align: center;
    font-size: 0.78rem;
    color: #94a3b8;
    transition: border-color 0.2s;
}
.forecast-day:hover { border-color: rgba(59,130,246,0.5); }
.forecast-day .fday  { font-weight: 600; color: #f1f5f9; margin-bottom: 0.3rem; font-size: 0.8rem; }
.forecast-day .ftemp { font-size: 1.1rem; font-weight: 700; color: #06b6d4; }

/* ── Chat Interface ───────────────────────────────────────────────────────── */
.chat-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
}
.chat-bubble-user {
    background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(6,182,212,0.20));
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 16px 16px 4px 16px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.9rem;
    line-height: 1.6;
    color: var(--text-primary);
    animation: fadeInRight 0.3s ease;
}
.chat-bubble-ai {
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 16px 16px 16px 4px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.9rem;
    line-height: 1.7;
    color: var(--text-primary);
    animation: fadeInLeft 0.3s ease;
}
.chat-label-user { text-align: right; font-size: 0.72rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; }
.chat-label-ai   { font-size: 0.72rem; color: var(--accent-purple); font-weight: 600; margin-bottom: 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; }

@keyframes fadeInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* ── Section Titles ───────────────────────────────────────────────────────── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 0.5rem;
}

/* ── Domain Pills ─────────────────────────────────────────────────────────── */
.domain-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

/* ── AQI Bar ──────────────────────────────────────────────────────────────── */
.aqi-bar-wrap { margin: 0.5rem 0; }
.aqi-bar { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444); position: relative; }
.aqi-marker { position: absolute; top: -4px; width: 16px; height: 16px; background: white; border-radius: 50%; border: 3px solid #3b82f6; transform: translateX(-50%); transition: left 0.5s; }

/* ── Voice Button ─────────────────────────────────────────────────────────── */
.voice-btn {
    background: linear-gradient(135deg, rgba(139,92,246,0.3), rgba(59,130,246,0.3));
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 50px;
    padding: 0.5rem 1.2rem;
    color: #c4b5fd;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: all 0.2s;
}
.voice-btn:hover { background: rgba(139,92,246,0.4); }

/* ── Overrides ────────────────────────────────────────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #3b82f6 !important;
    border-bottom: 2px solid #3b82f6 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
}
div[data-testid="stMetricValue"] { color: var(--text-primary) !important; }
.element-container { animation: fadeUp 0.4s ease; }
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
LANGUAGES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te",
    "বাংলা (Bengali)": "bn",
    "ಕನ್ನಡ (Kannada)": "kn",
    "मराठी (Marathi)": "mr",
    "ગુજરાતી (Gujarati)": "gu",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "മലയാളം (Malayalam)": "ml",
}

DOMAINS = {
    "🌍 General":                    "General",
    "🌾 Agriculture / Farming":      "Agriculture / Farming",
    "✈️ Aviation":                   "Aviation",
    "🌊 Flood & Cyclone Warning":    "Flood & Cyclone Warning",
    "🏙️ Smart City / Urban":         "Smart City / Urban",
    "⚓ Marine & Fisheries":          "Marine & Fisheries",
    "🔬 Climate Research":           "Climate Research",
}

DOMAIN_COLORS = {
    "General":                 "#3b82f6",
    "Agriculture / Farming":   "#10b981",
    "Aviation":                "#f59e0b",
    "Flood & Cyclone Warning": "#ef4444",
    "Smart City / Urban":      "#06b6d4",
    "Marine & Fisheries":      "#8b5cf6",
    "Climate Research":        "#64748b",
}

POPULAR_CITIES = [
    "Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Bhopal", "Bhubaneswar", "Patna", "Guwahati", "Srinagar",
    "Chandigarh", "Kochi", "Visakhapatnam", "Nagpur",
]

AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
AQI_COLORS = {1: "#10b981", 2: "#84cc16", 3: "#f59e0b", 4: "#f97316", 5: "#ef4444"}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "chat_history": [],
    "location": "Delhi",
    "language": "English",
    "domain_label": "🌍 General",
    "weather_data": None,
    "last_city": "",
    "api_status": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def check_api() -> bool:
    try:
        r = requests.get(f"{BACKEND}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def fetch_weather(city: str) -> dict | None:
    try:
        r = requests.get(f"{BACKEND}/weather/", params={"city": city}, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def send_chat(question: str, city: str, lang_code: str, domain: str) -> str:
    try:
        payload = {
            "user_question": question,
            "location": city,
            "language_code": lang_code,
            "domain": domain,
        }
        r = requests.post(f"{BACKEND}/chat/", json=payload, timeout=30)
        if r.status_code == 200:
            return r.json().get("response", "⚠️ Empty response from AI.")
    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        return f"⚠️ Error: {e}"
    return _mock_response(question, city)


def fetch_alerts(city: str) -> dict | None:
    try:
        r = requests.get(f"{BACKEND}/alerts/", params={"city": city}, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def fetch_climate(city: str, month: int) -> dict | None:
    try:
        r = requests.post(f"{BACKEND}/climate/", json={"city": city, "month": month}, timeout=20)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _mock_response(question: str, city: str) -> str:
    """Friendly fallback when backend is offline."""
    q = question.lower()
    if "rain" in q or "rainfall" in q:
        return f"🌧️ Based on typical patterns, {city} may see moderate rainfall. Connect the backend for live AI forecasts."
    if "forecast" in q or "tomorrow" in q:
        return f"📅 For a 5-day AI forecast for {city}, please start the FastAPI backend (`uvicorn backend.main:app --reload`)."
    if "alert" in q or "warning" in q:
        return f"⚠️ No active alerts retrieved — backend offline. Start the API server for live IMD-style warnings."
    return f"METEOR backend is offline. Start it with `uvicorn backend.main:app --reload` to get real-time answers for {city}."


def wind_direction_arrow(degrees: int) -> str:
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    idx = round(degrees / 45) % 8
    arrows = ["↑","↗","→","↘","↓","↙","←","↖"]
    return f"{arrows[idx]} {dirs[idx]}"


def render_weather_card(wd: dict):
    temp      = wd.get("temp", "--")
    feels     = wd.get("feels_like", "--")
    tmin      = wd.get("temp_min", "--")
    tmax      = wd.get("temp_max", "--")
    condition = wd.get("condition", "--")
    desc      = wd.get("description", "")
    humidity  = wd.get("humidity", "--")
    wind      = wd.get("wind_speed", "--")
    wind_dir  = wd.get("wind_direction", 0)
    vis       = wd.get("visibility", "--")
    aqi       = wd.get("aqi")
    city      = wd.get("city", st.session_state.location)
    country   = wd.get("country", "")
    alert     = wd.get("alert")

    # Condition emoji
    cond_lower = condition.lower()
    if "thunder" in cond_lower: cond_emoji = "⛈️"
    elif "snow" in cond_lower:  cond_emoji = "❄️"
    elif "rain" in cond_lower:  cond_emoji = "🌧️"
    elif "cloud" in cond_lower: cond_emoji = "☁️"
    elif "clear" in cond_lower: cond_emoji = "☀️"
    elif "mist"  in cond_lower or "fog" in cond_lower: cond_emoji = "🌫️"
    elif "haze"  in cond_lower: cond_emoji = "😶‍🌫️"
    else: cond_emoji = "🌡️"

    # Alert banner
    if alert:
        sev_class = "alert-extreme" if "RED" in alert or "Severe" in alert else "alert-severe"
        st.markdown(f"""
        <div class="alert-box {sev_class}">
            <div class="alert-title">⚡ Active Weather Warning</div>
            {alert}
        </div>""", unsafe_allow_html=True)

    # Hero temp display
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown(f"""
        <div style="padding:1rem 0">
            <div style="font-size:4rem;font-weight:800;color:#f1f5f9;line-height:1">{temp}°C</div>
            <div style="font-size:1rem;color:#94a3b8;margin-top:0.3rem">{cond_emoji} {desc}</div>
            <div style="font-size:0.8rem;color:#64748b;margin-top:0.5rem">
                Feels like {feels}°C &nbsp;·&nbsp; {tmin}°C / {tmax}°C
            </div>
            <div style="font-size:1.1rem;font-weight:600;color:#06b6d4;margin-top:0.6rem">
                📍 {city}, {country}
            </div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-icon">💧</div>
                <div class="metric-value">{humidity}%</div>
                <div class="metric-label">Humidity</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">💨</div>
                <div class="metric-value">{wind} km/h</div>
                <div class="metric-label">{wind_direction_arrow(wind_dir)} Wind</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">👁️</div>
                <div class="metric-value">{vis} km</div>
                <div class="metric-label">Visibility</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🌬️</div>
                <div class="metric-value">{AQI_LABELS.get(aqi, 'N/A')}</div>
                <div class="metric-label">Air Quality</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Forecast strip
    forecast = wd.get("forecast", [])
    if forecast:
        st.markdown('<div class="section-title">📅 5-Day Forecast</div>', unsafe_allow_html=True)
        cards = ""
        for day in forecast:
            parts = day.split(":")
            label = parts[0].strip() if len(parts) > 0 else "—"
            detail = parts[1].strip() if len(parts) > 1 else day
            temp_val = detail.split("°C")[0].strip().split(",")[-1].strip() if "°C" in detail else "—"
            desc_val = detail.split(",")[1].strip() if "," in detail else "—"
            cards += f"""
            <div class="forecast-day">
                <div class="fday">{label}</div>
                <div class="ftemp">{temp_val}°</div>
                <div>{desc_val[:14]}</div>
            </div>"""
        st.markdown(f'<div class="forecast-strip">{cards}</div>', unsafe_allow_html=True)


def render_chat_history():
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:#475569">
            <div style="font-size:2.5rem;margin-bottom:0.5rem">💬</div>
            <div style="font-size:1rem;font-weight:600;color:#64748b">Ask anything about weather</div>
            <div style="font-size:0.82rem;margin-top:0.3rem;color:#475569">
                Try: "Will it rain tomorrow?" · "Is it safe to fly?" · "Flood risk this week?"
            </div>
        </div>""", unsafe_allow_html=True)
        return

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-label-user">You</div>
            <div class="chat-bubble-user">{msg["content"]}</div>""",
            unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-label-ai">METEOR Telemetry</div>
            <div class="chat-bubble-ai">{msg["content"]}</div>""",
            unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.2rem 0 0.5rem">
        <div style="font-size:1.1rem;font-weight:700;color:#f1f5f9">METEOR Telemetry</div>
        <div style="font-size:0.72rem;color:#64748b;margin-top:2px">National Operations System</div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0">
    """, unsafe_allow_html=True)

    # ── Connection status
    if st.button("🔗 Test Backend Connection", use_container_width=True):
        st.session_state.api_status = check_api()

    if st.session_state.api_status is True:
        st.success("✅ Backend connected", icon="✅")
    elif st.session_state.api_status is False:
        st.error("❌ Backend offline — using mock data", icon="⚠️")
    else:
        st.info("Click above to test connection", icon="ℹ️")

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0">', unsafe_allow_html=True)

    # ── Location
    st.markdown("**📍 Location**")
    city_input = st.selectbox(
        "Select City", POPULAR_CITIES, index=POPULAR_CITIES.index("Delhi"), label_visibility="collapsed"
    )
    custom_city = st.text_input("Or type any city…", placeholder="e.g. Mangalore, Shimla", label_visibility="collapsed")
    city = custom_city.strip() if custom_city.strip() else city_input
    st.session_state.location = city

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0">', unsafe_allow_html=True)

    # ── Language
    st.markdown("**🌐 Response Language**")
    lang_label = st.selectbox("Language", list(LANGUAGES.keys()), label_visibility="collapsed")
    lang_code  = LANGUAGES[lang_label]
    st.session_state.language = lang_label

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0">', unsafe_allow_html=True)

    # ── Domain
    st.markdown("**🎯 Advisory Domain**")
    domain_label = st.selectbox("Domain", list(DOMAINS.keys()), label_visibility="collapsed")
    domain = DOMAINS[domain_label]
    domain_color = DOMAIN_COLORS.get(domain, "#3b82f6")
    st.session_state.domain_label = domain_label
    st.markdown(f"""<div class="domain-pill" style="background:{domain_color}22;
        border:1px solid {domain_color}55;color:{domain_color}">
        {domain_label}</div>""", unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0">', unsafe_allow_html=True)

    # ── Quick actions
    st.markdown("**⚡ Quick Prompts**")
    quick_prompts = {
        "🌡️ Current conditions": f"What is the current weather in {city}?",
        "📅 5-day forecast":     f"Give me a 5-day forecast for {city}.",
        "⚠️ Any alerts?":         f"Are there any weather alerts or warnings for {city}?",
        "🌾 Crop advisory":      f"Is the weather suitable for farming activities in {city} this week?",
        "✈️ Aviation briefing":  f"Give me an aviation weather briefing for {city}.",
        "🌊 Flood risk":         f"What is the flood risk in {city} this week?",
    }
    for label, prompt_text in quick_prompts.items():
        if st.button(label, use_container_width=True, key=f"qp_{label}"):
            st.session_state["_quick_prompt"] = prompt_text

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("""
    <div style="margin-top:1rem;font-size:0.7rem;color:#475569;text-align:center">
        Powered by Google Gemini · OpenWeatherMap<br>
        Open-Meteo · FastAPI · Streamlit
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">🌦️ WeatherGPT</div>
    <div class="hero-subtitle">
        AI-Powered Conversational Platform for Weather Forecasting, Alerts & Climate Intelligence
    </div>
    <div class="badge-row">
        <span class="badge">Real-time Data</span>
        <span class="badge">Gemini AI</span>
        <span class="badge">10 Indian Languages</span>
        <span class="badge">IMD Alerts</span>
        <span class="badge">Climate Analytics</span>
        <span class="badge">7 Use-Case Domains</span>
    </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Main tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_weather, tab_chat, tab_alerts, tab_climate = st.tabs([
    "🌡️ Live Weather", "💬 AI Chat", "⚠️ Alerts & Warnings", "📊 Climate Analytics"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — Live Weather
# ═════════════════════════════════════════════════════════════════════════════
with tab_weather:
    col_refresh, col_ts = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.weather_data = None
            st.session_state.last_city    = ""

    # Fetch weather if city changed or no data
    if st.session_state.last_city != city or st.session_state.weather_data is None:
        with st.spinner(f"Fetching live weather for **{city}**…"):
            wd = fetch_weather(city)
        if wd:
            st.session_state.weather_data = wd
            st.session_state.last_city    = city
        else:
            st.session_state.weather_data = None

    with col_ts:
        st.markdown(f"""<div style="color:#64748b;font-size:0.8rem;padding-top:0.7rem">
            Last updated: {datetime.now().strftime('%d %b %Y · %H:%M')} &nbsp;·&nbsp;
            Location: <strong style="color:#06b6d4">{city}</strong>
        </div>""", unsafe_allow_html=True)

    if st.session_state.weather_data:
        render_weather_card(st.session_state.weather_data)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#475569;">
            <div style="font-size:3rem">🌐</div>
            <div style="font-size:1rem;font-weight:600;margin-top:0.5rem">Backend offline — showing sample layout</div>
            <div style="font-size:0.82rem;margin-top:0.3rem">
                Run <code>uvicorn backend.main:app --reload</code> and add your API keys to .env
            </div>
        </div>""", unsafe_allow_html=True)

        # Demo metric cards
        st.markdown("""
        <div class="metric-grid">
            <div class="metric-card"><div class="metric-icon">🌡️</div>
                <div class="metric-value">—°C</div><div class="metric-label">Temperature</div></div>
            <div class="metric-card"><div class="metric-icon">💧</div>
                <div class="metric-value">—%</div><div class="metric-label">Humidity</div></div>
            <div class="metric-card"><div class="metric-icon">💨</div>
                <div class="metric-value">— km/h</div><div class="metric-label">Wind</div></div>
            <div class="metric-card"><div class="metric-icon">👁️</div>
                <div class="metric-value">— km</div><div class="metric-label">Visibility</div></div>
        </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — AI Chat
# ═════════════════════════════════════════════════════════════════════════════
with tab_chat:
    # Domain context banner
    st.markdown(f"""
    <div style="background:{domain_color}18;border:1px solid {domain_color}44;
         border-radius:10px;padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.83rem;color:{domain_color}">
        <strong>Advisory Mode:</strong> {domain_label} &nbsp;·&nbsp;
        <strong>Language:</strong> {lang_label} &nbsp;·&nbsp;
        <strong>Location:</strong> {city}
    </div>""", unsafe_allow_html=True)

    # Voice input widget
    st.markdown("""
    <div style="margin-bottom:0.8rem">
        <span style="font-size:0.8rem;color:#64748b">
            🎤 Voice input (HTML5 Speech API — Chrome/Edge only):
        </span>
    </div>""", unsafe_allow_html=True)

    voice_html = """
    <div style="margin-bottom:0.5rem">
        <button class="voice-btn" onclick="startVoice()" id="voiceBtn">🎙️ Speak Now</button>
        <span id="voiceStatus" style="font-size:0.78rem;color:#64748b;margin-left:0.8rem"></span>
    </div>
    <input type="text" id="voiceResult" placeholder="Voice transcript will appear here…"
        style="width:100%;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
               border-radius:8px;padding:0.5rem 0.8rem;color:#f1f5f9;font-family:Inter,sans-serif;
               font-size:0.85rem;margin-bottom:0.5rem;box-sizing:border-box" readonly>
    <script>
    function startVoice() {
        var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) { document.getElementById('voiceStatus').innerText='Not supported in this browser.'; return; }
        var rec = new SpeechRec();
        rec.lang = 'en-IN';
        rec.interimResults = false;
        document.getElementById('voiceBtn').innerText = '🔴 Listening…';
        document.getElementById('voiceStatus').innerText = 'Speak clearly into your microphone…';
        rec.start();
        rec.onresult = function(e) {
            var transcript = e.results[0][0].transcript;
            document.getElementById('voiceResult').value = transcript;
            document.getElementById('voiceBtn').innerText = '🎙️ Speak Now';
            document.getElementById('voiceStatus').innerText = 'Done! Copy the text above into the chat box.';
        };
        rec.onerror = function() {
            document.getElementById('voiceBtn').innerText = '🎙️ Speak Now';
            document.getElementById('voiceStatus').innerText = 'Error — try again.';
        };
    }
    </script>
    """
    st.components.v1.html(voice_html, height=100)

    # Chat history
    chat_container = st.container()
    with chat_container:
        render_chat_history()

    # Input
    user_input = st.chat_input(
        f"Ask WeatherGPT about {city} weather… (in any language)",
        key="main_chat_input",
    )

    # Handle quick-prompt injection
    if "_quick_prompt" in st.session_state:
        user_input = st.session_state.pop("_quick_prompt")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Processing telemetry parameters…"):
            ai_reply = send_chat(user_input, city, lang_code, domain)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — Alerts & Warnings
# ═════════════════════════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown(f"""
    <div class="section-title">⚠️ Active Weather Alerts — {city}</div>""",
    unsafe_allow_html=True)

    col_fetch, _ = st.columns([1, 3])
    with col_fetch:
        fetch_alerts_btn = st.button("🔍 Check Alerts Now", use_container_width=True)

    if fetch_alerts_btn:
        with st.spinner(f"Checking IMD-style alerts for {city}…"):
            alert_data = fetch_alerts(city)

        if alert_data:
            alerts_list = alert_data.get("alerts", [])
            summary     = alert_data.get("summary")

            if summary:
                st.markdown(f"""
                <div class="alert-box alert-severe">
                    <div class="alert-title">🚨 Alert Summary</div>
                    {summary}
                </div>""", unsafe_allow_html=True)

            if alerts_list:
                for a in alerts_list:
                    sev = a.get("severity", "Minor")
                    sev_class = {
                        "Extreme":  "alert-extreme",
                        "Severe":   "alert-severe",
                        "Moderate": "alert-moderate",
                        "Minor":    "alert-minor",
                    }.get(sev, "alert-minor")
                    sev_emoji = {"Extreme":"🔴","Severe":"🟠","Moderate":"🟡","Minor":"🟢"}.get(sev,"⚪")
                    st.markdown(f"""
                    <div class="alert-box {sev_class}">
                        <div class="alert-title">{sev_emoji} [{sev}] {a.get('event','Alert')}</div>
                        <div>{a.get('description','No description.')}</div>
                        <div style="margin-top:0.5rem;font-size:0.78rem;color:#94a3b8">
                            {'🕐 ' + a['start'] if a.get('start') else ''} 
                            {'→ ' + a['end'] if a.get('end') else ''}
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-box alert-minor">
                    <div class="alert-title">✅ No Active Alerts</div>
                    No warnings or advisories are currently in effect for this location.
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Backend offline or alerts unavailable. Start the API server to fetch live IMD alerts.")

    # IMD Warning scale reference
    st.markdown('<div class="section-title">📖 IMD Warning Color Code Reference</div>', unsafe_allow_html=True)
    severity_data = [
        ("🟢 Green",  "No Warning",  "Normal weather. No significant weather expected."),
        ("🟡 Yellow", "Watch",       "Severe weather possible. Stay updated."),
        ("🟠 Orange", "Alert",       "Severe weather expected. Be prepared."),
        ("🔴 Red",    "Warning",     "Extremely severe weather. Take action immediately."),
    ]
    cols = st.columns(4)
    for i, (color, level, desc) in enumerate(severity_data):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:left">
                <div style="font-size:1.2rem;margin-bottom:0.3rem">{color}</div>
                <div style="font-weight:700;font-size:0.9rem;margin-bottom:0.3rem">{level}</div>
                <div style="font-size:0.75rem;color:#94a3b8">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — Climate Analytics
# ═════════════════════════════════════════════════════════════════════════════
with tab_climate:
    st.markdown('<div class="section-title">📊 Historical Climate Analysis</div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.82rem;color:#64748b;margin-bottom:1rem">
        Powered by Open-Meteo Historical API (1940–present) with AI-generated trend summaries.
    </div>""", unsafe_allow_html=True)

    cc1, cc2, cc3 = st.columns([2, 1, 1])
    with cc1:
        clim_city = st.text_input("City", value=city, key="clim_city")
    with cc2:
        clim_month = st.selectbox("Month", range(1, 13),
                                   format_func=lambda m: MONTH_NAMES[m-1],
                                   index=datetime.now().month - 2,
                                   key="clim_month")
    with cc3:
        st.write("")
        st.write("")
        analyze_btn = st.button("📈 Analyze", use_container_width=True, key="analyze_btn")

    if analyze_btn:
        with st.spinner(f"Fetching climate data for {clim_city} in {MONTH_NAMES[clim_month-1]}…"):
            clim_data = fetch_climate(clim_city, clim_month)

        if clim_data:
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("🌡️ Avg Temperature",
                          f"{clim_data.get('avg_temp','--')} °C")
            with m2:
                st.metric("💧 Avg Humidity",
                          f"{clim_data.get('avg_humidity','--')} %")
            with m3:
                st.metric("🌧️ Total Rainfall",
                          f"{clim_data.get('avg_rainfall_mm','--')} mm")

            summary = clim_data.get("trend_summary", "")
            if summary:
                st.markdown(f"""
                <div class="alert-box alert-moderate" style="margin-top:1rem">
                    <div class="alert-title">50-Year ERA5 Climate Summary</div>
                    {summary}
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Backend offline. Start the API server to fetch historical climate data from Open-Meteo.")

    # Use-case cards
    st.markdown('<div class="section-title">Operational Sectors</div>', unsafe_allow_html=True)
    use_cases = [
        ("🌾", "Agriculture", "Crop-weather advisories, irrigation scheduling, frost alerts, harvest windows."),
        ("✈️", "Aviation",    "TAF briefings, turbulence, icing, wind shear, SIGMET integration."),
        ("🌊", "Disaster Mgmt","Cyclone tracks, flood inundation mapping, early warning dissemination."),
        ("🏙️", "Smart Cities", "Urban heat islands, AQI alerts, traffic disruption, infrastructure risk."),
        ("⚓", "Marine",       "Wave height, swell, fishing window advisories, port conditions."),
        ("🔬", "Research",     "Climate anomaly detection, trend analysis, El Niño/La Niña impact."),
    ]
    uc_cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(use_cases):
        with uc_cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:left;margin-bottom:0.8rem;min-height:130px">
                <div style="font-size:1.8rem;margin-bottom:0.4rem">{icon}</div>
                <div style="font-weight:700;font-size:0.95rem;margin-bottom:0.4rem;color:#f1f5f9">{title}</div>
                <div style="font-size:0.78rem;color:#94a3b8;line-height:1.5">{desc}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:2rem 0 1rem">
<div style="text-align:center;font-size:0.75rem;color:#475569;padding-bottom:1rem">
    <strong style="color:#64748b">WeatherGPT</strong> — Hackathon Demo &nbsp;·&nbsp;
    AI-Powered Weather Intelligence for India &nbsp;·&nbsp;
    Powered by <span style="color:#3b82f6">Google Gemini</span> · 
    <span style="color:#06b6d4">OpenWeatherMap</span> · 
    <span style="color:#10b981">Open-Meteo</span>
</div>""", unsafe_allow_html=True)