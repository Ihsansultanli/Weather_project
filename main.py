import streamlit as st
import folium
import json
import requests
from streamlit_folium import st_folium

st.set_page_config(page_title="Netherlands Weather App", layout="wide")
st.title("🇳🇱 Netherlands Weather App")

@st.cache_data
def load_geojson():
    with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

geojson_data = load_geojson()

province_names = sorted([
    feature["properties"]["name"]
    for feature in geojson_data["features"]
])

# ─Sidebar
st.sidebar.title("🗺️ Provincies")
search_province = st.sidebar.text_input("🔍 Zoek provincie", placeholder="bijv. Utrecht")

filtered_provinces = [
    p for p in province_names
    if search_province.lower() in p.lower()
]

if search_province:
    st.sidebar.markdown(f"**{len(filtered_provinces)} resultaat(en):**")
    for p in filtered_provinces:
        st.sidebar.markdown(f"- {p}")

# map
def get_style(feature):
    name = feature["properties"]["name"]
    is_match = search_province and search_province.lower() in name.lower()
    return {
        "fillColor": "orange" if is_match else "turquoise",
        "color": "black",
        "weight": 2 if is_match else 1,
        "fillOpacity": 0.6 if is_match else 0.3,
    }

m = folium.Map(location=[52.1326, 5.2913], zoom_start=7)

folium.GeoJson(
    geojson_data,
    name="Netherlands Provinces",
    style_function=get_style,
    highlight_function=lambda feature: {
        "fillColor": "yellow",
        "color": "red",
        "weight": 3,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["name"],
        aliases=["Provincie:"]
    )
).add_to(m)

output = st_folium(m, use_container_width=True, height=550)

# ─Geselecteerde provincie
if output.get("last_active_drawing"):
    province = output["last_active_drawing"]["properties"]["name"]
    st.subheader(f"📍 Geselecteerde provincie: {province}")
    st.info("Hier kun je straks het weer voor deze provincie tonen.")
