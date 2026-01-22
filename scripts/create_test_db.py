#!/usr/bin/env python
"""Create a test database for migration testing."""

import sys

sys.path.insert(0, "src")

from datetime import date
from pathlib import Path

from database.connection import init_database
from employee.models import Employee


def create_test_database(db_path: str = "test_employee.db"):
    """
    Create a test database with sample data.

    Args:
        db_path: Path to test database file

    Returns:
        Path to created database
    """
    # Remove existing test database
    if Path(db_path).exists():
        Path(db_path).unlink()
        print(f"[INFO] Removed existing test database: {db_path}")

    # Initialize database
    init_database(Path(db_path))
    print(f"[OK] Database initialized: {db_path}")

    # Create sample employees
    employees = [
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "current_status": "active",
            "workspace": "Zone A",
            "role": "Cariste",
            "contract_type": "CDI",
            "entry_date": date(2024, 1, 15),
        },
        {
            "first_name": "Marie",
            "last_name": "Martin",
            "current_status": "active",
            "workspace": "Zone B",
            "role": "Préparateur de commandes",
            "contract_type": "CDD",
            "entry_date": date(2024, 3, 1),
        },
        {
            "first_name": "Pierre",
            "last_name": "Bernard",
            "current_status": "inactive",
            "workspace": "Zone A",
            "role": "Magasinier",
            "contract_type": "Interim",
            "entry_date": date(2023, 6, 15),
        },
    ]

    for emp_data in employees:
        Employee.create(**emp_data)

    print(f"[OK] Created {len(employees)} test employees")
    print(f"\nTest employees:")
    for emp in Employee.select():
        print(f"  - {emp.full_name} ({emp.current_status})")

    return db_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create test database")
    parser.add_argument("--db", default="test_employee.db", help="Path to test database")

    args = parser.parse_args()

    create_test_database(args.db)

    print(f"\n[OK] Test database ready: {args.db}")
    print("You can now test migration on this database.")
