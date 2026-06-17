import json
import asyncio
import streamlit as st
import python_weather

@st.cache_data
def load_geojson():
    with open("the-netherlands.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

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