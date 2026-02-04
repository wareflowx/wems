"""Configuration loader with JSON and YAML support.

This module provides flexible configuration management supporting both JSON and YAML formats.
YAML is recommended for user-friendly configuration with comments and more forgiving syntax.

Features:
- Automatic format detection (JSON or YAML)
- Comments allowed in YAML (not in JSON)
- More readable YAML syntax
- Backward compatible with existing JSON configs
- Validation with helpful error messages
- Environment variable overrides
"""

import copy
import json
import os
from pathlib import Path
from typing import Any

# Try to load YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Try to load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed


# Default configuration values
DEFAULT_CONFIG = {
    "alerts": {
        "critical_days": 7,
        "warning_days": 30,
        # Alert when certifications expire within these days
    },
    "lock": {
        "timeout_minutes": 2,
        "heartbeat_interval_seconds": 30,
        # Application lock settings to prevent concurrent access
    },
    "organization": {
        "roles": ["Cariste", "Préparateur de commandes", "Magasinier",
                 "Réceptionnaire", "Gestionnaire", "Chef d'équipe"],
        # Job roles in the organization
        "workspaces": ["Quai", "Zone A", "Zone B", "Zone C", "Bureau", "Stockage"],
        # Physical work areas/locations
    },
}


def _detect_format(config_path: Path) -> str:
    """Detect configuration file format from extension.

    Args:
        config_path: Path to configuration file

    Returns:
        'json', 'yaml', or 'yml' (lowercase)

    Raises:
        ValueError: If format is not supported
    """
    suffix = config_path.suffix.lower()

    if suffix == '.json':
        return 'json'
    elif suffix in ['.yaml', '.yml']:
        return 'yaml'
    else:
        raise ValueError(
            f"Unsupported config format: {suffix}. "
            "Supported formats: .json, .yaml, .yml"
        )


def _load_json(config_path: Path) -> dict[str, Any]:
    """Load configuration from JSON file.

    Args:
        config_path: Path to JSON file

    Returns:
        Configuration dictionary

    Raises:
        json.JSONDecodeError: If JSON is invalid
        IOError: If file cannot be read
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML file

    Returns:
        Configuration dictionary

    Raises:
        yaml.YAMLError: If YAML is invalid
        IOError: If file cannot be read
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is not installed. Install it with: pip install pyyaml"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _save_json(config: dict[str, Any], config_path: Path) -> None:
    """Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Path to save file

    Raises:
        IOError: If file cannot be written
    """
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _save_yaml(config: dict[str, Any], config_path: Path) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        config_path: Path to save file

    Raises:
        IOError: If file cannot be written
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is not installed. Install it with: pip install pyyaml"
        )

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """
    Load configuration from JSON or YAML file.

    Automatically detects format from file extension.
    If the file doesn't exist or is invalid, returns default configuration.
    Missing keys in user config are filled with defaults.

    Args:
        config_path: Path to configuration file.
                    If None, searches for config.yaml, config.yml, or config.json
                    in that order.

    Returns:
        Configuration dictionary with all required keys

    Raises:
        ValueError: If config format is not supported

    Example:
        >>> # Auto-detect format
        >>> config = load_config()
        >>> print(config['alerts']['warning_days'])
        30

        >>> # Load specific file
        >>> config = load_config(Path("custom_config.yaml"))
        >>> if config != DEFAULT_CONFIG:
        ...     print("Using custom configuration")

        >>> # JSON still works (backward compatible)
        >>> config = load_config(Path("legacy_config.json"))
    """
    # Auto-detect config file if not specified
    if config_path is None:
        for filename in ["config.yaml", "config.yml", "config.json"]:
            test_path = Path(filename)
            if test_path.exists():
                config_path = test_path
                break
        else:
            # No config file found, use defaults
            return copy.deepcopy(DEFAULT_CONFIG)

    # Start with defaults (deep copy to avoid modifying DEFAULT_CONFIG)
    config = copy.deepcopy(DEFAULT_CONFIG)

    # Detect format
    try:
        format_type = _detect_format(config_path)
    except ValueError as e:
        print(f"Warning: {e}")
        print("Using default configuration.")
        return config

    # Try to load user configuration
    try:
        if format_type == 'json':
            user_config = _load_json(config_path)
        elif format_type == 'yaml':
            user_config = _load_yaml(config_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        # Merge user config with defaults (deep merge for nested dicts)
        config = _deep_merge(config, user_config)

    except (json.JSONDecodeError, yaml.YAMLError, IOError) as e:
        # If file is invalid, use defaults
        print(f"Warning: Could not load config from {config_path}: {e}")
        print("Using default configuration.")

    return config


def save_config(
    config: dict[str, Any],
    config_path: Path | None = None,
    format: str | None = None
) -> None:
    """
    Save configuration to JSON or YAML file.

    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the file.
                      If None, saves to config.yaml (YAML is recommended)
        format: Format to save ('json', 'yaml', or 'yml').
                If None, detects from config_path extension.
                If config_path is also None, defaults to 'yaml'.

    Raises:
        IOError: If file cannot be written
        ValueError: If config is invalid
        ImportError: If PyYAML not installed for YAML format

    Example:
        >>> config = load_config()
        >>> config['alerts']['warning_days'] = 45
        >>>
        >>> # Save to YAML (recommended)
        >>> save_config(config, Path("config.yaml"))
        >>>
        >>> # Save to JSON (legacy format)
        >>> save_config(config, Path("config.json"))
    """
    # Validate before saving
    is_valid, errors = validate_config(config)
    if not is_valid:
        raise ValueError(f"Invalid configuration: {errors}")

    # Determine path and format
    if config_path is None:
        config_path = Path("config.yaml")
        format = format or 'yaml'
    elif format is None:
        format = _detect_format(config_path)

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Save in appropriate format
    if format == 'json':
        _save_json(config, config_path)
    elif format in ['yaml', 'yml']:
        _save_yaml(config, config_path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def migrate_to_yaml(
    json_path: Path,
    yaml_path: Path | None = None
) -> Path:
    """
    Migrate configuration from JSON to YAML format.

    Converts existing JSON config to YAML with:
    - Comments explaining each section
    - More readable formatting
    - Recommended defaults applied

    Args:
        json_path: Path to existing JSON config file
        yaml_path: Path for new YAML file.
                    If None, uses same name but with .yaml extension

    Returns:
        Path to the created YAML file

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        ValueError: If JSON is invalid

    Example:
        >>> # Migrate config.json to config.yaml
        >>> yaml_path = migrate_to_yaml(Path("config.json"))
        >>> print(f"Created: {yaml_path}")
        >>>
        >>> # Migrate to custom path
        >>> yaml_path = migrate_to_yaml(
        ...     Path("old_config.json"),
        ...     Path("new_config.yaml")
        ... )
    """
    if not json_path.exists():
        raise FileNotFoundError(f"JSON config not found: {json_path}")

    # Load existing config
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Determine output path
    if yaml_path is None:
        yaml_path = json_path.with_suffix('.yaml')

    # Save with comments
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is not installed. Install it with: pip install pyyaml"
        )

    # Add comments explaining the structure
    comments = """# Wareflow EMS Configuration
# This file controls application behavior and settings.
#
# For help with configuration, see:
# https://github.com/wareflowx/wareflow-ems/docs/
#
# Format: YAML (recommended over JSON for readability)
# - Comments start with # (like this line)
# - Indentation matters (use spaces, not tabs)
# - Strings don't need quotes (most of the time)

"""

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(comments)
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Migrated configuration: {json_path} -> {yaml_path}")
    return yaml_path


def _deep_merge(base: dict, update: dict) -> dict:
    """
    Deep merge two dictionaries.

    Values from 'update' override values in 'base'.
    Nested dictionaries are merged recursively.

    Args:
        base: Base dictionary (defaults)
        update: Dictionary with updates (user config)

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _deep_merge(result[key], value)
        else:
            # Override with new value
            result[key] = value

    return result


# ===== Helper Functions =====

def get_alert_thresholds(config: dict[str, Any]) -> dict[str, int]:
    """
    Get alert thresholds from config.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary with alert thresholds:
        {
            'critical_days': int,  # default 7
            'warning_days': int    # default 30
        }

    Example:
        >>> config = load_config()
        >>> thresholds = get_alert_thresholds(config)
        >>> print(f"Warning at {thresholds['warning_days']} days")
    """
    alerts = config.get("alerts", {})
    return {
        "critical_days": alerts.get("critical_days", 7),
        "warning_days": alerts.get("warning_days", 30)
    }


def get_lock_timeout(config: dict[str, Any]) -> int:
    """
    Get lock timeout in minutes.

    Args:
        config: Configuration dictionary

    Returns:
        Lock timeout in minutes (default: 2)

    Example:
        >>> config = load_config()
        >>> timeout = get_lock_timeout(config)
        >>> print(f"Lock timeout: {timeout} minutes")
    """
    lock = config.get("lock", {})
    return lock.get("timeout_minutes", 2)


def get_lock_heartbeat_interval(config: dict[str, Any]) -> int:
    """
    Get lock heartbeat interval in seconds.

    Args:
        config: Configuration dictionary

    Returns:
        Heartbeat interval in seconds (default: 30)

    Example:
        >>> config = load_config()
        >>> interval = get_lock_heartbeat_interval(config)
        >>> print(f"Heartbeat every {interval} seconds")
    """
    lock = config.get("lock", {})
    return lock.get("heartbeat_interval_seconds", 30)


def get_roles(config: dict[str, Any]) -> list[str]:
    """
    Get list of valid roles from config.

    Args:
        config: Configuration dictionary

    Returns:
        List of valid role names

    Example:
        >>> config = load_config()
        >>> roles = get_roles(config)
        >>> print(f"Available roles: {roles}")
    """
    org = config.get("organization", {})
    return org.get("roles", [])


def get_workspaces(config: dict[str, Any]) -> list[str]:
    """
    Get list of valid workspaces from config.

    Args:
        config: Configuration dictionary

    Returns:
        List of valid workspace names

    Example:
        >>> config = load_config()
        >>> workspaces = get_workspaces(config)
        >>> print(f"Available workspaces: {workspaces}")
    """
    org = config.get("organization", {})
    return org.get("workspaces", [])


def validate_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate configuration values.

    Checks:
    - Alert thresholds are positive integers
    - Lock timeout is positive integer
    - Lock heartbeat interval is positive integer
    - Roles list is not empty
    - Workspaces list is not empty
    - All values have correct types

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> config = load_config()
        >>> is_valid, errors = validate_config(config)
        >>> if not is_valid:
        ...     print("Configuration errors:")
        ...     for error in errors:
        ...         print(f"  - {error}")
    """
    errors = []

    # Validate alerts section
    if "alerts" in config:
        alerts = config["alerts"]

        # Check critical_days
        if "critical_days" in alerts:
            critical_days = alerts["critical_days"]
            if not isinstance(critical_days, int):
                errors.append("alerts.critical_days must be an integer")
            elif critical_days <= 0:
                errors.append("alerts.critical_days must be positive")

        # Check warning_days
        if "warning_days" in alerts:
            warning_days = alerts["warning_days"]
            if not isinstance(warning_days, int):
                errors.append("alerts.warning_days must be an integer")
            elif warning_days <= 0:
                errors.append("alerts.warning_days must be positive")

        # Check logical consistency
        if (
            "critical_days" in alerts
            and "warning_days" in alerts
            and isinstance(alerts["critical_days"], int)
            and isinstance(alerts["warning_days"], int)
        ):
            if alerts["critical_days"] > alerts["warning_days"]:
                errors.append("alerts.critical_days should not be greater than alerts.warning_days")

    # Validate lock section
    if "lock" in config:
        lock = config["lock"]

        # Check timeout_minutes
        if "timeout_minutes" in lock:
            timeout = lock["timeout_minutes"]
            if not isinstance(timeout, int):
                errors.append("lock.timeout_minutes must be an integer")
            elif timeout <= 0:
                errors.append("lock.timeout_minutes must be positive")

        # Check heartbeat_interval_seconds
        if "heartbeat_interval_seconds" in lock:
            interval = lock["heartbeat_interval_seconds"]
            if not isinstance(interval, int):
                errors.append("lock.heartbeat_interval_seconds must be an integer")
            elif interval <= 0:
                errors.append("lock.heartbeat_interval_seconds must be positive")

    # Validate organization section
    if "organization" in config:
        org = config["organization"]

        # Check roles
        if "roles" in org:
            roles = org["roles"]
            if not isinstance(roles, list):
                errors.append("organization.roles must be a list")
            elif len(roles) == 0:
                errors.append("organization.roles cannot be empty")
            elif not all(isinstance(role, str) for role in roles):
                errors.append("organization.roles must contain only strings")

        # Check workspaces
        if "workspaces" in org:
            workspaces = org["workspaces"]
            if not isinstance(workspaces, list):
                errors.append("organization.workspaces must be a list")
            elif len(workspaces) == 0:
                errors.append("organization.workspaces cannot be empty")
            elif not all(isinstance(ws, str) for ws in workspaces):
                errors.append("organization.workspaces must contain only strings")

    is_valid = len(errors) == 0
    return is_valid, errors


def get_default_config() -> dict[str, Any]:
    """
    Get a copy of the default configuration.

    Useful for creating a new config file from scratch.

    Returns:
        Default configuration dictionary

    Example:
        >>> default = get_default_config()
        >>> save_config(default, Path("new_config.yaml"))
    """
    return copy.deepcopy(DEFAULT_CONFIG)


# ===== Database Configuration =====

def get_database_dir() -> Path:
    """
    Get database directory from environment variable or use default.

    Environment variable: DATABASE_DIR (default: "data")

    Returns:
        Path to database directory

    Example:
        >>> os.environ['DATABASE_DIR'] = '/var/lib/wareflow'
        >>> db_dir = get_database_dir()
        >>> print(db_dir)
        /var/lib/wareflow
    """
    db_dir = os.getenv("DATABASE_DIR", "data")
    return Path(db_dir)


def get_database_name() -> str:
    """
    Get database filename from environment variable or use default.

    Environment variable: DATABASE_NAME (default: "employee_manager.db")

    Returns:
        Database filename

    Example:
        >>> name = get_database_name()
        >>> print(name)
        employee_manager.db
    """
    return os.getenv("DATABASE_NAME", "employee_manager.db")


def get_database_path() -> Path:
    """
    Get full database path from environment variables or use default.

    Environment variables:
    - DATABASE_PATH (full path, takes precedence)
    - DATABASE_DIR (directory, default: "data")
    - DATABASE_NAME (filename, default: "employee_manager.db")

    If DATABASE_PATH is set, it's used directly.
    Otherwise, DATABASE_DIR/DATABASE_NAME is used.

    Returns:
        Path to database file

    Example:
        >>> # Default behavior
        >>> path = get_database_path()
        >>> print(path)
        data/employee_manager.db

        >>> # Custom directory
        >>> os.environ['DATABASE_DIR'] = '/var/lib/wareflow'
        >>> path = get_database_path()
        >>> print(path)
        /var/lib/wareflow/employee_manager.db

        >>> # Full path override
        >>> os.environ['DATABASE_PATH'] = '/opt/db/prod.db'
        >>> path = get_database_path()
        >>> print(path)
        /opt/db/prod.db
    """
    # Check if full path is specified
    db_path = os.getenv("DATABASE_PATH")
    if db_path:
        return Path(db_path)

    # Use directory + filename
    db_dir = get_database_dir()
    db_name = get_database_name()

    return db_dir / db_name


def ensure_database_directory() -> Path:
    """
    Ensure database directory exists, creating it if necessary.

    Returns:
        Path to database directory

    Raises:
        OSError: If directory cannot be created
    """
    db_dir = get_database_dir()
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir


def get_workspace_choices(config: dict[str, Any] | None = None) -> list[str]:
    """
    Get workspace choices from config or use defaults.

    This function provides the workspace list for UI dropdowns and validation.
    It first tries to load from config, then falls back to defaults.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        List of workspace names

    Example:
        >>> workspaces = get_workspace_choices()
        >>> print(workspaces)
        ['Quai', 'Zone A', 'Zone B', 'Bureau']
    """
    if config is None:
        config = load_config()

    return get_workspaces(config)


def get_role_choices(config: dict[str, Any] | None = None) -> list[str]:
    """
    Get role choices from config or use defaults.

    This function provides the role list for UI dropdowns and validation.
    It first tries to load from config, then falls back to defaults.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        List of role names

    Example:
        >>> roles = get_role_choices()
        >>> print(roles)
        ['Cariste', 'Préparateur de commandes', 'Magasinier']
    """
    if config is None:
        config = load_config()

    return get_roles(config)


def get_contract_type_choices(config: dict[str, Any] | None = None) -> list[str]:
    """
    Get contract type choices from config or use defaults.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        List of contract type names

    Example:
        >>> contracts = get_contract_type_choices()
        >>> print(contracts)
        ['CDI', 'CDD', 'Interim', 'Alternance']
    """
    if config is None:
        config = load_config()

    organization = config.get("organization", {})

    # If contract types are defined in organization section, use them
    if "contract_types" in organization:
        return organization["contract_types"]

    # Otherwise, use default contract types
    return ["CDI", "CDD", "Interim", "Alternance", "Stage"]


def ensure_default_config() -> Path | None:
    """
    Create default config.yaml if no config file exists.

    This function checks for existing config files (config.yaml, config.yml, config.json).
    If none exist, it creates a config.yaml file with default values and helpful comments.

    Returns:
        Path to created config.yaml, or None if config already exists or YAML not available

    Example:
        >>> config_path = ensure_default_config()
        >>> if config_path:
        ...     print(f"Created: {config_path}")
    """
    # Check if any config file already exists
    for filename in ["config.yaml", "config.yml", "config.json"]:
        if Path(filename).exists():
            return None  # Config already exists, don't overwrite

    # Check if YAML is available
    if not YAML_AVAILABLE:
        # Can't create YAML file, will use defaults
        return None

    # Create default config.yaml with comments
    default_config_content = """# Wareflow EMS Configuration File
# This file controls application behavior and settings.
#
# Format: YAML (recommended over JSON for readability)
# - Comments start with # (like this line)
# - Indentation matters (use spaces, not tabs)
# - Strings don't need quotes (most of the time)

# ============================================================================
# ALERT SETTINGS
# ============================================================================
# Configure when alerts are shown for expiring certifications and visits
alerts:
  # Warning period: Show warnings when expiration is within this many days
  warning_days: 30

  # Critical period: Show critical alerts when expiration is within this many days
  critical_days: 7

# ============================================================================
# LOCK SETTINGS
# ============================================================================
# Prevent multiple users from modifying the database simultaneously
lock:
  # Auto-lock timeout: Release lock after this many minutes of inactivity
  timeout_minutes: 2

  # Heartbeat interval: Send heartbeat signal every N seconds to maintain lock
  heartbeat_interval_seconds: 30

# ============================================================================
# ORGANIZATION SETTINGS
# ============================================================================
# Define your organization structure (roles and workspaces)
# These values are used in employee dropdowns and validation
organization:
  # Job positions/roles in your organization
  roles:
    - Cariste
    - Préparateur de commandes
    - Magasinier
    - Réceptionnaire
    - Gestionnaire
    - Chef d'équipe

  # Physical work areas/locations in your warehouse
  workspaces:
    - Quai
    - Zone A
    - Zone B
    - Zone C
    - Bureau
    - Stockage

# ============================================================================
# ADVANCED SETTINGS (OPTIONAL)
# ============================================================================
# These settings have sensible defaults and rarely need to be changed
#
# Database location (use environment variables DATABASE_DIR and DATABASE_NAME instead)
# See README.md for more details on configuration
"""

    try:
        config_path = Path("config.yaml")

        # Write the default config file
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_config_content)

        return config_path

    except (IOError, OSError) as e:
        # Silent fail - application will use defaults
        # This avoids issues in read-only environments
        return None
