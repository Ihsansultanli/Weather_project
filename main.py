import streamlit as st
import folium
import json
import asyncio
import python_weather
from datetime import datetime
import pytz
from streamlit_folium import st_folium


#pagina dingen

st.set_page_config(
    page_title="Weer App Nederland",
    layout="wide"
)

st.title("🇳🇱 Weer App Nederland")
st.info("Selecteer of zoek een provincie ")



#Geojson

@st.cache_data
def load_geojson():
    with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
        return json.load(f)


geojson_data = load_geojson()

# lijt maken van her proventies
province_list = [f["properties"]["name"] for f in geojson_data["features"]]


# weer ophalen en async functies
async def get_weather(city):
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(city)
        return weather


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)


# zijkant menu (sidebar)
st.sidebar.title(" Provincies")

search = st.sidebar.text_input(" Zoek provincie")

# huidige tijd van nederland hier
amsterdam_tz = pytz.timezone("Europe/Amsterdam")
current_time = datetime.now(amsterdam_tz).strftime("%H:%M")

st.sidebar.markdown(f"###  TIjd (NU): `{current_time}`")
st.sidebar.markdown("--------")


# kaart kleur en stijl
def style(feature):
    name = feature["properties"]["name"]
    match = search and search.lower() in name.lower()
    return {
        "fillColor": "orange" if match else "turquoise",
        "color": "black",
        "weight": 2 if match else 1,
        "fillOpacity": 0.6 if match else 0.3,
    }


# map maken met de coordinaten
m = folium.Map(
    location=[52.1326, 5.2913],
    zoom_start=7
)

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


# kijken welke provincie is gekozen (zoeken of klikken)
selected_province = None

if search:
    matched_provinces = [p for p in province_list if search.lower() in p.lower()]
    if matched_provinces:
        selected_province = matched_provinces[0]

if not selected_province and output.get("last_active_drawing"):
    selected_province = output["last_active_drawing"]["properties"]["name"]



# WEATHER INFO DISPLAY (Nederlands)


# dagen afkortingen voor voorspelling
dagen_nl = {0: "MA", 1: "DI", 2: "WO", 3: "DO", 4: "VR", 5: "ZA", 6: "ZO"}

if selected_province:
    try:
        weather = run_async(get_weather(selected_province))
        forecasts = list(weather.daily_forecasts)

        # 1. info laten zien op de sidebar
        st.sidebar.markdown(f"## 📍 {selected_province}")
        st.sidebar.info(f"**Status:** {weather.description}")

        if forecasts:
            st.sidebar.write(" Zonsopkomst: 05:42")
            st.sidebar.write(" Zonsondergang: 21:35")

        # 2. grote metrics op het scherm
        st.subheader(f"📊 Live Weerrapport {selected_province}")

        col1, col2, col3 = st.columns(3)
        col1.metric(" Temperatuur", f"{weather.temperature}°C")
        col2.metric(" Luchtvochtigheid", f"{weather.humidity}%")
        col3.metric(" Windsnelheid", f"{weather.wind_speed} km/h")

        # 3. 5 dagen voorspelling hieronder
        st.markdown("###  3-Daagse Voorspelling")
        cols = st.columns(3)

        for i in range(min(5, len(forecasts))):
            dag = forecasts[i]

            if i == 0:
                dag_naam = "VANDAAG"
            elif i == 1:
                dag_naam = "MORGEN"
            else:
                dag_naam = dagen_nl[dag.date.weekday()]

            with cols[i]:
                st.info(dag_naam)
                st.write(f"Max: **{dag.highest_temperature}°C**")
                st.write(f"Min: **{dag.lowest_temperature}°C**")

    except Exception as e:
        st.sidebar.error("Fout bij het laden van het weer.")
        st.error(f"Foutdetails: {e}")

else:
    st.sidebar.warning("! Zoek een provincie of klik op de kaart om het weer te bekijken.")
