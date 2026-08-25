import requests
import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Live Weather App",
    page_icon="🌤️",
    layout="wide"
)

# --------------------------------------------------
# API URLs
# --------------------------------------------------

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# --------------------------------------------------
# Find city coordinates
# --------------------------------------------------

@st.cache_data(ttl=3600)
def find_city(city):
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    return data["results"][0]


# --------------------------------------------------
# Get current weather
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_weather(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),
        "timezone": "auto"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# Weather description
# --------------------------------------------------

def weather_description(code):

    descriptions = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Fog",
        48: "🌫️ Depositing rime fog",
        51: "🌦️ Light drizzle",
        53: "🌦️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        71: "🌨️ Slight snow",
        73: "🌨️ Moderate snow",
        75: "❄️ Heavy snow",
        80: "🌦️ Rain showers",
        81: "🌧️ Moderate rain showers",
        82: "⛈️ Heavy rain showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with hail",
        99: "⛈️ Thunderstorm with heavy hail"
    }

    return descriptions.get(code, "🌤️ Unknown weather")


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🌤️ Live Weather App")

st.write(
    "Check the current weather of any city using "
    "the free Open-Meteo weather API."
)

st.divider()


# --------------------------------------------------
# City input
# --------------------------------------------------

city = st.text_input(
    "🏙️ Enter City Name",
    value="Delhi",
    placeholder="Example: Delhi, Mumbai, London"
)


# --------------------------------------------------
# Get weather button
# --------------------------------------------------

if st.button("🔍 Get Weather", type="primary"):

    if not city.strip():
        st.warning("Please enter a city name.")
        st.stop()

    try:

        with st.spinner("Getting live weather..."):

            # Find city
            location = find_city(city.strip())

            if location is None:
                st.error(
                    "City not found. Please check the spelling "
                    "and try again."
                )
                st.stop()

            # Get coordinates
            latitude = location["latitude"]
            longitude = location["longitude"]

            # Get weather
            weather = get_weather(
                latitude,
                longitude
            )

        # --------------------------------------------------
        # Location information
        # --------------------------------------------------

        city_name = location["name"]
        country = location.get("country", "")
        admin = location.get("admin1", "")

        st.subheader(
            f"📍 {city_name}, {admin}, {country}"
        )

        # --------------------------------------------------
        # Current weather
        # --------------------------------------------------

        current = weather["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        feels_like = current["apparent_temperature"]
        wind_speed = current["wind_speed_10m"]
        wind_direction = current["wind_direction_10m"]
        weather_code = current["weather_code"]

        description = weather_description(weather_code)

        st.write(f"### {description}")

        # --------------------------------------------------
        # Weather metrics
        # --------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🌡️ Temperature",
                f"{temperature} °C"
            )

        with col2:
            st.metric(
                "🤗 Feels Like",
                f"{feels_like} °C"
            )

        with col3:
            st.metric(
                "💧 Humidity",
                f"{humidity}%"
            )

        with col4:
            st.metric(
                "💨 Wind",
                f"{wind_speed} km/h"
            )

        # --------------------------------------------------
        # Extra information
        # --------------------------------------------------

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"🧭 Wind Direction: "
                f"{wind_direction}°"
            )

        with col2:
            st.info(
                f"🕒 Timezone: "
                f"{weather['timezone']}"
            )

        # --------------------------------------------------
        # API response
        # --------------------------------------------------

        with st.expander("📦 Show API Response"):
            st.json(weather)

    except requests.exceptions.Timeout:

        st.error(
            "The weather service took too long to respond."
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Network error: {error}"
        )

    except Exception as error:

        st.error(
            f"Something went wrong: {error}"
        )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Weather data provided by Open-Meteo. "
    "This app uses the Open-Meteo Weather and Geocoding APIs."
)
