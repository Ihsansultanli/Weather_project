CSS_STYLING = """
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
}

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
"""

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

# Uitgebreide Nederlandse vertalingen
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

DAGEN_NL = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]