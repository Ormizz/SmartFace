#!/usr/bin/env python3
"""
SmartFace Client - Simple Version
Audio-only client for Raspberry Pi or Mac
"""

import pyaudio
import wave
import requests
import subprocess
import time
import audioop
from io import BytesIO

# Import depuis smartface.config ✅
from smartface.config import (
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
        
        print("="*60)
        print("🤖 SmartFace Client")
        print("="*60)
        print(f"📡 Server: {server_url}\n")
        
        # Test connection
        try:
            r = requests.get(f"{server_url}/health", timeout=5)
            if r.status_code == 200:
                print("✅ Connected to server\n")
            else:
                print("⚠️  Server responded but not healthy\n")
        except Exception as e:
            print(f"⚠️  Cannot reach server: {e}\n")
            print("Make sure server is running!\n")
        
        # Start audio
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            print("✅ Microphone ready\n")
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            raise
    
    def record(self) -> bytes:
        """Record audio until silence"""
        print("🎙️  Listening... Speak now!")
        
        frames = []
        silence = 0
        spoken = False
        start_time = time.time()
        
        try:
            while True:
                # Timeout check
                if time.time() - start_time > LISTEN_TIMEOUT:
                    print("⏱️  Timeout")
                    break
                
                # Read audio
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)
                
                # Voice Activity Detection
                rms = audioop.rms(data, 2)
                
                if rms > ENERGY_THRESHOLD:
                    if not spoken:
                        print("🎤 Speech detected...")
                    spoken = True
                    silence = 0
                elif spoken:
                    silence += 1
                
                # Stop if silence after speech
                if spoken and silence > SILENCE_THRESHOLD:
                    print("🔇 Speech complete")
                    break
        
        except KeyboardInterrupt:
            print("\n⏹️  Recording stopped")
            return None
        
        if not spoken:
            print("❌ No speech detected")
            return None
        
        # Convert to WAV
        buf = BytesIO()
        try:
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(b''.join(frames))
            
            duration = len(frames) * CHUNK_SIZE / SAMPLE_RATE
            print(f"✅ Recorded {duration:.1f}s\n")
            
            return buf.getvalue()
        except Exception as e:
            print(f"❌ WAV error: {e}")
            return None
    
    def send(self, audio: bytes) -> dict:
        """Send audio to server"""
        print("📤 Sending to server...")
        
        try:
            files = {'file': ('audio.wav', audio, 'audio/wav')}
            r = requests.post(
                f"{self.server_url}/process_audio",
                files=files,
                timeout=30
            )
            
            print(f"📥 Response: {r.status_code}\n")
            return r.json()
        
        except requests.exceptions.Timeout:
            print("❌ Server timeout\n")
            return {"error": "timeout"}
        except Exception as e:
            print(f"❌ Send error: {e}\n")
            return {"error": str(e)}
    
    def speak(self, text: str):
        """Speak text with TTS"""
        if not text:
            return
        
        print(f"💬 Response: {text}\n")
        
        try:
            # macOS
            subprocess.run(
                ['say', '-r', str(TTS_RATE), text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            try:
                # Linux/Pi
                subprocess.run(
                    ['espeak', '-s', str(TTS_RATE), text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                pass  # No TTS available
    
    def run(self):
        """Main loop"""
        print("="*60)
        print("✨ Ready! Press Ctrl+C to exit")
        print("="*60 + "\n")
        
        self.speak("Hello! I'm SmartFace.")
        
        count = 0
        
        try:
            while True:
                count += 1
                print(f"{'─'*60}")
                print(f"Interaction #{count}")
                print('─'*60 + "\n")
                
                # 1. Record audio
                audio = self.record()
                
                if not audio:
                    self.speak("I didn't catch that.")
                    continue
                
                # 2. Send to server
                result = self.send(audio)
                
                # 3. Handle response
                if 'error' in result:
                    print(f"❌ Error: {result['error']}\n")
                    self.speak("Sorry, I had trouble with that.")
                    continue
                
                text = result.get('text', '')
                intent = result.get('intent', '')
                confidence = result.get('confidence', 0)
                response = result.get('response', '')
                
                print(f"📝 You said: \"{text}\"")
                print(f"💡 Intent: {intent} (confidence: {confidence:.2f})\n")
                
                # 4. Speak response
                if response:
                    self.speak(response)
                
                # Check exit
                if intent == 'goodbye':
                    print("\n👋 Goodbye!")
                    break
                
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
            self.speak("Goodbye!")
        
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.p.terminate()
            print("\n✅ Client closed\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SmartFace Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 client.py --server http://localhost:8000
  python3 client.py --server http://192.168.1.100:8000
        """
    )
    
    parser.add_argument(
        '--server',
        required=True,
        help='Server URL (e.g., http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    client = SmartFaceClient(args.server)
    client.run()

if __name__ == "__main__":
    main()