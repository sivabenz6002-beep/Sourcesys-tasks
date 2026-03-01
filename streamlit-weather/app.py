import streamlit as st
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Advanced Weather App", layout="wide")

# -----------------------------
# Animated Gradient + Modern UI
# -----------------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(-45deg, #1e3c72, #2a5298, #0f2027, #203a43);
            background-size: 400% 400%;
            animation: gradient 12s ease infinite;
            color: white;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .block-container {
            background: rgba(255, 255, 255, 0.08);
            padding: 2rem;
            border-radius: 20px;
            backdrop-filter: blur(15px);
        }

        .stButton>button {
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            color: white;
            border-radius: 12px;
            height: 45px;
            width: 150px;
            font-weight: bold;
            border: none;
        }

        .stTextInput>div>div>input {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Advanced Weather Dashboard")

# -----------------------------
# Auto Detect Location
# -----------------------------
def get_location():
    try:
        res = requests.get("http://ip-api.com/json/")
        data = res.json()
        return data["city"]
    except:
        return None

auto_city = get_location()
city = st.text_input("Enter City Name", value=auto_city if auto_city else "")

# -----------------------------
# Fetch Weather
# -----------------------------
if st.button("Get Weather"):

    if not api_key:
        st.error("API key not found! Check your .env file.")
        st.stop()

    if city:

        # Current Weather API
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
        response = requests.get(current_url)
        data = response.json()

        if data["cod"] != 200:
            st.error("City not found!")
            st.stop()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📍 {data['name']}")
            st.metric("🌡 Temperature (°C)", data['main']['temp'])
            st.write(f"💧 Humidity: {data['main']['humidity']}%")
            st.write(f"🌬 Wind Speed: {data['wind']['speed']} m/s")

        with col2:
            icon = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
            st.image(icon_url)
            st.write(f"🌥 {data['weather'][0]['description']}")

        # Weather Condition Indicator
        condition = data['weather'][0]['main'].lower()
        if "cloud" in condition:
            st.info("☁ Cloudy Weather")
        elif "rain" in condition:
            st.warning("🌧 Rainy Weather")
        elif "clear" in condition:
            st.success("☀ Clear Sky")
        else:
            st.info("🌤 Weather Update")

        # -----------------------------
        # 5 Day Forecast
        # -----------------------------
        st.subheader("📅 5-Day Forecast")

        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        forecast_list = forecast_data["list"]

        dates = []
        temps = []

        for item in forecast_list:
            if "12:00:00" in item["dt_txt"]:
                dates.append(item["dt_txt"])
                temps.append(item["main"]["temp"])

        forecast_df = pd.DataFrame({
            "Date": dates,
            "Temperature (°C)": temps
        })

        st.dataframe(forecast_df, use_container_width=True)

        # -----------------------------
        # Temperature Chart
        # -----------------------------
        st.subheader("📈 Temperature Trend")

        plt.figure()
        plt.plot(forecast_df["Date"], forecast_df["Temperature (°C)"])
        plt.xticks(rotation=45)
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.tight_layout()

        st.pyplot(plt)

    else:
        st.warning("Please enter a city name.")