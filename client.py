#!/usr/bin/env python3
"""
SmartFace Client - Simple Version
Audio-only client for Raspberry Pi
"""

import pyaudio
import wave
import requests
import subprocess
import time
import audioop
from io import BytesIO
from smartface.config import (
    SERVER_URL,
    SAMPLE_RATE,
    CHUNK_SIZE,
    SILENCE_THRESHOLD,
    ENERGY_THRESHOLD,
    LISTEN_TIMEOUT,
    TTS_RATE,
    TTS_VOLUME
)

class SmartFaceClient:
    """Simple audio client"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        print(f"🤖 SmartFace Client")
        print(f"📡 Server: {server_url}\n")
        
        # Test connection
        try:
            r = requests.get(f"{server_url}/health", timeout=5)
            print("✅ Connected to server\n")
        except:
            print("⚠️  Cannot reach server!\n")
        
        # Start audio
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
    
    def record(self) -> bytes:
        """Record audio until silence"""
        print("🎙️  Listening...")
        
        frames = []
        silence = 0
        spoken = False
        
        while True:
            data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
            
            rms = audioop.rms(data, 2)
            
            if rms > ENERGY_THRESHOLD:
                spoken = True
                silence = 0
            elif spoken:
                silence += 1
            
            if spoken and silence > SILENCE_THRESHOLD:
                break
        
        print("✅ Recorded\n")
        
        # Convert to WAV
        buf = BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
        
        return buf.getvalue()
    
    def send(self, audio: bytes) -> dict:
        """Send audio to server"""
        print("📤 Sending to server...")
        
        files = {'file': ('audio.wav', audio, 'audio/wav')}
        r = requests.post(f"{self.server_url}/process_audio", files=files)
        
        return r.json()
    
    def speak(self, text: str):
        """Speak text with eSpeak"""
        print(f"💬 {text}\n")
        
        try:
            subprocess.run(
                ['espeak', '-s', str(TTS_RATE), text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except:
            pass
    
    def run(self):
        """Main loop"""
        print("="*60)
        print("✨ Ready! Press Ctrl+C to exit")
        print("="*60 + "\n")
        
        self.speak("Hello! I'm SmartFace.")
        
        try:
            while True:
                # Record
                audio = self.record()
                
                # Send to server
                result = self.send(audio)
                
                # Show results
                if 'error' in result:
                    print(f"❌ {result['error']}\n")
                    self.speak("Sorry, I had trouble with that.")
                    continue
                
                text = result.get('text', '')
                intent = result.get('intent', '')
                response = result.get('response', '')
                
                print(f"📝 You: {text}")
                print(f"💡 Intent: {intent}")
                
                # Speak response
                if response:
                    self.speak(response)
                
                # Check exit
                if intent == 'goodbye':
                    break
                
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            self.speak("Goodbye!")
        
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Server URL')
    args = parser.parse_args()
    
    client = SmartFaceClient(args.server)
    client.run()

if __name__ == "__main__":
    main()