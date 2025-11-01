import requests
import re


class WeatherSkill:
    """
    Weather information using OpenWeatherMap API
    Get free API key: https://openweathermap.org/api
    """
    
    def __init__(self, api_key=None):
        self.name = "WeatherSkill"
        self.api_key = api_key or "a42d24d326db9153a9ebebdaab56d41b"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.default_city = "Mohali"
        
        # Test API connection
        if api_key and api_key != "a42d24d326db9153a9ebebdaab56d41b":
            self._test_connection()
    
    def _test_connection(self):
        """Test if API key works"""
        try:
            params = {
                'q': 'London',
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                print("✅ Weather API connected")
                return True
            else:
                print(f"⚠️ Weather API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Weather API connection failed: {e}")
            return False
    
    def get_intents(self):
        """Return list of (intent_name, examples) tuples"""
        return [
            ('weather', [
                'what\'s the weather', 'how\'s the weather', 'weather today',
                'is it raining', 'will it rain', 'temperature outside',
                'weather forecast', 'is it sunny', 'is it cold',
                'what\'s the temperature', 'how hot is it', 'how cold is it',
                'weather report', 'current weather', 'outside temperature'
            ]),
            ('weather_city', [
                'weather in Paris', 'temperature in London',
                'what\'s the weather in New York', 'weather in Tokyo',
                'how\'s the weather in Berlin', 'temperature in Mumbai'
            ])
        ]
    
    def handle(self, intent, entities, user_text):
        """Handle weather request"""
        # Extract city from text
        city = self._extract_city(user_text, entities)
        
        if not city:
            city = self.default_city
        
        # Get weather data
        weather_data = self._get_weather(city)
        
        if not weather_data:
            return f"Sorry, I couldn't get weather information for {city}. Please check the city name or try again later."
        
        # Format response
        return self._format_weather_response(weather_data)
    
    def _extract_city(self, text, entities):
        """Extract city name from text"""
        # Check if city is in entities
        if 'city' in entities:
            return entities['city']
        
        # Pattern matching for "in CITY"
        patterns = [
            r'in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in Paris"
            r'for ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "for London"
            r'at ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',   # "at Tokyo"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        # Check for common cities
        common_cities = [
            'Paris', 'London', 'New York', 'Tokyo', 'Berlin', 
            'Mumbai', 'Delhi', 'Sydney', 'Toronto', 'Dubai',
            'Singapore', 'Moscow', 'Madrid', 'Rome', 'Amsterdam'
        ]
        
        text_words = text.split()
        for city in common_cities:
            city_words = city.split()
            if all(word.lower() in [w.lower() for w in text_words] for word in city_words):
                return city
        
        return None
    
    def _get_weather(self, city):
        """Fetch weather from API"""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("❌ Invalid API key")
                return None
            elif response.status_code == 404:
                print(f"❌ City not found: {city}")
                return None
            else:
                print(f"❌ Weather API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Weather API timeout")
            return None
        except Exception as e:
            print(f"❌ Weather API error: {e}")
            return None
    
    def _format_weather_response(self, data):
        """Format weather data into speech"""
        try:
            city = data['name']
            country = data['sys']['country']
            temp = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            temp_min = round(data['main']['temp_min'])
            temp_max = round(data['main']['temp_max'])
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = round(data['wind']['speed'] * 3.6)
            
            # Build response
            response = f"In {city}, {country}, it's currently {temp} degrees Celsius with {description}. "
            
            # Add feels like if different
            if abs(temp - feels_like) > 2:
                response += f"It feels like {feels_like} degrees. "
            
            # Add min/max
            if temp_max != temp or temp_min != temp:
                response += f"Today's high is {temp_max} and low is {temp_min} degrees. "
            
            # Add humidity if notable
            if humidity > 70:
                response += f"Humidity is quite high at {humidity} percent. "
            elif humidity < 30:
                response += f"It's quite dry with {humidity} percent humidity. "
            
            # Add wind if notable
            if wind_speed > 20:
                response += f"It's windy with speeds of {wind_speed} kilometers per hour."
            
            return response
            
        except Exception as e:
            print(f"❌ Error formatting weather: {e}")
            return "I got the weather data but had trouble reading it."
    
    def set_default_city(self, city):
        """Set default city for weather queries"""
        self.default_city = city
        print(f"✅ Default weather city set to: {city}")


class WeatherSkillOffline:
    """
    Offline weather skill (uses wttr.in - no API key needed!)
    """
    
    def __init__(self):
        self.name = "WeatherSkillOffline"
        self.base_url = "https://wttr.in"
        self.default_city = "London"
    
    def get_intents(self):
        return [
            ('weather', [
                'what\'s the weather', 'how\'s the weather', 'weather today',
                'is it raining', 'temperature outside', 'weather forecast'
            ]),
            ('weather_city', [
                'weather in Paris', 'temperature in London',
                'what\'s the weather in New York'
            ])
        ]
    
    def handle(self, intent, entities, user_text):
        city = self._extract_city(user_text)
        
        if not city:
            city = self.default_city
        
        weather_data = self._get_weather_wttr(city)
        
        if not weather_data:
            return f"Sorry, I couldn't get weather information for {city}."
        
        return weather_data
    
    def _extract_city(self, text):
        """Extract city from text"""
        match = re.search(r'in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if match:
            return match.group(1)
        return None
    
    def _get_weather_wttr(self, city):
        """Get weather from wttr.in (no API key needed)"""
        try:
            url = f"{self.base_url}/{city}?format=3"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                weather_text = response.text.strip()
                weather_text = weather_text.replace('°C', ' degrees Celsius')
                weather_text = weather_text.replace('°F', ' degrees Fahrenheit')
                return f"The weather is: {weather_text}"
            else:
                return None
                
        except Exception as e:
            print(f"❌ Weather error: {e}")
            return None
    
    def set_default_city(self, city):
        """Set default city"""
        self.default_city = city