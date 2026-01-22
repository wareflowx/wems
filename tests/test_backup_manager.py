"""
Tests for Backup Manager Module

Tests cover:
- Backup creation and validation
- Backup restoration
- Automatic cleanup of old backups
- Backup validation (SQLite integrity)
- Edge cases (missing database, invalid backups, etc.)
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.utils.backup_manager import BackupManager


@pytest.fixture
def temp_database():
    """Create a temporary SQLite database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    # Create test database with sample data
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test_table (name) VALUES ('test1')")
    cursor.execute("INSERT INTO test_table (name) VALUES ('test2')")
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def backup_manager(temp_database):
    """Create BackupManager instance with temporary database."""
    backup_dir = Path(tempfile.mkdtemp())
    manager = BackupManager(
        database_path=temp_database,
        backup_dir=backup_dir,
        max_backups=5
    )
    yield manager

    # Cleanup
    shutil.rmtree(backup_dir, ignore_errors=True)


class TestBackupCreation:
    """Test backup creation functionality."""

    def test_create_backup_creates_file(self, backup_manager):
        """Test that create_backup creates a backup file."""
        backup_path = backup_manager.create_backup()

        assert backup_path.exists()
        assert backup_path.stat().st_size > 0

    def test_create_backup_with_description(self, backup_manager):
        """Test creating backup with custom description."""
        backup_path = backup_manager.create_backup(description="manual")

        assert "manual" in backup_path.name
        assert backup_path.exists()

    def test_create_backup_generates_unique_name(self, backup_manager):
        """Test that each backup has a unique timestamped name."""
        backup1 = backup_manager.create_backup()
        backup2 = backup_manager.create_backup()

        assert backup1.name != backup2.name

    def test_create_backup_valid_database(self, backup_manager):
        """Test that backup is a valid SQLite database."""
        backup_path = backup_manager.create_backup()

        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()

        assert len(tables) > 0

    def test_create_backup_preserves_data(self, backup_manager, temp_database):
        """Test that backup contains same data as original."""
        # Read original data
        conn_orig = sqlite3.connect(str(temp_database))
        cursor_orig = conn_orig.cursor()
        cursor_orig.execute("SELECT * FROM test_table")
        original_data = cursor_orig.fetchall()
        conn_orig.close()

        # Create backup
        backup_path = backup_manager.create_backup()

        # Read backup data
        conn_backup = sqlite3.connect(str(backup_path))
        cursor_backup = conn_backup.cursor()
        cursor_backup.execute("SELECT * FROM test_table")
        backup_data = cursor_backup.fetchall()
        conn_backup.close()

        assert original_data == backup_data

    def test_create_backup_nonexistent_database(self):
        """Test creating backup when database doesn't exist."""
        # Use temp directory to ensure file doesn't exist
        temp_dir = Path(tempfile.mkdtemp())
        nonexistent_db = temp_dir / "nonexistent_database.db"

        manager = BackupManager(
            database_path=nonexistent_db,
            backup_dir=Path(tempfile.mkdtemp())
        )

        with pytest.raises(FileNotFoundError):
            manager.create_backup()


class TestBackupCleanup:
    """Test automatic cleanup of old backups."""

    def test_cleanup_removes_old_backups(self, backup_manager):
        """Test that old backups are removed when limit is exceeded."""
        # Create 7 backups (limit is 5)
        for _ in range(7):
            backup_manager.create_backup()

        backups = backup_manager.list_backups()
        assert len(backups) == 5

    def test_cleanup_keeps_newest_backups(self, backup_manager):
        """Test that newest backups are kept."""
        # Create backups with delays
        backup_paths = []
        for i in range(5):
            backup_paths.append(backup_manager.create_backup())

        backups = backup_manager.list_backups()
        backup_names = [b['name'] for b in backups]

        # All should be kept (within limit)
        for path in backup_paths:
            assert path.name in backup_names

    def test_max_backups_limit(self, backup_manager):
        """Test that backup count never exceeds max_backups."""
        for _ in range(20):
            backup_manager.create_backup()

        backups = backup_manager.list_backups()
        assert len(backups) <= backup_manager.max_backups


class TestBackupListing:
    """Test backup listing functionality."""

    def test_list_backups_returns_list(self, backup_manager):
        """Test that list_backups returns a list."""
        backup_manager.create_backup()
        backups = backup_manager.list_backups()

        assert isinstance(backups, list)

    def test_list_backups_includes_metadata(self, backup_manager):
        """Test that backups include path, name, size, and date."""
        backup_manager.create_backup()
        backups = backup_manager.list_backups()

        assert len(backups) == 1
        backup = backups[0]

        assert 'path' in backup
        assert 'name' in backup
        assert 'size_mb' in backup
        assert 'created' in backup

    def test_list_backups_sorted_by_date(self, backup_manager):
        """Test that backups are sorted newest first."""
        backup_manager.create_backup()
        backup_manager.create_backup()
        backup_manager.create_backup()

        backups = backup_manager.list_backups()

        # Check sorted descending by date
        for i in range(len(backups) - 1):
            assert backups[i]['created'] >= backups[i+1]['created']

    def test_list_backups_empty_initially(self, backup_manager):
        """Test that list_backups is empty initially."""
        backups = backup_manager.list_backups()
        assert len(backups) == 0


class TestBackupValidation:
    """Test backup validation functionality."""

    def test_validate_valid_database(self, backup_manager):
        """Test validation of valid SQLite database."""
        backup_path = backup_manager.create_backup()

        assert backup_manager._validate_sqlite_database(backup_path) is True

    def test_validate_invalid_database(self, backup_manager):
        """Test validation of invalid file."""
        invalid_file = backup_manager.backup_dir / "invalid.db"
        invalid_file.write_text("Not a database")

        assert backup_manager._validate_sqlite_database(invalid_file) is False

    def test_validate_nonexistent_file(self, backup_manager):
        """Test validation of nonexistent file."""
        # Use absolute path to ensure file doesn't exist
        nonexistent_path = Path(tempfile.gettempdir()) / "truly_nonexistent_file_12345.db"
        assert backup_manager._validate_sqlite_database(nonexistent_path) is False


class TestBackupRestore:
    """Test backup restoration functionality."""

    def test_restore_backup_success(self, backup_manager, temp_database):
        """Test successful restore from backup."""
        # Modify database
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_table (name) VALUES ('before_restore')")
        conn.commit()
        conn.close()

        # Create backup
        backup_path = backup_manager.create_backup()

        # Modify database again
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_table WHERE name = 'test1'")
        conn.commit()
        conn.close()

        # Verify data changed
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count_after = cursor.fetchone()[0]
        conn.close()

        assert count_after == 2  # test2 and before_restore

        # Restore backup
        backup_manager.restore_backup(backup_path)

        # Verify data restored
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count_restored = cursor.fetchone()[0]
        conn.close()

        assert count_restored == 3  # test1, test2, before_restore

    def test_restore_creates_pre_restore_backup(self, backup_manager, temp_database):
        """Test that restore creates pre-restore backup."""
        backup_path = backup_manager.create_backup()

        # Modify database
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_table (name) VALUES ('modified')")
        conn.commit()
        conn.close()

        # Restore
        backup_manager.restore_backup(backup_path)

        # Check pre-restore backup exists
        pre_restore_backups = list(
            temp_database.parent.glob("*.pre_restore_*.db")
        )

        assert len(pre_restore_backups) > 0

    def test_restore_nonexistent_backup(self, backup_manager):
        """Test restoring from nonexistent backup."""
        # Use temp directory to ensure file doesn't exist
        temp_dir = Path(tempfile.mkdtemp())
        nonexistent_backup = temp_dir / "nonexistent_backup.db"

        with pytest.raises(FileNotFoundError):
            backup_manager.restore_backup(nonexistent_backup)

    def test_restore_invalid_backup(self, backup_manager):
        """Test restoring from invalid backup file."""
        # Create invalid file
        invalid_backup = backup_manager.backup_dir / "invalid.db"
        invalid_backup.write_text("Not a database")

        with pytest.raises(ValueError):
            backup_manager.restore_backup(invalid_backup)


class TestBackupSize:
    """Test backup size calculation."""

    def test_get_backup_size(self, backup_manager):
        """Test calculating total backup size."""
        backup_manager.create_backup()
        backup_manager.create_backup()

        size = backup_manager.get_backup_size()

        assert size > 0
        assert isinstance(size, (int, float))

    def test_get_backup_size_empty(self, backup_manager):
        """Test backup size when no backups exist."""
        size = backup_manager.get_backup_size()
        assert size == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_create_multiple_backups_in_sequence(self, backup_manager):
        """Test creating many backups in quick succession."""
        backup_paths = []
        for _ in range(10):
            backup_paths.append(backup_manager.create_backup())

        # All should have unique names
        names = [p.name for p in backup_paths]
        assert len(names) == len(set(names))

    def test_restore_database_same_path(self, backup_manager, temp_database):
        """Test that restore replaces database file."""
        backup_path = backup_manager.create_backup()

        # Get original row count
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        original_count = cursor.fetchone()[0]
        conn.close()

        # Modify database
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        for i in range(100):
            cursor.execute(f"INSERT INTO test_table (name) VALUES ('extra{i}')")
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        modified_count = cursor.fetchone()[0]
        conn.close()

        # Verify data changed
        assert modified_count > original_count

        # Restore
        backup_manager.restore_backup(backup_path)

        # Verify data restored
        conn = sqlite3.connect(str(temp_database))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        restored_count = cursor.fetchone()[0]
        conn.close()

        assert restored_count == original_count

    def test_backup_manager_creates_backup_dir(self):
        """Test that BackupManager creates backup directory if needed."""
        temp_dir = tempfile.mkdtemp()
        non_existent_dir = Path(temp_dir) / "new_backups"

        manager = BackupManager(
            database_path=Path(temp_dir) / "test.db",
            backup_dir=non_existent_dir
        )

        assert non_existent_dir.exists()

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
