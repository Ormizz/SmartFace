from smartface.stt import SpeechToText
from smartface.tts import TextToSpeech
from smartface.nlp import NLPProcessor
from smartface.response_handler import ResponseHandler
from smartface.skills.web_search import WebSearchSkill
from smartface.skills.reminder import ReminderSkill
from smartface.skills.smart_home import SmartHomeSkill
from smartface.skills.weather import WeatherSkill, WeatherSkillOffline
import time
import os
import platform

# Detect if on Raspberry Pi
IS_RPI = os.path.exists('/sys/firmware/devicetree/base/model')

if IS_RPI:
    # Use Pi-specific config
    from smartface.config_rpi import *
else:
    from smartface.config import *
    
# Import API keys if available
try:
    from smartface.api_keys import OPENWEATHER_API_KEY, DEFAULT_WEATHER_CITY
except ImportError:
    OPENWEATHER_API_KEY = None
    DEFAULT_WEATHER_CITY = "London"


class SmartFace:
    """
    Main SmartFace Voice Assistant
    """
    
    def __init__(self):
        print("\n" + "="*60)
        print("🤖 SmartFace Voice Assistant")
        print("="*60 + "\n")
        
        # Initialize components
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.nlp = NLPProcessor()
        self.response_handler = ResponseHandler()
        
        # Initialize skills
        self.web_search = WebSearchSkill()
        self.reminders = ReminderSkill()
        self.smart_home = SmartHomeSkill()
        
        # Initialize weather skill
        if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "a42d24d326db9153a9ebebdaab56d41b":
            self.weather = WeatherSkill(api_key=OPENWEATHER_API_KEY)
            self.weather.set_default_city(DEFAULT_WEATHER_CITY)
        else:
            print("⚠️  No OpenWeather API key found, using offline weather")
            self.weather = WeatherSkillOffline()
        
        # Track conversation state
        self.running = False
        self.conversation_count = 0
        
        print("\n" + "="*60)
        print("✅ SmartFace is ready!")
        print("="*60 + "\n")
    
    def start(self):
        """Start the voice assistant"""
        self.running = True
        
        # Welcome message
        welcome = "Hello! I'm SmartFace, your voice assistant. How can I help you today?"
        print(f"🤖 {welcome}")
        self.tts.speak(welcome)
        time.sleep(0.5)
        
        try:
            self._conversation_loop()
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
            self._shutdown()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self._shutdown()
    
    def _conversation_loop(self):
        """Main conversation loop"""
        while self.running:
            self.conversation_count += 1
            print(f"\n{'─'*60}")
            print(f"Exchange #{self.conversation_count}")
            print('─'*60)
            
            # Listen for user input
            user_text = self.stt.listen()
            
            # Handle empty input
            if not user_text:
                response = "I didn't catch that. Please try again."
                print(f"🤖 {response}")
                self.tts.speak(response)
                time.sleep(0.5)
                continue
            
            # Process input
            response = self._process_input(user_text)
            
            # Speak response
            if response:
                print(f"🤖 {response}")
                self.tts.speak(response)
                time.sleep(0.5)
    
    def _process_input(self, text):
        """Process user input and generate response"""
        print(f"\n📝 Processing: \"{text}\"")
        
        # Classify intent
        intent, confidence = self.nlp.classify_intent(text)
        print(f"💡 Intent: {intent} (confidence: {confidence:.2f})")
        
        # Extract entities
        entities = self.nlp.extract_entities(text, intent)
        if entities:
            print(f"🔍 Entities: {entities}")
        
        # Check for exit commands
        if intent == 'goodbye' or text.lower() in ['exit', 'quit', 'stop']:
            farewell = self.response_handler.generate_response('goodbye')
            print(f"🤖 {farewell}")
            self.tts.speak(farewell)
            time.sleep(1)
            self.running = False
            return None
        
        # If unknown intent but looks like a search query, treat as web search
        if intent == 'unknown' and entities.get('likely_search'):
            print("🔍 Detected question pattern - treating as web search")
            intent = 'web_search'
            confidence = 0.7
        
        # Route to appropriate handler based on intent
        if intent in ['greet', 'goodbye', 'how_are_you', 'thank', 'name', 
                      'help', 'joke', 'time', 'date']:
            response = self.response_handler.generate_response(intent, entities, confidence)
        
        elif intent == 'web_search':
            response = self._handle_web_search(entities)
        
        elif intent in ['reminder_set', 'reminder_list']:
            response = self._handle_reminder(intent, entities, text)
        
        elif intent in ['light_on', 'light_off', 'temperature_set', 'device_status']:
            response = self._handle_smart_home(intent, entities, text)
        
        elif intent in ['weather', 'weather_city']:
            response = self._handle_weather(entities, text)
        
        else:
            # Unknown intent - try to be helpful
            if entities.get('query'):
                response = f"I'm not sure what you're asking, but I can search for information. Would you like me to search for '{entities['query']}'?"
            else:
                response = self.response_handler.generate_response('unknown')
        
        return response
    
    def _handle_web_search(self, entities):
        """Handle web search requests"""
        query = entities.get('query', '').strip()
        
        if not query:
            return "What would you like me to search for?"
        
        print(f"🌐 Performing web search for: {query}")
        result = self.web_search.search(query)
        
        # Summarize if too long
        if len(result) > 300:
            parts = result.split('\n\n')
            if len(parts) > 1:
                return parts[0]
            else:
                return result[:300] + "... Would you like to know more?"
        
        return result
    
    def _handle_reminder(self, intent, entities, text):
        """Handle reminder requests"""
        if intent == 'reminder_set':
            reminder_text = entities.get('reminder_text', '').strip()
            
            if not reminder_text:
                return "What would you like me to remind you about?"
            
            return self.reminders.add_reminder(reminder_text)
        
        elif intent == 'reminder_list':
            return self.reminders.list_reminders()
        
        return "I'm not sure what you want to do with reminders."
    
    def _handle_smart_home(self, intent, entities, text):
        """Handle smart home control"""
        room = entities.get('room')
        number = entities.get('number')
        
        if intent == 'light_on':
            return self.smart_home.turn_on_light(room)
        
        elif intent == 'light_off':
            return self.smart_home.turn_off_light(room)
        
        elif intent == 'temperature_set':
            if number:
                return self.smart_home.set_temperature(number)
            else:
                return "What temperature would you like to set?"
        
        elif intent == 'device_status':
            return self.smart_home.get_status()
        
        return "I'm not sure what you want to do with your devices."
    
    def _handle_weather(self, entities, text):
        """Handle weather requests"""
        print(f"🌤️ Getting weather information...")
        return self.weather.handle('weather', entities, text)
    
    def _shutdown(self):
        """Clean shutdown"""
        print("\n🔧 Shutting down SmartFace...")
        
        if hasattr(self, 'stt'):
            self.stt.close()
        
        print(f"📊 Total exchanges: {self.conversation_count}")
        print("✅ Goodbye!\n")


def main():
    """Main entry point"""
    assistant = SmartFace()
    assistant.start()


if __name__ == "__main__":
    main()
