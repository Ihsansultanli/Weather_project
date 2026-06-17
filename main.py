import streamlit as st
from datetime import datetime
import pytz

from CSS_Extra import CSS_STYLING, DAGEN_NL
from weer_service import load_geojson
import Visuele_onderdelen as ui

# 1. Pagina & Styling Setup
st.set_page_config(page_title="Weer App Nederland", layout="wide")
st.markdown(CSS_STYLING, unsafe_allow_html=True)

# 2. Data
geojson_data = load_geojson()

# 3. Sidebar Klok
amsterdam_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(amsterdam_tz)
st.sidebar.title("🗺️ Provincies")
st.sidebar.markdown(f"### 🕒 {DAGEN_NL[now.weekday()]} {now.strftime('%H:%M')}")
st.sidebar.markdown("---")

# 4. Render de UI Componenten
selected_province, selected_city = ui.render_sidebar_inputs(geojson_data)
ui.render_map(geojson_data)
ui.render_weather_displays(selected_province, selected_city)