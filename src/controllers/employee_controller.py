"""Employee controller - business logic for employee views."""

from typing import Any, Dict, Optional

from employee import calculations
from employee.models import Caces, Employee, MedicalVisit, OnlineTraining


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
        return list(
            Employee.select()
            .where(Employee.current_status == "active")
            .order_by(Employee.last_name, Employee.first_name)
        )
