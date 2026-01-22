#!/usr/bin/env python
"""Phase 0 validation script."""

import sys
from pathlib import Path


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def check_imports():
    """Check all required imports."""
    print_section("CHECKING IMPORTS")

    all_ok = True

    # Check CustomTkinter
    try:
        import customtkinter

        version = customtkinter.__version__
        print(f"[OK] CustomTkinter {version}")
    except ImportError as e:
        print(f"[FAIL] CustomTkinter: {e}")
        all_ok = False

    # Check Pillow
    try:
        from PIL import Image

        print("[OK] Pillow")
    except ImportError as e:
        print(f"[FAIL] Pillow: {e}")
        all_ok = False

    # Check Peewee
    try:
        import peewee

        print("[OK] Peewee")
    except ImportError as e:
        print(f"[FAIL] Peewee: {e}")
        all_ok = False

    # Check openpyxl
    try:
        import openpyxl

        print("[OK] openpyxl")
    except ImportError as e:
        print(f"[FAIL] openpyxl: {e}")
        all_ok = False

    return all_ok


def check_customtkinter():
    """Check CustomTkinter functionality."""
    print_section("CHECKING CUSTOMTKINTER")

    all_ok = True

    try:
        import customtkinter as ctk

        # Test theme modes
        for mode in ["System", "Dark", "Light"]:
            ctk.set_appearance_mode(mode)
        print("[OK] Theme modes (System, Dark, Light)")

        # Test color themes
        for theme in ["blue", "green", "dark-blue"]:
            ctk.set_default_color_theme(theme)
        print("[OK] Color themes (blue, green, dark-blue)")

        return True
    except Exception as e:
        print(f"[FAIL] CustomTkinter functionality: {e}")
        return False


def check_database():
    """Check database connection."""
    print_section("CHECKING DATABASE")

    try:
        sys.path.insert(0, "src")
        from pathlib import Path

        from database.connection import database, init_database
        from employee.models import Employee

        # Initialize database with default path
        db_path = Path("employee_manager.db")
        if not db_path.exists():
            # Try alternative path
            db_path = Path("data/employee_manager.db")

        init_database(db_path)

        # Check if already connected from previous test
        try:
            # If already connected, just query
            tables = database.get_tables()
            print("[OK] Database already connected (reusing)")
        except:
            # Not connected, connect now
            database.connect()
            print("[OK] Database connection established")

        # Check tables exist
        tables = database.get_tables()
        print(f"[OK] Tables found: {', '.join(tables)}")

        # Check Employee model
        count = Employee.select().count()
        print(f"[OK] Employee table ({count} rows)")

        # Don't close - let Peewee handle connection pooling
        return True
    except Exception as e:
        print(f"[FAIL] Database: {e}")
        return False


def check_folder_structure():
    """Check folder structure."""
    print_section("CHECKING FOLDER STRUCTURE")

    required = [
        ("src/employee", "Employee models"),
        ("src/database", "Database setup"),
        ("src/controllers", "Controllers"),
        ("src/state", "State management"),
        ("src/lock", "Lock manager"),
        ("src/ui_ctk", "CustomTkinter UI"),
        ("src/ui_ctk/views", "UI Views"),
        ("src/ui_ctk/forms", "UI Forms"),
        ("src/ui_ctk/widgets", "Custom Widgets"),
        ("src/ui_ctk/utils", "Utilities"),
    ]

    all_ok = True
    for folder, description in required:
        path = Path(folder)
        if path.exists() and path.is_dir():
            print(f"[OK] {folder} ({description})")
        else:
            print(f"[FAIL] {folder} ({description}) - missing")
            all_ok = False

    return all_ok


def check_ui_ctk_package():
    """Check ui_ctk package structure."""
    print_section("CHECKING UI_CTK PACKAGE")

    all_ok = True

    # Check constants
    try:
        sys.path.insert(0, "src")
        from ui_ctk.constants import APP_NAME, APP_TITLE

        print(f"[OK] constants.py (APP_NAME={APP_NAME})")
    except ImportError as e:
        print(f"[FAIL] constants.py: {e}")
        all_ok = False

    # Check base view
    try:
        from ui_ctk.views.base_view import BaseView

        print("[OK] views/base_view.py")
    except ImportError as e:
        print(f"[FAIL] views/base_view.py: {e}")
        all_ok = False

    # Check base form
    try:
        from ui_ctk.forms.base_form import BaseFormDialog

        print("[OK] forms/base_form.py")
    except ImportError as e:
        print(f"[FAIL] forms/base_form.py: {e}")
        all_ok = False

    return all_ok


def check_phone_email_fields():
    """Check that phone and email fields exist in Employee model."""
    print_section("CHECKING EMPLOYEE MODEL")

    try:
        sys.path.insert(0, "src")
        from employee.models import Employee

        # Check if phone field exists
        if hasattr(Employee, "phone"):
            print("[OK] Employee.phone field exists")
        else:
            print("[FAIL] Employee.phone field missing")
            return False

        # Check if email field exists
        if hasattr(Employee, "email"):
            print("[OK] Employee.email field exists")
        else:
            print("[FAIL] Employee.email field missing")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Employee model check: {e}")
        return False


def main():
    """Run all validation checks."""
    print("=" * 50)
    print(" PHASE 0 VALIDATION")
    print("=" * 50)

    results = []

    # Run all checks
    results.append(("Imports", check_imports()))
    results.append(("CustomTkinter", check_customtkinter()))
    results.append(("Database", check_database()))
    results.append(("Folder Structure", check_folder_structure()))
    results.append(("UI Package", check_ui_ctk_package()))
    results.append(("Employee Model", check_phone_email_fields()))

    # Print summary
    print_section("VALIDATION SUMMARY")

    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    # Final result
    print("\n" + "=" * 50)
    if all_passed:
        print(" [OK] ALL CHECKS PASSED")
        print(" Phase 0 complete. Ready for Phase 1.")
        print("=" * 50)
        return 0
    else:
        print(" [FAIL] SOME CHECKS FAILED")
        print(" Please fix the issues above before proceeding.")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())
