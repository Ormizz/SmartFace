from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class NLPProcessor:
    """
    Natural Language Processing for intent classification
    Uses sentence embeddings for semantic understanding
    """
    
    def __init__(self):
        print("🔧 Initializing NLP processor...")
        
        # Load sentence transformer model
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ NLP model loaded")
        except Exception as e:
            print(f"❌ Error loading NLP model: {e}")
            raise
        
        # Define intents with example phrases
        self.intents = {
            'greet': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon',
                'good evening', 'greetings', 'howdy', 'what\'s up', 'yo'
            ],
            'goodbye': [
                'bye', 'goodbye', 'see you', 'farewell', 'take care',
                'see you later', 'catch you later', 'gotta go', 'bye bye'
            ],
            'how_are_you': [
                'how are you', 'how are you doing', 'how do you feel',
                'are you ok', 'what\'s up with you', 'how\'s it going'
            ],
            'thank': [
                'thank you', 'thanks', 'thank you very much', 'thanks a lot',
                'appreciate it', 'cheers', 'thx'
            ],
            'weather': [
                'what\'s the weather', 'how\'s the weather', 'is it raining',
                'will it rain today', 'weather forecast', 'temperature outside',
                'is it sunny', 'weather today', 'will it snow'
            ],
            'time': [
                'what time is it', 'current time', 'tell me the time',
                'what\'s the time', 'time please', 'do you have the time'
            ],
            'date': [
                'what\'s the date', 'what day is it', 'tell me the date',
                'what\'s today\'s date', 'current date'
            ],
            'joke': [
                'tell me a joke', 'make me laugh', 'say something funny',
                'do you know any jokes', 'joke please', 'tell a joke'
            ],
            'name': [
                'what\'s your name', 'who are you', 'your name please',
                'what should I call you', 'introduce yourself', 'tell me your name'
            ],
            'help': [
                'help me', 'what can you do', 'your capabilities',
                'how do you work', 'what are your features', 'help'
            ],
            'web_search': [
                'search for', 'look up', 'find information about',
                'google', 'search the web', 'what is', 'who is',
                'tell me about', 'search wikipedia'
            ],
            'reminder_set': [
                'remind me', 'set a reminder', 'create reminder',
                'don\'t let me forget', 'reminder to', 'remember to'
            ],
            'reminder_list': [
                'list reminders', 'show reminders', 'what are my reminders',
                'do I have any reminders', 'my reminders'
            ],
            'light_on': [
                'turn on the light', 'turn on light', 'lights on',
                'switch on the light', 'enable light', 'light on',
                'turn the light on', 'turn lights on', 'switch lights on',
                'turn on living room light', 'turn on bedroom light'
            ],
            'light_off': [
                'turn off the light', 'turn off light', 'lights off',
                'switch off the light', 'disable light', 'light off',
                'turn the light off', 'turn lights off', 'switch lights off',
                'turn off living room light', 'turn off bedroom light'
            ],
            'temperature_set': [
                'set temperature', 'change temperature', 'adjust temperature',
                'make it warmer', 'make it cooler', 'set thermostat'
            ],
            'device_status': [
                'device status', 'what\'s the status', 'are lights on',
                'check devices', 'home status', 'show devices'
            ],
            'weather': [
                'what\'s the weather', 'how\'s the weather', 'is it raining',
                'will it rain today', 'weather forecast', 'temperature outside',
                'is it sunny', 'weather today', 'will it snow', 'what\'s the temperature',
                'how hot is it', 'how cold is it', 'weather in', 'forecast for',
                'tell me the weather', 'check the weather', 'weather conditions',
                'is it going to rain', 'will it be sunny', 'weather tomorrow',
                'three day forecast', 'weekly weather', 'weather report'
            ],
        }
        
        # Precompute embeddings for all intent examples
        print("🔧 Computing intent embeddings...")
        self.intent_embeddings = {}
        for intent, examples in self.intents.items():
            self.intent_embeddings[intent] = self.model.encode(examples)
        
        print(f"✅ Loaded {len(self.intents)} intents")
    
    def classify_intent(self, text, threshold=0.5):
        """
        Classify user intent using semantic similarity
        
        Args:
            text: User input text
            threshold: Minimum confidence score (0-1)
            
        Returns:
            tuple: (intent, confidence_score)
        """
        if not text or not text.strip():
            return "unknown", 0.0
        
        text = text.strip().lower()
        
        # Encode user input
        text_embedding = self.model.encode([text])[0]
        
        best_intent = "unknown"
        best_score = 0.0
        
        # Compare with all intents
        for intent, embeddings in self.intent_embeddings.items():
            # Calculate similarity with all examples of this intent
            similarities = cosine_similarity([text_embedding], embeddings)[0]
            max_similarity = np.max(similarities)
            
            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent
        
        # Only return intent if confidence is above threshold
        if best_score < threshold:
            return "unknown", best_score
        
        return best_intent, best_score
    
    def extract_entities(self, text, intent):
        """
        Extract relevant entities from text based on intent
        
        Args:
            text: User input text
            intent: Classified intent
            
        Returns:
            dict: Extracted entities
        """
        text_lower = text.lower()
        entities = {}
        
        # Extract room names
        rooms = ['living room', 'bedroom', 'kitchen', 'bathroom', 'garage']
        for room in rooms:
            if room in text_lower:
                entities['room'] = room
                break
        
        # Extract numbers (for temperature, time, etc.)
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities['number'] = int(numbers[0])
        
        # Extract search query for web_search intent OR if question words detected
        question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'tell me about', 'search']
        is_question = any(word in text_lower for word in question_words)
        
        if intent == 'web_search' or is_question or intent == 'unknown':
            # Remove common search phrases
            query = text
            search_phrases = [
                'search for', 'look up', 'find', 'what is', 'who is', 
                'tell me about', 'google', 'search', 'what are',
                'who are', 'where is', 'when is', 'why is', 'how is'
            ]
            for phrase in search_phrases:
                query = re.sub(r'\b' + phrase + r'\b', '', query, flags=re.IGNORECASE)
            
            entities['query'] = query.strip()
            
            # If we have a query and intent was unknown, suggest it might be a search
            if is_question and intent == 'unknown':
                entities['likely_search'] = True
        

        # Extract city names for weather queries
        if intent == 'weather':
            # Common cities (extend as needed)
            cities = [
                'mohali', 'chandigarh', 'delhi', 'mumbai', 'bangalore',
                'hyderabad', 'chennai', 'kolkata', 'pune', 'ahmedabad',
                'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore',
                'paris', 'london', 'new york', 'tokyo', 'beijing',
                'sydney', 'toronto', 'berlin', 'madrid', 'rome'
            ]
            
            for city in cities:
                if city in text_lower:
                    entities['city'] = city.title()
                    break
            
            # Check if it's a forecast request
            forecast_keywords = [
                'tomorrow', 'forecast', 'next', 'week', 'coming',
                'three day', '3 day', 'weekly', 'upcoming', 'future'
            ]
            if any(keyword in text_lower for keyword in forecast_keywords):
                entities['forecast'] = True
            else:
                entities['forecast'] = False

                
        # Extract reminder text
        if intent == 'reminder_set':
            # Try to extract text after "remind me to" or similar
            reminder_patterns = ['remind me to', 'remind me', 'reminder to', 
                            'don\'t let me forget to', 'remember to']
            for pattern in reminder_patterns:
                if pattern in text_lower:
                    reminder_text = text.split(pattern, 1)[-1].strip()
                    entities['reminder_text'] = reminder_text
                    break
            
            # If no pattern matched, use the whole text
            if 'reminder_text' not in entities:
                entities['reminder_text'] = text
        
        return entities
    
    def add_intent_examples(self, intent, examples):
        """
        Add new examples to an existing intent or create new intent
        
        Args:
            intent: Intent name
            examples: List of example phrases
        """
        if intent in self.intents:
            self.intents[intent].extend(examples)
        else:
            self.intents[intent] = examples
        
        # Recompute embeddings for this intent
        self.intent_embeddings[intent] = self.model.encode(self.intents[intent])
        print(f"✅ Updated intent '{intent}' with {len(examples)} new examples")