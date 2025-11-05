"""
SmartFace Configuration - Simple Version
"""

import os

# Disable warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ============================================================================
# PATHS
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Vosk model
VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk", "small-en")

# Reminders
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders", "reminders.json")

# ============================================================================
# SERVER
# ============================================================================

SERVER_HOST = "192.168.1.72"
SERVER_PORT = 8000

# Change this to your server IP!
DEFAULT_SERVER_IP = "192.168.1.100"
SERVER_URL = f"http://{DEFAULT_SERVER_IP}:{SERVER_PORT}"

# ============================================================================
# AUDIO
# ============================================================================

SAMPLE_RATE = 16000
CHUNK_SIZE = 8192

# Voice detection
SILENCE_THRESHOLD = 50
ENERGY_THRESHOLD = 500
LISTEN_TIMEOUT = 15

# ============================================================================
# TTS (Client)
# ============================================================================

TTS_RATE = 175
TTS_VOLUME = 100

# ============================================================================
# NLP (Server)
# ============================================================================

INTENT_CONFIDENCE_THRESHOLD = 0.4

# ============================================================================
# SMART HOME
# ============================================================================

SMART_HOME_DEVICES = {
    "living_room_light": {"type": "light", "state": "off", "brightness": 0},
    "bedroom_light": {"type": "light", "state": "off", "brightness": 0},
    "thermostat": {"type": "thermostat", "state": "off", "temperature": 20},
    "garage_door": {"type": "door", "state": "closed"},
}

# ============================================================================
# WEATHER (Optional)
# ============================================================================

OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"
DEFAULT_WEATHER_CITY = "London"