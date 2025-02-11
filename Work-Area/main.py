import sys
from pathlib import Path
import logging
import torch  # Import torch for device selection
import whisper # Import Whisper for model loading

# Add project root to Python path (essential for imports)
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import ConfigManager
from src.audio.converter import convert_audio
from src.transcription.transcribe import transcribe_audio  # Import transcribe_audio
# from src.summary.summarizer import TranscriptProcessor  # For summarization (commented out)

def main():
    """Main entry point. Orchestrates the workflow."""
    try:
        # 1. Load Configuration:
        config_manager = ConfigManager()
        config = config_manager.config

        # 2. Logging Setup:
        logging.info("Configuration loaded and logging set up.")

        # 3. Audio Processing (Conversion):
        audio_file_path = Path(config['paths']['audio_file'])
        converted_audio_dir = Path(config['audio_processing']['converted_audio_directory'])
        output_format = config['audio']['output_format']

        if audio_file_path.suffix.lower() != output_format:  # Check if conversion is needed
            converted_audio_path = converted_audio_dir / f"{audio_file_path.stem}.{output_format}" # Corrected file extension
            print(f"Converting {audio_file_path} to {output_format} and saving to {converted_audio_path}")

            try:
                if not convert_audio(str(audio_file_path), output_format, str(converted_audio_path)):
                    raise ValueError(f"Audio conversion failed for {audio_file_path}")
            except RuntimeError as e:
                logging.error(f"FFmpeg Error: {e}")
                sys.exit(1)

            audio_file_path = converted_audio_path  # Use the *converted* path for transcription
            logging.info(f"Audio converted to: {audio_file_path}")
        else:
            logging.info("No audio conversion needed. Skipping.")

        # 4. Whisper Model Loading:
        model_name = config['transcription']['model_selection']
        device = "cuda" if torch.cuda.is_available() else "cpu"  # GPU check
        print(f"Loading Whisper model '{model_name}' on {device}...")
        try:
            model = whisper.load_model(model_name, device=device)
            print(f"Whisper model '{model_name}' loaded successfully on {device}.")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            sys.exit(1)

        # 5. Transcription:
        logging.info("Starting transcription...")
        transcription_dir = config['transcription']['transcription_directory']
        try:
            transcribe_audio(str(audio_file_path), str(transcription_dir), model)  # Pass model
        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            sys.exit(1)

    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        sys.exit(1)

        '''# 6. Summarization:
        logging.info("Starting summarization...")
        processor = TranscriptProcessor(config)  # Initialize the summarizer
        summary_file_path = processor.process_and_save_summary(transcription)  # Generate and save the summary
        logging.info(f"Summary saved to: {summary_file_path}")

        logging.info("Meeting transcription and summarization complete.")  # Log completion message'''

    except Exception as e:  # Catch any exceptions that occur during the process
        logging.exception(f"An error occurred: {e}")  # Debug
        sys.exit(1)  # Exit the program with an error code

if __name__ == "__main__":
    main()  # Call the main function when the script is executed