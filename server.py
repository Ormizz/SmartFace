#!/usr/bin/env python3
"""
SmartFace FastAPI Server
Ultra-simple API server for voice processing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import wave
import json
import tempfile
import os

# Vosk
from vosk import Model, KaldiRecognizer

# SmartFace components - IMPORTS CORRIGÉS! ✅
from smartface.config import VOSK_MODEL_PATH, SERVER_HOST, SERVER_PORT
from smartface.nlp import NLPProcessor
from smartface.response_handler import ResponseHandler
from smartface.skills.web_search import WebSearchSkill
from smartface.skills.reminder import ReminderSkill
from smartface.skills.smart_home import SmartHomeSkill

# Weather skill
try:
    from smartface.api_keys import OPENWEATHER_API_KEY
    from smartface.skills.weather import WeatherSkill
    weather = WeatherSkill(api_key=OPENWEATHER_API_KEY)
except:
    from smartface.skills.weather import WeatherSkillOffline
    weather = WeatherSkillOffline()

# ============================================================================
# INITIALIZE
# ============================================================================

app = FastAPI(
    title="SmartFace API",
    description="Simple voice assistant API",
    version="1.0.0"
)

print("\n🚀 Loading SmartFace components...")

# Load Vosk
print(f"📦 Loading Vosk model: {VOSK_MODEL_PATH}")
vosk_model = Model(VOSK_MODEL_PATH)
print("✅ Vosk ready")

# Load NLP
print("🧠 Loading NLP...")
nlp = NLPProcessor()
print("✅ NLP ready")

# Initialize components
response_handler = ResponseHandler()
web_search = WebSearchSkill()
reminders = ReminderSkill()
smart_home = SmartHomeSkill()

print("✅ SmartFace Server Ready!\n")

# ============================================================================
# MODELS
# ============================================================================

class TextRequest(BaseModel):
    text: str

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "SmartFace API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Process audio file (WAV)
    Upload WAV file, get transcription + response
    """
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Recognize speech
            text = recognize_speech(tmp_path)
            
            if not text:
                return JSONResponse({
                    "error": "No speech detected",
                    "response": "I didn't catch that."
                }, status_code=400)
            
            # Process query
            result = process_query(text)
            return result
            
        finally:
            os.unlink(tmp_path)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_text")
def process_text(request: TextRequest):
    """
    Process text query directly
    Send text, get intent + response
    """
    try:
        text = request.text.strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="Empty text")
        
        result = process_query(text)
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HELPERS
# ============================================================================

def recognize_speech(wav_path: str) -> str:
    """Recognize speech from WAV file"""
    try:
        wf = wave.open(wav_path, "rb")
        rec = KaldiRecognizer(vosk_model, wf.getframerate())
        
        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text += result.get('text', '') + " "
        
        final = json.loads(rec.FinalResult())
        text += final.get('text', '')
        
        wf.close()
        
        return text.strip()
    
    except Exception as e:
        print(f"❌ Recognition error: {e}")
        return ""

def process_query(text: str) -> dict:
    """Process query and return response"""
    print(f"📝 Query: {text}")
    
    # NLP
    intent, confidence = nlp.classify_intent(text)
    entities = nlp.extract_entities(text, intent)
    
    print(f"💡 Intent: {intent} ({confidence:.2f})")
    
    # Generate response
    response_text = generate_response(intent, entities, text)
    
    return {
        "text": text,
        "intent": intent,
        "confidence": float(confidence),
        "entities": entities,
        "response": response_text
    }

def generate_response(intent: str, entities: dict, text: str) -> str:
    """Generate response based on intent"""
    
    # Simple intents
    if intent in ['greet', 'goodbye', 'how_are_you', 'thank', 
                  'name', 'help', 'joke', 'time', 'date']:
        return response_handler.generate_response(intent, entities)
    
    # Web search
    elif intent == 'web_search' or entities.get('likely_search'):
        query = entities.get('query', text)
        result = web_search.search(query)
        # Truncate if too long
        if len(result) > 300:
            parts = result.split('\n\n')
            return parts[0] if parts else result[:300]
        return result
    
    # Reminders
    elif intent == 'reminder_set':
        reminder = entities.get('reminder_text', '')
        return reminders.add_reminder(reminder) if reminder else "What should I remind you about?"
    
    elif intent == 'reminder_list':
        return reminders.list_reminders()
    
    # Smart home
    elif intent == 'light_on':
        return smart_home.turn_on_light(entities.get('room'))
    
    elif intent == 'light_off':
        return smart_home.turn_off_light(entities.get('room'))
    
    elif intent == 'temperature_set':
        temp = entities.get('number')
        return smart_home.set_temperature(temp) if temp else "What temperature?"
    
    elif intent == 'device_status':
        return smart_home.get_status()
    
    # Weather
    elif intent in ['weather', 'weather_city']:
        return weather.handle(intent, entities, text)
    
    # Unknown
    else:
        return response_handler.generate_response('unknown')

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🚀 SmartFace FastAPI Server 🚀                 ║
║                                                          ║
║  Running on: http://{SERVER_HOST}:{SERVER_PORT}                        ║
║                                                          ║
║  Endpoints:                                              ║
║    GET  /          - Root                                ║
║    GET  /health    - Health check                        ║
║    POST /process_audio - Upload WAV file                 ║
║    POST /process_text  - Send text query                 ║
║                                                          ║
║  Docs: http://localhost:{SERVER_PORT}/docs                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )