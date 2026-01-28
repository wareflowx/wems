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
    APPRENTICESHIP = "Apprenticeship"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"
    ALL = [CDI, CDD, INTERIM, ALTERNANCE, APPRENTICESHIP, INTERNSHIP, FREELANCE]


class ContractStatus:
    """Contract status values."""

    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"
    PENDING = "pending"
    ALL = [ACTIVE, ENDED, CANCELLED, PENDING]


class ContractEndReason:
    """Reasons for contract ending."""

    RESIGNATION = "resignation"
    TERMINATION = "termination"
    COMPLETION = "completion"
    MUTUAL_AGREEMENT = "mutual_agreement"
    RETIREMENT = "retirement"
    DEATH = "death"
    OTHER = "other"
    ALL = [RESIGNATION, TERMINATION, COMPLETION, MUTUAL_AGREEMENT, RETIREMENT, DEATH, OTHER]


class ContractAmendmentType:
    """Types of contract amendments."""

    SALARY_CHANGE = "salary_change"
    POSITION_CHANGE = "position_change"
    DEPARTMENT_CHANGE = "department_change"
    HOURS_CHANGE = "hours_change"
    CONTRACT_TYPE_CHANGE = "contract_type_change"
    OTHER = "other"
    ALL = [SALARY_CHANGE, POSITION_CHANGE, DEPARTMENT_CHANGE, HOURS_CHANGE, CONTRACT_TYPE_CHANGE, OTHER]


# Amendment types with display names
CONTRACT_AMENDMENT_TYPES = {
    "salary_change": "Salary Change",
    "position_change": "Position Change",
    "department_change": "Department Change",
    "hours_change": "Hours Change",
    "extension": "Contract Extension",
    "other": "Other",
}

# Contract end reasons with display names
CONTRACT_END_REASONS = {
    "resignation": "Resignation",
    "termination": "Termination",
    "completion": "Contract Completion",
    "mutual_agreement": "Mutual Agreement",
    "retirement": "Retirement",
    "death": "Death",
    "other": "Other",
}


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

# Default departments for contracts
DEFAULT_DEPARTMENTS = [
    "Logistics",
    "Production",
    "Maintenance",
    "Administration",
    "Warehouse",
    "Shipping",
    "Receiving",
]

# Default positions for contracts
DEFAULT_POSITIONS = [
    "Operator",
    "Warehouse Worker",
    "Forklift Operator",
    "Team Lead",
    "Supervisor",
    "Manager",
]

# Default weekly hours by contract type
DEFAULT_WEEKLY_HOURS = {
    "CDI": 35.0,
    "CDD": 35.0,
    "Interim": 35.0,
    "Alternance": 35.0,
    "Apprenticeship": 39.0,
    "Internship": 35.0,
    "Freelance": 35.0,
}

# Standard trial period duration in days by contract type
TRIAL_PERIOD_DAYS = {
    "CDI": 60,  # 2 months for CDI
    "CDD": None,  # No statutory trial period for CDD
    "Interim": None,  # No trial period for interim
    "Alternance": 45,  # 45 days for apprenticeship
    "Apprenticeship": 45,
    "Internship": None,
    "Freelance": None,
}

# Alert thresholds for contracts (in days)
CONTRACT_EXPIRATION_WARNING_DAYS = 90
CONTRACT_EXPIRATION_CRITICAL_DAYS = 30
TRIAL_PERIOD_WARNING_DAYS = 7
