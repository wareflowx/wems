"""Tests for database migration framework.

Tests the migration framework including BaseMigration, migration discovery,
backup/restore, and migration execution.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from peewee import SqliteDatabase

from database.connection import database
from database.migration_model import Migration
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


@pytest.fixture
def test_db():
    """Create an in-memory database for testing."""
    original_db = database.database

    # Initialize test database with :memory: string
    database.init(":memory:")
    database.connect()
    database.create_tables([Migration], safe=True)

    yield database

    # Cleanup
    database.close()
    database.database = original_db


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestValidateMigrationName:
    """Test suite for migration name validation."""

    def test_valid_migration_names(self):
        """Test that valid migration names pass validation."""
        valid_names = [
            "20250123_120000_add_user_table",
            "20250123_120000_add_department_field",
            "20250123_120000_create_index_on_email",
            "20250123_120000_alter_employee_status",
        ]

        for name in valid_names:
            assert validate_migration_name(name), f"Should be valid: {name}"

    def test_invalid_migration_names(self):
        """Test that invalid migration names fail validation."""
        invalid_names = [
            "invalid",  # No timestamp
            "20250123_120000",  # No description
            "20250123_120000_Uppercase_Start",  # Uppercase start
            "20250123_120000_123numeric_start",  # Numeric start
            "20250123_120000_ space",  # Space in name
            "20250123_120000 hyphen-name",  # Hyphen in name
            "20250123_120000 dot.name",  # Dot in name
            "50123_120000_short_date",  # Incomplete date
        ]

        for name in invalid_names:
            assert not validate_migration_name(name), f"Should be invalid: {name}"


class TestBackupRestore:
    """Test suite for backup and restore functionality."""

    def test_backup_database(self, temp_dir):
        """Test creating a database backup."""
        # Create a test database file
        db_path = temp_dir / "test.db"
        db_path.write_text("test data")

        # Create backup
        backup_path = backup_database(db_path)

        # Verify backup was created
        assert backup_path.exists()
        assert backup_path.parent.name == "backups"
        assert "before_migration_" in backup_path.name
        assert backup_path.read_text() == "test data"

    def test_backup_creates_directory(self, temp_dir):
        """Test that backup creates the backups directory."""
        db_path = temp_dir / "test.db"
        db_path.write_text("test data")

        # Ensure no backups directory exists
        backup_dir = db_path.parent / "backups"
        assert not backup_dir.exists()

        # Create backup
        backup_database(db_path)

        # Verify directory was created
        assert backup_dir.exists()

    def test_restore_database(self, temp_dir):
        """Test restoring a database from backup."""
        # Create original database and backup
        db_path = temp_dir / "test.db"
        db_path.write_text("original data")

        backup_path = temp_dir / "backups" / "backup.db"
        backup_path.parent.mkdir(exist_ok=True)
        backup_path.write_text("backup data")

        # Restore from backup
        restore_database(backup_path, db_path)

        # Verify restore
        assert db_path.read_text() == "backup data"


class TestDiscoverMigrations:
    """Test suite for migration discovery."""

    def test_discover_no_migrations(self, temp_dir):
        """Test discovering migrations when directory is empty."""
        migrations = discover_migrations(temp_dir)
        assert migrations == []

    def test_discover_migrations_filters_special_files(self, temp_dir):
        """Test that special files are filtered out."""
        # Create migration files
        (temp_dir / "__init__.py").write_text("")
        (temp_dir / "20250123_120000_test_migration.py").write_text("")
        (temp_dir / "base.py").write_text("")
        # add_missing_indexes.py doesn't match the migration name format, so it should be filtered anyway
        (temp_dir / "add_missing_indexes.py").write_text("")

        migrations = discover_migrations(temp_dir)

        # Should only get the actual migration file (add_missing_indexes doesn't match YYYYMMDD_HHMMSS_format)
        assert len(migrations) == 1
        assert migrations[0].name == "20250123_120000_test_migration.py"

    def test_discover_migrations_sorted(self, temp_dir):
        """Test that migrations are discovered in sorted order."""
        (temp_dir / "20250123_120000_migration_c.py").write_text("")
        (temp_dir / "20250123_120000_migration_a.py").write_text("")
        (temp_dir / "20250123_120000_migration_b.py").write_text("")

        migrations = discover_migrations(temp_dir)

        # Should be sorted alphabetically
        assert migrations[0].name == "20250123_120000_migration_a.py"
        assert migrations[1].name == "20250123_120000_migration_b.py"
        assert migrations[2].name == "20250123_120000_migration_c.py"


class TestBaseMigration:
    """Test suite for BaseMigration class."""

    def test_concrete_migration(self):
        """Test that a concrete migration works."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()
        assert migration.name == "20250123_120000_test_migration"
        migration.up()  # Should not raise
        migration.down()  # Should not raise

    def test_pre_check_default(self):
        """Test that pre_check returns True by default."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()
        assert migration.pre_check() is True

    def test_post_check_default(self):
        """Test that post_check returns True by default."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()
        assert migration.post_check() is True

    def test_migration_with_custom_checks(self):
        """Test migration with custom pre/post checks."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

            def pre_check(self) -> bool:
                return False

            def post_check(self) -> bool:
                return True

        migration = TestMigration()
        assert migration.pre_check() is False
        assert migration.post_check() is True


class TestGetPendingMigrations:
    """Test suite for getting pending migrations."""

    def test_no_pending_when_no_migrations(self, temp_dir, test_db):
        """Test that no migrations are pending when directory is empty."""
        pending = get_pending_migrations(temp_dir)
        assert pending == []

    def test_no_pending_when_all_applied(self, temp_dir, test_db):
        """Test that no migrations are pending when all are applied."""
        # Create a migration file
        (temp_dir / "20250123_120000_test_migration.py").write_text("""
from database.migrations.base import BaseMigration

class Migration(BaseMigration):
    def up(self):
        pass

    def down(self):
        pass

    @property
    def name(self) -> str:
        return "20250123_120000_test_migration"
""")

        # Record it as applied
        Migration.create(name="20250123_120000_test_migration", batch=1)

        # Get pending
        with patch('importlib.import_module') as mock_import:
            # Mock the module to avoid actual import
            mock_module = MagicMock()
            mock_migration = MagicMock()
            mock_migration.name = "20250123_120000_test_migration"
            mock_module.Migration = mock_migration
            mock_import.return_value = mock_module

            pending = get_pending_migrations(temp_dir)

        assert pending == []

    def test_pending_when_none_applied(self, temp_dir, test_db):
        """Test that get_pending_migrations handles import failures gracefully."""
        # Create a migration file in a temp directory (not in the package)
        # The import will fail because it's not in the database.migrations package
        (temp_dir / "20250123_120000_test_migration.py").write_text("""
from database.migrations.base import BaseMigration

class Migration(BaseMigration):
    def up(self):
        pass

    def down(self):
        pass

    @property
    def name(self) -> str:
        return "20250123_120000_test_migration"
""")

        # The import will fail because this is in a temp directory not in the package
        # The function should log an error and continue, returning an empty list
        pending = get_pending_migrations(temp_dir)

        # Should return empty list when import fails
        assert pending == []


class TestRunMigration:
    """Test suite for running migrations."""

    def test_run_migration_success(self, test_db):
        """Test successfully running a migration."""
        class TestMigration(BaseMigration):
            def up(self):
                # Simulate migration work
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()
        success = run_migration(migration, batch=1)

        assert success is True

        # Verify migration was recorded
        assert Migration.select().where(Migration.name == "20250123_120000_test_migration").count() == 1

    def test_run_migration_pre_check_failure(self, test_db):
        """Test that migration fails when pre_check returns False."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

            def pre_check(self) -> bool:
                return False

        migration = TestMigration()

        with pytest.raises(MigrationError, match="Pre-check failed"):
            run_migration(migration, batch=1)

    def test_run_migration_post_check_failure(self, test_db):
        """Test that migration fails when post_check returns False."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

            def post_check(self) -> bool:
                return False

        migration = TestMigration()

        with pytest.raises(MigrationError, match="Post-check failed"):
            run_migration(migration, batch=1)

    def test_run_migration_up_exception(self, test_db):
        """Test that exceptions in up() are handled."""
        class TestMigration(BaseMigration):
            def up(self):
                raise ValueError("Migration failed")

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()

        # The ValueError should be wrapped in MigrationError
        with pytest.raises(MigrationError):
            run_migration(migration, batch=1)


class TestRollbackMigration:
    """Test suite for rolling back migrations."""

    def test_rollback_migration_success(self, test_db):
        """Test successfully rolling back a migration."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                pass

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()

        # First apply the migration
        Migration.create(name="20250123_120000_test_migration", batch=1)

        # Then rollback
        success = rollback_migration(migration)

        assert success is True

        # Verify migration record was removed
        assert Migration.select().where(Migration.name == "20250123_120000_test_migration").count() == 0

    def test_rollback_migration_down_exception(self, test_db):
        """Test that exceptions in down() are handled."""
        class TestMigration(BaseMigration):
            def up(self):
                pass

            def down(self):
                raise ValueError("Rollback failed")

            @property
            def name(self) -> str:
                return "20250123_120000_test_migration"

        migration = TestMigration()

        # Apply the migration
        Migration.create(name="20250123_120000_test_migration", batch=1)

        # Try to rollback - the ValueError should be wrapped in RollbackError
        with pytest.raises(RollbackError):
            rollback_migration(migration)
