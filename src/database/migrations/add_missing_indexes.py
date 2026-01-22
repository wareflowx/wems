"""Migration script to add missing database indexes.

This script adds performance indexes to existing databases:
- Employee table: current_status, workspace, role, contract_type
- MedicalVisit table: result

Run this script on existing databases to improve query performance.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import database
from utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=True)
logger = get_logger(__name__)


def migrate():
    """
    Add missing indexes to existing database.

    This function creates indexes that may be missing from older databases.
    It's safe to run multiple times - indexes will only be created if they don't exist.
    """
    logger.info("Starting database index migration...")

    try:
        # Connect to database
        if database.is_closed():
            database.connect()

        cursor = database.cursor()

        # Employee table indexes
        logger.info("Adding Employee table indexes...")

        employee_indexes = [
            ("idx_employee_current_status", "employees", "current_status"),
            ("idx_employee_workspace", "employees", "workspace"),
            ("idx_employee_role", "employees", "role"),
            ("idx_employee_contract_type", "employees", "contract_type"),
        ]

        for index_name, table, column in employee_indexes:
            try:
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})"
                )
                logger.info(f"Created index: {index_name}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_name}: {e}")

        # MedicalVisit table indexes
        logger.info("Adding MedicalVisit table indexes...")

        medical_indexes = [
            ("idx_medical_result", "medical_visits", "result"),
        ]

        for index_name, table, column in medical_indexes:
            try:
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})"
                )
                logger.info(f"Created index: {index_name}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_name}: {e}")

        # Commit changes
        database.commit()

        # Verify indexes were created
        logger.info("Verifying indexes...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
        indexes = cursor.fetchall()

        logger.info(f"Total indexes in database: {len(indexes)}")

        # List our new indexes
        new_indexes = [
            "idx_employee_current_status",
            "idx_employee_workspace",
            "idx_employee_role",
            "idx_employee_contract_type",
            "idx_medical_result",
        ]

        created_indexes = [idx[0] for idx in indexes if idx[0] in new_indexes]

        if created_indexes:
            logger.info(f"Successfully created {len(created_indexes)} new indexes:")
            for idx in created_indexes:
                logger.info(f"  - {idx}")
        else:
            logger.warning("No new indexes were created (they may already exist)")

        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        if not database.is_closed():
            database.close()
            logger.info("Database connection closed")


def rollback():
    """
    Rollback the migration by dropping the created indexes.

    Use this if you need to remove the indexes.
    """
    logger.info("Rolling back database index migration...")

    try:
        # Connect to database
        if database.is_closed():
            database.connect()

        cursor = database.cursor()

        # Indexes to drop
        indexes_to_drop = [
            "idx_employee_current_status",
            "idx_employee_workspace",
            "idx_employee_role",
            "idx_employee_contract_type",
            "idx_medical_result",
        ]

        for index_name in indexes_to_drop:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
                logger.info(f"Dropped index: {index_name}")
            except Exception as e:
                logger.warning(f"Failed to drop index {index_name}: {e}")

        # Commit changes
        database.commit()

        logger.info("Rollback completed successfully!")

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise
    finally:
        if not database.is_closed():
            database.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database index migration")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (drop indexes)",
    )

    args = parser.parse_args()

    if args.rollback:
        rollback()
    else:
        migrate()
