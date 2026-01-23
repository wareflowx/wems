"""Database migrations package.

This package contains all database migration scripts and the migration framework.

To create a new migration:
1. Create a new file in this directory with format: YYYYMMDD_HHMMSS_description.py
2. Inherit from BaseMigration and implement up() and down() methods
3. The migration will be automatically discovered and can be applied via CLI

Example:
    class AddDepartmentField(BaseMigration):
        def up(self):
            # Add department column to employees
            pass

        def down(self):
            # Remove department column
            pass

        @property
        def name(self) -> str:
            return "20250123_143000_add_department_field"
"""

from database.migrations.base import (
    BaseMigration,
    MigrationError,
    RollbackError,
    backup_database,
    discover_migrations,
    get_pending_migrations,
    restore_database,
    rollback_migration,
    run_migration,
    validate_migration_name,
)

__all__ = [
    "BaseMigration",
    "MigrationError",
    "RollbackError",
    "backup_database",
    "discover_migrations",
    "get_pending_migrations",
    "restore_database",
    "rollback_migration",
    "run_migration",
    "validate_migration_name",
]
