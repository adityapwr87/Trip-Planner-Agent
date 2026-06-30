import os
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH, override=True)


GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
MAKCORPS_API_KEY = os.getenv("MAKCORPS_API_KEY")
RAPIDAPI_BOOKING_KEY = os.getenv("RAPIDAPI_BOOKING_KEY")
