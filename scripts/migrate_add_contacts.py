#!/usr/bin/env python
"""
Manual SQLite migration for adding contact fields to Employee table.

This script adds phone and email columns to the employees table.

Usage:
    python scripts/migrate_add_contacts.py

Rollback:
    python scripts/migrate_add_contacts.py --rollback
"""

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def migrate(db_path: str, dry_run: bool = False):
    """
    Add phone and email columns to employees table.

    Args:
        db_path: Path to SQLite database file
        dry_run: If True, show SQL without executing
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Start transaction
    cursor.execute("BEGIN TRANSACTION")

    try:
        # Get current schema
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {', '.join(columns)}")

        # Check if phone column exists
        phone_exists = "phone" in columns
        email_exists = "email" in columns

        # Add phone column
        if not phone_exists:
            sql_phone = "ALTER TABLE employees ADD COLUMN phone TEXT"
            if dry_run:
                print(f"\n[DRY RUN] Would execute: {sql_phone}")
            else:
                cursor.execute(sql_phone)
                print("\n[OK] Column 'phone' added")
        else:
            print("\n[SKIP] Column 'phone' already exists")

        # Add email column
        if not email_exists:
            sql_email = "ALTER TABLE employees ADD COLUMN email TEXT"
            if dry_run:
                print(f"[DRY RUN] Would execute: {sql_email}")
            else:
                cursor.execute(sql_email)
                print("[OK] Column 'email' added")
        else:
            print("[SKIP] Column 'email' already exists")

        # Verify new schema
        cursor.execute("PRAGMA table_info(employees)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\nNew columns: {', '.join(new_columns)}")

        # Commit transaction
        if not dry_run:
            conn.commit()
            print("\n[OK] Migration committed successfully")
        else:
            conn.rollback()
            print("\n[OK] Dry run complete (no changes made)")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise

    finally:
        conn.close()


def rollback(db_path: str, dry_run: bool = False):
    """
    Rollback migration by removing phone and email columns.

    WARNING: SQLite doesn't support DROP COLUMN directly.
    This requires recreating the table.

    Args:
        db_path: Path to SQLite database file
        dry_run: If True, show SQL without executing
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Start transaction
    cursor.execute("BEGIN TRANSACTION")

    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]

        phone_exists = "phone" in columns
        email_exists = "email" in columns

        if not phone_exists and not email_exists:
            print("[SKIP] Columns don't exist, nothing to rollback")
            conn.rollback()
            return

        print("\n[WARN] SQLite DROP COLUMN limitation detected")
        print("[INFO] To rollback, you need to:")
        print("  1. Export data excluding phone/email")
        print("  2. Drop the employees table")
        print("  3. Recreate table without phone/email")
        print("  4. Import data back")
        print("\n[RECOMMENDATION] Use database backup instead:")
        print("  1. Restore from: employee_manager.db.backup")
        print("  2. Or use git to revert changes")

        # Show SQL for manual rollback
        print("\n[INFO] Manual rollback SQL (for reference):")

        # Get CREATE TABLE statement
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='employees'")
        create_sql = cursor.fetchone()[0]
        print(f"\nCurrent schema:\n{create_sql}")

        if dry_run:
            print("\n[DRY RUN] Rollback not executed")

        conn.rollback()

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Rollback failed: {e}")
        raise

    finally:
        conn.close()


def backup_database(db_path: str) -> str:
    """
    Create backup of database before migration.

    Args:
        db_path: Path to database file

    Returns:
        Path to backup file
    """
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"\n[INFO] Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print(f"[OK] Backup created: {backup_path}")

    return backup_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate database: Add phone and email columns")
    parser.add_argument("--db", default="employee_manager.db", help="Path to database file")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL without executing")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration")
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser.add_argument("--no-backup", action="store_true", help="Skip automatic backup")

    args = parser.parse_args()

    db_path = args.db

    # Check if database exists
    if not Path(db_path).exists():
        print(f"[ERROR] Database file not found: {db_path}")
        return 1

    # Create backup unless explicitly skipped
    if not args.no_backup and not args.rollback and not args.dry_run:
        backup_database(db_path)

    # Run migration or rollback
    if args.rollback:
        print("=" * 50)
        print(" ROLLBACK MIGRATION")
        print("=" * 50)
        rollback(db_path, args.dry_run)
    else:
        print("=" * 50)
        print(" MIGRATE DATABASE")
        print("=" * 50)
        migrate(db_path, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
