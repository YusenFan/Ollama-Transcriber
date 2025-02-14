import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydub.silence import split_on_silence

def preprocess_audio(audio_segment, target_sample_rate=16000):
    """Preprocesses audio for improved transcription quality.
    
    Performs several audio processing steps:
    1. Volume normalization
    2. Silence removal
    3. Sample rate adjustment
    4. Noise reduction
    
    Args:
        audio_segment (pydub.AudioSegment): Input audio to be processed
        target_sample_rate (int): Desired output sample rate in Hz (default: 16000)
    
    Returns:
        pydub.AudioSegment: Processed audio segment optimized for transcription
        
    Raises:
        ValueError: If audio_segment is invalid or processing fails
    """
    if not isinstance(audio_segment, AudioSegment):
        raise ValueError("Input must be a pydub AudioSegment")

    try:
        # Step 1: Normalize audio levels
        print("Normalizing volume...")
        audio_segment = audio_segment.normalize()

        # Step 2: Remove silence while preserving natural pauses
        print("Trimming silence from the audio...")
        chunks = split_on_silence(
            audio_segment,
            # Minimum length of silence to consider (in ms)
            min_silence_len=700,
            # Silence threshold in dB (-40 is a good starting point)
            silence_thresh=-40,
            # Amount of silence to keep on either side of non-silent chunks
            keep_silence=500
        )

        # Reconstruct audio from non-silent chunks
        if chunks:
            audio_segment = sum(chunks, AudioSegment.empty())
        else:
            print("No silence detected, using original audio")

        # Step 3: Resample audio if needed
        original_rate = audio_segment.frame_rate
        if original_rate != target_sample_rate:
            print(f"Resampling audio from {original_rate}Hz to {target_sample_rate}Hz...")
            audio_segment = audio_segment.set_frame_rate(target_sample_rate)

        # Step 4: Convert to numpy array for noise reduction
        print("Converting audio for noise reduction...")
        audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        
        # Normalize array to [-1, 1] range
        audio_np = audio_np / np.max(np.abs(audio_np))

        # Step 5: Apply noise reduction
        print("Performing noise reduction...")
        reduced_noise = nr.reduce_noise(
            y=audio_np,
            sr=target_sample_rate,
            stationary=True,
            prop_decrease=0.75
        )

        # Step 6: Prepare audio for conversion back to AudioSegment
        # Clip values to int16 range
        reduced_noise = np.clip(reduced_noise * 32767, -32768, 32767)
        reduced_noise = reduced_noise.astype(np.int16)

        # Step 7: Convert processed audio back to AudioSegment
        print("Finalizing audio processing...")
        processed_audio = AudioSegment(
            reduced_noise.tobytes(),
            frame_rate=target_sample_rate,
            sample_width=2,  # 16-bit audio
            channels=audio_segment.channels
        )

        print("Audio preprocessing completed successfully")
        return processed_audio

    except Exception as e:
        error_msg = f"Audio preprocessing failed: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg) from e
