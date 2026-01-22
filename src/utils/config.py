"""Configuration JSON loader."""

import copy
import json
from pathlib import Path
from typing import Any

# Default configuration values
DEFAULT_CONFIG = {
    "alerts": {"critical_days": 7, "warning_days": 30},
    "lock": {"timeout_minutes": 2, "heartbeat_interval_seconds": 30},
    "organization": {
        "roles": ["Cariste", "Préparateur", "Magasinier", "Réceptionnaire", "Gestionnaire", "Chef d'équipe"],
        "workspaces": ["Quai", "Zone A", "Zone B", "Zone C", "Bureau", "Stockage"],
    },
}


def load_config(config_path: Path = Path("config.json")) -> dict[str, Any]:
    """
    Load configuration from JSON file.

    If the file doesn't exist or is invalid, returns default configuration.
    Missing keys in user config are filled with defaults.

    Args:
        config_path: Path to configuration file (default: "config.json")

    Returns:
        Configuration dictionary with all required keys

    Example:
        >>> config = load_config()
        >>> print(config['alerts']['warning_days'])
        30

        >>> config = load_config(Path("custom_config.json"))
        >>> if config != DEFAULT_CONFIG:
        ...     print("Using custom configuration")
    """
    # Start with defaults (deep copy to avoid modifying DEFAULT_CONFIG)
    config = copy.deepcopy(DEFAULT_CONFIG)

    # Try to load user configuration
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Merge user config with defaults (deep merge for nested dicts)
            config = _deep_merge(config, user_config)

    except (json.JSONDecodeError, IOError) as e:
        # If file is invalid, use defaults
        print(f"Warning: Could not load config from {config_path}: {e}")
        print("Using default configuration.")

    return config


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

    return {"critical_days": alerts.get("critical_days", 7), "warning_days": alerts.get("warning_days", 30)}


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


def save_config(config: dict[str, Any], config_path: Path = Path("config.json")) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the file (default: "config.json")

    Raises:
        IOError: If file cannot be written
        ValueError: If config is invalid

    Example:
        >>> config = load_config()
        >>> config['alerts']['warning_days'] = 45
        >>> save_config(config)
    """
    # Validate before saving
    is_valid, errors = validate_config(config)
    if not is_valid:
        raise ValueError(f"Invalid configuration: {errors}")

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file with nice formatting
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_default_config() -> dict[str, Any]:
    """
    Get a copy of the default configuration.

    Useful for creating a new config file from scratch.

    Returns:
        Default configuration dictionary

    Example:
        >>> default = get_default_config()
        >>> save_config(default, Path("new_config.json"))
    """
    return copy.deepcopy(DEFAULT_CONFIG)
