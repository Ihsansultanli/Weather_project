# Visuele_onderdelen.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from CSS_Extra import PROVINCE_CITY_MAP, WEATHER_TRANSLATIONS, DAGEN_NL
from weer_service import get_weather, run_async


def render_sidebar_inputs(geojson_data):
    """Regelt de selectie van provincie en stad in de sidebar."""
    province_list = sorted([f["properties"]["name"] for f in geojson_data["features"]])

    if "selected_province" not in st.session_state:
        st.session_state.selected_province = None

    default_index = None
    if st.session_state.selected_province in province_list:
        default_index = province_list.index(st.session_state.selected_province)

    selected_province = st.sidebar.selectbox(
        "🔍 Zoek provincie",
        options=province_list,
        index=default_index,
        placeholder="Typ een provincie...",
        key="province_box",
        on_change=lambda: st.session_state.update({"selected_province": st.session_state.province_box})
    )

    if selected_province:
        st.session_state.selected_province = selected_province

    selected_city = None
    if st.session_state.selected_province:
        cities = PROVINCE_CITY_MAP.get(st.session_state.selected_province, [])
        selected_city = st.sidebar.selectbox("🏙️ Kies een stad", options=cities, index=0)

    return st.session_state.selected_province, selected_city


def render_map(geojson_data):
    """Tekent de interactieve kaart en registreert kliks."""

    def style_function(feature):
        name = feature["properties"]["name"]
        match = st.session_state.get("selected_province") and st.session_state[
            "selected_province"].lower() == name.lower()
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
        highlight_function=lambda f: {"fillColor": "yellow", "color": "red", "weight": 3, "fillOpacity": 0.7},
        tooltip=folium.GeoJsonTooltip(fields=["name"])
    ).add_to(m)

    output = st_folium(m, height=500, use_container_width=True)

    if output and output.get("last_active_drawing"):
        clicked_province = output["last_active_drawing"]["properties"]["name"]
        if clicked_province != st.session_state.get("selected_province"):
            st.session_state.selected_province = clicked_province
            st.rerun()


def render_weather_displays(selected_province, selected_city):
    """Toont het huidige weer in de sidebar en de voorspelling op het scherm."""
    if not selected_province or not selected_city:
        st.sidebar.warning("⚠️ Zoek een provincie of klik op de kaart om het weer te bekijken.")
        return

    try:
        weather = run_async(get_weather(selected_city))
        forecasts = list(weather.daily_forecasts)

        # Sidebar Live Status
        st.sidebar.markdown(f"## 📍 {selected_province} — {selected_city}")
        nl_desc = WEATHER_TRANSLATIONS.get(weather.description, weather.description)
        st.sidebar.markdown(f'<div class="sidebar-weather-status">⛅ {nl_desc}</div>', unsafe_allow_html=True)

        # Sidebar Statisteken
        st.sidebar.markdown("## 🌤️ Vandaag weer")
        col1, col2, col3 = st.sidebar.columns(3)
        col1.markdown(
            f'<div class="sidebar-stat-card"><div class="sidebar-stat-label">🌡️ Temp</div><div class="sidebar-stat-value">{weather.temperature}°C</div></div>',
            unsafe_allow_html=True)
        col2.markdown(
            f'<div class="sidebar-stat-card"><div class="sidebar-stat-label">💧 Vocht</div><div class="sidebar-stat-value">{weather.humidity}%</div></div>',
            unsafe_allow_html=True)
        col3.markdown(
            f'<div class="sidebar-stat-card"><div class="sidebar-stat-label">💨 Wind</div><div class="sidebar-stat-value">{weather.wind_speed} <span style="font-size:11px;">km/h</span></div></div>',
            unsafe_allow_html=True)

        if forecasts:
            st.sidebar.markdown("<br>", unsafe_allow_html=True)
            st.sidebar.success(
                f"📈 Max: {forecasts[0].highest_temperature}°C  |  📉 Min: {forecasts[0].lowest_temperature}°C")

        # Hoofdscherm Kaarten (Komende dagen)
        st.markdown("## 📅 Komende dagen")
        future = forecasts[1:4]
        cols = st.columns(len(future))

        for i, dag in enumerate(future):
            dag_naam = "MORGEN" if i == 0 else DAGEN_NL[dag.date.weekday()].upper()
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