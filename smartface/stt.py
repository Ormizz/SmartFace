import vosk
import pyaudio
import json
import time
from smartface.config import (
    VOSK_MODEL_PATH,
    SAMPLE_RATE,
    CHUNK_SIZE,
    SILENCE_THRESHOLD,
    LISTEN_TIMEOUT
)

import os
import platform

# Detect if on Raspberry Pi
IS_RPI = os.path.exists('/sys/firmware/devicetree/base/model')

if IS_RPI:
    # Use Pi-specific config
    from smartface.config_rpi import *
else:
    from smartface.config import *

class SpeechToText:
    """
    Speech-to-Text using Vosk offline recognition
    """
    
    def __init__(self):
        print("🔧 Initializing Speech Recognition...")
        
        # Load Vosk model
        try:
            self.model = vosk.Model(VOSK_MODEL_PATH)
            self.rec = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
            self.rec.SetWords(True)
            print("✅ Vosk model loaded")
        except Exception as e:
            print(f"❌ Error loading Vosk model: {e}")
            print(f"Make sure model exists at: {VOSK_MODEL_PATH}")
            raise
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # Start audio stream
        self._start_stream()
        
        # Silence detection
        self.silence_counter = 0
        # Dans __init__, ajoute:
        if IS_RPI:
            print("🍓 Running on Raspberry Pi - using optimized settings")
            # Smaller buffer for Pi
            CHUNK_SIZE = 2048
    
    def _start_stream(self):
        """Start audio input stream"""
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            self.stream.start_stream()
            print("✅ Microphone ready")
        except Exception as e:
            print(f"❌ Error opening microphone: {e}")
            raise
    
    def listen(self, timeout=None):
        """
        Listen for a complete sentence from the user
        
        Args:
            timeout: Maximum time to listen (seconds)
            
        Returns:
            str: Recognized text
        """
        if timeout is None:
            timeout = LISTEN_TIMEOUT
        
        print("\n🎙️  Listening... Speak now!")
        
        full_text = []
        start_time = time.time()
        self.silence_counter = 0
        last_partial = ""
        has_spoken = False
        
        try:
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    print("\n⏱️  Timeout reached")
                    break
                
                # Read audio data
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                
                # Process with Vosk
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").strip()
                    
                    if text:
                        has_spoken = True
                        full_text.append(text)
                        print(f"\r📝 {text}" + " " * 20)
                        self.silence_counter = 0
                    else:
                        if has_spoken:
                            self.silence_counter += 1
                else:
                    partial = json.loads(self.rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    
                    if partial_text and partial_text != last_partial:
                        has_spoken = True
                        print(f"\r💬 {partial_text}", end='', flush=True)
                        last_partial = partial_text
                        self.silence_counter = 0
                    else:
                        if has_spoken:
                            self.silence_counter += 1
                
                # Stop if silence after speech
                if has_spoken and self.silence_counter > SILENCE_THRESHOLD:
                    print("\n🔇 Speech complete")
                    break
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped listening")
            return ""
        except Exception as e:
            print(f"\n❌ Error during listening: {e}")
            return ""
        
        final_text = " ".join(full_text).strip()
        
        if final_text:
            print(f"✅ Complete: \"{final_text}\"\n")
        else:
            print("❌ No speech detected\n")
        
        return final_text
    
    def close(self):
        """Clean up resources"""
        print("\n🔧 Closing microphone...")
        
        if self.stream:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
        
        print("✅ Microphone closed")