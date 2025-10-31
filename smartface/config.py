import os
from dotenv import load_dotenv

# Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Charger les variables d'environnement
load_dotenv()

# API Configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Mohali')
DEFAULT_UNITS = os.getenv('DEFAULT_UNITS', 'metric')
LANGUAGE = os.getenv('LANGUAGE', 'en')

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Vosk model
VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk", "small-en")

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 8192

# Speech recognition
SILENCE_THRESHOLD = 50  # Augmenté de 30 à 50 (plus de patience)
LISTEN_TIMEOUT = 15  # Augmenté de 10 à 15 secondes

# TTS settings
TTS_RATE = 175  # Augmenté pour voix plus naturelle

# NLP settings
INTENT_CONFIDENCE_THRESHOLD = 0.4

# Reminders
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders", "reminders.json")

# Smart home simulation
SMART_HOME_DEVICES = {
    "living_room_light": {"type": "light", "state": "off", "brightness": 0},
    "bedroom_light": {"type": "light", "state": "off", "brightness": 0},
    "thermostat": {"type": "thermostat", "state": "off", "temperature": 20},
    "garage_door": {"type": "door", "state": "closed"},
}

