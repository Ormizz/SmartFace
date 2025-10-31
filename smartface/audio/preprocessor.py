import numpy as np
import scipy.signal as signal
from scipy.io import wavfile


class AudioPreprocessor:
    """
    Audio preprocessing to improve Vosk recognition
    """
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
    
    def preprocess(self, audio_data):
        """
        Apply preprocessing pipeline
        
        Args:
            audio_data: Raw audio bytes or numpy array
            
        Returns:
            Preprocessed audio
        """
        # Convert to numpy array if bytes
        if isinstance(audio_data, bytes):
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
        else:
            audio_array = audio_data
        
        # 1. Normalize volume
        audio_array = self._normalize(audio_array)
        
        # 2. Remove DC offset
        audio_array = self._remove_dc_offset(audio_array)
        
        # 3. Apply noise reduction
        audio_array = self._reduce_noise(audio_array)
        
        # 4. Apply band-pass filter (human voice: 300-3400 Hz)
        audio_array = self._bandpass_filter(audio_array)
        
        # 5. Apply pre-emphasis (boost high frequencies)
        audio_array = self._pre_emphasis(audio_array)
        
        return audio_array
    
    def _normalize(self, audio):
        """Normalize audio volume"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio.astype(np.float32) / max_val * 32767
        return audio.astype(np.int16)
    
    def _remove_dc_offset(self, audio):
        """Remove DC offset (mean)"""
        return audio - np.mean(audio)
    
    def _reduce_noise(self, audio):
        """Simple noise gate"""
        # Calculate noise floor
        noise_floor = np.percentile(np.abs(audio), 10)
        threshold = noise_floor * 2
        
        # Apply noise gate
        audio_float = audio.astype(np.float32)
        audio_float[np.abs(audio_float) < threshold] *= 0.1
        
        return audio_float.astype(np.int16)
    
    def _bandpass_filter(self, audio, lowcut=300, highcut=3400):
        """Apply bandpass filter for human voice"""
        nyquist = self.sample_rate / 2
        low = lowcut / nyquist
        high = highcut / nyquist
        
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, audio)
        
        return filtered.astype(np.int16)
    
    def _pre_emphasis(self, audio, alpha=0.97):
        """Apply pre-emphasis filter"""
        emphasized = np.append(audio[0], audio[1:] - alpha * audio[:-1])
        return emphasized.astype(np.int16)
    
    def enhance_speech(self, audio):
        """
        Enhance speech clarity using spectral subtraction
        More advanced noise reduction
        """
        # Convert to float
        audio_float = audio.astype(np.float32)
        
        # Compute spectrogram
        f, t, Zxx = signal.stft(audio_float, fs=self.sample_rate)
        
        # Estimate noise (first 0.5 seconds)
        noise_frames = int(0.5 * len(t))
        noise_spectrum = np.mean(np.abs(Zxx[:, :noise_frames]), axis=1, keepdims=True)
        
        # Subtract noise
        magnitude = np.abs(Zxx)
        phase = np.angle(Zxx)
        
        # Spectral subtraction
        clean_magnitude = np.maximum(magnitude - 2 * noise_spectrum, 0.1 * magnitude)
        
        # Reconstruct
        clean_spectrum = clean_magnitude * np.exp(1j * phase)
        _, enhanced = signal.istft(clean_spectrum, fs=self.sample_rate)
        
        return enhanced.astype(np.int16)