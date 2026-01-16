"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile
from datetime import date

import cli
from cli import app

runner = CliRunner()


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_help_command(self):
        """Should display help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Simple Employee Manager" in result.stdout

    def test_version_command(self):
        """Should display version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Simple Employee Manager" in result.stdout


class TestEmployeeCommands:
    """Tests for employee commands."""

    def test_list_employees_empty(self, db):
        """Should show message when no employees."""
        result = runner.invoke(app, ["employee", "list"])
        assert result.exit_code == 0
        assert "Aucun employé" in result.stdout or "0 employé" in result.stdout

    def test_list_employees_with_data(self, db, sample_employee):
        """Should list employees."""
        result = runner.invoke(app, ["employee", "list"])
        assert result.exit_code == 0
        assert sample_employee.external_id in result.stdout
        assert sample_employee.full_name in result.stdout

    def test_show_employee(self, db, sample_employee):
        """Should show employee details."""
        result = runner.invoke(app, ["employee", "show", sample_employee.external_id])
        assert result.exit_code == 0
        assert sample_employee.full_name in result.stdout
        assert sample_employee.external_id in result.stdout

    def test_show_nonexistent_employee(self, db):
        """Should show error for non-existent employee."""
        result = runner.invoke(app, ["employee", "show", "NONEXISTENT"])
        assert result.exit_code == 1
        assert "non trouvé" in result.stdout.lower()

    def test_add_employee_non_interactive(self, db):
        """Should add employee with flags."""
        result = runner.invoke(app, [
            "employee", "add",
            "--first-name", "Test",
            "--last-name", "User",
            "--external-id", "CLI-001",
            "--workspace", "Quai",
            "--role", "Cariste",
            "--contract", "CDI",
            "--entry-date", "2020-01-15"
        ])
        assert result.exit_code == 0
        assert "créé avec succès" in result.stdout.lower()
        assert "CLI-001" in result.stdout

    def test_add_employee_duplicate_id(self, db, sample_employee):
        """Should show error for duplicate ID."""
        result = runner.invoke(app, [
            "employee", "add",
            "--first-name", "Test",
            "--last-name", "User",
            "--external-id", sample_employee.external_id,
            "--workspace", "Quai",
            "--role", "Cariste",
            "--contract", "CDI",
            "--entry-date", "2020-01-15"
        ])
        assert result.exit_code == 1
        assert "existe déjà" in result.stdout.lower()

    def test_add_employee_missing_fields(self, db):
        """Should show error for missing required fields."""
        result = runner.invoke(app, [
            "employee", "add",
            "--first-name", "Test",
            "--last-name", "User"
        ])
        assert result.exit_code == 1
        assert "requis" in result.stdout.lower()

    def test_update_employee(self, db, sample_employee):
        """Should update employee."""
        result = runner.invoke(app, [
            "employee", "update", sample_employee.external_id,
            "--workspace", "Zone A",
            "--role", "Magasinier"
        ])
        assert result.exit_code == 0
        assert "mis à jour" in result.stdout.lower()
        assert "Zone A" in result.stdout

    def test_update_nonexistent_employee(self, db):
        """Should show error for non-existent employee."""
        result = runner.invoke(app, [
            "employee", "update", "NONEXISTENT",
            "--workspace", "Zone A"
        ])
        assert result.exit_code == 1

    def test_delete_employee_with_flag(self, db, sample_employee):
        """Should delete employee with --yes flag."""
        result = runner.invoke(app, [
            "employee", "delete", sample_employee.external_id,
            "--yes"
        ])
        assert result.exit_code == 0
        assert "supprimé" in result.stdout.lower()

    def test_delete_employee_without_flag(self, db, sample_employee):
        """Should prompt for confirmation without --yes flag."""
        result = runner.invoke(app, [
            "employee", "delete", sample_employee.external_id
        ])
        # Should show message about --yes since questionary not available in test
        assert result.exit_code == 1 or "annulée" in result.stdout.lower()

    def test_compliance_command(self, db, sample_employee):
        """Should show compliance information."""
        result = runner.invoke(app, ["employee", "compliance", sample_employee.external_id])
        assert result.exit_code == 0
        assert "Compliance" in result.stdout


class TestReportCommands:
    """Tests for report commands."""

    def test_dashboard_empty(self, db):
        """Should show dashboard with no data."""
        result = runner.invoke(app, ["report", "dashboard"])
        assert result.exit_code == 0
        assert "Tableau de Bord" in result.stdout

    def test_dashboard_with_data(self, db, sample_employee):
        """Should show dashboard with employee data."""
        result = runner.invoke(app, ["report", "dashboard"])
        assert result.exit_code == 0
        assert "Tableau de Bord" in result.stdout

    def test_alerts_empty(self, db):
        """Should show no alerts when no expiring items."""
        result = runner.invoke(app, ["report", "alerts"])
        assert result.exit_code == 0

    def test_export_excel(self, db, sample_employee, tmp_path):
        """Should export to Excel."""
        output = tmp_path / "test_export.xlsx"
        result = runner.invoke(app, ["report", "export", str(output)])
        assert result.exit_code == 0
        assert "Export terminé" in result.stdout
        assert output.exists()

    def test_export_excel_no_sheets(self, db, sample_employee, tmp_path):
        """Should export without specific sheets."""
        output = tmp_path / "test_export2.xlsx"
        result = runner.invoke(app, [
            "report", "export", str(output),
            "--no-caces", "--no-visits", "--no-trainings"
        ])
        assert result.exit_code == 0
        assert output.exists()

    def test_stats_empty(self, db):
        """Should show statistics with no data."""
        result = runner.invoke(app, ["report", "stats"])
        assert result.exit_code == 0
        assert "Statistiques" in result.stdout

    def test_stats_with_data(self, db, sample_employee):
        """Should show statistics with data."""
        result = runner.invoke(app, ["report", "stats"])
        assert result.exit_code == 0
        assert "Statistiques" in result.stdout

    def test_compliance_summary(self, db, sample_employee):
        """Should show compliance summary."""
        result = runner.invoke(app, ["report", "compliance-summary"])
        assert result.exit_code == 0
        assert "Résumé de compliance" in result.stdout


class TestCacesCommands:
    """Tests for CACES commands."""

    def test_list_caces_empty(self, db, sample_employee):
        """Should show message when no CACES."""
        result = runner.invoke(app, ["caces", "list", sample_employee.external_id])
        assert result.exit_code == 0
        assert "Aucun CACES" in result.stdout

    def test_list_caces_with_data(self, db, sample_employee, sample_caces):
        """Should list CACES certifications."""
        result = runner.invoke(app, ["caces", "list", sample_employee.external_id])
        assert result.exit_code == 0
        assert sample_caces.kind in result.stdout

    def test_add_caces(self, db, sample_employee):
        """Should add CACES certification."""
        result = runner.invoke(app, [
            "caces", "add", sample_employee.external_id,
            "--kind", "R489-1A",
            "--completion-date", "2020-03-01"
        ])
        assert result.exit_code == 0
        assert "CACES ajouté" in result.stdout

    def test_add_caces_invalid_date(self, db, sample_employee):
        """Should show error for invalid date format."""
        result = runner.invoke(app, [
            "caces", "add", sample_employee.external_id,
            "--kind", "R489-1A",
            "--completion-date", "invalid-date"
        ])
        assert result.exit_code == 1
        assert "Format de date invalide" in result.stdout

    def test_add_caces_nonexistent_employee(self, db):
        """Should show error for non-existent employee."""
        result = runner.invoke(app, [
            "caces", "add", "NONEXISTENT",
            "--kind", "R489-1A",
            "--completion-date", "2020-03-01"
        ])
        assert result.exit_code == 1
        assert "non trouvé" in result.stdout

    def test_expiring_caces_empty(self, db):
        """Should show message when no expiring CACES."""
        result = runner.invoke(app, ["caces", "expiring"])
        assert result.exit_code == 0

    def test_expired_caces_empty(self, db):
        """Should show message when no expired CACES."""
        result = runner.invoke(app, ["caces", "expired"])
        assert result.exit_code == 0


class TestMedicalCommands:
    """Tests for medical visit commands."""

    def test_list_visits_empty(self, db, sample_employee):
        """Should show message when no visits."""
        result = runner.invoke(app, ["medical", "list", sample_employee.external_id])
        assert result.exit_code == 0
        assert "Aucune visite" in result.stdout

    def test_list_visits_with_data(self, db, sample_employee, medical_visit):
        """Should list medical visits."""
        result = runner.invoke(app, ["medical", "list", sample_employee.external_id])
        assert result.exit_code == 0
        assert medical_visit.visit_type in result.stdout

    def test_add_visit(self, db, sample_employee):
        """Should add medical visit."""
        result = runner.invoke(app, [
            "medical", "add", sample_employee.external_id,
            "--type", "periodic",
            "--date", "2024-01-15",
            "--result", "fit"
        ])
        assert result.exit_code == 0
        assert "Visite médicale ajoutée" in result.stdout

    def test_add_visit_invalid_type(self, db, sample_employee):
        """Should show error for invalid visit type."""
        result = runner.invoke(app, [
            "medical", "add", sample_employee.external_id,
            "--type", "invalid",
            "--date", "2024-01-15",
            "--result", "fit"
        ])
        assert result.exit_code == 1
        assert "invalide" in result.stdout

    def test_add_visit_invalid_result(self, db, sample_employee):
        """Should show error for invalid result."""
        result = runner.invoke(app, [
            "medical", "add", sample_employee.external_id,
            "--type", "periodic",
            "--date", "2024-01-15",
            "--result", "invalid"
        ])
        assert result.exit_code == 1
        assert "invalide" in result.stdout

    def test_expiring_visits_empty(self, db):
        """Should show message when no expiring visits."""
        result = runner.invoke(app, ["medical", "expiring"])
        assert result.exit_code == 0

    def test_unfit_empty(self, db):
        """Should show message when no unfit employees."""
        result = runner.invoke(app, ["medical", "unfit"])
        assert result.exit_code == 0
        assert "Aucun employé inapte" in result.stdout


class TestTrainingCommands:
    """Tests for training commands."""

    def test_list_trainings_empty(self, db, sample_employee):
        """Should show message when no trainings."""
        result = runner.invoke(app, ["training", "list", sample_employee.external_id])
        assert result.exit_code == 0
        assert "Aucune formation" in result.stdout

    def test_list_trainings_with_data(self, db, sample_employee, online_training):
        """Should list trainings."""
        result = runner.invoke(app, ["training", "list", sample_employee.external_id])
        assert result.exit_code == 0
        assert online_training.title in result.stdout

    def test_add_training(self, db, sample_employee):
        """Should add training with validity."""
        result = runner.invoke(app, [
            "training", "add", sample_employee.external_id,
            "--title", "Safety Training",
            "--completion-date", "2024-01-15",
            "--validity-months", "12"
        ])
        assert result.exit_code == 0
        assert "Formation ajoutée" in result.stdout

    def test_add_permanent_training(self, db, sample_employee):
        """Should add permanent training."""
        result = runner.invoke(app, [
            "training", "add", sample_employee.external_id,
            "--title", "Fire Safety",
            "--completion-date", "2024-01-15",
            "--permanent"
        ])
        assert result.exit_code == 0
        assert "Formation ajoutée" in result.stdout
        assert "Permanent" in result.stdout

    def test_add_training_missing_expiration(self, db, sample_employee):
        """Should show error when neither permanent nor validity specified."""
        result = runner.invoke(app, [
            "training", "add", sample_employee.external_id,
            "--title", "Safety Training",
            "--completion-date", "2024-01-15"
        ])
        assert result.exit_code == 1
        assert "permanent" in result.stdout.lower() or "validity" in result.stdout.lower()

    def test_expiring_trainings_empty(self, db):
        """Should show message when no expiring trainings."""
        result = runner.invoke(app, ["training", "expiring"])
        assert result.exit_code == 0


class TestLockCommands:
    """Tests for lock commands."""

    def test_lock_status_no_lock(self, db):
        """Should show status when no lock."""
        result = runner.invoke(app, ["lock", "status"])
        assert result.exit_code == 0
        assert "Libre" in result.stdout

    def test_lock_acquire_and_release(self, db):
        """Should acquire and release lock."""
        # Acquire
        result = runner.invoke(app, ["lock", "acquire"])
        assert result.exit_code == 0
        assert "acquis" in result.stdout.lower()

        # Status
        result = runner.invoke(app, ["lock", "status"])
        assert result.exit_code == 0
        assert "Verrouillé" in result.stdout

        # Release
        result = runner.invoke(app, ["lock", "release"])
        assert result.exit_code == 0
        assert("libéré" in result.stdout.lower() or "non trouvé" in result.stdout.lower())

    def test_lock_refresh(self, db):
        """Should refresh lock heartbeat."""
        # First acquire
        runner.invoke(app, ["lock", "acquire"])

        # Then refresh
        result = runner.invoke(app, ["lock", "refresh"])
        assert result.exit_code == 0
        assert "Heartbeat" in result.stdout

        # Clean up
        runner.invoke(app, ["lock", "release"])

    def test_lock_info(self, db):
        """Should show detailed lock information."""
        # Acquire first
        runner.invoke(app, ["lock", "acquire"])

        # Get info
        result = runner.invoke(app, ["lock", "info"])
        assert result.exit_code == 0

        # Clean up
        runner.invoke(app, ["lock", "release"])


class TestCLIWorkflows:
    """Tests for complete CLI workflows."""

    def test_full_employee_workflow(self, db, tmp_path):
        """Test complete employee management workflow."""
        employee_id = "WORKFLOW-001"

        # 1. Create employee
        result = runner.invoke(app, [
            "employee", "add",
            "--first-name", "Workflow",
            "--last-name", "Test",
            "--external-id", employee_id,
            "--workspace", "Quai",
            "--role", "Cariste",
            "--contract", "CDI",
            "--entry-date", "2020-01-15"
        ])
        assert result.exit_code == 0
        assert "créé avec succès" in result.stdout.lower()

        # 2. Add CACES
        result = runner.invoke(app, [
            "caces", "add", employee_id,
            "--kind", "R489-1A",
            "--completion-date", "2020-03-01"
        ])
        assert result.exit_code == 0

        # 3. Add medical visit
        result = runner.invoke(app, [
            "medical", "add", employee_id,
            "--type", "periodic",
            "--date", "2024-01-15",
            "--result", "fit"
        ])
        assert result.exit_code == 0

        # 4. Check compliance
        result = runner.invoke(app, ["employee", "compliance", employee_id])
        assert result.exit_code == 0

        # 5. Export to Excel
        output = tmp_path / "workflow.xlsx"
        result = runner.invoke(app, ["report", "export", str(output)])
        assert result.exit_code == 0
        assert output.exists()

        # 6. Delete employee
        result = runner.invoke(app, [
            "employee", "delete", employee_id,
            "--yes"
        ])
        assert result.exit_code == 0
        assert "supprimé" in result.stdout.lower()

    def test_dashboard_aggregation(self, db, sample_employee, sample_caces, medical_visit, online_training):
        """Test that dashboard aggregates data correctly."""
        result = runner.invoke(app, ["report", "dashboard"])
        assert result.exit_code == 0
        assert "Tableau de Bord" in result.stdout
