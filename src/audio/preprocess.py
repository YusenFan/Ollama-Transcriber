import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence

def preprocess_audio(audio_segment, target_sample_rate=16000):
    """Preprocesses audio specifically for Whisper transcription.
    
    Performs essential audio processing steps in order of importance:
    1. Volume normalization
    2. Basic silence removal
    3. Sample rate conversion to Whisper's required 16kHz
    4. Channel conversion to mono
    
    Args:
        audio_segment (pydub.AudioSegment): Input audio segment to process
        target_sample_rate (int): Target sample rate, defaults to 16000 (Whisper requirement)
    
    Returns:
        pydub.AudioSegment: Processed audio optimized for Whisper transcription
    
    Raises:
        ValueError: If input validation fails
        Exception: If any processing step fails
    """
    # Input validation
    if not isinstance(audio_segment, AudioSegment):
        raise ValueError("Input must be a pydub AudioSegment")
    
    try:
        # Step 1: Normalize audio levels
        # This adjusts the volume to a standard level and prevents clipping
        # Normalization is crucial for consistent transcription quality
        print("Normalizing audio levels...")
        audio_segment = audio_segment.normalize()

        # Step 2: Remove extended silences
        # This improves transcription efficiency without losing context
        print("Removing extended silences...")

        """Here you can modify the silence removal parameters to suit your needs, the defaults are a good starting point:
        
        min_silence_len=2000,    # Only remove 2+ second silences
        silence_thresh=-45,       # More lenient silence threshold
        keep_silence=500          # Keep more silence

        NOTE: the key is to ensure that the silence removal is not too aggressive, as it can cut off speech and that your audio is of high a quality as possible. If noise is present, rename `preprocess.py` to `preprocess_nr.py` and re-run main.py.

        """
        chunks = split_on_silence(
            audio_segment,
            # Minimum silence length (1 second)
            min_silence_len=1000,
            # Silence threshold in dB (-40 is a good balance)
            silence_thresh=-40,
            # Keep 300ms of silence for natural speech patterns
            keep_silence=300
        )
        
        # Reconstruct audio from non-silent chunks
        if chunks:
            print(f"Found {len(chunks)} audio segments after silence removal")
            audio_segment = sum(chunks, AudioSegment.empty())
        else:
            print("No significant silences found, using original audio")

        # Step 3: Convert sample rate to Whisper's required 16kHz
        # This is mandatory for Whisper to function correctly
        if audio_segment.frame_rate != target_sample_rate:
            print(f"Converting sample rate from {audio_segment.frame_rate}Hz to {target_sample_rate}Hz")
            audio_segment = audio_segment.set_frame_rate(target_sample_rate)

        # Step 4: Convert to mono if needed
        # Whisper works best with mono audio
        if audio_segment.channels > 1:
            print(f"Converting from {audio_segment.channels} channels to mono")
            audio_segment = audio_segment.set_channels(1)

        # Final verification
        print("Audio preprocessing completed successfully:")
        print(f"- Duration: {len(audio_segment)/1000:.2f} seconds")
        print(f"- Channels: {audio_segment.channels}")
        print(f"- Sample Rate: {audio_segment.frame_rate}Hz")
        print(f"- Sample Width: {audio_segment.sample_width} bytes")

        return audio_segment

    except Exception as e:
        error_msg = f"Audio preprocessing failed: {str(e)}"
        print(error_msg)
        raise