import platform
import subprocess
import pyttsx3
from smartface.config import TTS_RATE


class TextToSpeech:
    """
    Text-to-Speech using macOS native 'say' command or pyttsx3
    """
    
    def __init__(self, voice_name=None, use_native=True):
        print("🔧 Initializing Text-to-Speech...")
        
        self.system = platform.system().lower()
        self.use_native = use_native and self.system == 'darwin'
        
        if self.use_native:
            # Use macOS native 'say' command (more reliable)
            print("✅ Using macOS native speech")
            self.voice = voice_name or "Samantha"
            self.rate = TTS_RATE
            # Test it works
            self._test_native()
        else:
            # Use pyttsx3 (fallback for other OS)
            self._init_pyttsx3(voice_name)
        
        print("✅ Text-to-Speech ready")
    
    def _test_native(self):
        """Test that native say command works"""
        try:
            subprocess.run(
                ['say', '-v', self.voice, 'Ready'],
                check=True,
                capture_output=True,
                timeout=3
            )
        except Exception as e:
            print(f"⚠️  Native speech test failed: {e}")
            print("Falling back to pyttsx3...")
            self.use_native = False
            self._init_pyttsx3(None)
    
    def _init_pyttsx3(self, voice_name):
        """Initialize pyttsx3 engine"""
        try:
            if self.system == 'darwin':
                self.engine = pyttsx3.init('nsss')
            elif self.system == 'linux':
                self.engine = pyttsx3.init('espeak')
            else:
                self.engine = pyttsx3.init()
            
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('rate', TTS_RATE)
            
            voices = self.engine.getProperty('voices')
            if voices:
                if voice_name:
                    for voice in voices:
                        if voice_name.lower() in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            break
                else:
                    self.engine.setProperty('voice', voices[0].id)
            
            print("✅ pyttsx3 initialized")
        except Exception as e:
            print(f"❌ Error initializing TTS: {e}")
            raise
    
    def speak(self, text):
        """
        Speak the given text
        
        Args:
            text: Text to speak
        """
        if not text:
            return
        
        print(f"🔊 Speaking: \"{text}\"")
        
        if self.use_native:
            self._speak_native(text)
        else:
            self._speak_pyttsx3(text)
    
    def _speak_native(self, text):
        """Speak using macOS native say command"""
        try:
            # Calculate rate for 'say' command (words per minute)
            # say uses rate in words/min, default is 175
            rate = self.rate
            
            subprocess.run(
                ['say', '-v', self.voice, '-r', str(rate), text],
                check=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            print("⚠️  Speech timeout")
        except Exception as e:
            print(f"❌ Error speaking (native): {e}")
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ Error speaking (pyttsx3): {e}")
    
    def set_rate(self, rate):
        """
        Set speaking rate
        
        Args:
            rate: Words per minute (typical range: 100-200)
        """
        self.rate = rate
        if not self.use_native and hasattr(self, 'engine'):
            try:
                self.engine.setProperty('rate', rate)
                print(f"✅ Speech rate set to {rate} WPM")
            except Exception as e:
                print(f"❌ Error setting rate: {e}")
    
    def set_volume(self, volume):
        """
        Set volume (only works with pyttsx3)
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not self.use_native and hasattr(self, 'engine'):
            try:
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
                print(f"✅ Volume set to {volume}")
            except Exception as e:
                print(f"❌ Error setting volume: {e}")
        else:
            print("⚠️  Volume control not available with native speech")
    
    def set_voice(self, voice_name):
        """
        Change voice
        
        Args:
            voice_name: Voice name (e.g., 'Samantha', 'Alex', 'Daniel')
        """
        if self.use_native:
            self.voice = voice_name
            print(f"✅ Voice set to: {voice_name}")
        else:
            self.set_voice_by_name(voice_name)
    
    def list_voices(self):
        """List all available voices"""
        if self.use_native:
            print("\n📢 Listing macOS voices:")
            try:
                result = subprocess.run(
                    ['say', '-v', '?'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(result.stdout)
            except Exception as e:
                print(f"❌ Error listing voices: {e}")
        else:
            if hasattr(self, 'engine'):
                voices = self.engine.getProperty('voices')
                print("\n📢 Available voices:")
                for i, voice in enumerate(voices):
                    print(f"  {i}: {voice.name}")
    
    def set_voice_by_name(self, name):
        """
        Change voice by name (pyttsx3 only)
        
        Args:
            name: Voice name (partial match works)
        """
        if self.use_native:
            self.voice = name
            print(f"✅ Voice set to: {name}")
            return True
        
        if not hasattr(self, 'engine'):
            return False
        
        try:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if name.lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"✅ Voice changed to: {voice.name}")
                    return True
            print(f"❌ Voice '{name}' not found")
            return False
        except Exception as e:
            print(f"❌ Error changing voice: {e}")
            return False