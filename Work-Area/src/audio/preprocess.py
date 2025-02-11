import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydub.silence import split_on_silence

def preprocess_audio(audio_segment, target_sample_rate=16000):
    """Preprocesses the audio.

    Args:
        audio_segment (pydub.AudioSegment): The audio segment to preprocess.
        target_sample_rate (int): The target sample rate.

    Returns:
        pydub.AudioSegment: The preprocessed audio segment.
        or None on error.
    """
    try:
        sample_rate = audio_segment.frame_rate

        # Normalize audio (adjust the gain to average volume)
        print("Normalizing volume...")
        audio_segment = audio_segment.normalize()

        # Trim silence at the beginning and end
        print("Trimming silence from the audio...")

        audio_segment_copy = AudioSegment(  # Create a copy to avoid modifying the original audio
            audio_segment.raw_data,
            sample_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels
        )

        chunks = split_on_silence(audio_segment_copy, min_silence_len=700, silence_thresh=-40)

        # Join the chunks back together (if any chunks were found)
        if chunks:  # Check if chunks is not empty
            audio_segment = AudioSegment.silent(duration=500).join(chunks)  # Add brief silence between chunks
        else:
            print("No silence chunks found. Keeping original audio.")  # Log this message
            # No change to audio_segment, it's already the original


        # Resample audio to the target sample rate (e.g., 16kHz) if necessary
        if sample_rate != target_sample_rate:
            print(f"Resampling audio from {sample_rate} Hz to {target_sample_rate} Hz...")
            audio_segment = audio_segment.set_frame_rate(target_sample_rate)

        # Convert audio to numpy array for noise reduction
        audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        audio_np = audio_np / np.max(np.abs(audio_np))  # Normalize to [-1, 1]

        # Perform noise reduction
        print("Performing noise reduction...")
        reduced_noise_audio = nr.reduce_noise(y=audio_np, sr=target_sample_rate)

        # Clipping to int16 range conversion
        reduced_noise_audio = np.clip(reduced_noise_audio, -32768, 32767)      
        
        # Convert to int16
        reduced_noise_audio = reduced_noise_audio.astype(np.int16)
        
        # Convert the noise-reduced numpy array back to pydub AudioSegment
        print("Converting noise-reduced audio back to AudioSegment...")
        audio_segment = AudioSegment(
            reduced_noise_audio.tobytes(),
            frame_rate=target_sample_rate,
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels
        )

        print("Preprocessing complete.")
        return audio_segment

    except Exception as e:
        print(f"Error during audio preprocessing: {e}")
        return None