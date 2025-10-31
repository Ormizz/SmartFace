import random
from datetime import datetime


class ResponseHandler:
    """
    Handles response generation for different intents
    Provides static responses for basic intents
    """
    
    def __init__(self):
        print("🔧 Initializing Response Handler...")
        
        # Define responses for each intent
        self.responses = {
            'greet': [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! Nice to hear from you!",
                "Greetings! How may I assist you?",
                "Hello! I'm here to help!"
            ],
            'goodbye': [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Bye! Come back soon!",
                "Farewell! Stay safe!",
                "Take care! See you next time!"
            ],
            'how_are_you': [
                "I'm doing great, thank you for asking! How are you?",
                "I'm excellent! Always ready to help. How about you?",
                "I'm functioning perfectly! What can I do for you?",
                "I'm wonderful, thanks! How can I assist you today?"
            ],
            'thank': [
                "You're welcome!",
                "Happy to help!",
                "My pleasure!",
                "Anytime!",
                "Glad I could help!"
            ],
            'name': [
                "I'm SmartFace, your voice assistant!",
                "You can call me SmartFace. I'm here to help!",
                "My name is SmartFace. Nice to meet you!",
                "I'm SmartFace, your personal assistant!"
            ],
            'help': [
                "I can help you with: conversations, web searches, setting reminders, and controlling smart home devices. Just ask!",
                "I can search the web, set reminders, control lights and temperature, and chat with you. What would you like to do?",
                "My capabilities include: answering questions, web searches, reminders, and smart home control. How can I help?"
            ],
            'joke': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call a bear with no teeth? A gummy bear!",
                "Why did the scarecrow win an award? He was outstanding in his field!",
                "What do you call a fake noodle? An impasta!",
                "Why don't eggs tell jokes? They'd crack each other up!",
                "What did the ocean say to the beach? Nothing, it just waved!",
                "Why can't a bicycle stand on its own? It's two tired!"
            ],
            'time': [],  # Handled dynamically
            'date': [],  # Handled dynamically
            'unknown': [
                "I'm not sure I understood that. Could you rephrase?",
                "Sorry, I didn't quite catch that. Can you say it differently?",
                "I'm still learning. Could you try asking in another way?",
                "Hmm, I'm not sure about that. What else can I help with?",
                "I didn't understand that. Try asking me about the weather, time, or setting a reminder."
            ]
        }
        
        print("✅ Response Handler ready")
    
    def generate_response(self, intent, entities=None, confidence=0.0):
        """
        Generate appropriate response for given intent
        
        Args:
            intent: Classified intent
            entities: Extracted entities (optional)
            confidence: Confidence score
            
        Returns:
            str: Response text
        """
        entities = entities or {}
        
        # Handle dynamic responses
        if intent == 'time':
            return self._get_time_response()
        elif intent == 'date':
            return self._get_date_response()
        elif intent == 'weather':
            return self._get_weather_response(entities)
        
        # Get random response from predefined list
        if intent in self.responses and self.responses[intent]:
            return random.choice(self.responses[intent])
        
        # Default to unknown
        return random.choice(self.responses['unknown'])
    
    def _get_time_response(self):
        """Get current time"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}"
    
    def _get_date_response(self):
        """Get current date"""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}"
    
    def _get_weather_response(self, entities):
        """
        Placeholder for weather response
        In a real implementation, this would call a weather API
        """
        return "I don't have access to real-time weather data yet, but you can check weather.com or your local weather app!"
    
    def add_response(self, intent, response):
        """
        Add a new response option for an intent
        
        Args:
            intent: Intent name
            response: Response text
        """
        if intent in self.responses:
            self.responses[intent].append(response)
        else:
            self.responses[intent] = [response]
        
        print(f"✅ Added response to '{intent}'")