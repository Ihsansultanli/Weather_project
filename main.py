import streamlit as st
import folium
import json
import asyncio
import python_weather
from datetime import datetime
import pytz
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Weer App Nederland",
    layout="wide"
)

# 1. Styling voor betere uitzicht (Geüpdatet voor mooiere sidebar-weergave)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #e8f4fd 0%, #ddeeff 50%, #eaf6f0 100%);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f3460 0%, #16213e 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #7ec8e3 !important;
    font-weight: 700;
    letter-spacing: 0.03em;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.85) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(126,200,227,0.4) !important;
    border-radius: 10px !important;
    color: #fff !important;
}

/* Grote custom kaart voor het huidige weer-status */
.sidebar-weather-status {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(126, 200, 227, 0.4);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    color: #ffffff !important;
    margin-bottom: 20px;
    box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
}

/* Grotere en duidelijkere statistieken onderin de sidebar */
.sidebar-stat-card {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px 5px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
}
.sidebar-stat-label {
    font-size: 13px;
    color: #7ec8e3 !important;
    font-weight: 600;
    margin-bottom: 4px;
}
.sidebar-stat-value {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff !important;
}

.weather-card {
    background: #ffffff;
    border-radius: 16px;
    border: none;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(55,138,221,0.12);
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.weather-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #378ADD, #7ec8e3);
    border-radius: 16px 16px 0 0;
}
.weather-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 36px rgba(55,138,221,0.22);
}
.weather-card h3 {
    font-size: 11px;
    font-weight: 700;
    color: #7ec8e3;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
    text-transform: uppercase;
}
.weather-card p {
    font-size: 16px;
    font-weight: 600;
    color: #0f3460;
    margin: 4px 0;
}

h2 {
    color: #0f3460 !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em;
}

div[data-testid="stVerticalBlock"] > div:has(iframe) {
    background: white;
    border-radius: 16px;
    padding: 4px;
    box-shadow: 0 4px 20px rgba(55,138,221,0.1);
}
</style>
""", unsafe_allow_html=True)

# 2. Nederlandse vertalingen voor weersomstandigheden
WEATHER_TRANSLATIONS = {
    "Patchy rain nearby": "Lokale regenbuien in de buurt",
    "Patchy rain possible": "Kans op lokale regen",
    "Sunny": "Heerlijk zonnig",
    "Partly cloudy": "Licht bewolkt",
    "Cloudy": "Bewolkt",
    "Overcast": "Geheel bewolkt",
    "Clear": "Helder",
    "Mist": "Mistig",
    "Fog": "Dichte mist",
    "Light rain": "Lichte regen",
    "Moderate rain": "Matige regen",
    "Heavy rain": "Zware regenval",
    "Patchy snow nearby": "Kans op natte sneeuw",
    "Thundery outbreaks nearby": "Onweer in de buurt",
    "Light drizzle": "Lichte motregen",
    "Light rain shower": "Lichte regenbui"
}


@st.cache_data
def load_geojson():
    with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
        return json.load(f)


geojson_data = load_geojson()
province_list = sorted([f["properties"]["name"] for f in geojson_data["features"]])

PROVINCE_CITY_MAP = {
    "Noord-Brabant": ["Eindhoven", "Tilburg", "Breda", "Den Bosch", "Helmond", "Oss"],
    "Utrecht": ["Utrecht", "Amersfoort", "Veenendaal", "Nieuwegein", "Zeist"],
    "Noord-Holland": ["Amsterdam", "Haarlem", "Alkmaar", "Zaandam", "Hoorn", "Purmerend"],
    "Zuid-Holland": ["Rotterdam", "Den Haag", "Leiden", "Dordrecht", "Delft", "Zoetermeer"],
    "Gelderland": ["Arnhem", "Nijmegen", "Apeldoorn", "Ede", "Doetinchem", "Tiel"],
    "Overijssel": ["Zwolle", "Enschede", "Almelo", "Deventer", "Hengelo"],
    "Flevoland": ["Almere", "Lelystad", "Dronten", "Urk", "Emmeloord"],
    "Groningen": ["Groningen", "Veendam", "Stadskanaal", "Delfzijl", "Hoogezand"],
    "Friesland": ["Leeuwarden", "Drachten", "Sneek", "Heerenveen", "Franeker"],
    "Drenthe": ["Assen", "Emmen", "Meppel", "Hoogeveen", "Coevorden"],
    "Zeeland": ["Middelburg", "Vlissingen", "Goes", "Terneuzen", "Hulst"],
    "Limburg": ["Maastricht", "Venlo", "Roermond", "Sittard", "Weert", "Heerlen"]
}


async def get_weather(city):
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        return await client.get(city)


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)


if "selected_province" not in st.session_state:
    st.session_state.selected_province = None


def on_selectbox_change():
    st.session_state.selected_province = st.session_state.province_box


st.sidebar.title("🗺️ Provincies")

amsterdam_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(amsterdam_tz)
dagen_nl = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
st.sidebar.markdown(f"### 🕒 {dagen_nl[now.weekday()]} {now.strftime('%H:%M')}")
st.sidebar.markdown("---")

default_index = None
if st.session_state.selected_province in province_list:
    default_index = province_list.index(st.session_state.selected_province)

selected_province = st.sidebar.selectbox(
    "🔍 Zoek provincie",
    options=province_list,
    index=default_index,
    placeholder="Typ een provincie...",
    key="province_box",
    on_change=on_selectbox_change
)

if selected_province:
    st.session_state.selected_province = selected_province

selected_city = None
if st.session_state.selected_province:
    cities = PROVINCE_CITY_MAP.get(st.session_state.selected_province, [])
    selected_city = st.sidebar.selectbox(
        "🏙️ Kies een stad",
        options=cities,
        index=0
    )


def style_function(feature):
    name = feature["properties"]["name"]
    match = st.session_state.selected_province and st.session_state.selected_province.lower() == name.lower()
    return {
        "fillColor": "orange" if match else "turquoise",
        "color": "black",
        "weight": 2 if match else 1,
        "fillOpacity": 0.6 if match else 0.3,
    }


m = folium.Map(location=[52.2130, 5.2794], zoom_start=7)

folium.GeoJson(
    geojson_data,
    style_function=style_function,
    highlight_function=lambda f: {
        "fillColor": "yellow",
        "color": "red",
        "weight": 3,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=["name"])
).add_to(m)

output = st_folium(m, height=500, use_container_width=True)

if output and output.get("last_active_drawing"):
    clicked_province = output["last_active_drawing"]["properties"]["name"]
    if clicked_province != st.session_state.selected_province:
        st.session_state.selected_province = clicked_province
        st.rerun()

dagen_kort_nl = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]

if st.session_state.selected_province and selected_city:
    try:
        weather = run_async(get_weather(selected_city))
        forecasts = list(weather.daily_forecasts)

        st.sidebar.markdown(f"## 📍 {st.session_state.selected_province} — {selected_city}")

        # Vertaal de Engelse omschrijving naar het Nederlands
        eng_desc = weather.description
        nl_desc = WEATHER_TRANSLATIONS.get(eng_desc, eng_desc)

        # Prachtige grote weergave van de huidige status
        st.sidebar.markdown(f'<div class="sidebar-weather-status">⛅ {nl_desc}</div>', unsafe_allow_html=True)

        st.sidebar.markdown("## 🌤️ Vandaag weer")

        # Nieuwe grotere kolommen in de sidebar
        col1, col2, col3 = st.sidebar.columns(3)
        col1.markdown(f"""
        <div class="sidebar-stat-card">
            <div class="sidebar-stat-label">🌡️ Temp</div>
            <div class="sidebar-stat-value">{weather.temperature}°C</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="sidebar-stat-card">
            <div class="sidebar-stat-label">💧 Vocht</div>
            <div class="sidebar-stat-value">{weather.humidity}%</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="sidebar-stat-card">
            <div class="sidebar-stat-label">💨 Wind</div>
            <div class="sidebar-stat-value">{weather.wind_speed} <span style="font-size:11px;">km/h</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        if forecasts:
            vandaag = forecasts[0]
            st.sidebar.success(f"📈 Max: {vandaag.highest_temperature}°C  |  📉 Min: {vandaag.lowest_temperature}°C")

        st.markdown("## 📅 Komende dagen")
        future = forecasts[1:4]
        cols = st.columns(len(future))

        for i, dag in enumerate(future):
            dag_naam = "MORGEN" if i == 0 else dagen_kort_nl[dag.date.weekday()]
            with cols[i]:
                st.markdown(f"""
                <div class="weather-card">
                    <h3>{dag_naam}</h3>
                    <p>🌡️ Max: <b>{dag.highest_temperature}°C</b></p>
                    <p>❄️ Min: <b>{dag.lowest_temperature}°C</b></p>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.sidebar.error("Fout bij het laden van het weer.")
        st.error(f"Foutdetails: {e}")
else:
    st.sidebar.warning("⚠️ Zoek een provincie of klik op de kaart om het weer te bekijken.")