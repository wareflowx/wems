"""Database connection setup with SQLite and WAL mode."""

from pathlib import Path

from peewee import SqliteDatabase

# IMPORTANT: Enable foreign_keys in SQLite to ensure CASCADE delete works
# SQLite by default has ON DELETE disabled, which can cause data integrity issues
database = SqliteDatabase(None, pragmas={"foreign_keys": 1})


def init_database(db_path: Path) -> None:
    """
    Initialize database connection with WAL mode and optimal PRAGMAs.

    Args:
        db_path: Path to SQLite database file
    """
    database.init(db_path)

    # Enable WAL mode for better concurrent read performance
    database.execute_sql("PRAGMA journal_mode=WAL")
    database.execute_sql("PRAGMA synchronous=NORMAL")
    database.execute_sql("PRAGMA busy_timeout=5000")

    # Import all models here to avoid circular imports
    from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
    from lock.models import AppLock

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


def get_database() -> SqliteDatabase:
    """Return the database instance."""
    return database
