import sys
from pathlib import Path
import logging
import torch
import whisper

# Add project root to Python path for proper import resolution
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import custom modules for audio processing, transcription, and summarization
from src.utils.config import ConfigManager
from src.audio.converter import convert_audio
from src.transcription.transcribe import transcribe_audio
from src.summary.summarize import TranscriptSummarizer

def main():
    """
    Main entry point for the audio processing, transcription, and summarization pipeline.
    
    Workflow:
    1. Configuration loading and logging setup
    2. Audio format conversion (if needed)
    3. Whisper model initialization
    4. Audio transcription
    5. Transcript summarization
    
    All paths and settings are driven by config.yaml configuration.
    """
    try:
        # Step 1: Configuration Loading and Logging Setup
        config_manager = ConfigManager()
        config = config_manager.config

        # Initialize logging with configuration from config.yaml
        logging.basicConfig(
            filename=config['output']['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config['output']['log_file']),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info("Configuration loaded and logging initialized.")

        # Step 2: Audio Processing and Conversion
        # Construct paths using PathLib for cross-platform compatibility
        audio_file_path = Path(config['paths']['audio_file'])
        converted_audio_dir = Path(config['audio_processing']['converted_audio_directory'])
        output_format = config['audio']['output_format']

        # Create converted audio directory if it doesn't exist
        converted_audio_dir.mkdir(parents=True, exist_ok=True)

        # Check if audio format conversion is needed
        if audio_file_path.suffix.lower() != f".{output_format}":
            # Generate path for converted audio file
            converted_audio_path = converted_audio_dir / f"{audio_file_path.stem}.{output_format}"
            logging.info(f"Converting {audio_file_path} to {output_format}")
            
            try:
                # Attempt audio conversion
                if not convert_audio(str(audio_file_path), output_format, str(converted_audio_path)):
                    raise ValueError(f"Audio conversion failed for {audio_file_path}")
                logging.info(f"Audio converted successfully to: {converted_audio_path}")
            except RuntimeError as e:
                logging.error(f"FFmpeg Error during conversion: {e}")
                sys.exit(1)

            # Update path to use converted audio
            audio_file_path = converted_audio_path
        else:
            logging.info("Audio already in correct format. Skipping conversion.")

        # Step 3: Whisper Model Loading
        # Configure model based on settings and available hardware
        model_name = config['transcription']['model_selection']
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Loading Whisper model '{model_name}' on {device}")
        
        try:
            # Initialize Whisper model
            model = whisper.load_model(model_name, device=device)
            logging.info(f"Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            sys.exit(1)

        # Step 4: Audio Transcription
        # Prepare transcription directory
        transcription_dir = Path(config['transcription']['transcription_directory'])
        transcription_dir.mkdir(parents=True, exist_ok=True)
        
        logging.info("Starting audio transcription...")
        try:
            # Perform transcription
            transcribe_audio(str(audio_file_path), str(transcription_dir), model)
            logging.info("Transcription completed successfully")
        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            sys.exit(1)

        # Step 5: Summary Generation
        logging.info("Starting summary generation...")
        try:
            # Initialize summarizer with configuration
            summarizer = TranscriptSummarizer(config)
            
            # Construct paths for transcript and summary
            transcript_filename = f"{audio_file_path.stem}.txt"
            transcript_path = transcription_dir / transcript_filename
            
            # Verify transcript exists
            if not transcript_path.exists():
                raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
            
            # Generate summary
            summary_path = summarizer.process_transcript(
                transcript_path=str(transcript_path),
                audio_path=str(audio_file_path)
            )
            
            logging.info(f"Summary generated and saved to: {summary_path}")
            logging.info("Complete pipeline executed successfully")
            
        except Exception as e:
            logging.error(f"Summary generation failed: {e}")
            sys.exit(1)

    except Exception as e:
        # Catch any unexpected exceptions in the main workflow
        logging.exception(f"Unexpected error in main process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
