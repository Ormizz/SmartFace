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
from smartface.audio.preprocessor import AudioPreprocessor


class SpeechToText:
    """
    Speech-to-Text with audio preprocessing
    """
    
    def __init__(self, enable_preprocessing=True):
        print("🔧 Initializing Speech Recognition...")
        
        # Load Vosk model
        try:
            self.model = vosk.Model(VOSK_MODEL_PATH)
            self.rec = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
            self.rec.SetWords(True)
            print("✅ Vosk model loaded")
        except Exception as e:
            print(f"❌ Error loading Vosk model: {e}")
            raise
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        self._start_stream()
        
        # Silence detection
        self.silence_counter = 0
        
        # Audio preprocessing
        self.enable_preprocessing = enable_preprocessing
        if enable_preprocessing:
            self.preprocessor = AudioPreprocessor(SAMPLE_RATE)
            print("✅ Audio preprocessing enabled")
    
    def listen(self, timeout=None):
        """Listen with preprocessing"""
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
                if time.time() - start_time > timeout:
                    print("\n⏱️  Timeout reached")
                    break
                
                # Read audio data
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                
                # Apply preprocessing
                if self.enable_preprocessing:
                    data = self.preprocessor.preprocess(data)
                    # Convert back to bytes
                    data = data.tobytes()
                
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
    
    def _is_sentence_complete(self, text):
        """
        Check if sentence appears complete
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if sentence looks complete
        """
        # Check for sentence-ending punctuation
        if text.endswith(('.', '?', '!')):
            return True
        
        # Check for common ending words
        ending_words = ['please', 'thanks', 'thank you', 'ok', 'okay', 'done']
        last_word = text.split()[-1].lower() if text.split() else ""
        
        return last_word in ending_words
    
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