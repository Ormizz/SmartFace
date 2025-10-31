# 🤖 SmartFace Voice Assistant

A fully functional offline voice assistant built with Python, featuring speech recognition, natural language understanding, and multiple skills.

## ✨ Features

- 🎤 **Offline Speech Recognition** (Vosk)
- 🔊 **Natural Text-to-Speech** (macOS native)
- 🧠 **Intent Classification** (Sentence Transformers)
- 🌐 **Web Search** (Wikipedia)
- 📅 **Reminders Management**
- 🏠 **Smart Home Control** (Simulated)
- 💬 **Natural Conversations**

## 🚀 Installation

### Prerequisites
- Python 3.9+
- macOS (for native TTS)

### Setup
```bash
# Clone repository
cd ~/Documents/SCHOOL/MINOR\ PROJECT/SmartFace

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyobjc-core==9.2 pyobjc-framework-Cocoa==9.2

# Download Vosk model
cd models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 small-en
cd ../..
```

## 🎮 Usage
```bash
# Run the assistant
python3 run.py

# Or directly
python3 -m smartface.main
```

## 🗣️ Example Commands

### Basic Conversation
- "hello"
- "how are you"
- "what time is it"
- "tell me a joke"
- "thank you"

### Web Search
- "who is Barack Obama"
- "what is artificial intelligence"
- "search for Python programming"

### Reminders
- "remind me to buy milk"
- "list my reminders"

### Smart Home
- "turn on the living room light"
- "turn off the bedroom light"
- "set temperature to 22"
- "device status"

### Exit
- "goodbye"
- "exit"
- "quit"

## 📁 Project Structure
```
SmartFace/
├── smartface/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── stt.py               # Speech-to-Text
│   ├── tts.py               # Text-to-Speech
│   ├── nlp.py               # NLP & Intent Classification
│   ├── response_handler.py  # Response generation
│   └── skills/
│       ├── web_search.py    # Web search skill
│       ├── reminder.py      # Reminder skill
│       └── smart_home.py    # Smart home skill
├── models/vosk/small-en/    # Vosk speech model
├── data/reminders/          # Reminder storage
├── requirements.txt
└── run.py                   # Launcher
```

## ⚙️ Configuration

Edit `smartface/config.py`:
```python
# Speech recognition
SILENCE_THRESHOLD = 50      # Adjust mic sensitivity
LISTEN_TIMEOUT = 15         # Max listen time

# TTS settings
TTS_RATE = 175             # Speech speed (WPM)

# NLP
INTENT_CONFIDENCE_THRESHOLD = 0.4  # Intent confidence
```

## 🔧 Troubleshooting

### Microphone cuts off too quickly
Increase `SILENCE_THRESHOLD` in `config.py` to 70-80

### Voice too fast/slow
Adjust `TTS_RATE` (150-200 recommended)

### Speech not recognized
- Speak clearly and not too fast
- Check microphone permissions in System Preferences
- Ensure environment is not too noisy

## 📊 Technologies Used

- **Vosk** - Offline speech recognition
- **PyAudio** - Audio I/O
- **Sentence Transformers** - NLP embeddings
- **Wikipedia API** - Knowledge retrieval
- **macOS `say`** - Text-to-speech

## 🎯 Future Enhancements

- [ ] Time-based reminders
- [ ] Real smart home integration (HomeKit, etc.)
- [ ] Multiple language support
- [ ] Voice wake word detection
- [ ] Conversation history
- [ ] Custom skills API

## 👨‍💻 Author

Minor Project - School Year 2025

## 📝 License

Educational project - Feel free to use and modify!# SmartFace
