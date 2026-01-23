"""Migration tracking model for database schema versioning.

This model keeps track of which migrations have been applied to the database,
enabling automated migration and rollback capabilities.
"""

from datetime import datetime
from typing import Optional

from peewee import *

from database.connection import database


class Migration(Model):
    """Track applied database migrations."""

    id = AutoField()
    name = CharField(max_length=255, unique=True, index=True)
    # Migration name format: YYYYMMDD_HHMMSS_description
    # Example: 20250123_143000_add_department_field
    batch = IntegerField(default=1)  # Batch number for rollback
    applied_at = DateTimeField(default=datetime.now, index=True)

    # Optional rollback information
    rollback_name = CharField(max_length=255, null=True)

    class Meta:
        database = database
        table_name = "migrations"
        indexes = (
            # Create index on (name) for unique lookups
            (("name",), True),
        )


def get_applied_migrations() -> set[str]:
    """Get set of applied migration names."""
    if database.is_closed():
        database.connect()

    return {m.name for m in Migration.select(Migration.name)}


def record_migration(name: str, batch: int, rollback_name: Optional[str] = None) -> Migration:
    """Record that a migration has been applied."""
    if database.is_closed():
        database.connect()

    return Migration.create(
        name=name,
        batch=batch,
        rollback_name=rollback_name
    )


def get_last_batch_number() -> int:
    """Get the last migration batch number."""
    if database.is_closed():
        database.connect()

    try:
        last = Migration.select().order_by(Migration.batch.desc()).first()
        return last.batch if last else 0
    except Exception:
        return 0


def delete_migration(name: str) -> bool:
    """Remove a migration record (for rollback).

    Args:
        name: Migration name to remove

    Returns:
        True if migration was deleted, False otherwise
    """
    if database.is_closed():
        database.connect()

    count = Migration.delete().where(Migration.name == name).execute()
    return count > 0
