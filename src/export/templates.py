"""Excel templates, column definitions, and styles."""

from typing import Any

# ========== COLUMN DEFINITIONS ==========

# Column definitions for employee export
EMPLOYEE_COLUMNS = [
    {"key": "external_id", "header": "ID WMS", "width": 15},
    {"key": "full_name", "header": "Nom Complet", "width": 25},
    {"key": "workspace", "header": "Zone", "width": 15},
    {"key": "role", "header": "Poste", "width": 20},
    {"key": "contract_type", "header": "Contrat", "width": 12},
    {"key": "entry_date", "header": "Date Entrée", "width": 15},
    {"key": "seniority", "header": "Ancienneté (ans)", "width": 18},
    {"key": "status", "header": "Statut", "width": 15},
]

# Column definitions for CACES certifications
CACES_COLUMNS = [
    {"key": "employee_external_id", "header": "ID Employé", "width": 15},
    {"key": "employee_name", "header": "Employé", "width": 25},
    {"key": "kind", "header": "Type CACES", "width": 15},
    {"key": "completion_date", "header": "Date Obtention", "width": 15},
    {"key": "expiration_date", "header": "Date Expiration", "width": 15},
    {"key": "days_until_expiration", "header": "Jours Restants", "width": 15},
    {"key": "status", "header": "Statut", "width": 12},
    {"key": "document_path", "header": "Document", "width": 40},
]

# Column definitions for medical visits
MEDICAL_COLUMNS = [
    {"key": "employee_external_id", "header": "ID Employé", "width": 15},
    {"key": "employee_name", "header": "Employé", "width": 25},
    {"key": "visit_type", "header": "Type Visite", "width": 15},
    {"key": "visit_date", "header": "Date Visite", "width": 15},
    {"key": "expiration_date", "header": "Date Expiration", "width": 15},
    {"key": "days_until_expiration", "header": "Jours Restants", "width": 15},
    {"key": "result", "header": "Résultat", "width": 15},
    {"key": "status", "header": "Statut", "width": 12},
    {"key": "document_path", "header": "Document", "width": 40},
]

# Column definitions for online trainings
TRAINING_COLUMNS = [
    {"key": "employee_external_id", "header": "ID Employé", "width": 15},
    {"key": "employee_name", "header": "Employé", "width": 25},
    {"key": "title", "header": "Titre Formation", "width": 30},
    {"key": "completion_date", "header": "Date Complétion", "width": 15},
    {"key": "expiration_date", "header": "Date Expiration", "width": 15},
    {"key": "days_until_expiration", "header": "Jours Restants", "width": 15},
    {"key": "status", "header": "Statut", "width": 12},
    {"key": "certificate_path", "header": "Certificat", "width": 40},
]

# Column definitions for summary sheet
SUMMARY_COLUMNS = [
    {"key": "metric", "header": "Métrique", "width": 30},
    {"key": "value", "header": "Valeur", "width": 15},
]


# ========== CELL STYLES ==========

# Header row style (blue background, white text, bold)
HEADER_STYLE = {
    "font": {"bold": True, "size": 12, "color": "FFFFFF"},
    "fill": {"fgColor": "4472C4", "bgColor": "4472C4", "fill_type": "solid"},
    "alignment": {"horizontal": "center", "vertical": "center"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}

# Critical/expired status style (red background, white text, bold)
CRITICAL_STYLE = {
    "font": {"bold": True, "color": "FFFFFF"},
    "fill": {"fgColor": "C0504D", "bgColor": "C0504D", "fill_type": "solid"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}

# Warning/critical status style (yellow background, black text, bold)
WARNING_STYLE = {
    "font": {"bold": True, "color": "000000"},
    "fill": {"fgColor": "FFEB9C", "bgColor": "FFEB9C", "fill_type": "solid"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}

# Valid/compliant style (green background, black text)
VALID_STYLE = {
    "font": {"color": "000000"},
    "fill": {"fgColor": "C6EFCE", "bgColor": "C6EFCE", "fill_type": "solid"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}

# Default/neutral style (light gray background)
DEFAULT_STYLE = {
    "font": {"color": "000000"},
    "fill": {"fgColor": "FFFFFF", "bgColor": "FFFFFF", "fill_type": "solid"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}

# Summary metric style (bold, larger)
METRIC_STYLE = {
    "font": {"bold": True, "size": 11},
    "fill": {"fgColor": "F2F2F2", "bgColor": "F2F2F2", "fill_type": "solid"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}

# Summary value style (centered, bold)
VALUE_STYLE = {
    "font": {"bold": True, "size": 12},
    "alignment": {"horizontal": "center", "vertical": "center"},
    "fill": {"fgColor": "E7E6E6", "bgColor": "E7E6E6", "fill_type": "solid"},
    "border": {"top": "thin", "left": "thin", "bottom": "thin", "right": "thin"},
}


# ========== HELPER FUNCTIONS ==========


def get_column_widths(columns: list[dict[str, Any]]) -> list[float]:
    """
    Extract column widths from column definitions.

    Args:
        columns: List of column definition dicts

    Returns:
        List of column widths

    Example:
        >>> widths = get_column_widths(EMPLOYEE_COLUMNS)
        >>> print(widths)
        [15, 25, 15, 20, 12, 15, 18, 15]
    """
    return [col["width"] for col in columns]


def get_style_for_status(status: str) -> dict[str, Any]:
    """
    Return cell style based on status value.

    Args:
        status: Status string ('critical', 'warning', 'valid', 'expired', etc.)

    Returns:
        Style dictionary for the status

    Example:
        >>> style = get_style_for_status('critical')
        >>> print(style['fill']['fgColor'])
        'C0504D'
    """
    status_lower = status.lower()

    if status_lower in ["critical", "expired", "unfit"]:
        return CRITICAL_STYLE
    elif status_lower in ["warning", "expiring_soon"]:
        return WARNING_STYLE
    elif status_lower in ["valid", "compliant", "fit"]:
        return VALID_STYLE
    else:
        return DEFAULT_STYLE


def get_headers_for_columns(columns: list[dict[str, Any]]) -> list[str]:
    """
    Extract header names from column definitions.

    Args:
        columns: List of column definition dicts

    Returns:
        List of header strings

    Example:
        >>> headers = get_headers_for_columns(EMPLOYEE_COLUMNS)
        >>> print(headers[0])
        'ID WMS'
    """
    return [col["header"] for col in columns]


def get_keys_for_columns(columns: list[dict[str, Any]]) -> list[str]:
    """
    Extract data keys from column definitions.

    Args:
        columns: List of column definition dicts

    Returns:
        List of data keys

    Example:
        >>> keys = get_keys_for_columns(EMPLOYEE_COLUMNS)
        >>> print(keys[0])
        'external_id'
    """
    return [col["key"] for col in columns]


def get_all_column_definitions() -> dict[str, list[dict[str, Any]]]:
    """
    Get all column definitions as a dictionary.

    Returns:
        Dictionary mapping entity types to their column definitions

    Example:
        >>> columns = get_all_column_definitions()
        >>> print(columns['employees'][0]['header'])
        'ID WMS'
    """
    return {
        "employees": EMPLOYEE_COLUMNS,
        "caces": CACES_COLUMNS,
        "medical": MEDICAL_COLUMNS,
        "training": TRAINING_COLUMNS,
        "summary": SUMMARY_COLUMNS,
    }
