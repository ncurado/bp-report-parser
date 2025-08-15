"""
Configuration management for BP Extractor.

Author: Nuno Curado
Date: 15th of August, 2025
Version: 1.1

License:
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

import yaml
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Union
import re


@dataclass
class ExtractionConfig:
    """Configuration for data extraction patterns and formats."""
    
    # Date and time formats
    input_date_format: str = "%d %B, %y %H:%M"
    output_date_format: str = "%m/%d/%y %H:%M"
    
    # Regex pattern for extracting BP data
    bp_data_pattern: str = r"(\d{1,2}\s\w+,\s\d{2})\s(\d{2}:\d{2})\s+(\d+)\s+(\d+)\s+(\d+)"
    
    # CSV output settings
    csv_headers: List[str] = None
    csv_delimiter: str = ","
    
    # Processing settings
    skip_first_page: bool = True
    progress_bar: bool = True
    
    # Validation ranges
    min_systolic: int = 50
    max_systolic: int = 300
    min_diastolic: int = 30
    max_diastolic: int = 200
    min_heart_rate: int = 30
    max_heart_rate: int = 250
    
    def __post_init__(self):
        """Initialize default values that need to be mutable."""
        if self.csv_headers is None:
            self.csv_headers = ["Date/Time", "Systolic", "Diastolic", "Pulse"]
    
    def validate_bp_values(self, systolic: int, diastolic: int, heart_rate: int) -> bool:
        """
        Validate if blood pressure and heart rate values are within reasonable ranges.
        
        Args:
            systolic: Systolic blood pressure
            diastolic: Diastolic blood pressure
            heart_rate: Heart rate in BPM
            
        Returns:
            bool: True if all values are within valid ranges
        """
        return (
            self.min_systolic <= systolic <= self.max_systolic and
            self.min_diastolic <= diastolic <= self.max_diastolic and
            self.min_heart_rate <= heart_rate <= self.max_heart_rate
        )
    
    def get_compiled_pattern(self) -> re.Pattern:
        """
        Get the compiled regex pattern for BP data extraction.
        
        Returns:
            re.Pattern: Compiled regex pattern
        """
        return re.compile(self.bp_data_pattern)


class ConfigManager:
    """Manages configuration loading and validation."""
    
    DEFAULT_CONFIG_FILENAME = "bp_extractor_config.yaml"
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        self.config_path = self._resolve_config_path(config_path)
        self._config: Optional[ExtractionConfig] = None
    
    def _resolve_config_path(self, config_path: Optional[Union[str, Path]]) -> Path:
        """
        Resolve the configuration file path.
        
        Args:
            config_path: User-provided config path or None
            
        Returns:
            Path: Resolved configuration file path
        """
        if config_path:
            return Path(config_path)
        
        # Look for config file in several locations
        possible_paths = [
            Path.cwd() / self.DEFAULT_CONFIG_FILENAME,
            Path(__file__).parent / self.DEFAULT_CONFIG_FILENAME,
            Path.home() / ".config" / "bp_extractor" / self.DEFAULT_CONFIG_FILENAME,
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Return the first option as default location for new config
        return possible_paths[0]
    
    def load_config(self) -> ExtractionConfig:
        """
        Load configuration from file or create default.
        
        Returns:
            ExtractionConfig: Loaded or default configuration
        """
        if self._config is not None:
            return self._config
        
        if self.config_path.exists():
            try:
                self._config = self._load_from_file()
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                print("Using default configuration.")
                self._config = ExtractionConfig()
        else:
            print(f"No configuration file found at {self.config_path}")
            print("Using default configuration.")
            self._config = ExtractionConfig()
        
        return self._config
    
    def _load_from_file(self) -> ExtractionConfig:
        """Load configuration from file based on extension."""
        suffix = self.config_path.suffix.lower()
        
        with open(self.config_path, 'r', encoding='utf-8') as file:
            if suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(file)
            elif suffix == '.json':
                data = json.load(file)
            else:
                raise ValueError(f"Unsupported configuration file format: {suffix}")
        
        # Create ExtractionConfig from loaded data
        return ExtractionConfig(**data)
    
    def save_config(self, config: Optional[ExtractionConfig] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save. If None, saves current config.
        """
        if config is None:
            config = self.load_config()
        
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary
        config_dict = asdict(config)
        
        # Save based on file extension
        suffix = self.config_path.suffix.lower()
        
        with open(self.config_path, 'w', encoding='utf-8') as file:
            if suffix in ['.yaml', '.yml']:
                yaml.safe_dump(config_dict, file, default_flow_style=False, indent=2)
            elif suffix == '.json':
                json.dump(config_dict, file, indent=2)
            else:
                raise ValueError(f"Unsupported configuration file format: {suffix}")
        
        print(f"Configuration saved to: {self.config_path}")
    
    def create_default_config(self) -> ExtractionConfig:
        """
        Create and save a default configuration file.
        
        Returns:
            ExtractionConfig: Default configuration
        """
        config = ExtractionConfig()
        self.save_config(config)
        return config
    
    @property
    def config(self) -> ExtractionConfig:
        """Get the current configuration, loading if necessary."""
        return self.load_config()


def get_config(config_path: Optional[Union[str, Path]] = None) -> ExtractionConfig:
    """
    Convenience function to get configuration.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ExtractionConfig: Loaded configuration
    """
    manager = ConfigManager(config_path)
    return manager.load_config()
