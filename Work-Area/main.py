import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import configuration management
from src.utils.config import ConfigManager
from src.audio.converter import (
    check_ffmpeg,
    get_supported_formats,
    validate_format,
    convert_audio
)

def main():
    """
    Main entry point for the meeting transcriber application.
    Initializes configuration and sets up the processing pipeline.
    """
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        logging.info("Configuration loaded successfully")

        # Log important paths for verification
        paths = config_manager.get_paths()
        logging.info("Configured Paths:")
        logging.info(f"Input transcript path: {paths['input_transcript']}")
        logging.info(f"Output directory: {paths['output_directory']}")
        logging.info(f"Audio file path: {paths['audio_file']}")

    except Exception as e:
        logging.error(f"Initialization error: {e}")
        raise

if __name__ == "__main__":
    main()

