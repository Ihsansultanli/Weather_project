import streamlit as st
import folium
import json
import asyncio
import python_weather
from datetime import datetime
import pytz
from streamlit_folium import st_folium


#pagina config

st.set_page_config(
    page_title="Weer App Nederland",
    layout="wide"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Sayfa arka planı ── */
.stApp {
    background: linear-gradient(135deg, #e8f4fd 0%, #ddeeff 50%, #eaf6f0 100%);
}

/* ── Sidebar ── */
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

/* ── Sidebar selectbox ── */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(126,200,227,0.4) !important;
    border-radius: 10px !important;
    color: #fff !important;
}

/* ── Sidebar info/success/warning kutuları ── */
section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(126,200,227,0.3) !important;
    border-radius: 10px !important;
    color: #7ec8e3 !important;
}

/* ── Metric kutular (sidebar columns) ── */
section[data-testid="stSidebar"] div[data-testid="column"] {
    background: rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 8px 4px;
    border: 1px solid rgba(255,255,255,0.08);
    text-align: center;
}

/* ── Forecast weather-card (ana içerik) ── */
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

/* ── Başlıklar ── */
h2 {
    color: #0f3460 !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em;
}

/* ── Main alan arka plan kartı ── */
div[data-testid="stVerticalBlock"] > div:has(iframe) {
    background: white;
    border-radius: 16px;
    padding: 4px;
    box-shadow: 0 4px 20px rgba(55,138,221,0.1);
}
</style>
""", unsafe_allow_html=True)





# GEOJSON

@st.cache_data
def load_geojson():
    with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

geojson_data = load_geojson()
province_list = [f["properties"]["name"] for f in geojson_data["features"]]



# PROVINCE TO CITY MAPPER


PROVINCE_CITY_MAP = {
    "Noord-Brabant": "Eindhoven",
    "Utrecht": "Utrecht",
    "Noord-Holland": "Amsterdam",
    "Zuid-Holland": "Rotterdam",
    "Gelderland": "Arnhem",
    "Overijssel": "Zwolle",
    "Flevoland": "Almere",
    "Groningen": "Groningen",
    "Friesland": "Leeuwarden",
    "Drenthe": "Assen",
    "Zeeland": "Middelburg",
    "Limburg": "Maastricht"
}



#api van de weer

async def get_weather(city_or_province):
    # Eğer eşleme tablomuzda varsa şehre çevir, yoksa (veya yazım farkı varsa) temizleyip gönder
    search_query = PROVINCE_CITY_MAP.get(city_or_province, city_or_province.replace("-", " "))
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        return await client.get(search_query)


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)



# SIDEBAR

st.sidebar.title("🗺️ Provincies")

selected_province = st.sidebar.selectbox(
    "🔍 Zoek provincie",
    options=province_list,
    index=None,
    placeholder="Typ een provincie..."
)

amsterdam_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(amsterdam_tz)

dagen_nl = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]

st.sidebar.markdown(f"### 🕒 {dagen_nl[now.weekday()]} {now.strftime('%H:%M')}")
st.sidebar.markdown("---")



# gewoon map
def style(feature):
    name = feature["properties"]["name"]
    match = selected_province and selected_province.lower() == name.lower()
    return {
        "fillColor": "orange" if match else "turquoise",
        "color": "black",
        "weight": 2 if match else 1,
        "fillOpacity": 0.6 if match else 0.3,
    }


m = folium.Map(location=[52.2130, 5.2794], zoom_start=7)

folium.GeoJson(
    geojson_data,
    style_function=style,
    highlight_function=lambda f: {
        "fillColor": "yellow",
        "color": "red",
        "weight": 3,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=["name"])
).add_to(m)

output = st_folium(m, height=500, use_container_width=True)

if not selected_province and output.get("last_active_drawing"):
    selected_province = output["last_active_drawing"]["properties"]["name"]



# FORECAST LABELS Onder de map

dagen_kort_nl = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]


# Weer seciton

if selected_province:
    try:
        weather = run_async(get_weather(selected_province))
        forecasts = list(weather.daily_forecasts)


        # SIDEBAR TODAYYY

        st.sidebar.markdown(f"## 📍 {selected_province}")
        st.sidebar.info(weather.description)

        st.sidebar.markdown("## 🌤️ Vandaag weer")

        col1, col2, col3 = st.sidebar.columns(3)

        col1.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:12px;color:gray;">🌡️ Temp</div>
            <div style="font-size:16px;font-weight:600;color:#1f2a44;">{weather.temperature}°C</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:12px;color:gray;">💧 Vocht</div>
            <div style="font-size:16px;font-weight:600;color:#1f2a44;">{weather.humidity}%</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:12px;color:gray;">💨 Wind</div>
            <div style="font-size:16px;font-weight:600;color:#1f2a44;">{weather.wind_speed} km/h</div>
        </div>
        """, unsafe_allow_html=True)

        if forecasts:
            vandaag = forecasts[0]
            st.sidebar.success("VANDAAG")
            st.sidebar.write(f"⬆️ Max: {vandaag.highest_temperature}°C")
            st.sidebar.write(f"⬇️ Min: {vandaag.lowest_temperature}°C")

        
        # MAIN FORECAST
      
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
