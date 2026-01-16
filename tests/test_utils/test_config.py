"""Tests for configuration utilities."""

import pytest
import json
from pathlib import Path

from utils import config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_config(self, tmp_path):
        """Should return default config when file doesn't exist."""
        config_path = tmp_path / "nonexistent.json"
        cfg = config.load_config(config_path)

        assert cfg == config.DEFAULT_CONFIG

    def test_load_custom_config(self, tmp_path):
        """Should load custom config and merge with defaults."""
        config_file = tmp_path / "config.json"
        custom_config = {
            "alerts": {
                "warning_days": 45
            }
        }

        config_file.write_text(json.dumps(custom_config))

        cfg = config.load_config(config_file)

        # Should have custom warning_days
        assert cfg['alerts']['warning_days'] == 45

        # Should still have default critical_days
        assert cfg['alerts']['critical_days'] == 7

        # Should have other default sections
        assert 'lock' in cfg
        assert 'organization' in cfg

    def test_load_invalid_json(self, tmp_path, capsys):
        """Should use defaults when JSON is invalid."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("invalid json content")

        cfg = config.load_config(config_file)

        # Should return defaults
        assert cfg == config.DEFAULT_CONFIG

        # Should print warning
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "Could not load config" in captured.out

    def test_deep_merge_nested_dicts(self, tmp_path):
        """Should deep merge nested dictionaries."""
        config_file = tmp_path / "config.json"
        custom_config = {
            "organization": {
                "roles": ["Custom Role"]
            }
        }

        config_file.write_text(json.dumps(custom_config))

        cfg = config.load_config(config_file)

        # Should have custom role
        assert "Custom Role" in cfg['organization']['roles']

        # Should still have default workspaces
        assert len(cfg['organization']['workspaces']) > 0


class TestGetAlertThresholds:
    """Tests for get_alert_thresholds function."""

    def test_get_alert_thresholds_defaults(self):
        """Should return default thresholds."""
        cfg = {"alerts": {}}
        thresholds = config.get_alert_thresholds(cfg)

        assert thresholds == {
            'critical_days': 7,
            'warning_days': 30
        }

    def test_get_alert_thresholds_custom(self):
        """Should return custom thresholds."""
        cfg = {
            "alerts": {
                "critical_days": 5,
                "warning_days": 20
            }
        }
        thresholds = config.get_alert_thresholds(cfg)

        assert thresholds == {
            'critical_days': 5,
            'warning_days': 20
        }

    def test_get_alert_thresholds_partial(self):
        """Should use defaults for missing values."""
        cfg = {
            "alerts": {
                "warning_days": 45
            }
        }
        thresholds = config.get_alert_thresholds(cfg)

        assert thresholds['critical_days'] == 7  # default
        assert thresholds['warning_days'] == 45  # custom


class TestGetLockTimeout:
    """Tests for get_lock_timeout function."""

    def test_get_lock_timeout_default(self):
        """Should return default timeout."""
        cfg = {"lock": {}}
        timeout = config.get_lock_timeout(cfg)

        assert timeout == 2

    def test_get_lock_timeout_custom(self):
        """Should return custom timeout."""
        cfg = {
            "lock": {
                "timeout_minutes": 5
            }
        }
        timeout = config.get_lock_timeout(cfg)

        assert timeout == 5


class TestGetLockHeartbeatInterval:
    """Tests for get_lock_heartbeat_interval function."""

    def test_get_heartbeat_interval_default(self):
        """Should return default interval."""
        cfg = {"lock": {}}
        interval = config.get_lock_heartbeat_interval(cfg)

        assert interval == 30

    def test_get_heartbeat_interval_custom(self):
        """Should return custom interval."""
        cfg = {
            "lock": {
                "heartbeat_interval_seconds": 60
            }
        }
        interval = config.get_lock_heartbeat_interval(cfg)

        assert interval == 60


class TestGetRoles:
    """Tests for get_roles function."""

    def test_get_roles_default(self):
        """Should return default roles."""
        cfg = config.get_default_config()
        roles = config.get_roles(cfg)

        assert len(roles) > 0
        assert "Cariste" in roles
        assert "Préparateur" in roles

    def test_get_roles_custom(self):
        """Should return custom roles."""
        cfg = {
            "organization": {
                "roles": ["Role A", "Role B"]
            }
        }
        roles = config.get_roles(cfg)

        assert roles == ["Role A", "Role B"]

    def test_get_roles_empty(self):
        """Should return empty list if no roles."""
        cfg = {"organization": {}}
        roles = config.get_roles(cfg)

        assert roles == []


class TestGetWorkspaces:
    """Tests for get_workspaces function."""

    def test_get_workspaces_default(self):
        """Should return default workspaces."""
        cfg = config.get_default_config()
        workspaces = config.get_workspaces(cfg)

        assert len(workspaces) > 0
        assert "Quai" in workspaces
        assert "Bureau" in workspaces

    def test_get_workspaces_custom(self):
        """Should return custom workspaces."""
        cfg = {
            "organization": {
                "workspaces": ["Zone X", "Zone Y"]
            }
        }
        workspaces = config.get_workspaces(cfg)

        assert workspaces == ["Zone X", "Zone Y"]

    def test_get_workspaces_empty(self):
        """Should return empty list if no workspaces."""
        cfg = {"organization": {}}
        workspaces = config.get_workspaces(cfg)

        assert workspaces == []


class TestValidateConfig:
    """Tests for validate_config function."""

    def test_validate_default_config(self):
        """Should validate default config successfully."""
        is_valid, errors = config.validate_config(config.get_default_config())

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_critical_days(self):
        """Should pass validation when critical_days is missing."""
        cfg = {
            "alerts": {
                "warning_days": 30
            },
            "lock": {
                "timeout_minutes": 2
            },
            "organization": {
                "roles": ["Role"],
                "workspaces": ["Zone"]
            }
        }
        is_valid, errors = config.validate_config(cfg)

        # Missing fields are not errors (defaults used)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_negative_critical_days(self):
        """Should fail validation for negative critical_days."""
        cfg = {
            "alerts": {
                "critical_days": -5
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "must be positive" in errors[0]

    def test_validate_invalid_type_critical_days(self):
        """Should fail validation for non-integer critical_days."""
        cfg = {
            "alerts": {
                "critical_days": "seven"
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "must be an integer" in errors[0]

    def test_validate_critical_greater_than_warning(self):
        """Should fail validation when critical > warning."""
        cfg = {
            "alerts": {
                "critical_days": 30,
                "warning_days": 7
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "should not be greater" in errors[0]

    def test_validate_negative_timeout(self):
        """Should fail validation for negative timeout."""
        cfg = {
            "lock": {
                "timeout_minutes": -1
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "must be positive" in errors[0]

    def test_validate_empty_roles(self):
        """Should fail validation for empty roles list."""
        cfg = {
            "organization": {
                "roles": []
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "cannot be empty" in errors[0]

    def test_validate_invalid_roles_type(self):
        """Should fail validation for non-list roles."""
        cfg = {
            "organization": {
                "roles": "Not a list"
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "must be a list" in errors[0]

    def test_validate_invalid_role_items(self):
        """Should fail validation for non-string roles."""
        cfg = {
            "organization": {
                "roles": ["Valid", 123, "Also Valid"]
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "must contain only strings" in errors[0]

    def test_validate_empty_workspaces(self):
        """Should fail validation for empty workspaces list."""
        cfg = {
            "organization": {
                "workspaces": []
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert "cannot be empty" in errors[0]

    def test_validate_multiple_errors(self):
        """Should collect all validation errors."""
        cfg = {
            "alerts": {
                "critical_days": -5,
                "warning_days": "invalid"
            },
            "lock": {
                "timeout_minutes": 0
            },
            "organization": {
                "roles": [],
                "workspaces": []
            }
        }
        is_valid, errors = config.validate_config(cfg)

        assert is_valid is False
        assert len(errors) > 1


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config_creates_file(self, tmp_path):
        """Should create config file."""
        config_path = tmp_path / "test_config.json"
        cfg = config.get_default_config()

        config.save_config(cfg, config_path)

        assert config_path.exists()

    def test_save_config_valid_content(self, tmp_path):
        """Should save valid config content."""
        config_path = tmp_path / "test_config.json"
        cfg = config.get_default_config()

        config.save_config(cfg, config_path)

        # Load and verify (specify encoding for French characters)
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        assert loaded == cfg

    def test_save_config_invalid_raises_error(self, tmp_path):
        """Should raise ValueError for invalid config."""
        config_path = tmp_path / "test_config.json"
        cfg = {
            "alerts": {
                "critical_days": -5
            }
        }

        with pytest.raises(ValueError, match="Invalid configuration"):
            config.save_config(cfg, config_path)

    def test_save_config_creates_directory(self, tmp_path):
        """Should create parent directory if needed."""
        config_path = tmp_path / "nested" / "dir" / "config.json"
        cfg = config.get_default_config()

        config.save_config(cfg, config_path)

        assert config_path.exists()


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_get_default_config_returns_dict(self):
        """Should return a dictionary."""
        default = config.get_default_config()

        assert isinstance(default, dict)

    def test_get_default_config_has_all_sections(self):
        """Should have all required sections."""
        default = config.get_default_config()

        assert 'alerts' in default
        assert 'lock' in default
        assert 'organization' in default

    def test_get_default_config_is_copy(self):
        """Should return a copy, not the original."""
        default1 = config.get_default_config()
        default2 = config.get_default_config()

        # Modify one copy
        default1['alerts']['warning_days'] = 999

        # Other copy should be unchanged
        assert default2['alerts']['warning_days'] == 30


class TestDeepMerge:
    """Tests for _deep_merge helper function."""

    def test_deep_merge_simple_override(self):
        """Should override simple values."""
        base = {"a": 1, "b": 2}
        update = {"b": 3}

        result = config._deep_merge(base, update)

        assert result == {"a": 1, "b": 3}

    def test_deep_merge_nested_dicts(self):
        """Should merge nested dictionaries."""
        base = {
            "alerts": {"critical_days": 7, "warning_days": 30},
            "lock": {"timeout_minutes": 2}
        }
        update = {
            "alerts": {"warning_days": 45}
        }

        result = config._deep_merge(base, update)

        assert result['alerts']['critical_days'] == 7  # unchanged
        assert result['alerts']['warning_days'] == 45  # updated
        assert result['lock']['timeout_minutes'] == 2  # unchanged

    def test_deep_merge_add_new_keys(self):
        """Should add new keys from update."""
        base = {"a": 1}
        update = {"b": 2, "c": 3}

        result = config._deep_merge(base, update)

        assert result == {"a": 1, "b": 2, "c": 3}


class TestConfigIntegration:
    """Integration tests for configuration module."""

    def test_full_config_lifecycle(self, tmp_path):
        """Should handle full config lifecycle: load, modify, save, load."""
        config_path = tmp_path / "config.json"

        # Load default
        cfg1 = config.load_config(config_path)

        # Modify
        cfg1['alerts']['warning_days'] = 45

        # Save
        config.save_config(cfg1, config_path)

        # Load again
        cfg2 = config.load_config(config_path)

        # Should have saved value
        assert cfg2['alerts']['warning_days'] == 45
        assert cfg2['alerts']['critical_days'] == 7  # default preserved

    def test_load_partial_custom_config(self, tmp_path):
        """Should merge partial custom config with defaults."""
        config_file = tmp_path / "config.json"
        partial_config = {
            "alerts": {
                "critical_days": 5
            }
        }

        config_file.write_text(json.dumps(partial_config, indent=2))

        cfg = config.load_config(config_file)

        # Custom value
        assert cfg['alerts']['critical_days'] == 5

        # Defaults merged in
        assert cfg['alerts']['warning_days'] == 30
        assert 'lock' in cfg
        assert 'organization' in cfg
