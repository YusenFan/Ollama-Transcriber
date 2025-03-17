from pathlib import Path
import yaml
import logging
import os
from typing import Dict

class ConfigManager:
    """
    Manages configuration loading and validation for the meeting transcriber project.
    Handles path resolution, logging setup, and configuration validation.
    """
    def __init__(self, config_path=None):
        # Determine the application root directory (two levels up from utils/config.py)
        # This assumes config.py is in src/utils/config.py
        self.app_root = Path(__file__).parent.parent.parent.absolute()
        
        # Resolve config.yaml path relative to config.py location
        if config_path is None:
            self.config_path = Path(__file__).parent / "config.yaml"
        else:
            self.config_path = Path(config_path)
        
        # Load configuration first
        self.config = self._load_config()
        
        # Set default paths relative to application root
        self._set_default_paths()
        
        # Setup logging after config is loaded and defaults are set
        self._setup_logging()
        
        # Verify all required paths exist
        self._verify_paths()

    def _load_config(self) -> Dict:
        """
        Loads and validates the YAML configuration file.
        
        Raises:
            FileNotFoundError: If config.yaml is not found
            ValueError: If YAML is invalid or missing required sections
        
        Returns:
            Dict: Configuration dictionary
        """
        try:
            # Attempt to open and parse config.yaml
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                # Validate configuration structure
                self._validate_config(config)
                return config
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found at: {self.config_path}\n"
                f"Current working directory: {Path.cwd()}"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

    def _validate_config(self, config: Dict) -> None:
        """
        Validates that all required configuration sections are present.
        
        Args:
            config: Dictionary containing configuration data
            
        Raises:
            ValueError: If any required section is missing
        """
        # Check for required top-level sections
        required_sections = ['llm', 'output', 'paths', 'audio', 'audio_processing', 
                            'transcription', 'prompts', 'document_format']
        
        missing_sections = [section for section in required_sections if section not in config]
        if missing_sections:
            raise ValueError(f"Missing required config sections: {', '.join(missing_sections)}")
        
        # Ensure sections are dictionaries, not None
        for section in required_sections:
            if config[section] is None:
                config[section] = {}  # Initialize as empty dict if None


    def _set_default_paths(self) -> None:
        """
        Sets default paths relative to application root if not specified in config.
        Creates a more user-friendly experience without requiring direct config edits.
        """
        # Create data directories structure
        data_dir = self.app_root / "results"
        
        # Define default paths relative to app root
        default_paths = {
            'paths': {
                'input_transcript': str(data_dir / "transcribed-text"),
                'audio_file': str(data_dir / "raw-audio")
            },
            'audio_processing': {
                'converted_audio_directory': str(data_dir / "converted_audio")
            },
            'transcription': {
                'transcription_directory': str(data_dir / "transcribed-text"),
                'meeting_summary_directory': str(data_dir / "meeting-summaries")
            },
            'output': {
                'log_file': str(data_dir / "logs" / "transcript_processor.log")
            }
        }
        
        # Set defaults for any missing paths
        for section, paths in default_paths.items():
            for key, default_path in paths.items():
                # Only set default if path is empty, None, or doesn't exist in config
                if key not in self.config[section] or not self.config[section][key]:
                    self.config[section][key] = default_path
                    logging.debug(f"Set default path for {section}.{key}: {default_path}")

    def _setup_logging(self) -> None:
        """
        Configures logging with both file and console output.
        Uses logging configuration from config.yaml.
        """
        # Create log directory if it doesn't exist
        log_file = Path(self.config['output']['log_file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging with both file and console handlers
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_file)),
                logging.StreamHandler()
            ]
        )
        logging.info(f"Logging initialized: {log_file}")

    def _verify_paths(self) -> None:
        """
        Verifies existence of required directories and creates them if necessary.
        Logs the verification process.
        """
        # Create all necessary directories
        directories_to_create = [
            ('paths', 'input_transcript'),
            ('audio_processing', 'converted_audio_directory'),
            ('transcription', 'transcription_directory'),
            ('transcription', 'meeting_summary_directory')
        ]
        
        for section, key in directories_to_create:
            path = Path(self.config[section][key])
            path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Verified directory: {path}")

    def get_paths(self) -> Dict:
        """Returns the paths configuration section."""
        return self.config['paths']

    def get_llm_config(self) -> Dict:
        """Returns the LLM configuration section."""
        return self.config['llm']
    
    def update_config(self, updates: Dict) -> None:
        """
        Updates configuration with new values, typically from CLI or GUI.
        
        Args:
            updates: Dictionary containing configuration updates
                    Format: {'section': {'key': 'value'}}
        """
        # Update configuration with new values
        for section, values in updates.items():
            if section in self.config:
                for key, value in values.items():
                    if value:  # Only update if value is not None/empty
                        self.config[section][key] = value
                        logging.info(f"Updated config {section}.{key} = {value}")
        
        # Re-verify paths after updates
        self._verify_paths()