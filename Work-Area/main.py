import sys
from pathlib import Path
import logging

# Add project root to Python path. This is crucial for importing modules
# within your project correctly, even if you run the script from a different
# directory.  It makes the imports relative to your project's root.
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import necessary modules.
from src.utils.config import ConfigManager  # For loading config.yaml
from src.audio.converter import convert_audio  # For audio conversion
# from src.transcription.transcriber import transcribe_audio  # For transcription
# from src.summary.summarizer import TranscriptProcessor  # For summarization


def main():
    """
    Main entry point. Orchestrates the workflow (audio conversion only for now).
    """
    try:
        # 1. Load Configuration (using ConfigManager):
        config_manager = ConfigManager()  # Create ConfigManager object
        config = config_manager.config  # Access the config

        # 2. Logging Setup:
        logging.info("Configuration loaded and logging set up.")  # Just log the confirmation

        # 3. Audio Processing (Conversion):
        audio_file_path = Path(config['paths']['audio_file'])
        converted_audio_dir = Path(config['audio_processing']['converted_audio_directory'])
        output_format = config['audio']['output_format']

        if audio_file_path.suffix.lower() != output_format:
            converted_audio_path = converted_audio_dir / f"{audio_file_path.stem}{output_format}"
            print(f"Converting {audio_file_path} to {output_format} and saving to {converted_audio_path}") # Debug print

            try:
                if not convert_audio(str(audio_file_path), output_format, str(converted_audio_path)):
                    raise ValueError(f"Audio conversion failed for {audio_file_path}")
            except RuntimeError as e:
                logging.error(f"FFmpeg Error: {e}")
                sys.exit(1)

            audio_file_path = converted_audio_path
            logging.info(f"Audio converted to: {audio_file_path}")
        else:
            logging.info("No audio conversion needed. Skipping.")

        '''# 5. Transcription:
        logging.info("Starting transcription...")
        transcription = transcribe_audio(str(audio_file_path), config)  # Perform transcription
        if not transcription:  # Check if transcription was successful
            raise ValueError("Transcription failed.")

        # 6. Summarization:
        logging.info("Starting summarization...")
        processor = TranscriptProcessor(config)  # Initialize the summarizer
        summary_file_path = processor.process_and_save_summary(transcription)  # Generate and save the summary
        logging.info(f"Summary saved to: {summary_file_path}")

        logging.info("Meeting transcription and summarization complete.")  # Log completion message'''

    except Exception as e:  # Catch any exceptions that occur during the process
        logging.exception(f"An error occurred: {e}")  # Log the exception with traceback (very important for debugging)
        sys.exit(1)  # Exit the program with an error code

if __name__ == "__main__":
    main()  # Call the main function when the script is executed