#!/usr/bin/env python3
"""
SmartFace Client with automatic audio initialization
"""

import pyaudio
import wave
import requests
import subprocess
import time
import audioop
from io import BytesIO

from smartface.config import (
    SAMPLE_RATE,
    CHUNK_SIZE,
    SILENCE_THRESHOLD,
    ENERGY_THRESHOLD,
    LISTEN_TIMEOUT,
    TTS_RATE,
    TTS_VOLUME
)

# Import audio utilities
try:
    from smartface.audio_utils import initialize_audio
    AUDIO_UTILS_AVAILABLE = True
except ImportError:
    AUDIO_UTILS_AVAILABLE = False
    print("⚠️  Audio utils not found - manual configuration required")

# Import LED controller
try:
    from smartface.led import LEDController
    LED_AVAILABLE = True
except ImportError:
    LED_AVAILABLE = False
    print("⚠️  LED controller not found - running without LEDs")


class SmartFaceClient:
    """Simple audio client with LED status indicators"""
    
    def __init__(self, server_url: str, auto_init_audio: bool = True):
        # Fix URL if missing protocol
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"http://{server_url}"
        
        self.server_url = server_url
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.bluetooth_device_index = None
        
        # Initialize LED controller
        if LED_AVAILABLE:
            self.led = LEDController()
        else:
            self.led = None
        
        print("="*60)
        print("🤖 SmartFace Client")
        print("="*60)
        print(f"📡 Server: {server_url}\n")
        
        # Set idle state (RED LED)
        if self.led:
            self.led.set_idle()
        
        # Auto-initialize audio if requested
        if auto_init_audio and AUDIO_UTILS_AVAILABLE:
            audio_config = initialize_audio()
            if audio_config:
                self.bluetooth_device_index = audio_config['bluetooth_index']
                print(f"📌 Using Bluetooth device index: {self.bluetooth_device_index}\n")
        
        # Test connection
        try:
            r = requests.get(f"{server_url}/health", timeout=5)
            if r.status_code == 200:
                print("✅ Connected to server\n")
            else:
                print(f"⚠️  Server error: {r.status_code}\n")
        except Exception as e:
            print(f"❌ Connection failed: {e}\n")
            if self.led:
                self.led.set_error()
        
        # List available devices if no auto-init
        if not auto_init_audio or not AUDIO_UTILS_AVAILABLE:
            print("\n📋 Available audio devices:")
            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"  [{i}] {info['name']} (in:{info['maxInputChannels']})")
            print()
        
        # Start audio stream
        self._init_audio_stream()
    
    def _init_audio_stream(self):
        """Initialize audio input stream"""
        try:
            # Try with Bluetooth device if found
            if self.bluetooth_device_index is not None:
                try:
                    self.stream = self.p.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=SAMPLE_RATE,
                        input=True,
                        input_device_index=self.bluetooth_device_index,
                        frames_per_buffer=CHUNK_SIZE
                    )
                    print(f"✅ Microphone ready (Bluetooth device {self.bluetooth_device_index})\n")
                    return
                except Exception as e:
                    print(f"⚠️  Bluetooth device failed: {e}")
                    print("   Falling back to default device...\n")
            
            # Fallback to default device
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            print("✅ Microphone ready (default device)\n")
            
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            if self.led:
                self.led.set_error()
            raise
    
    def record(self) -> bytes:
        """Record audio until silence - BLUE LED ON"""
        print("🎙️  Listening... Speak now!")
        
        # 🔵 BLUE LED ON - Listening
        if self.led:
            self.led.set_listening()
        
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
            if self.led:
                self.led.set_idle()
            return None
        
        # 🔴 RED LED ON - Processing
        if self.led:
            self.led.set_processing()
        
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
            if self.led:
                self.led.set_error()
            return None
    
    def send(self, audio: bytes) -> dict:
        """Send audio to server - RED LED stays ON"""
        print("📤 Sending to server...")
        
        # Keep RED LED on during network transfer
        if self.led:
            self.led.set_processing()
        
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
            if self.led:
                self.led.set_error()
            return {"error": "timeout"}
        except Exception as e:
            print(f"❌ Send error: {e}\n")
            if self.led:
                self.led.set_error()
            return {"error": str(e)}
    
    def speak(self, text: str):
        """Speak text with TTS - RED LED stays ON"""
        if not text:
            return
        
        print(f"💬 Response: {text}\n")
        
        # Keep RED LED on during TTS
        if self.led:
            self.led.set_processing()
        
        try:
            # Générer avec espeak et jouer via PipeWire
            cmd = f'espeak -v en -s {TTS_RATE} "{text}" --stdout | pw-play -'
            subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception as e:
            print(f"⚠️  TTS error: {e}")
            # Fallback to text display only
    
    def run(self):
        """Main loop"""
        print("="*60)
        print("✨ Ready! Press Ctrl+C to exit")
        print("="*60 + "\n")
        
        # Start in idle state (RED LED)
        if self.led:
            self.led.set_idle()
        
        self.speak("Hello! I'm SmartFace.")
        
        count = 0
        
        try:
            while True:
                count += 1
                print(f"{'─'*60}")
                print(f"Interaction #{count}")
                print('─'*60 + "\n")
                
                # Set idle before recording (RED LED)
                if self.led:
                    self.led.set_idle()
                
                time.sleep(0.5)  # Brief pause
                
                # 1. Record audio (BLUE LED)
                audio = self.record()
                
                if not audio:
                    self.speak("I didn't catch that.")
                    continue
                
                # 2. Send to server (RED LED)
                result = self.send(audio)
                
                # 3. Handle response
                if 'error' in result:
                    print(f"❌ Error: {result['error']}\n")
                    if self.led:
                        self.led.set_error()
                    self.speak("Sorry, I had trouble with that.")
                    continue
                
                text = result.get('text', '')
                intent = result.get('intent', '')
                confidence = result.get('confidence', 0)
                response = result.get('response', '')
                
                print(f"📝 You said: \"{text}\"")
                print(f"💡 Intent: {intent} (confidence: {confidence:.2f})\n")
                
                # 4. Speak response (RED LED)
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
            # Cleanup
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.p.terminate()
            
            # Turn off LEDs
            if self.led:
                self.led.cleanup()
            
            print("\n✅ Client closed\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SmartFace Client with LED indicators',
        epilog="""
LED Status:
  🔵 Blue:  Listening (recording audio)
  🔴 Red:   Processing / Idle / Speaking
  🔴🔵 Both: Error (blinks 3 times)
        """
    )
    
    parser.add_argument(
        '--server',
        required=True,
        help='Server URL (e.g., http://192.168.1.72:8000)'
    )
    
    parser.add_argument(
        '--no-auto-init',
        action='store_true',
        help='Disable automatic audio initialization'
    )
    
    args = parser.parse_args()
    
    client = SmartFaceClient(
        args.server,
        auto_init_audio=not args.no_auto_init
    )
    client.run()


if __name__ == "__main__":
    main()