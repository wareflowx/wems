"""Employee-related constants and enums."""


class EmployeeStatus:
    """Employee employment status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = [ACTIVE, INACTIVE]


class ContractType:
    """Employment contract types."""

    CDI = "CDI"
    CDD = "CDD"
    INTERIM = "Interim"
    ALTERNANCE = "Alternance"
    ALL = [CDI, CDD, INTERIM, ALTERNANCE]


class VisitType:
    """Medical visit types."""

    INITIAL = "initial"
    PERIODIC = "periodic"
    RECOVERY = "recovery"
    ALL = [INITIAL, PERIODIC, RECOVERY]


class VisitResult:
    """Medical visit results."""

    FIT = "fit"
    UNFIT = "unfit"
    FIT_WITH_RESTRICTIONS = "fit_with_restrictions"
    ALL = [FIT, UNFIT, FIT_WITH_RESTRICTIONS]


# Standard French CACES certifications
CACES_TYPES = [
    "R489-1A",  # Forklift with upright (porté-à-faux)
    "R489-1B",  # Forklift with retractable mast (mât rétractable)
    "R489-3",  # Heavy forklift ≥ 6 tons
    "R489-4",  # Heavy retractable mast forklift ≥ 6 tons
    "R489-5",  # Side-loading forklift
]

# CACES validity periods in years (configurable in future)
CACES_VALIDITY_YEARS = {
    "R489-1A": 5,
    "R489-1B": 5,
    "R489-3": 5,
    "R489-4": 5,
    "R489-5": 10,  # Different validity period
}

# Medical visit validity periods in years
VISIT_VALIDITY_YEARS = {
    "initial": 2,
    "periodic": 2,
    "recovery": 1,
}

# Default workspaces (configurable in config.json)
DEFAULT_WORKSPACES = [
    "Quai",
    "Zone A",
    "Zone B",
    "Bureau",
]

# Default roles (configurable in config.json)
DEFAULT_ROLES = [
    "Préparateur",
    "Réceptionnaire",
    "Cariste",
]
