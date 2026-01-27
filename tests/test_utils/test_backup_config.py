"""Tests for backup configuration module.

Unit tests for BackupConfig covering configuration loading,
saving, validation, and management.
"""

import json
import tempfile
import shutil
from pathlib import Path

import pytest

from utils.backup_config import BackupConfig


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def config(temp_config_dir):
    """Create BackupConfig with temporary config path."""
    config_path = Path(temp_config_dir) / "backup_config.json"
    return BackupConfig(config_path=config_path)


class TestBackupConfigInit:
    """Test BackupConfig initialization."""

    def test_init_with_defaults(self, temp_config_dir):
        """Test initialization with default path."""
        config = BackupConfig()

        assert config.config_path == Path("config/backup_config.json")
        assert config.config["backup_time"] == "02:00"
        assert config.config["retention_days"] == 30

    def test_init_with_custom_path(self, temp_config_dir):
        """Test initialization with custom config path."""
        config_path = Path(temp_config_dir) / "custom_config.json"
        config = BackupConfig(config_path=config_path)

        assert config.config_path == config_path

    def test_init_loads_from_file(self, temp_config_dir):
        """Test loading configuration from existing file."""
        config_path = Path(temp_config_dir) / "backup_config.json"

        # Create config file
        config_data = {
            "backup_time": "03:30",
            "retention_days": 60,
            "enabled": False,
        }
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = BackupConfig(config_path=config_path)

        # Should load values from file
        assert config.config["backup_time"] == "03:30"
        assert config.config["retention_days"] == 60
        assert config.config["enabled"] is False
        # Default values should be preserved
        assert config.config["automatic_daily"] is True

    def test_init_uses_defaults_when_no_file(self, temp_config_dir):
        """Test that defaults are used when config file doesn't exist."""
        config_path = Path(temp_config_dir) / "nonexistent_config.json"
        config = BackupConfig(config_path=config_path)

        assert config.config == BackupConfig.DEFAULT_CONFIG

    def test_init_handles_corrupted_json(self, temp_config_dir):
        """Test handling of corrupted JSON file."""
        config_path = Path(temp_config_dir) / "corrupted.json"

        # Create invalid JSON file
        with open(config_path, "w") as f:
            f.write("{invalid json}")

        config = BackupConfig(config_path=config_path)

        # Should fall back to defaults
        assert config.config == BackupConfig.DEFAULT_CONFIG


class TestSaveConfig:
    """Test configuration saving."""

    def test_save_creates_file(self, config):
        """Test that save creates config file."""
        result = config.save_config()

        assert result is True
        assert config.config_path.exists()

    def test_save_creates_directory(self, temp_config_dir):
        """Test that save creates directory if needed."""
        config_path = Path(temp_config_dir) / "subdir" / "config.json"
        config = BackupConfig(config_path=config_path)

        result = config.save_config()

        assert result is True
        assert config_path.parent.exists()
        assert config_path.exists()

    def test_save_valid_json(self, config):
        """Test that saved file is valid JSON."""
        config.save_config()

        with open(config.config_path, "r") as f:
            loaded = json.load(f)

        assert loaded == config.config

    def test_save_with_validation_error(self, config):
        """Test that save raises error for invalid config."""
        # Set invalid backup_time
        config.config["backup_time"] = "invalid"

        with pytest.raises(ValueError, match="Invalid configuration"):
            config.save_config()

    def test_save_persist_changes(self, config):
        """Test that changes persist after save."""
        # Modify config
        config.config["backup_time"] = "05:00"
        config.config["retention_days"] = 90
        config.save_config()

        # Create new config to load from file
        new_config = BackupConfig(config_path=config.config_path)

        assert new_config.config["backup_time"] == "05:00"
        assert new_config.config["retention_days"] == 90


class TestValidation:
    """Test configuration validation."""

    def test_validate_valid_config(self, config):
        """Test validation of valid configuration."""
        errors = config.validate_config()

        assert errors == []

    def test_validate_invalid_time_format(self, config):
        """Test validation rejects invalid time format."""
        config.config["backup_time"] = "25:00"  # Invalid hour

        errors = config.validate_config()

        assert len(errors) > 0
        assert any("backup_time" in e for e in errors)

    def test_validate_negative_retention(self, config):
        """Test validation rejects negative retention."""
        config.config["retention_days"] = -10

        errors = config.validate_config()

        assert len(errors) > 0
        assert any("retention_days" in e for e in errors)

    def test_validate_zero_retention(self, config):
        """Test validation rejects zero retention."""
        config.config["retention_days"] = 0

        errors = config.validate_config()

        assert len(errors) > 0
        assert any("retention_days" in e for e in errors)

    def test_validate_empty_backup_directory(self, config):
        """Test validation rejects empty backup directory."""
        config.config["backup_directory"] = ""

        errors = config.validate_config()

        assert len(errors) > 0
        assert any("backup_directory" in e for e in errors)

    def test_validate_non_boolean_enabled(self, config):
        """Test validation rejects non-boolean enabled."""
        config.config["enabled"] = "yes"

        errors = config.validate_config()

        assert len(errors) > 0
        assert any("enabled" in e for e in errors)


class TestGettersSetters:
    """Test getter and setter methods."""

    def test_get_existing_key(self, config):
        """Test getting existing configuration value."""
        assert config.get("backup_time") == "02:00"
        assert config.get("retention_days") == 30

    def test_get_missing_key_with_default(self, config):
        """Test getting missing key with default."""
        assert config.get("nonexistent", "default") == "default"
        assert config.get("nonexistent") is None

    def test_set_value(self, config):
        """Test setting configuration value."""
        config.set("backup_time", "06:00")

        assert config.config["backup_time"] == "06:00"

    def test_update_multiple_values(self, config):
        """Test updating multiple values at once."""
        config.update({
            "backup_time": "07:30",
            "retention_days": 60,
            "enabled": False,
        })

        assert config.config["backup_time"] == "07:30"
        assert config.config["retention_days"] == 60
        assert config.config["enabled"] is False

    def test_update_preserves_other_values(self, config):
        """Test that update preserves existing values."""
        config.update({"backup_time": "08:00"})

        # Other values should be preserved
        assert config.config["retention_days"] == 30
        assert config.config["enabled"] is True


class TestUtilityMethods:
    """Test utility and convenience methods."""

    def test_get_scheduler_config(self, config):
        """Test getting scheduler configuration subset."""
        scheduler_config = config.get_scheduler_config()

        assert scheduler_config["enabled"] is True
        assert scheduler_config["automatic_daily"] is True
        assert scheduler_config["backup_time"] == "02:00"
        # Should not include all config values
        assert "retention_days" not in scheduler_config

    def test_get_backup_directory(self, config):
        """Test getting backup directory path."""
        backup_dir = config.get_backup_directory()

        assert isinstance(backup_dir, Path)
        assert backup_dir == Path("backups")

    def test_get_backup_directory_custom(self, config):
        """Test getting custom backup directory."""
        config.config["backup_directory"] = "custom_backups"
        backup_dir = config.get_backup_directory()

        assert backup_dir == Path("custom_backups")

    def test_get_max_backups(self, config):
        """Test getting max backups count."""
        assert config.get_max_backups() == 30

    def test_get_max_backups_custom(self, config):
        """Test getting custom max backups."""
        config.config["retention_days"] = 45
        assert config.get_max_backups() == 45

    def test_is_enabled_true(self, config):
        """Test is_enabled returns True when enabled."""
        assert config.is_enabled() is True

    def test_is_enabled_false(self, config):
        """Test is_enabled returns False when disabled."""
        config.config["enabled"] = False
        assert config.is_enabled() is False

    def test_should_verify_true(self, config):
        """Test should_verify returns True when enabled."""
        assert config.should_verify() is True

    def test_should_verify_false(self, config):
        """Test should_verify returns False when disabled."""
        config.config["verify_after_backup"] = False
        assert config.should_verify() is False

    def test_keep_manual_backups_true(self, config):
        """Test keep_manual_backups returns True when enabled."""
        assert config.keep_manual_backups() is True

    def test_keep_manual_backups_false(self, config):
        """Test keep_manual_backups returns False when disabled."""
        config.config["keep_manual_backups"] = False
        assert config.keep_manual_backups() is False


class TestToDict:
    """Test to_dict conversion."""

    def test_to_dict_returns_copy(self, config):
        """Test that to_dict returns a copy, not reference."""
        config_dict = config.to_dict()

        # Modify returned dict
        config_dict["backup_time"] = "99:99"

        # Original should be unchanged
        assert config.config["backup_time"] == "02:00"

    def test_to_dict_contains_all_values(self, config):
        """Test that to_dict contains all configuration."""
        config_dict = config.to_dict()

        for key, value in BackupConfig.DEFAULT_CONFIG.items():
            assert key in config_dict
            assert config_dict[key] == value


class TestFromDict:
    """Test from_dict class method."""

    def test_from_dict_creates_config(self):
        """Test creating config from dictionary."""
        config_dict = {
            "backup_time": "04:00",
            "retention_days": 45,
            "enabled": False,
        }

        config = BackupConfig.from_dict(config_dict)

        assert config.config["backup_time"] == "04:00"
        assert config.config["retention_days"] == 45
        assert config.config["enabled"] is False


class TestResetToDefaults:
    """Test reset functionality."""

    def test_reset_to_defaults(self, config):
        """Test resetting configuration to defaults."""
        # Modify config
        config.config["backup_time"] = "12:00"
        config.config["retention_days"] = 999
        config.config["enabled"] = False

        # Reset
        config.reset_to_defaults()

        # Should match defaults
        assert config.config == BackupConfig.DEFAULT_CONFIG

    def test_reset_preserves_defaults(self, config):
        """Test that reset doesn't modify defaults."""
        # Get defaults copy
        original_defaults = BackupConfig.DEFAULT_CONFIG.copy()

        config.reset_to_defaults()

        # Defaults should be unchanged
        assert BackupConfig.DEFAULT_CONFIG == original_defaults


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_config_mutation_after_get(self, config):
        """Test that modifying config dict affects internal state."""
        config_dict = config.to_dict()

        # Modify returned dict
        config_dict["backup_time"] = "invalid"

        # Should not affect internal config
        assert config.config["backup_time"] == "02:00"

    def test_multiple_saves(self, config):
        """Test that multiple saves work correctly."""
        config.save_config()
        config.config["backup_time"] = "05:00"
        config.save_config()

        # Load new instance to verify
        new_config = BackupConfig(config_path=config.config_path)
        assert new_config.config["backup_time"] == "05:00"

    def test_all_default_config_values_valid(self):
        """Test that all default values are valid."""
        config = BackupConfig()
        errors = config.validate_config()

        assert errors == []
