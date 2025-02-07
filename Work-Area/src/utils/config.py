from pathlib import Path
import yaml
import logging
from typing import Dict

class ConfigManager:
    """
    Manages configuration loading and validation for the meeting transcriber project.
    Handles path resolution, logging setup, and configuration validation.
    """
    def __init__(self, config_path=None):
        # Resolve config.yaml path relative to main.py location
        if config_path is None:
            # Get the directory where main.py is located and specify the path to config.yaml
            self.config_path = Path(__file__).parent / "config.yaml"
        else:
            self.config_path = Path(config_path)
        
        # Load and validate configuration
        self.config = self._load_config()
        # Setup logging after config is loaded
        self._setup_logging()
        # Verify all required paths exist
        self._verify_paths()

    def _load_config(self) -> Dict:
        """
        Loads and validates the YAML configuration file.
        FileNotFoundError: If config.yaml is not found
        ValueError: If YAML is invalid or missing required sections
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
        Validates that all required configuration sections and paths are present.
        config: Dictionary containing configuration data  
        ValueError: If any required section or path is missing
        """
        # Check for required top-level sections
        required_sections = ['llm', 'output', 'paths', 'audio', 'prompts', 'document_format']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")

        # Check for required paths within the paths section
        required_paths = ['input_transcript', 'output_directory', 'audio_file']
        for path in required_paths:
            if path not in config['paths']:
                raise ValueError(f"Missing required path: {path}")

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

    def _verify_paths(self) -> None:
        """
        Verifies existence of required directories and creates them if necessary.
        Logs the verification process.
        """
        # Create output directory if it doesn't exist
        output_dir = Path(self.config['paths']['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Verified output directory: {output_dir}")

    def get_paths(self) -> Dict:
        """Returns the paths configuration section."""
        return self.config['paths']

    def get_llm_config(self) -> Dict:
        """Returns the LLM configuration section."""
        return self.config['llm']