import streamlit as st
import folium
import json
from streamlit_folium import st_folium

st.title("NWeather App")

# Maak de map
m = folium.Map(
    location=[52.1326, 5.2913],
    zoom_start=7
)

#Open goejson
with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Province layer
geojson = folium.GeoJson(
    geojson_data,
    name="Netherlands Provinces",
    style_function=lambda feature: {
        "fillColor": "blue",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.3,
    },
    highlight_function=lambda feature: {
        "fillColor": "orange",
        "color": "red",
        "weight": 3,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["name"],
        aliases=["Province:"]
    )
)

#Map
geojson.add_to(m)

# Streamlit map
output = st_folium(
    m,
    width=700,
    height=500
)

#Output
st.write(output)
