"""Test configuration and shared fixtures."""

import tempfile
from datetime import date
from pathlib import Path

import pytest
from peewee import SqliteDatabase


@pytest.fixture(scope="session")
def test_database_file():
    """Create a temporary database file for tests."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".db") as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    try:
        db_path.unlink()
    except:
        pass


@pytest.fixture(scope="function")
def db(test_database_file):
    """Create a fresh database for each test."""
    # Import database connection
    from database.connection import database
    from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
    from lock.models import AppLock

    # Initialize database with temporary file
    database.init(test_database_file)

    # Enable WAL mode
    database.execute_sql("PRAGMA journal_mode=WAL")
    database.execute_sql("PRAGMA synchronous=NORMAL")
    database.execute_sql("PRAGMA busy_timeout=5000")

    # Create all tables
    database.create_tables(
        [
            Employee,
            Caces,
            MedicalVisit,
            OnlineTraining,
            AppLock,
        ],
        safe=True,
    )

    yield database

    # Clean up after test
    database.drop_tables(
        [
            Employee,
            Caces,
            MedicalVisit,
            OnlineTraining,
            AppLock,
        ]
    )

    # Close database
    database.close()


# Keep old test_db for backward compatibility (but not used anymore)
test_db = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})


@pytest.fixture
def sample_employee(db):
    """Create a sample employee for tests."""
    from employee.models import Employee

    employee = Employee.create(
        first_name="John",
        last_name="Doe",
        external_id="EMP001",
        current_status="active",
        workspace="Quai",
        role="Préparateur",
        contract_type="CDI",
        entry_date=date(2020, 1, 15),
    )
    return employee


@pytest.fixture
def inactive_employee(db):
    """Create an inactive employee for tests."""
    from employee.models import Employee

    employee = Employee.create(
        first_name="Jane",
        last_name="Smith",
        external_id="EMP002",
        current_status="inactive",
        workspace="Bureau",
        role="Réceptionnaire",
        contract_type="CDD",
        entry_date=date(2023, 6, 1),
    )
    return employee


@pytest.fixture
def sample_caces(db, sample_employee):
    """Create a sample CACES certification."""
    from employee.models import Caces

    caces = Caces.create(
        employee=sample_employee,
        kind="R489-1A",
        completion_date=date(2023, 1, 1),
        document_path="/documents/caces/test.pdf",
    )
    return caces


@pytest.fixture
def expired_caces(db, sample_employee):
    """Create an expired CACES certification."""
    from employee.models import Caces

    # Create CACES that expired in 2020
    caces = Caces.create(
        employee=sample_employee,
        kind="R489-1B",
        completion_date=date(2015, 1, 1),
        document_path="/documents/caces/expired.pdf",
    )
    return caces


@pytest.fixture
def medical_visit(db, sample_employee):
    """Create a sample medical visit."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type="periodic",
        visit_date=date(2023, 6, 15),
        result="fit",
        document_path="/documents/medical/test.pdf",
    )
    return visit


@pytest.fixture
def unfit_visit(db, sample_employee):
    """Create an unfit medical visit."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type="periodic",  # Changed from 'recovery' (recovery must have restrictions)
        visit_date=date(2023, 1, 1),
        result="unfit",
        document_path="/documents/medical/unfit.pdf",
    )
    return visit


@pytest.fixture
def online_training(db, sample_employee):
    """Create a sample online training."""
    from employee.models import OnlineTraining

    training = OnlineTraining.create(
        employee=sample_employee,
        title="Safety Training",
        completion_date=date(2023, 3, 1),
        validity_months=12,
        certificate_path="/documents/training/test.pdf",
    )
    return training


@pytest.fixture
def permanent_training(db, sample_employee):
    """Create a permanent (non-expiring) training."""
    from employee.models import OnlineTraining

    training = OnlineTraining.create(
        employee=sample_employee,
        title="General Orientation",
        completion_date=date(2023, 1, 1),
        validity_months=None,  # Permanent
    )
    return training


@pytest.fixture
def sample_employee_with_data(db):
    """Create sample employee with CACES, visits, and training."""
    from employee.models import Employee, Caces, MedicalVisit, OnlineTraining

    # Create employee
    employee = Employee.create(
        external_id="DATA001",
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="0987654321",
        entry_date=date(2020, 1, 15),
        current_status="active",
        workspace="Paris",
        role="Engineer",
        contract_type="CDI"
    )

    # Add CACES
    Caces.create(
        employee=employee,
        kind="R489-1A",
        completion_date=date(2020, 1, 1),
        expiration_date=date(2025, 1, 1),
        document_path="/docs/caces.pdf"
    )

    # Add medical visit
    MedicalVisit.create(
        employee=employee,
        visit_type="initial",
        visit_date=date(2020, 1, 10),
        expiration_date=date(2025, 1, 10),
        result="fit",
        document_path="/docs/medical.pdf"
    )

    # Add training
    OnlineTraining.create(
        employee=employee,
        title="Safety Training",
        completion_date=date(2020, 2, 1),
        expiration_date=date(2023, 2, 1),
        certificate_path="/docs/training.pdf"
    )

    return employee


@pytest.fixture
def multiple_employees(db):
    """Create multiple employees for testing."""
    from employee.models import Employee

    employees = []

    for i in range(10):
        employee = Employee.create(
            external_id=f"MULTI{i:03d}",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            email=f"multi{i}@example.com",
            phone=f"12345678{i}",
            entry_date=date(2020, 1, i+1),
            current_status="active" if i % 2 == 0 else "inactive",
            workspace=f"Site{i % 3}",
            role=f"Role{i % 5}",
            contract_type="CDI"
        )
        employees.append(employee)

    return employees
