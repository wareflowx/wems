"""Database migration framework.

Provides base classes and utilities for creating and managing database migrations.

Migration Lifecycle:
1. Create migration file with unique timestamp
2. Implement up() and down() methods
3. Run migration: adds record to migrations table
4. Rollback: removes record and calls down()
"""

import importlib
import re
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional

from database.connection import database
from database.migration_model import (
    delete_migration,
    get_applied_migrations,
    get_last_batch_number,
    record_migration,
)
from utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=False)
logger = get_logger(__name__)


class MigrationError(Exception):
    """Base exception for migration errors."""
    pass


class RollbackError(Exception):
    """Exception raised when rollback fails."""
    pass


class BaseMigration(ABC):
    """Base class for all migrations.

    Each migration must implement:
    - up(): Apply the migration
    - down(): Rollback the migration
    - name(): Unique identifier (format: YYYYMMDD_HHMMSS_description)
    """

    @abstractmethod
    def up(self) -> None:
        """Apply the migration.

        This method should contain all SQL/ORM changes to upgrade the database.
        """
        pass

    @abstractmethod
    def down(self) -> None:
        """Rollback the migration.

        This method should reverse all changes made in up().
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return unique migration name.

        Format: YYYYMMDD_HHMMSS_description
        Example: 20250123_143000_add_department_field
        """
        pass

    def pre_check(self) -> bool:
        """Run pre-migration validation. Return True if safe to proceed.

        Override this method to add custom validation logic.
        """
        return True

    def post_check(self) -> bool:
        """Run post-migration validation. Return True if migration succeeded.

        Override this method to add custom validation logic.
        """
        return True


def backup_database(db_path: Path) -> Path:
    """Create a backup of the database before migration.

    Args:
        db_path: Path to database file

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    backup_name = f"before_migration_{timestamp}.db"
    backup_path = backup_dir / backup_name

    logger.info(f"Creating database backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    logger.info(f"Backup created successfully")

    return backup_path


def restore_database(backup_path: Path, db_path: Path) -> None:
    """Restore database from backup.

    Args:
        backup_path: Path to backup file
        db_path: Target database path
    """
    logger.info(f"Restoring database from: {backup_path}")
    shutil.copy2(backup_path, db_path)
    logger.info(f"Database restored successfully")


def validate_migration_name(name: str) -> bool:
    """Validate migration name format.

    Args:
        name: Migration name to validate

    Returns:
        True if valid, False otherwise

    Format: YYYYMMDD_HHMMSS_description
    Example: 20250123_143000_add_department_field
    """
    pattern = r"^\d{8}_\d{6}_[a-z][a-z0-9_]*$"
    return bool(re.match(pattern, name))


def discover_migrations(migrations_dir: Path) -> list[Path]:
    """Discover all migration files in the migrations directory.

    Args:
        migrations_dir: Path to migrations directory

    Returns:
        Sorted list of migration file paths
    """
    if not migrations_dir.exists():
        logger.warning(f"Migrations directory not found: {migrations_dir}")
        return []

    migration_files = sorted(migrations_dir.glob("*.py"))
    # Exclude __init__.py and migration_model.py
    migration_files = [
        f for f in migration_files
        if f.name not in ("__init__.py", "migration_model.py", "base.py")
    ]

    # Also filter by migration name format (YYYYMMDD_HHMMSS_description)
    migration_files = [
        f for f in migration_files
        if validate_migration_name(f.stem)
    ]

    return migration_files


def get_pending_migrations(migrations_dir: Path) -> list[BaseMigration]:
    """Get list of pending (not yet applied) migrations.

    Args:
        migrations_dir: Path to migrations directory

    Returns:
        List of migration instances that need to be applied
    """
    applied = get_applied_migrations()
    migration_files = discover_migrations(migrations_dir)

    pending = []

    for migration_file in migration_files:
        # Extract migration name from filename
        migration_name = migration_file.stem

        # Skip if already applied
        if migration_name in applied:
            continue

        # Validate migration name format
        if not validate_migration_name(migration_name):
            logger.warning(f"Invalid migration name format: {migration_name}")
            continue

        # Import and instantiate migration
        try:
            # Dynamic import: migrations.add_missing_indexes -> AddMissingIndexes
            module_name = f"database.migrations.{migration_name}"

            # Import module
            import importlib
            module = importlib.import_module(module_name)

            # Get migration class (should be the only class inheriting from BaseMigration)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseMigration)
                    and attr is not BaseMigration
                ):
                    migration_instance = attr()
                    pending.append(migration_instance)
                    break

        except Exception as e:
            logger.error(f"Failed to load migration {migration_name}: {e}")
            # Skip this migration and continue with others
            continue

    return pending


def run_migration(migration: BaseMigration, batch: int) -> bool:
    """Run a single migration.

    Args:
        migration: Migration instance to run
        batch: Batch number for this migration run

    Returns:
        True if successful, False otherwise

    Raises:
        MigrationError: If migration fails
    """
    logger.info(f"Running migration: {migration.name}")

    # Pre-migration check
    if not migration.pre_check():
        raise MigrationError(f"Pre-check failed for migration: {migration.name}")

    # Connect to database if closed
    if database.is_closed():
        database.connect()

    try:
        # Start transaction
        with database.atomic():
            # Apply migration
            migration.up()
            logger.info(f"Migration up() completed: {migration.name}")

            # Record migration
            rollback_name = f"rollback_{migration.name}"
            record_migration(migration.name, batch, rollback_name)
            logger.info(f"Migration recorded: {migration.name}")

            # Post-migration check
            if not migration.post_check():
                raise MigrationError(f"Post-check failed for migration: {migration.name}")

            logger.info(f"Migration completed successfully: {migration.name}")
            return True

    except MigrationError:
        # Re-raise MigrationError as-is
        raise
    except Exception as e:
        # Wrap other exceptions in MigrationError
        logger.error(f"Migration failed: {migration.name} - {e}")
        raise MigrationError(f"Migration failed: {migration.name} - {e}") from e


def rollback_migration(migration: BaseMigration) -> bool:
    """Rollback a single migration.

    Args:
        migration: Migration instance to rollback

    Returns:
        True if successful, False otherwise

    Raises:
        RollbackError: If rollback fails
    """
    logger.info(f"Rolling back migration: {migration.name}")

    # Connect to database if closed
    if database.is_closed():
        database.connect()

    try:
        # Start transaction
        with database.atomic():
            # Rollback migration
            migration.down()
            logger.info(f"Migration down() completed: {migration.name}")

            # Remove migration record
            delete_migration(migration.name)
            logger.info(f"Migration record removed: {migration.name}")

            logger.info(f"Migration rolled back successfully: {migration.name}")
            return True

    except RollbackError:
        # Re-raise RollbackError as-is
        raise
    except Exception as e:
        # Wrap other exceptions in RollbackError
        logger.error(f"Rollback failed: {migration.name} - {e}")
        raise RollbackError(f"Rollback failed: {migration.name} - {e}") from e
