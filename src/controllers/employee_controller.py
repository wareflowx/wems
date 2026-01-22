"""Employee controller - business logic for employee views."""

from typing import Dict, Any, Optional, List
from datetime import date
import logging

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from employee import queries, calculations
from peewee import prefetch

from utils.validation import InputValidator, ValidationError

logger = logging.getLogger(__name__)


class EmployeeController:
    """
    Controller for Employee views.

    Orchestrates data fetching and business logic
    for employee detail and list views.
    """

    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID.

        Args:
            employee_id: Employee UUID as string

        Returns:
            Employee object or None if not found
        """
        try:
            return Employee.get_by_id(employee_id)
        except Employee.DoesNotExist:
            return None

    def get_employee_details(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete employee details for display.

        Args:
            employee_id: Employee UUID as string

        Returns:
            Dictionary with employee data or None if not found:
            {
                'employee': Employee,
                'compliance_score': int,
                'caces_list': List[Caces],
                'medical_visits': List[MedicalVisit],
                'trainings': List[OnlineTraining],
            }
        """
        emp = self.get_employee_by_id(employee_id)
        if not emp:
            return None

        # Get compliance score
        score_data = calculations.calculate_compliance_score(emp)

        # Get certifications with prefetch
        caces = list(emp.caces.order_by(-Caces.expiration_date))
        visits = list(emp.medical_visits.order_by(-MedicalVisit.visit_date))
        trainings = list(emp.trainings.order_by(-OnlineTraining.completion_date))

        # Calculate simple breakdown based on valid/expired counts
        # This is a simplified version for UI display
        caces_valid = sum(1 for c in caces if not c.is_expired)
        caces_score = min(caces_valid * 30, 30) if caces else 0

        medical_valid = sum(1 for v in visits if not v.is_expired and v.result == "fit")
        medical_score = min(medical_valid * 30, 30) if visits else 0

        training_valid = sum(1 for t in trainings if not t.is_expired)
        training_score = min(training_valid * 40, 40) if trainings else 0

        breakdown = {
            "caces": caces_score,
            "medical": medical_score,
            "training": training_score,
        }

        return {
            "employee": emp,
            "compliance_score": score_data["score"],
            "score_breakdown": breakdown,
            "caces_list": caces,
            "medical_visits": visits,
            "trainings": trainings,
        }

    def get_all_employees(self) -> list:
        """
        Get list of all employees for list view.

        Returns:
            List of Employee objects
        """
        return list(Employee.select().order_by(Employee.last_name, Employee.first_name))

    def get_active_employees(self) -> list:
        """
        Get list of active employees.

        Returns:
            List of active Employee objects
        """
        return list(Employee.select()
                    .where(Employee.current_status == 'active')
                    .order_by(Employee.last_name, Employee.first_name))

    def get_employees_with_relations(self) -> List[Employee]:
        """
        Get all employees with related data efficiently using prefetch.

        This method solves the N+1 query problem by loading all related
        data (CACES, Medical Visits, Online Training) in just 4 queries
        instead of 1 + 3N queries.

        Returns:
            List of Employee objects with related data preloaded

        Performance:
            - 100 employees: 4 queries instead of 301 (98.7% reduction)
            - Load time: < 500ms for 100 employees (local DB)
        """
        employees = list(Employee
                         .select()
                         .order_by(Employee.last_name, Employee.first_name)
                         .prefetch(Caces, MedicalVisit, OnlineTraining))
        return employees

    def get_active_employees_with_relations(self) -> List[Employee]:
        """
        Get active employees with related data efficiently.

        Returns:
            List of active Employee objects with related data preloaded

        Performance:
            - Uses prefetch to avoid N+1 queries
            - Filters for active employees
        """
        employees = list(Employee
                         .select()
                         .where(Employee.current_status == 'active')
                         .prefetch(Caces, MedicalVisit, OnlineTraining)
                         .order_by(Employee.last_name, Employee.first_name))
        return employees

    def create_employee(self, **kwargs) -> Employee:
        """
        Create new employee with validation.

        Args:
            **kwargs: Employee data fields

        Returns:
            Created Employee object

        Raises:
            ValueError: If validation fails or duplicate external_id
        """
        try:
            # Validate all input data
            validated_data = InputValidator.validate_employee_data(kwargs)

            # Check for duplicate external_id
            if Employee.select().where(Employee.external_id == validated_data['external_id']).exists():
                raise ValueError(f"Employee with external_id '{validated_data['external_id']}' already exists")

            # Create employee with validated data
            employee = Employee.create(**validated_data)

            logger.info(f"Employee created: {employee.full_name} ({employee.external_id})")
            return employee

        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            raise ValueError(f"Validation error - {e.field}: {e.message}")

    def update_employee(self, employee: Employee, **kwargs) -> Employee:
        """
        Update employee with validation.

        Args:
            employee: Existing Employee object
            **kwargs: Employee data fields to update

        Returns:
            Updated Employee object

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate all input data
            validated_data = InputValidator.validate_employee_data(kwargs)

            # Check if external_id is being changed and if it conflicts
            if 'external_id' in validated_data:
                new_external_id = validated_data['external_id']
                if new_external_id != employee.external_id:
                    if Employee.select().where(
                        (Employee.external_id == new_external_id) &
                        (Employee.id != employee.id)
                    ).exists():
                        raise ValueError(f"Employee with external_id '{new_external_id}' already exists")

            # Update employee fields
            for key, value in validated_data.items():
                setattr(employee, key, value)

            employee.save()

            logger.info(f"Employee updated: {employee.full_name} ({employee.external_id})")
            return employee

        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            raise ValueError(f"Validation error - {e.field}: {e.message}")
