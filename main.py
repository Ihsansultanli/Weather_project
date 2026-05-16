import streamlit as st
import folium
import json
from streamlit_folium import st_folium

st.title("Netherlands Provinces Map")

m = folium.Map(
    location=[52.1326, 5.2913],
    zoom_start=7
)

with open("the-netherlands.geojson", "r", encoding="utf-8") as f:    geojson_data = json.load(f)

# Province layer ekle
folium.GeoJson(
    geojson_data,
    tooltip=folium.GeoJsonTooltip(
        fields=["name"],
        aliases=["Province:"]
    )
).add_to(m)

st_folium(m, width=700, height=500)