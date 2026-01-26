"""Comprehensive tests for the migration system.

Tests cover:
- Version tracking initialization
- Migration detection
- Automatic migration execution
- Rollback functionality
- Migration validation
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestVersionTracking(TestCase):
    """Test version tracking functionality."""

    def setUp(self):
        """Set up test database."""
        from database.connection import database

        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        database.init(self.db_path)
        database.connect()

        # Import models after database initialization
        from database.version_model import AppVersion

        self.AppVersion = AppVersion

    def tearDown(self):
        """Clean up test database."""
        from database.connection import database

        database.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_initialize_version_tracking_new_db(self):
        """Test version tracking initialization on new database."""
        from database.version import initialize_version_tracking, get_current_app_version, APP_VERSION

        # Initialize version tracking
        initialize_version_tracking()

        # Check version was set
        current = get_current_app_version()
        self.assertEqual(current, APP_VERSION)

        # Check record exists in database
        count = self.AppVersion.select().count()
        self.assertEqual(count, 1)

        record = self.AppVersion.select().first()
        self.assertEqual(record.app_version, APP_VERSION)
        self.assertIsNotNone(record.applied_at)

    def test_initialize_version_tracking_existing_db(self):
        """Test version tracking initialization on existing database."""
        from database.version import (
            initialize_version_tracking,
            get_current_app_version,
            APP_VERSION,
            SCHEMA_VERSION,
        )

        # Initialize first time
        initialize_version_tracking()
        current = get_current_app_version()
        self.assertEqual(current, APP_VERSION)

        # Update to different version
        from database.version_model import set_version

        set_version("0.0.1", 1, "Old version")
        current = get_current_app_version()
        self.assertEqual(current, "0.0.1")

        # Initialize again - should update to current version
        initialize_version_tracking()
        current = get_current_app_version()
        self.assertEqual(current, APP_VERSION)

    def test_check_migration_needed_new_db(self):
        """Test migration check on new database."""
        from database.version import check_migration_needed, APP_VERSION

        # New database needs migration
        needs_migration = check_migration_needed()
        self.assertTrue(needs_migration)

    def test_check_migration_needed_up_to_date(self):
        """Test migration check when up to date."""
        from database.version import initialize_version_tracking, check_migration_needed

        # Initialize to current version
        initialize_version_tracking()

        # Should not need migration
        needs_migration = check_migration_needed()
        self.assertFalse(needs_migration)

    def test_check_migration_needed_old_version(self):
        """Test migration check when on old version."""
        from database.version import initialize_version_tracking, check_migration_needed
        from database.version_model import set_version

        # Set to old version
        set_version("0.0.1", 1, "Old version")

        # Should need migration
        needs_migration = check_migration_needed()
        self.assertTrue(needs_migration)


class TestMigrationManager(TestCase):
    """Test MigrationManager functionality."""

    def setUp(self):
        """Set up test environment."""
        from database.connection import database

        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        database.init(self.db_path)
        database.connect()

        # Create temporary backup directory
        self.backup_dir = tempfile.mkdtemp()

        # Import models
        from database.version_model import AppVersion
        from database.migration_model import Migration
        from employee.models import Employee

        self.AppVersion = AppVersion
        self.Migration = Migration
        self.Employee = Employee

        # Create tables
        database.create_tables([AppVersion, Migration, Employee], safe=True)

        # Initialize version tracking
        from database.version import initialize_version_tracking

        initialize_version_tracking()

    def tearDown(self):
        """Clean up test environment."""
        from database.connection import database
        import shutil

        database.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        shutil.rmtree(self.backup_dir)

    def test_get_migration_plan_up_to_date(self):
        """Test migration plan when up to date."""
        from database.migration_manager import get_migration_manager
        from utils.backup_manager import BackupManager

        backup_manager = BackupManager(database_path=Path(self.db_path), backup_dir=Path(self.backup_dir))
        manager = get_migration_manager(backup_manager=backup_manager)

        plan = manager.get_migration_plan()

        self.assertEqual(plan["current_version"], "0.1.0")
        self.assertEqual(plan["target_version"], "0.1.0")
        self.assertEqual(plan["pending_count"], 0)
        self.assertEqual(len(plan["migrations"]), 0)

    def test_check_and_migrate_no_migration_needed(self):
        """Test migration check when up to date."""
        from database.migration_manager import get_migration_manager
        from utils.backup_manager import BackupManager

        backup_manager = BackupManager(database_path=Path(self.db_path), backup_dir=Path(self.backup_dir))
        manager = get_migration_manager(backup_manager=backup_manager)

        success, message = manager.check_and_migrate(auto_migrate=False)

        self.assertTrue(success)
        self.assertIn("up to date", message.lower())

    def test_migration_manager_creates_backup(self):
        """Test that migration manager creates backup before migration."""
        from database.migration_manager import get_migration_manager
        from utils.backup_manager import BackupManager
        from database.version_model import set_version

        # Set to old version to trigger migration
        set_version("0.0.1", 1, "Old version")

        backup_manager = BackupManager(database_path=Path(self.db_path), backup_dir=Path(self.backup_dir))
        manager = get_migration_manager(backup_manager=backup_manager)

        # Get migration count before
        backups_before = len(list(backup_manager.list_backups()))

        # Attempt migration (may not have actual migrations, but should create backup)
        manager.check_and_migrate(auto_migrate=True)

        # Check backup was created
        backups_after = len(list(backup_manager.list_backups()))
        self.assertGreater(backups_after, backups_before)


class TestMigrationValidation(TestCase):
    """Test migration validation system."""

    def setUp(self):
        """Set up test environment."""
        from database.connection import database

        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        database.init(self.db_path)
        database.connect()

        # Import models
        from database.version_model import AppVersion
        from database.migration_model import Migration

        self.AppVersion = AppVersion
        self.Migration = Migration

        # Create tables
        database.create_tables([AppVersion, Migration], safe=True)

    def tearDown(self):
        """Clean up test environment."""
        from database.connection import database

        database.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_migration_record_creation(self):
        """Test recording a migration."""
        from database.migration_model import record_migration

        # Record migration
        migration = record_migration("20250126_120000_test_migration", batch=1)

        self.assertEqual(migration.name, "20250126_120000_test_migration")
        self.assertEqual(migration.batch, 1)
        self.assertIsNotNone(migration.applied_at)

    def test_get_applied_migrations(self):
        """Test getting applied migrations."""
        from database.migration_model import record_migration, get_applied_migrations

        # Record some migrations
        record_migration("20250126_120000_test_migration_1", batch=1)
        record_migration("20250126_120001_test_migration_2", batch=1)

        # Get applied migrations
        applied = get_applied_migrations()

        self.assertIn("20250126_120000_test_migration_1", applied)
        self.assertIn("20250126_120001_test_migration_2", applied)
        self.assertEqual(len(applied), 2)

    def test_get_last_batch_number(self):
        """Test getting last batch number."""
        from database.migration_model import record_migration, get_last_batch_number

        # Initially should be 0
        last = get_last_batch_number()
        self.assertEqual(last, 0)

        # Add migrations in batch 1
        record_migration("20250126_120000_test_migration_1", batch=1)
        last = get_last_batch_number()
        self.assertEqual(last, 1)

        # Add migrations in batch 2
        record_migration("20250126_120001_test_migration_2", batch=2)
        last = get_last_batch_number()
        self.assertEqual(last, 2)

    def test_delete_migration(self):
        """Test deleting a migration record."""
        from database.migration_model import record_migration, delete_migration, get_applied_migrations

        # Record migration
        record_migration("20250126_120000_test_migration", batch=1)

        # Verify it exists
        applied = get_applied_migrations()
        self.assertIn("20250126_120000_test_migration", applied)

        # Delete it
        deleted = delete_migration("20250126_120000_test_migration")
        self.assertTrue(deleted)

        # Verify it's gone
        applied = get_applied_migrations()
        self.assertNotIn("20250126_120000_test_migration", applied)


if __name__ == "__main__":
    import unittest

    unittest.main()
