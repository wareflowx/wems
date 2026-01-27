"""Backup Configuration Module

Provides configuration management for backup system:
- Load/save configuration from JSON file
- Default configuration values
- Validation of configuration values
- Integration with BackupScheduler
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import time

logger = logging.getLogger(__name__)


class BackupConfig:
    """
    Manages backup configuration persistence and validation.

    Handles loading, saving, and validating backup configuration
    from a JSON configuration file.

    Attributes:
        config_path: Path to configuration file
        config: Current configuration dictionary
    """

    DEFAULT_CONFIG = {
        "enabled": True,
        "automatic_daily": True,
        "backup_time": "02:00",
        "backup_on_shutdown": False,
        "backup_directory": "backups",
        "retention_days": 30,
        "retention_weeks": 12,
        "retention_months": 12,
        "compress_backups": False,
        "verify_after_backup": True,
        "keep_manual_backups": True,
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize backup configuration.

        Args:
            config_path: Path to config file (default: config/backup_config.json)
        """
        self.config_path = config_path or Path("config/backup_config.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary (defaults if file doesn't exist)

        Raises:
            json.JSONDecodeError: If config file is corrupted
        """
        if not self.config_path.exists():
            logger.info("No backup config file found, using defaults")
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)

            # Merge with defaults to fill missing values
            config = self.DEFAULT_CONFIG.copy()
            config.update(loaded_config)

            logger.info(f"Backup config loaded from {self.config_path}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid backup config JSON: {e}")
            logger.info("Using default configuration")
            return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate before saving
        errors = self.validate_config()
        if errors:
            raise ValueError(f"Invalid configuration: {errors}")

        try:
            # Create directory if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file with nice formatting
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            logger.info(f"Backup config saved to {self.config_path}")
            return True

        except (OSError, IOError) as e:
            logger.error(f"Failed to save backup config: {e}")
            return False

    def validate_config(self) -> list[str]:
        """
        Validate current configuration.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate backup_time format
        backup_time = self.config.get("backup_time", "")
        if not self._is_valid_time(backup_time):
            errors.append(f"Invalid backup_time format: '{backup_time}' (expected HH:MM)")

        # Validate retention values
        for key in ["retention_days", "retention_weeks", "retention_months"]:
            value = self.config.get(key)
            if not isinstance(value, int) or value < 1:
                errors.append(f"{key} must be a positive integer")

        # Validate backup_directory
        backup_dir = self.config.get("backup_directory", "")
        if not isinstance(backup_dir, str) or not backup_dir.strip():
            errors.append("backup_directory must be a non-empty string")

        # Validate boolean values
        for key in ["enabled", "automatic_daily", "backup_on_shutdown",
                     "compress_backups", "verify_after_backup", "keep_manual_backups"]:
            value = self.config.get(key)
            if not isinstance(value, bool):
                errors.append(f"{key} must be a boolean")

        return errors

    def _is_valid_time(self, time_str: str) -> bool:
        """
        Validate time format (HH:MM).

        Args:
            time_str: Time string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            hour, minute = map(int, time_str.split(":"))
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: New value
        """
        self.config[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.config.update(updates)

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        logger.info("Backup config reset to defaults")

    def get_scheduler_config(self) -> Dict[str, Any]:
        """
        Get configuration subset for BackupScheduler.

        Returns:
            Dictionary with scheduler-relevant configuration
        """
        return {
            "enabled": self.config["enabled"],
            "automatic_daily": self.config["automatic_daily"],
            "backup_time": self.config["backup_time"],
        }

    def get_backup_directory(self) -> Path:
        """
        Get backup directory path.

        Returns:
            Path to backup directory
        """
        return Path(self.config["backup_directory"])

    def get_max_backups(self) -> int:
        """
        Get maximum number of backups to keep.

        Returns:
            Maximum backup count (based on retention_days)
        """
        return self.config["retention_days"]

    def is_enabled(self) -> bool:
        """
        Check if backups are enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.config.get("enabled", True)

    def should_verify(self) -> bool:
        """
        Check if backups should be verified after creation.

        Returns:
            True if verification enabled, False otherwise
        """
        return self.config.get("verify_after_backup", True)

    def keep_manual_backups(self) -> bool:
        """
        Check if manual backups should be kept indefinitely.

        Returns:
            True if manual backups preserved, False otherwise
        """
        return self.config.get("keep_manual_backups", True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "BackupConfig":
        """
        Create BackupConfig from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            BackupConfig instance
        """
        config = cls()
        config.config = config_dict
        return config
