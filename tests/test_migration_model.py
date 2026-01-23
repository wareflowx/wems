"""Tests for migration model and tracking.

Tests the Migration model that tracks applied database migrations.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from peewee import SqliteDatabase

from database.connection import database
from database.migration_model import (
    Migration,
    delete_migration,
    get_applied_migrations,
    get_last_batch_number,
    record_migration,
)


@pytest.fixture
def test_db():
    """Create an in-memory database for testing."""
    # Use in-memory SQLite for fast tests
    original_db = database.database

    # Initialize test database with :memory: string
    database.init(":memory:")
    database.connect()
    database.create_tables([Migration], safe=True)

    yield database

    # Cleanup
    database.close()
    database.database = original_db


class TestMigrationModel:
    """Test suite for Migration model."""

    def test_create_migration(self, test_db):
        """Test creating a migration record."""
        migration = Migration.create(
            name="20250123_120000_test_migration",
            batch=1,
            rollback_name="rollback_20250123_120000_test_migration"
        )

        assert migration.id is not None
        assert migration.name == "20250123_120000_test_migration"
        assert migration.batch == 1
        assert migration.rollback_name == "rollback_20250123_120000_test_migration"

    def test_migration_name_unique(self, test_db):
        """Test that migration names are unique."""
        Migration.create(
            name="20250123_120000_test_migration",
            batch=1
        )

        # Try to create duplicate
        with pytest.raises(Exception):  # Peewee raises IntegrityError
            Migration.create(
                name="20250123_120000_test_migration",
                batch=2
            )

    def test_get_applied_migrations(self, test_db):
        """Test getting set of applied migrations."""
        # Create some migrations
        Migration.create(name="20250123_120000_migration_1", batch=1)
        Migration.create(name="20250123_120000_migration_2", batch=1)
        Migration.create(name="20250123_120000_migration_3", batch=2)

        applied = get_applied_migrations()

        assert len(applied) == 3
        assert "20250123_120000_migration_1" in applied
        assert "20250123_120000_migration_2" in applied
        assert "20250123_120000_migration_3" in applied

    def test_get_applied_migrations_empty(self, test_db):
        """Test getting applied migrations when none exist."""
        applied = get_applied_migrations()
        assert applied == set()

    def test_get_last_batch_number(self, test_db):
        """Test getting the last batch number."""
        assert get_last_batch_number() == 0

        Migration.create(name="20250123_120000_migration_1", batch=1)
        assert get_last_batch_number() == 1

        Migration.create(name="20250123_120000_migration_2", batch=2)
        assert get_last_batch_number() == 2

        Migration.create(name="20250123_120000_migration_3", batch=2)
        assert get_last_batch_number() == 2

    def test_delete_migration(self, test_db):
        """Test deleting a migration record."""
        migration = Migration.create(
            name="20250123_120000_test_migration",
            batch=1
        )

        # Verify it exists
        assert Migration.select().where(Migration.name == "20250123_120000_test_migration").count() == 1

        # Delete it
        result = delete_migration("20250123_120000_test_migration")
        assert result is True

        # Verify it's gone
        assert Migration.select().where(Migration.name == "20250123_120000_test_migration").count() == 0

    def test_delete_nonexistent_migration(self, test_db):
        """Test deleting a migration that doesn't exist."""
        result = delete_migration("nonexistent_migration")
        assert result is False

    def test_record_migration(self, test_db):
        """Test recording a migration."""
        migration = record_migration(
            name="20250123_120000_test_migration",
            batch=1,
            rollback_name="rollback_20250123_120000_test_migration"
        )

        assert migration.name == "20250123_120000_test_migration"
        assert migration.batch == 1
        assert migration.rollback_name == "rollback_20250123_120000_test_migration"
