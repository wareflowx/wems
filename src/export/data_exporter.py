"""
Data Exporter Module

Provides export functionality for employee data in multiple formats:
- JSON (GDPR-compliant data portability)
- Excel (with multiple sheets and formatting)
- CSV (simple tabular format)

Ensures GDPR compliance with:
- Article 15: Right of Access
- Article 20: Data Portability
"""

import csv
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from peewee import prefetch

from employee.models import (
    Employee, Caces, MedicalVisit, OnlineTraining
)

logger = logging.getLogger(__name__)


class DataExporter:
    """Export employee data to various formats."""

    def export_employee_to_json(
        self,
        employee: Employee,
        output_path: Path
    ) -> bool:
        """
        Export single employee data to JSON (GDPR data portability).

        Args:
            employee: Employee to export
            output_path: Output file path

        Returns:
            True if successful, False otherwise

        Raises:
            IOError: If file write fails
        """
        try:
            # Load all related data using prefetch to avoid N+1 queries
            employee = Employee.get_by_id(employee.id)

            # Build complete employee data structure
            employee_data = {
                'employee': {
                    'external_id': employee.external_id,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'email': employee.email,
                    'phone': employee.phone,
                    'entry_date': employee.entry_date.isoformat() if employee.entry_date else None,
                    'current_status': employee.current_status,
                    'workspace': employee.workspace,
                    'role': employee.role,
                    'contract_type': employee.contract_type,
                    'comment': employee.comment,
                },
                'caces': [
                    {
                        'kind': c.kind,
                        'completion_date': c.completion_date.isoformat() if c.completion_date else None,
                        'expiration_date': c.expiration_date.isoformat() if c.expiration_date else None,
                        'document_path': c.document_path,
                    }
                    for c in employee.caces
                ],
                'medical_visits': [
                    {
                        'visit_type': v.visit_type,
                        'visit_date': v.visit_date.isoformat() if v.visit_date else None,
                        'expiration_date': v.expiration_date.isoformat() if v.expiration_date else None,
                        'document_path': v.document_path,
                    }
                    for v in employee.medical_visits
                ],
                'online_trainings': [
                    {
                        'title': t.title,
                        'completion_date': t.completion_date.isoformat() if t.completion_date else None,
                        'expiration_date': t.expiration_date.isoformat() if t.expiration_date else None,
                        'document_path': t.document_path,
                    }
                    for t in employee.online_trainings
                ],
                'export_metadata': {
                    'export_date': datetime.now().isoformat(),
                    'export_version': '1.0',
                    'purpose': 'GDPR data portability',
                }
            }

            # Write to file with UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(employee_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Employee {employee.external_id} exported to JSON: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export to JSON failed for employee {employee.external_id}: {e}")
            raise IOError(f"Failed to export employee to JSON: {e}")

    def export_all_to_excel(self, output_path: Path) -> bool:
        """
        Export all employees to Excel with multiple sheets.

        Creates four sheets:
        - Employés: Employee summary with related counts
        - CACES: Detailed CACES information
        - Visites Médicales: Medical visit details
        - Formations: Online training details

        Args:
            output_path: Output Excel file path

        Returns:
            True if successful, False otherwise

        Raises:
            IOError: If file write fails
        """
        try:
            wb = openpyxl.Workbook()

            # Remove default sheet
            wb.remove(wb.active)

            # Create all sheets
            self._create_employees_sheet(wb)
            self._create_caces_sheet(wb)
            self._create_medical_visits_sheet(wb)
            self._create_training_sheet(wb)

            # Save workbook
            wb.save(output_path)
            logger.info(f"All employees exported to Excel: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export to Excel failed: {e}")
            raise IOError(f"Failed to export to Excel: {e}")

    def _create_employees_sheet(self, workbook):
        """Create employees summary sheet."""
        ws = workbook.create_sheet("Employés")

        # Headers
        headers = [
            "ID Externe", "Nom", "Prénom", "Email", "Téléphone",
            "Date Entrée", "Statut", "Zone", "Poste", "Type Contrat",
            "CACES Actifs", "Visites Actives", "Formations Actives"
        ]

        ws.append(headers)

        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal='center')

        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        # Load employees with related data using prefetch
        employees = list(Employee.select().order_by(Employee.last_name))

        for emp in employees:
            ws.append([
                emp.external_id,
                emp.last_name,
                emp.first_name,
                emp.email or "",
                emp.phone or "",
                emp.entry_date.isoformat() if emp.entry_date else "",
                emp.current_status,
                emp.workspace or "",
                emp.role or "",
                emp.contract_type or "",
                emp.caces.count(),
                emp.medical_visits.count(),
                emp.online_trainings.count(),
            ])

        # Auto-width columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    def _create_caces_sheet(self, workbook):
        """Create CACES detail sheet."""
        ws = workbook.create_sheet("CACES")

        headers = ["Employé", "Kind", "Date Complétion", "Date Expiration", "Statut"]
        ws.append(headers)

        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

        # Load all CACES with employee info
        caces_list = (Caces
                      .select(Caces, Employee)
                      .join(Employee)
                      .order_by(Employee.last_name))

        for c in caces_list:
            status = "Expiré" if c.is_expired else "Valide"
            ws.append([
                c.employee.full_name,
                c.kind,
                c.completion_date.isoformat() if c.completion_date else "",
                c.expiration_date.isoformat() if c.expiration_date else "",
                status,
            ])

        # Auto-width columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    def _create_medical_visits_sheet(self, workbook):
        """Create medical visits sheet."""
        ws = workbook.create_sheet("Visites Médicales")

        headers = ["Employé", "Type Visite", "Date Visite", "Date Expiration", "Statut"]
        ws.append(headers)

        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

        # Load all medical visits with employee info
        visits = (MedicalVisit
                  .select(MedicalVisit, Employee)
                  .join(Employee)
                  .order_by(Employee.last_name))

        for v in visits:
            status = "Expiré" if v.is_expired else "Valide"
            ws.append([
                v.employee.full_name,
                v.visit_type,
                v.visit_date.isoformat() if v.visit_date else "",
                v.expiration_date.isoformat() if v.expiration_date else "",
                status,
            ])

        # Auto-width columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    def _create_training_sheet(self, workbook):
        """Create training sheet."""
        ws = workbook.create_sheet("Formations")

        headers = ["Employé", "Title", "Date Complétion", "Date Expiration", "Statut"]
        ws.append(headers)

        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

        # Load all trainings with employee info
        trainings = (OnlineTraining
                     .select(OnlineTraining, Employee)
                     .join(Employee)
                     .order_by(Employee.last_name))

        for t in trainings:
            status = "Expiré" if t.is_expired else "Valide"
            ws.append([
                t.employee.full_name,
                t.title,
                t.completion_date.isoformat() if t.completion_date else "",
                t.expiration_date.isoformat() if t.expiration_date else "",
                status,
            ])

        # Auto-width columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    def export_to_csv(
        self,
        output_path: Path,
        employees: Optional[List[Employee]] = None
    ) -> bool:
        """
        Export employee data to CSV.

        Args:
            output_path: Output CSV file path
            employees: List of employees to export (all if None)

        Returns:
            True if successful, False otherwise

        Raises:
            IOError: If file write fails
        """
        try:
            if employees is None:
                employees = list(Employee.select().order_by(Employee.last_name))

            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')

                # Headers
                headers = [
                    "ID Externe", "Nom", "Prénom", "Email", "Téléphone",
                    "Date Entrée", "Statut", "Zone", "Poste", "Type Contrat"
                ]
                writer.writerow(headers)

                # Data rows
                for emp in employees:
                    writer.writerow([
                        emp.external_id,
                        emp.last_name,
                        emp.first_name,
                        emp.email or "",
                        emp.phone or "",
                        emp.entry_date.isoformat() if emp.entry_date else "",
                        emp.current_status,
                        emp.workspace or "",
                        emp.role or "",
                        emp.contract_type or "",
                    ])

            logger.info(f"{len(employees)} employees exported to CSV: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export to CSV failed: {e}")
            raise IOError(f"Failed to export to CSV: {e}")
