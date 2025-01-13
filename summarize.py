import yaml
from pathlib import Path
import requests
import logging
from typing import Dict, Optional
from datetime import datetime
import sys
from time import sleep
from tqdm import tqdm
from pydub import AudioSegment

# Load config.yaml
def load_config():
    """Load and validate configuration from YAML file."""
    config_path = Path(__file__).parent / "config.yaml"
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            validate_config(config)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in configuration file: {e}")
    
def validate_config(config: dict) -> None:
    """Validate essential configuration elements."""
    required_sections = ['llm', 'output', 'paths', 'prompts', 'document_format']
    
    # Check for required sections
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
    
    # Validate paths
    input_path = Path(config['paths']['input_transcript'])
    if not input_path.parent.exists():
        raise ValueError(f"Input directory does not exist: {input_path.parent}")
    
    # Validate LLM settings
    required_llm_fields = ['model_name', 'max_retries', 'retry_delay', 'api_url', 'options']
    for field in required_llm_fields:
        if field not in config['llm']:
            raise ValueError(f"Missing required LLM config field: {field}")
    
    # Validate output settings
    if 'format' not in config['output'] or config['output']['format'] not in ['md', 'txt']:
        raise ValueError("Invalid or missing output format. Must be 'md' or 'txt'")

# Load configuration at module level
CONFIG = load_config()

def get_audio_duration(audio_path: str) -> str:
    """
    Get audio duration and return formatted string.
    audio_path: Path to audio file from config.yaml
    Outputs: Formatted duration string (e.g., "1h 30m 45s") or "Duration unavailable"
    """
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Get duration in seconds
        duration_seconds = len(audio) / 1000.0
        
        # Format duration
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
            
    except Exception as e:
        logging.warning(f"Could not determine audio duration: {e}")
        return "Duration unavailable"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG['output']['log_file']),
        logging.StreamHandler(sys.stdout)
    ]
)

def generate_metadata() -> Dict[str, str]:
    """
    Generate metadata for the document.
    Returns a dictionary with metadata fields from config.
    """
    metadata = {}
    
    # Get configured fields from config
    metadata_fields = CONFIG['document_format']['metadata']['fields']
    
    # Add standard fields
    metadata["date"] = datetime.now().strftime(CONFIG['document_format']['metadata']['date_format'])
    
    # Add default values for other fields
    default_values = {
        "duration": "Not specified",
        "participants": "Not specified",
        "location": "Not specified",
        "meeting_type": "Not specified"
    }
    
    # Only include fields that are specified in config
    for field in metadata_fields:
        metadata[field] = default_values.get(field, "Not specified")
    
    return metadata

class TranscriptProcessor:
    """
    A comprehensive processor for handling transcript summarization and formatting
    using local LLMs via Ollama.
    """
    
    def __init__(
        self, 
        model_name: str = CONFIG['llm']['model_name'],
        max_retries: int = CONFIG['llm']['max_retries'],
        retry_delay: int = CONFIG['llm']['retry_delay']
    ):
        self.model_name = model_name
        self.api_url = CONFIG['llm']['api_url']
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logging.info(f"Initialized TranscriptProcessor with model: {model_name}")

    def read_transcript(self, file_path: str) -> str:
        """Reads and validates the transcript file."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Transcript file not found: {file_path}")
                
            with path.open('r', encoding='utf-8') as file:
                content = file.read()
                logging.info(f"Successfully read transcript: {file_path}")
                return content
                
        except UnicodeDecodeError:
            logging.error(f"Failed to decode file: {file_path}")
            raise
            
    def generate_llm_response(self, prompt: str, text: str) -> str:
        """Generates a response from Ollama with retry mechanism."""
        for attempt in range(self.max_retries):
            try:
                data = {
                    "model": self.model_name,
                    "prompt": f"{prompt}\n\nText: {text}",
                    "stream": False,
                    "options": CONFIG['llm']['options']
                }
                
                response = requests.post(self.api_url, json=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()['response']
                if not result.strip():
                    raise ValueError("Empty response from LLM")
                    
                logging.info(f"Successfully generated response on attempt {attempt + 1}")
                return result
                
            except (requests.exceptions.RequestException, KeyError) as e:
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    sleep(self.retry_delay)
                else:
                    raise ConnectionError("Failed to connect to Ollama after max retries")

    def generate_summary(self, text: str) -> str:
        """Generates a comprehensive meeting summary."""
        prompt = CONFIG['prompts']['summary_prompt'] # Retrieves the instructions within config.yaml
        return self.generate_llm_response(prompt, text) # Returns the actual summary
    

    
    def generate_summaries(self, transcript: str) -> Dict[str, str]:
        """Generate summary with progress tracking using tqdm."""
        with tqdm(total=1, desc="Generating summary", unit="summary") as pbar:
            summary = self.generate_summary(transcript)
            pbar.update(1)
        return {"summary": summary} # Creates a dictionary using the text from LLM and places it into the key "summary"

    def format_document(self, summaries: Dict[str, str], metadata: Optional[Dict] = None) -> str:
        """Formats summary into a structured document."""
        metadata_section = ""
        if metadata:
            metadata_lines = [CONFIG['document_format']['metadata']['header']]
            for field in CONFIG['document_format']['metadata']['fields']:
                value = metadata.get(field, 'Not specified')
                metadata_lines.append(f"- {field.title()}: {value}")
            metadata_section = "\n".join(metadata_lines + ["\n"])

        generation_timestamp = datetime.now().strftime(
            CONFIG['document_format']['metadata']['date_format']
        )

        formatted_text = CONFIG['document_format']['template'].format(
            metadata_section=metadata_section,
            summary=summaries['summary'], # Formatting the final document and places our key of "summary" into the output
            generation_timestamp=generation_timestamp
        )

        return formatted_text

    def save_document(
        self, 
        formatted_text: str, 
        output_path: str, 
        format: str = CONFIG['output']['format']
    ):
        """Saves the formatted document to file."""
        supported_formats = ['md', 'txt']
        if format not in supported_formats:
            raise ValueError(f"Unsupported format. Use one of: {supported_formats}")
            
        try:
            path = Path(output_path)
            path.write_text(formatted_text, encoding='utf-8')
            logging.info(f"Successfully saved document to: {output_path}")
            
        except Exception as e:
            logging.error(f"Failed to save document: {str(e)}")
            raise

def main():
    try:
        # Initialize processor using config
        processor = TranscriptProcessor()
        
        # Create output directory if it doesn't exist
        output_dir = Path(CONFIG['paths']['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Config for input directory
        file_path = Path(CONFIG['paths']['input_transcript'])
        transcript = processor.read_transcript(str(file_path))

        # Get audio duration
        audio_duration = get_audio_duration(CONFIG['paths']['audio_file'])
        logging.info(f"Audio duration: {audio_duration}")
        
        # Generate summaries with tqdm progress tracking
        summaries = processor.generate_summaries(transcript)
        
        # Add metadata with actual duration and config defaults
        metadata = {
            "date": datetime.now().strftime(CONFIG['document_format']['metadata']['date_format']),
            "duration": audio_duration,
            "participants": CONFIG['document_format']['metadata']['defaults']['participants'],
            "location": CONFIG['document_format']['metadata']['defaults']['location'],
            "meeting_type": CONFIG['document_format']['metadata']['defaults']['meeting_type']
        }
        
        # Format and save document
        formatted_doc = processor.format_document(summaries, metadata)
        
        # Construct output filename using config directory and format
        output_filename = f"meeting_summary_{datetime.now().strftime('%Y%m%d')}.{CONFIG['output']['format']}"
        output_path = output_dir / output_filename
        
        # Save document
        processor.save_document(
            formatted_text=formatted_doc,
            output_path=str(output_path),
            format=CONFIG['output']['format']
        )
        
        logging.info(f"Successfully processed transcript and saved to: {output_path}")
        
    except Exception as e:
        logging.error(f"Failed to process transcript: {str(e)}")
        raise

if __name__ == "__main__":
    main()