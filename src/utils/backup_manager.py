"""
Backup Manager Module

Provides automated database backup functionality with:
- SQLite online backup API (safe, non-blocking)
- Automatic cleanup of old backups
- Backup validation
- Restore functionality
"""

import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages database backups with automatic scheduling."""

    def __init__(
        self,
        database_path: Path,
        backup_dir: Path = Path("backups"),
        max_backups: int = 30
    ):
        """
        Initialize backup manager.

        Args:
            database_path: Path to database file
            backup_dir: Directory to store backups
            max_backups: Maximum number of backups to keep
        """
        self.database_path = Path(database_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, description: str = "") -> Path:
        """
        Create a backup of the database.

        Args:
            description: Optional description for backup

        Returns:
            Path to created backup file

        Raises:
            FileNotFoundError: If database file doesn't exist
            IOError: If backup creation fails
        """
        if not self.database_path.exists():
            raise FileNotFoundError(f"Database not found: {self.database_path}")

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"employee_manager_{timestamp}.db"
        if description:
            backup_name = f"employee_manager_{timestamp}_{description}.db"

        backup_path = self.backup_dir / backup_name

        # Use SQLite backup API for safe backup
        try:
            source = sqlite3.connect(str(self.database_path))
            dest = sqlite3.connect(str(backup_path))

            # Backup with online backup API
            source.backup(dest)

            dest.close()
            source.close()

            logger.info(f"Backup created: {backup_path}")

            # Clean old backups
            self._cleanup_old_backups()

            return backup_path

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            raise IOError(f"Failed to create backup: {e}")

    def _cleanup_old_backups(self):
        """Remove old backups exceeding max_backups limit."""
        backups = sorted(
            self.backup_dir.glob("employee_manager_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Remove excess backups
        for old_backup in backups[self.max_backups:]:
            old_backup.unlink()
            logger.info(f"Removed old backup: {old_backup}")

    def list_backups(self) -> List[dict]:
        """
        List all available backups with metadata.

        Returns:
            List of backup dictionaries with keys: path, name, size_mb, created
        """
        backups = []

        for backup_path in self.backup_dir.glob("employee_manager_*.db"):
            stat = backup_path.stat()
            backups.append({
                'path': str(backup_path),
                'name': backup_path.name,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_mtime),
            })

        return sorted(backups, key=lambda b: b['created'], reverse=True)

    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If backup file doesn't exist
            ValueError: If backup file is invalid
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Validate backup is SQLite database
        if not self._validate_sqlite_database(backup_path):
            raise ValueError(f"Invalid SQLite database: {backup_path}")

        # Restore backup
        try:
            # Create backup of current database before restore
            if self.database_path.exists():
                pre_restore_backup = self.database_path.with_suffix(
                    f".pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )
                shutil.copy2(self.database_path, pre_restore_backup)
                logger.info(f"Pre-restore backup created: {pre_restore_backup}")

            # Copy backup to database location
            shutil.copy2(backup_path, self.database_path)

            logger.info(f"Restored from backup: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise IOError(f"Failed to restore backup: {e}")

    def _validate_sqlite_database(self, path: Path) -> bool:
        """
        Validate file is a valid SQLite database.

        Args:
            path: Path to file to validate

        Returns:
            True if valid SQLite database
        """
        # Check if file exists first (before SQLite tries to create it)
        if not path.exists() or not path.is_file():
            return False

        try:
            # Open in read-only mode to prevent accidental file creation
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()
            return True
        except Exception:
            return False

    def get_backup_size(self) -> int:
        """
        Get total size of all backups in MB.

        Returns:
            Total size in MB
        """
        total_bytes = sum(
            b.stat().st_size
            for b in self.backup_dir.glob("employee_manager_*.db")
        )
        return round(total_bytes / (1024 * 1024), 2)
