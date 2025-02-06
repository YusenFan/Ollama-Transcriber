import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydub.silence import split_on_silence

def preprocess_audio(file_path, target_sample_rate=16000):
    """
    Preprocess the audio by reducing noise, trimming silence, normalizing the volume,
    and resampling the audio to the target sample rate (16kHz by default).
    """
    try:
        # Load the audio file using pydub
        print(f"Loading audio for preprocessing: {file_path}")
        audio = AudioSegment.from_file(file_path)

        # Normalize audio (adjust the gain to average volume)
        print("Normalizing volume...")
        audio = audio.normalize()

        # Trim silence at the beginning and end
        print("Trimming silence from the audio...")
        chunks = split_on_silence(audio, min_silence_len=700, silence_thresh=-40)
        audio = AudioSegment.silent(duration=500).join(chunks)  # Add brief silence between chunks

        # Resample audio to the target sample rate (e.g., 16kHz) if necessary
        sample_rate = audio.frame_rate
        if sample_rate != target_sample_rate:
            print(f"Resampling audio from {sample_rate} Hz to {target_sample_rate} Hz...")
            audio = audio.set_frame_rate(target_sample_rate)

        # Convert audio to numpy array for noise reduction
        audio_np = np.array(audio.get_array_of_samples(), dtype=np.float32)
        audio_np = audio_np / np.max(np.abs(audio_np))  # Normalize to [-1, 1]

        # Perform noise reduction
        print("Performing noise reduction...")
        reduced_noise_audio = nr.reduce_noise(y=audio_np, sr=target_sample_rate)

        # Convert the noise-reduced numpy array back to pydub AudioSegment
        print("Converting noise-reduced audio back to AudioSegment...")
        audio_segment = AudioSegment(
            reduced_noise_audio.tobytes(),
            frame_rate=target_sample_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        )
        
        print("Preprocessing complete.")
        return audio_segment

    except Exception as e:
        print(f"Error during audio preprocessing: {e}")
        return None
