import sys
from pathlib import Path
import logging
import torch
import whisper
import argparse

# Add project root to Python path for proper import resolution
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import custom modules for audio processing, transcription, and summarization
from src.utils.config import ConfigManager
from src.audio.converter import convert_audio
from src.transcription.transcribe import transcribe_audio
from src.summary.summarize import TranscriptSummarizer
from src.utils.input_handler import select_audio_file

def parse_arguments():
    """
    Parse command line arguments for the audio transcription and summarization tool.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Audio Transcription and Summarization Tool',
        epilog='''
Examples:
  # Use GUI to select audio file
  python main.py --gui
  
  # Process specific audio file with default settings
  python main.py --audio path/to/recording.mp3
  
  # Specify output directory and Whisper model
  python main.py --audio path/to/recording.mp3 --output path/to/output --transcript medium
  
  # Use specific LLM model
  python main.py --audio path/to/recording.mp3 --llm mistral:latest
  
  # Full example with all options
  python main.py --audio path/to/recording.mp3 --output path/to/summaries --transcript medium --llm mistral:latest
''',
        formatter_class=argparse.RawDescriptionHelpFormatter  # Preserves formatting in epilog
    )
    
    parser.add_argument('--audio', type=str, 
                      help='Path to audio file to transcribe and summarize')
    
    parser.add_argument('--output', type=str,
                      help='Path to output directory for saving summaries')
    
    parser.add_argument('--llm', type=str,
                      help='Name of Ollama model to use for summarization (default: from config.yaml)')
    
    parser.add_argument('--transcript', type=str, 
                      choices=['tiny', 'base', 'small', 'medium', 'large'],
                      help='Whisper model selection for transcription (default: from config.yaml)')
    
    parser.add_argument('--gui', action='store_true',
                      help='Launch GUI file picker to select audio file')
    
    return parser.parse_args()

def main():
    """
    Main entry point for the audio processing, transcription, and summarization pipeline.
    
    Workflow:
    1. Parse command line arguments
    2. Configuration loading and logging setup
    3. Audio format conversion (if needed)
    4. Whisper model initialization
    5. Audio transcription
    6. Transcript summarization
    
    All paths and settings are driven by config.yaml configuration with optional
    overrides from command line arguments.
    """
    try:
        # Step 1: Parse command line arguments
        args = parse_arguments()
        
        # Step 2: Configuration Loading and Logging Setup
        config_manager = ConfigManager()
        config = config_manager.config

        # Process command line arguments to override config settings
        # If GUI flag is set, launch file picker
        if args.gui:
            file_path = select_audio_file()
            if file_path:
                config['paths']['audio_file'] = file_path
                print(f"Selected audio file: {file_path}")
            else:
                print("No audio file selected. Exiting.")
                sys.exit(1)
        # Otherwise use CLI arguments if provided
        elif args.audio:
            config['paths']['audio_file'] = args.audio
            print(f"Using audio file from command line: {args.audio}")

        # Update other config values if provided
        if args.output:
            config['transcription']['meeting_summary_directory'] = args.output
            print(f"Output directory set to: {args.output}")
        if args.llm:
            config['llm']['model_name'] = args.llm
            print(f"LLM model set to: {args.llm}")
        if args.transcript:
            config['transcription']['model_selection'] = args.transcript
            print(f"Whisper model set to: {args.transcript}")

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
        
        # Log the configuration settings being used
        logging.info(f"Audio file: {config['paths']['audio_file']}")
        logging.info(f"Output directory: {config['transcription']['meeting_summary_directory']}")
        logging.info(f"LLM model: {config['llm']['model_name']}")
        logging.info(f"Whisper model: {config['transcription']['model_selection']}")

        # Step 3: Audio Processing and Conversion
        # Construct paths using PathLib for cross-platform compatibility
        audio_file_path = Path(config['paths']['audio_file'])
        
        # Verify that audio file exists
        if not audio_file_path.exists():
            logging.error(f"Audio file not found: {audio_file_path}")
            print(f"Error: Audio file not found: {audio_file_path}")
            sys.exit(1)
            
        converted_audio_dir = Path(config['audio_processing']['converted_audio_directory'])
        output_format = config['audio']['output_format']

        # Create converted audio directory if it doesn't exist
        converted_audio_dir.mkdir(parents=True, exist_ok=True)

        # Check if audio format conversion is needed
        if audio_file_path.suffix.lower() != f".{output_format}":
            # Generate path for converted audio file
            converted_audio_path = converted_audio_dir / f"{audio_file_path.stem}.{output_format}"
            logging.info(f"Converting {audio_file_path} to {output_format}")
            print(f"Converting audio to {output_format} format...")
            
            try:
                # Attempt audio conversion
                if not convert_audio(str(audio_file_path), output_format, str(converted_audio_path)):
                    raise ValueError(f"Audio conversion failed for {audio_file_path}")
                logging.info(f"Audio converted successfully to: {converted_audio_path}")
                print(f"Audio converted successfully")
            except RuntimeError as e:
                logging.error(f"FFmpeg Error during conversion: {e}")
                print(f"Error: FFmpeg failed to convert audio: {e}")
                sys.exit(1)
            except FileNotFoundError as e:
                logging.error(f"File error during conversion: {e}")
                print(f"Error: {e}")
                sys.exit(1)

            # Update path to use converted audio
            audio_file_path = converted_audio_path
        else:
            logging.info("Audio already in correct format. Skipping conversion.")
            print("Audio already in correct format. Skipping conversion.")

        # Step 4: Whisper Model Loading
        # Configure model based on settings and available hardware
        model_name = config['transcription']['model_selection']
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Loading Whisper model '{model_name}' on {device}")
        print(f"Loading Whisper model '{model_name}' on {device}...")
        
        try:
            # Initialize Whisper model
            model = whisper.load_model(model_name, device=device)
            logging.info(f"Whisper model loaded successfully")
            print("Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            print(f"Error: Failed to load Whisper model: {e}")
            sys.exit(1)

        # Step 5: Audio Transcription
        # Prepare transcription directory
        transcription_dir = Path(config['transcription']['transcription_directory'])
        transcription_dir.mkdir(parents=True, exist_ok=True)
        
        logging.info("Starting audio transcription...")
        print("Starting audio transcription...")
        try:
            # Perform transcription
            transcribe_audio(str(audio_file_path), str(transcription_dir), model)
            logging.info("Transcription completed successfully")
            print("Transcription completed successfully")
        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            print(f"Error: Transcription failed: {e}")
            sys.exit(1)

        # Step 6: Summary Generation
        logging.info("Starting summary generation...")
        print("Starting summary generation...")
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
            print(f"Summary generated and saved to: {summary_path}")
            logging.info("Complete pipeline executed successfully")
            print("Complete pipeline executed successfully")
            
        except Exception as e:
            logging.error(f"Summary generation failed: {e}")
            print(f"Error: Summary generation failed: {e}")
            sys.exit(1)

    except Exception as e:
        # Catch any unexpected exceptions in the main workflow
        logging.exception(f"Unexpected error in main process: {e}")
        print(f"Error: Unexpected error in main process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
