import os
import json
import copy
from typing import Any, Optional, Tuple, Dict
from core.logger import FileLogger

class Config:
    def __init__(self, file_path: str, log_file_path: str, log_level: str = 'WARNING') -> None:
        """
        Initialize the Config object.
        :param file_path: Path to the configuration JSON file.
        :param log_file_path: Path to the log file used for recording configuration operations.
        :param log_level: Logging level (e.g., DEBUG, INFO, WARNING).
        """
        self.logger = FileLogger('Config', log_level, log_file_path)
        self.filepath = file_path
        self.data: Dict[str, Any] = {}
        self.load()

    def save(self) -> None:
        """Save the current configuration to the file."""
        try:
            tmp_path = f"{self.filepath}.tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
            os.replace(tmp_path, self.filepath)
            self.logger.info("Configuration saved successfully")
        except PermissionError:
            self.logger.error(f"No permission to write to {self.filepath}")
        except Exception as e:
            self.logger.error(f"Unexpected error while saving: {e}".replace("\n", ""))

    def load(self) -> None:
        """Load configuration data from the file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.logger.info("Configuration loaded successfully")
        except FileNotFoundError:
            self.data = {}
            self.logger.warning("Configuration file not found. Starting with an empty configuration.")
        except json.JSONDecodeError:
            self.data = {}
            self.logger.error("Failed to decode JSON. Starting with an empty configuration.")
        except Exception as e:
            self.logger.error(f"Unexpected error while loading configuration: {e}".replace("\n", ""))

    def reload(self) -> None:
        """Reload configuration from the file."""
        self.logger.info("Reloading configuration from file")
        self.load()

    def add(self, key: str, value: Any) -> None:
        """Add a key-value pair to the configuration."""
        if not isinstance(key, str):
            self.logger.error(f"Key must be a string, got {type(key).__name__}")
            return
        try:
            json.dumps(value)
        except (TypeError, ValueError) as e:
            self.logger.error(f"Value must be JSON serializable. Error: {e}")
            return

        self.data[key] = value
        self.save()
        self.logger.info(f"Added new entry: {key} = {value}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve the value associated with the given key."""
        value = self.data.get(key, default)
        self.logger.debug(f"Retrieved entry: {key} = {value}")
        return value

    def delete(self, key: str) -> None:
        """Delete the entry with the specified key."""
        if key in self.data:
            del self.data[key]
            self.save()
            self.logger.info(f"Deleted entry: {key}")

    def retrieve(self, *keys: str) -> Optional[Any]:
        """Retrieve a value from a nested configuration path."""
        try:
            config, final_key = self._traverse_config(keys)
            if not isinstance(config, dict):
                return None
            return config.get(final_key)
        except Exception as e:
            self.logger.error(f"Failed to get config value for {keys}. Error: {e}".replace("\n", ""))
            return None

    def set(self, *keys: str, value: Any) -> None:
        """Set a value in a nested configuration path."""
        try:
            config, final_key = self._traverse_config(keys, create_missing=True)
            config[final_key] = value
            self.save()
            self.logger.info(f"Updated config: {'.'.join(keys)} = {value}")
        except Exception as e:
            self.logger.error(f"Failed to set config value for {keys}. Error: {e}".replace("\n", ""))

    def remove(self, *keys: str) -> None:
        """Remove a value from a nested configuration path."""
        try:
            config, final_key = self._traverse_config(keys)
            if not isinstance(config, dict):
                self.logger.warning(f"Invalid config path: {'.'.join(keys[:-1])}")
                return
            if final_key in config:
                del config[final_key]
                self.save()
                self.logger.info(f"Removed config value: {'.'.join(keys)}")
            else:
                self.logger.warning(f"Config value not found: {'.'.join(keys)}")
        except Exception as e:
            self.logger.error(f"Failed to remove config value for {keys}. Error: {e}".replace("\n", ""))

    def _traverse_config(self, keys: Tuple[str, ...], create_missing: bool = False) -> Tuple[Dict[str, Any], str]:
        """Traverse nested dictionary using a sequence of keys."""
        config = self.data
        for key in keys[:-1]:
            if create_missing:
                if key not in config or not isinstance(config[key], dict):
                    config[key] = {}
            else:
                if key not in config:
                    raise KeyError(f"Key '{key}' not found in path: {'.'.join(keys)}")
                if not isinstance(config[key], dict):
                    raise TypeError(f"Intermediate config path '{key}' is not a dictionary")
            config = config[key]
        return config, keys[-1]

    def to_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the current configuration."""
        return copy.deepcopy(self.data)

    def from_dict(self, new_data: Dict[str, Any]) -> None:
        """Replace current configuration with a new dictionary."""
        if not isinstance(new_data, dict):
            self.logger.error("Input must be a dictionary")
            return
        self.data = copy.deepcopy(new_data)
        self.save()
        self.logger.info("Configuration replaced with new dictionary")
