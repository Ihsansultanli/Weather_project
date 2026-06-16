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
#styling voor betere uitzicht
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

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

section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(126,200,227,0.3) !important;
    border-radius: 10px !important;
    color: #7ec8e3 !important;
}

section[data-testid="stSidebar"] div[data-testid="column"] {
    background: rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 8px 4px;
    border: 1px solid rgba(255,255,255,0.08);
    text-align: center;
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

# 3. Data & Provincie mappen (Koppelt de steden aan de juiste provincie)
@st.cache_data
def load_geojson():
    with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

geojson_data = load_geojson()
province_list = [f["properties"]["name"] for f in geojson_data["features"]]

#namen van de provincie
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


#dit maakt de verbinding met internet voor weer
async def get_weather(city):
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        return await client.get(city)



def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)

#titel van het sidebar
st.sidebar.title("🗺️ Provincies")

#hiet kun jij zelf typen of kiezen
selected_province = st.sidebar.selectbox(
    "🔍 Zoek provincie",
    options=province_list,
    index=None,
    placeholder="Typ een provincie..."
)

#Stad kiezen binnen de regio

selected_city = None
if selected_province:
    cities = PROVINCE_CITY_MAP.get(selected_province, [])
    selected_city = st.sidebar.selectbox(
        "🏙️ Kies een stad",
        options=cities,
        index=0
    )

# Pakt de huidige tijd in Nederland en maakt een lijstje voor de Nederlandse dagen.
amsterdam_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(amsterdam_tz)

dagen_nl = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]

# Toont de dag en tijd bijv: 13:35 in de zijbalk en zet er een streep onder.
st.sidebar.markdown(f"### 🕒 {dagen_nl[now.weekday()]} {now.strftime('%H:%M')}")
st.sidebar.markdown("---")


#als je kiest dan zie je de kleur turquaz of oranje
def style(feature):
    name = feature["properties"]["name"]
    match = selected_province and selected_province.lower() == name.lower()
    return {
        "fillColor": "orange" if match else "turquoise",
        "color": "black",
        "weight": 2 if match else 1,
        "fillOpacity": 0.6 if match else 0.3,
    }

# 📍 LANDKAART OPSTARTEN
# Start de kaart op met de coördinaten van het midden van Nederland en zoomt in.
m = folium.Map(location=[52.2130, 5.2794], zoom_start=7)

# 🗺️ PROVINCIEGRENZEN EN HOVER-EFFECT
# Tekent de provincies, maakt ze geel/rood als je eroverheen hovert, en zet de naam erbij.
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

# 🖥️ KAART TONEN IN STREAMLIT

output = st_folium(m, height=500, use_container_width=True)


# Checkt of de gebruiker op een provincie heeft geklikt. Zo ja, dan selecteert de app die.
if not selected_province and output.get("last_active_drawing"):
    selected_province = output["last_active_drawing"]["properties"]["name"]


dagen_kort_nl = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]


if selected_province and selected_city:
    try:
        # Haalt de live weergegevens op via de API en stopt de voorspelling in een lijst.
        weather = run_async(get_weather(selected_city))
        forecasts = list(weather.daily_forecasts)


        st.sidebar.markdown(f"## 📍 {selected_province} — {selected_city}")
        st.sidebar.info(weather.description)

        st.sidebar.markdown("## 🌤️ Vandaag weer")


        # Maakt 3 mini-vakjes naast elkaar voor Temperatuur, Luchtvochtigheid en Windkracht.
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

       #dit is de max en minimaal weer
        if forecasts:
            vandaag = forecasts[0]
            st.sidebar.success("VANDAAG")
            st.sidebar.write(f"⬆️ Max: {vandaag.highest_temperature}°C")
            st.sidebar.write(f"⬇️ Min: {vandaag.lowest_temperature}°C")


        st.markdown("## 📅 Komende dagen")

        # data voor 3 dagen
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

    #
    # als staad niet bestaat of is er geen internet dan krijg je error
    except Exception as e:
        st.sidebar.error("Fout bij het laden van het weer.")
        st.error(f"Foutdetails: {e}")


else:
    st.sidebar.warning("⚠️ Zoek een provincie of klik op de kaart om het weer te bekijken.")
