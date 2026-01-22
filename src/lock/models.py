"""Lock mechanism data models."""

import uuid
from datetime import datetime, timedelta

from peewee import *

from database.connection import database


class AppLock(Model):
    """
    Application lock for concurrent access control.

    Ensures only one user can edit data at a time on shared network drives.
    Uses heartbeat mechanism to detect stale locks from crashed applications.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)

    # Lock holder identification
    hostname = CharField(index=True)  # Machine name
    username = CharField(null=True)  # Optional: user name

    # Timestamps
    locked_at = DateTimeField(default=datetime.now, index=True)
    last_heartbeat = DateTimeField(default=datetime.now, index=True)

    # Process identification
    process_id = IntegerField()  # PID for debugging

    # Metadata
    app_version = CharField(null=True)  # For debugging/version tracking

    class Meta:
        database = database
        table_name = "app_locks"

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_stale(self, timeout_minutes=2) -> bool:
        """
        Check if lock is stale (no recent heartbeat).

        Args:
            timeout_minutes: Minutes of inactivity before considering lock stale.
                            Default: 2 minutes (allows 4 missed heartbeats)

        Returns:
            True if lock is stale and can be safely overridden
        """
        threshold = datetime.now() - timedelta(minutes=timeout_minutes)
        return self.last_heartbeat < threshold

    @property
    def age_seconds(self) -> int:
        """Age of lock in seconds since acquisition."""
        return int((datetime.now() - self.locked_at).total_seconds())

    @property
    def heartbeat_age_seconds(self) -> int:
        """Seconds since last heartbeat."""
        return int((datetime.now() - self.last_heartbeat).total_seconds())

    # ========== CLASS METHODS ==========

    @classmethod
    def acquire(cls, hostname: str, username: str | None, pid: int, app_version: str | None = None) -> "AppLock":
        """
        Acquire application lock.

        Fails if an active lock already exists.

        Args:
            hostname: Machine name of lock holder
            username: Optional user name
            pid: Process ID
            app_version: Optional application version

        Returns:
            AppLock instance

        Raises:
            RuntimeError: If lock is already held by active host
        """
        # Check for existing lock (including stale ones)
        existing = cls.select().order_by(cls.locked_at.desc()).first()
        if existing:
            if not existing.is_stale:
                # Lock is active and held by another process
                raise RuntimeError(
                    f"Lock is held by {existing.hostname} (since {existing.locked_at.strftime('%H:%M:%S')})"
                )
            # Lock is stale, delete it
            existing.delete_instance()

        # Create new lock
        return cls.create(hostname=hostname, username=username, process_id=pid, app_version=app_version)

    @classmethod
    def release(cls, hostname: str, pid: int) -> bool:
        """
        Release lock (only if owned by caller).

        Args:
            hostname: Must match lock holder's hostname
            pid: Must match lock holder's process ID

        Returns:
            True if lock was released, False if not owned by caller
        """
        lock = cls.get_active_lock()
        if not lock:
            return False

        if lock.hostname != hostname or lock.process_id != pid:
            return False

        lock.delete_instance()
        return True

    @classmethod
    def refresh_heartbeat(cls, hostname: str, pid: int) -> bool:
        """
        Update heartbeat timestamp to keep lock alive.

        Should be called every 30 seconds while holding lock.

        Args:
            hostname: Must match lock holder's hostname
            pid: Must match lock holder's process ID

        Returns:
            True if heartbeat updated, False if not lock owner
        """
        lock = cls.get_active_lock()
        if not lock:
            return False

        if lock.hostname != hostname or lock.process_id != pid:
            return False

        lock.last_heartbeat = datetime.now()
        lock.save(only=[AppLock.last_heartbeat])  # Only update heartbeat field
        return True

    @classmethod
    def get_active_lock(cls) -> "AppLock | None":
        """
        Get current active lock, or None if no active lock exists.

        Returns None if lock is stale (considered inactive).
        """
        lock = cls.select().order_by(cls.locked_at.desc()).first()
        if not lock:
            return None

        # Return None if lock is stale
        if lock.is_stale:
            return None

        return lock
