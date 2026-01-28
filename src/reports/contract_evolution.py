"""Contract evolution reporting module.

This module provides functionality to analyze and report on employee contract
evolution over time, including:
- Position changes
- Salary progression
- Department transfers
- Contract type transitions
- Employment gaps
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from employee.models import Contract, Employee


@dataclass
class PositionChange:
    """Represents a position change in an employee's career."""

    from_position: str
    to_position: str
    change_date: date
    contract_type: str
    department: Optional[str] = None


@dataclass
class SalaryChange:
    """Represents a salary adjustment over time."""

    salary: float
    date: date
    position: str
    contract_type: str
    change_percentage: Optional[float] = None


@dataclass
class DepartmentChange:
    """Represents a department transfer."""

    from_department: str
    to_department: str
    change_date: date
    position: str
    contract_type: str


@dataclass
class EmploymentGap:
    """Represents a gap in employment (no active contract)."""

    gap_start: date
    gap_end: date
    gap_days: int
    previous_contract_type: Optional[str]
    next_contract_type: Optional[str]


@dataclass
class ContractEvolutionReport:
    """
    Comprehensive contract evolution report for an employee.

    Analyzes an employee's complete contract history to provide insights
    into career progression, salary evolution, and employment patterns.
    """

    employee: Employee
    total_contracts: int
    total_tenure_days: int
    total_experience_years: float
    position_changes: List[PositionChange] = field(default_factory=list)
    salary_evolution: List[SalaryChange] = field(default_factory=list)
    department_changes: List[DepartmentChange] = field(default_factory=list)
    contract_type_changes: List[dict] = field(default_factory=list)
    employment_gaps: List[EmploymentGap] = field(default_factory=list)

    # Summary statistics
    total_salary_increase: float = 0
    current_salary: Optional[float] = None
    starting_salary: Optional[float] = None
    career_path_levels: int = 0

    @property
    def has_gaps(self) -> bool:
        """Check if there are any employment gaps."""
        return len(self.employment_gaps) > 0

    @property
    def total_gap_days(self) -> int:
        """Calculate total days of unemployment gaps."""
        return sum(gap.gap_days for gap in self.employment_gaps)

    @property
    def average_tenure_per_contract(self) -> float:
        """Calculate average tenure per contract in days."""
        if self.total_contracts == 0:
            return 0.0
        return self.total_tenure_days / self.total_contracts

    @property
    def position_count(self) -> int:
        """Count unique positions held."""
        unique_positions = set(change.to_position for change in self.position_changes)
        return len(unique_positions)

    @property
    def department_count(self) -> int:
        """Count unique departments worked in."""
        unique_depts = set(change.to_department for change in self.department_changes if change.to_department)
        return len(unique_depts)

    def to_dict(self) -> dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "employee_id": str(self.employee.id),
            "employee_name": self.employee.full_name,
            "total_contracts": self.total_contracts,
            "total_tenure_days": self.total_tenure_days,
            "total_experience_years": self.total_experience_years,
            "total_gap_days": self.total_gap_days,
            "has_gaps": self.has_gaps,
            "position_changes_count": len(self.position_changes),
            "salary_changes_count": len(self.salary_evolution),
            "department_changes_count": len(self.department_changes),
            "current_salary": self.current_salary,
            "starting_salary": self.starting_salary,
            "total_salary_increase": self.total_salary_increase,
            "average_tenure_per_contract": self.average_tenure_per_contract,
            "position_count": self.position_count,
            "department_count": self.department_count,
            "position_changes": [
                {
                    "from_position": change.from_position,
                    "to_position": change.to_position,
                    "change_date": change.change_date.isoformat(),
                    "contract_type": change.contract_type,
                    "department": change.department,
                }
                for change in self.position_changes
            ],
            "salary_evolution": [
                {
                    "salary": change.salary,
                    "date": change.date.isoformat(),
                    "position": change.position,
                    "change_percentage": change.change_percentage,
                    "contract_type": change.contract_type,
                }
                for change in self.salary_evolution
            ],
            "department_changes": [
                {
                    "from_department": change.from_department,
                    "to_department": change.to_department,
                    "change_date": change.change_date.isoformat(),
                    "position": change.position,
                    "contract_type": change.contract_type,
                }
                for change in self.department_changes
            ],
            "employment_gaps": [
                {
                    "gap_start": gap.gap_start.isoformat(),
                    "gap_end": gap.gap_end.isoformat(),
                    "gap_days": gap.gap_days,
                    "previous_contract_type": gap.previous_contract_type,
                    "next_contract_type": gap.next_contract_type,
                }
                for gap in self.employment_gaps
            ],
        }


def generate_contract_evolution_report(employee: Employee) -> ContractEvolutionReport:
    """
    Generate a comprehensive contract evolution report for an employee.

    Analyzes all contracts in chronological order to detect:
    - Position changes and promotions
    - Salary progression over time
    - Department transfers
    - Contract type transitions (CDD → CDI, etc.)
    - Gaps in employment

    Args:
        employee: Employee object to analyze

    Returns:
        ContractEvolutionReport with complete analysis
    """
    contracts = list(
        Contract.select()
        .where(Contract.employee == employee)
        .order_by(Contract.start_date.asc())
    )

    if not contracts:
        # No contracts yet, create empty report
        return ContractEvolutionReport(
            employee=employee,
            total_contracts=0,
            total_tenure_days=employee.tenure_days,
            total_experience_years=employee.experience_years,
        )

    # Initialize tracking variables
    position_changes: List[PositionChange] = []
    salary_evolution: List[SalaryChange] = []
    department_changes: List[DepartmentChange] = []
    employment_gaps: List[EmploymentGap] = []
    contract_type_history: List[dict] = []

    previous_contract = None
    starting_salary: Optional[float] = None
    total_salary_increase = 0.0

    for i, contract in enumerate(contracts):
        # Track contract type history
        contract_type_history.append({
            "contract_type": contract.contract_type,
            "start_date": contract.start_date.isoformat(),
            "end_date": contract.end_date.isoformat() if contract.end_date else None,
            "position": contract.position,
            "department": contract.department,
            "status": contract.status,
        })

        # Track salary evolution
        if contract.gross_salary:
            current_salary = float(contract.gross_salary)
            salary_evolution.append(
                SalaryChange(
                    salary=current_salary,
                    date=contract.start_date,
                    position=contract.position,
                    contract_type=contract.contract_type,
                )
            )

            # Calculate salary increase
            if previous_contract and previous_contract.gross_salary:
                previous_salary = float(previous_contract.gross_salary)
                increase = current_salary - previous_salary
                if increase != 0:
                    percentage = (increase / previous_salary) * 100
                    salary_evolution[-1].change_percentage = percentage
                    total_salary_increase += increase

            # Set starting salary (first contract with salary)
            if starting_salary is None and i == 0:
                starting_salary = current_salary

        # Detect position changes
        if previous_contract and previous_contract.position != contract.position:
            position_changes.append(
                PositionChange(
                    from_position=previous_contract.position,
                    to_position=contract.position,
                    change_date=contract.start_date,
                    contract_type=contract.contract_type,
                    department=contract.department if contract.department else None,
                )
            )

        # Detect department changes
        if previous_contract and previous_contract.department != contract.department:
            department_changes.append(
                DepartmentChange(
                    from_department=previous_contract.department,
                    to_department=contract.department,
                    change_date=contract.start_date,
                    position=contract.position,
                    contract_type=contract.contract_type,
                )
            )

        # Detect employment gaps
        if previous_contract:
            if previous_contract.end_date and contract.start_date:
                gap = (contract.start_date - previous_contract.end_date).days
                if gap > 0:
                    employment_gaps.append(
                        EmploymentGap(
                            gap_start=previous_contract.end_date,
                            gap_end=contract.start_date,
                            gap_days=gap,
                            previous_contract_type=previous_contract.contract_type,
                            next_contract_type=contract.contract_type,
                        )
                    )

        previous_contract = contract

    # Get current salary (from most recent contract)
    current_salary = None
    if contracts and contracts[-1].gross_salary:
        current_salary = float(contracts[-1].gross_salary)

    # Calculate career path levels (simple heuristic: positions with "Lead", "Supervisor", "Manager")
    career_keywords = ["lead", "supervisor", "manager", "chef", "head"]
    career_path_levels = sum(
        1
        for change in position_changes
        if any(keyword in change.to_position.lower() for keyword in career_keywords)
    )

    # Calculate total tenure
    first_contract = contracts[0]
    last_contract = contracts[-1]
    if last_contract.end_date:
        # Employee not currently active
        total_tenure_days = (last_contract.end_date - first_contract.start_date).days
    else:
        # Currently employed or CDI
        total_tenure_days = employee.tenure_days

    return ContractEvolutionReport(
        employee=employee,
        total_contracts=len(contracts),
        total_tenure_days=total_tenure_days,
        total_experience_years=total_tenure_days / 365.25,
        position_changes=position_changes,
        salary_evolution=salary_evolution,
        department_changes=department_changes,
        contract_type_changes=contract_type_history,
        employment_gaps=employment_gaps,
        starting_salary=starting_salary,
        current_salary=current_salary,
        total_salary_increase=total_salary_increase,
        career_path_levels=career_path_levels,
    )


def generate_evolution_timeline_report(employee: Employee) -> List[dict]:
    """
    Generate a timeline visualization of employee's contract evolution.

    Returns a list of timeline events suitable for visualization.

    Args:
        employee: Employee object

    Returns:
        List of timeline events in chronological order
    """
    contracts = list(
        Contract.select()
        .where(Contract.employee == employee)
        .order_by(Contract.start_date.asc())
    )

    timeline = []

    for contract in contracts:
        # Start event
        timeline.append({
            "date": contract.start_date.isoformat(),
            "event_type": "contract_start",
            "title": f"Started {contract.contract_type}",
            "description": f"Position: {contract.position} in {contract.department}",
            "contract_type": contract.contract_type,
            "position": contract.position,
            "department": contract.department,
        })

        # Trial period end event (if applicable)
        if contract.trial_period_end:
            timeline.append({
                "date": contract.trial_period_end.isoformat(),
                "event_type": "trial_period_end",
                "title": "Trial period ended",
                "description": f"Successfully completed trial period",
            })

        # End event (if applicable)
        if contract.end_date:
            timeline.append({
                "date": contract.end_date.isoformat(),
                "event_type": "contract_end",
                "title": f"Contract ended ({contract.contract_type})",
                "description": f"Reason: {contract.end_reason or 'Not specified'}",
                "contract_type": contract.contract_type,
            })

    return timeline


def detect_employment_patterns(contracts: List[Contract]) -> dict:
    """
    Detect common employment patterns across multiple contracts.

    Args:
        contracts: List of Contract objects to analyze

    Returns:
        Dictionary with pattern analysis
    """
    if not contracts:
        return {
            "total_contracts": 0,
            "contract_types": {},
            "most_common_position": None,
            "most_common_department": None,
            "average_contract_duration_days": None,
        }

    contract_types = {}
    positions = []
    departments = []
    durations = []

    for contract in contracts:
        # Count contract types
        contract_types[contract.contract_type] = contract_types.get(contract.contract_type, 0) + 1

        # Track positions and departments
        positions.append(contract.position)
        departments.append(contract.department)

        # Track durations
        if contract.duration_days:
            durations.append(contract.duration_days)

    # Find most common
    most_common_position = max(set(positions), key=positions.count) if positions else None
    most_common_department = max(set(departments), key=departments.count) if departments else None

    # Calculate average duration
    average_duration = sum(durations) / len(durations) if durations else None

    return {
        "total_contracts": len(contracts),
        "contract_types": contract_types,
        "most_common_position": most_common_position,
        "most_common_department": most_common_department,
        "average_contract_duration_days": average_duration,
        "has_permanent_contract": any(c.end_date is None for c in contracts),
    }
