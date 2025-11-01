import os
import platform

# Detect Raspberry Pi
IS_RASPBERRY_PI = os.path.exists('/sys/firmware/devicetree/base/model')

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Vosk model
VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk", "small-en")

# Audio settings (optimized for Pi Zero)
SAMPLE_RATE = 16000
CHUNK_SIZE = 2048  # Smaller chunks for Pi Zero

# Speech recognition (more lenient for slower processing)
SILENCE_THRESHOLD = 60  # Higher = more patient
LISTEN_TIMEOUT = 20  # More time

# TTS settings
TTS_RATE = 140  # Slower for clarity

# NLP settings
INTENT_CONFIDENCE_THRESHOLD = 0.35  # Lower threshold

# Sentence Transformer (use lighter model)
SENTENCE_MODEL = 'paraphrase-MiniLM-L3-v2'  # Smallest model

# Reminders
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders", "reminders.json")

# Smart home
SMART_HOME_DEVICES = {
    "living_room_light": {"type": "light", "state": "off", "brightness": 0},
    "bedroom_light": {"type": "light", "state": "off", "brightness": 0},
    "thermostat": {"type": "thermostat", "state": "off", "temperature": 20},
}

# Memory optimization
ENABLE_VISUAL = False  # Disable visual on headless Pi
ENABLE_PREPROCESSING = False  # Disable audio preprocessing to save CPU