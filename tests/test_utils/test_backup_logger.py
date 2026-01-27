"""Tests for backup logger module.

Unit tests for BackupLogger covering logging functionality,
event tracking, and statistics.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import pytest

from utils.backup_logger import BackupLogger, BackupEvent


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def logger(temp_log_dir):
    """Create BackupLogger with temporary log directory."""
    return BackupLogger(log_dir=temp_log_dir)


class TestBackupLoggerInit:
    """Test BackupLogger initialization."""

    def test_init_creates_log_directory(self, temp_log_dir):
        """Test that initialization creates log directory."""
        log_dir = temp_log_dir / "logs"
        logger = BackupLogger(log_dir=log_dir)

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_init_creates_log_files(self, logger):
        """Test that initialization creates log files."""
        # Log files are created on first log message
        logger.log_backup_start()

        assert logger.log_file.exists()
        # JSON log file might not exist until first JSON event is logged
        # (which happens when we log a backup start)
        assert logger.json_log_file.exists()

    def test_init_with_default_log_dir(self):
        """Test initialization with default log directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            logger = BackupLogger()

            assert logger.log_dir == Path("logs")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_init_logs_initialization(self, logger):
        """Test that initialization is logged."""
        # Trigger log file creation
        logger.log_backup_start()
        logger.flush()

        # Check log file contains initialization message
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup logger initialized" in content


class TestLogBackupStart:
    """Test backup start logging."""

    def test_log_backup_start_manual(self, logger):
        """Test logging manual backup start."""
        logger.log_backup_start(backup_type="manual")
        logger.flush()

        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup started" in content
        assert "Type: manual" in content

    def test_log_backup_start_scheduled(self, logger):
        """Test logging scheduled backup start."""
        logger.log_backup_start(backup_type="scheduled")
        logger.flush()

        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Type: scheduled" in content

    def test_log_backup_start_creates_json_event(self, logger):
        """Test that backup start creates JSON event."""
        logger.log_backup_start(backup_type="manual")

        events = logger.get_recent_events()
        assert len(events) >= 1

        event = events[-1]  # Most recent
        assert event['event_type'] == 'start'
        assert event['backup_type'] == 'manual'


class TestLogBackupSuccess:
    """Test backup success logging."""

    def test_log_backup_success(self, logger, temp_log_dir):
        """Test logging successful backup."""
        backup_path = temp_log_dir / "test_backup.db"
        backup_path.write_text("test data")

        logger.log_backup_success(
            backup_path=backup_path,
            duration_seconds=2.5,
            size_bytes=1024 * 1024,
            backup_type="manual"
        )
        logger.flush()

        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup succeeded" in content
        assert "Type: manual" in content
        assert "Duration: 2.50s" in content
        assert "Size: 1.00 MB" in content

    def test_log_backup_success_creates_json_event(self, logger, temp_log_dir):
        """Test that success creates JSON event with details."""
        backup_path = temp_log_dir / "test_backup.db"
        backup_path.write_text("test data")

        logger.log_backup_success(
            backup_path=backup_path,
            duration_seconds=3.0,
            size_bytes=2048 * 1024,
            backup_type="scheduled"
        )

        events = logger.get_recent_events()
        event = events[0]  # Most recent

        assert event['event_type'] == 'success'
        assert event['backup_type'] == 'scheduled'
        assert event['duration_seconds'] == 3.0
        assert event['size_bytes'] == 2048 * 1024
        assert event['status'] == 'success'


class TestLogBackupFailure:
    """Test backup failure logging."""

    def test_log_backup_failure(self, logger):
        """Test logging failed backup."""
        logger.log_backup_failure(
            error="Disk full",
            backup_type="manual"
        )

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup failed" in content
        assert "Type: manual" in content
        assert "Error: Disk full" in content

    def test_log_backup_failure_with_path(self, logger, temp_log_dir):
        """Test logging failed backup with path."""
        backup_path = temp_log_dir / "failed_backup.db"

        logger.log_backup_failure(
            error="Permission denied",
            backup_type="scheduled",
            backup_path=backup_path
        )

        events = logger.get_recent_events()
        event = events[0]

        assert event['event_type'] == 'failure'
        assert event['backup_path'] == str(backup_path)
        assert event['error_message'] == "Permission denied"
        assert event['status'] == 'failed'


class TestLogBackupVerify:
    """Test backup verification logging."""

    def test_log_backup_verify_valid(self, logger, temp_log_dir):
        """Test logging valid backup verification."""
        backup_path = temp_log_dir / "valid_backup.db"
        backup_path.write_text("test data")

        logger.log_backup_verify(
            backup_path=backup_path,
            valid=True,
            employee_count=42
        )

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup verified" in content
        assert "Valid: Yes" in content
        assert "Employees: 42" in content

    def test_log_backup_verify_invalid(self, logger, temp_log_dir):
        """Test logging invalid backup verification."""
        backup_path = temp_log_dir / "invalid_backup.db"
        backup_path.write_text("corrupted data")

        logger.log_backup_verify(
            backup_path=backup_path,
            valid=False,
            error_message="Checksum mismatch"
        )

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup verification failed" in content
        assert "Error: Checksum mismatch" in content

    def test_log_backup_verify_creates_json_event(self, logger, temp_log_dir):
        """Test that verification creates JSON event."""
        backup_path = temp_log_dir / "backup.db"
        backup_path.write_text("data")

        logger.log_backup_verify(
            backup_path=backup_path,
            valid=True,
            employee_count=100
        )

        events = logger.get_recent_events()
        event = events[0]

        assert event['event_type'] == 'verify'
        assert event['status'] == 'valid'
        assert event['metadata']['employee_count'] == 100


class TestLogBackupRestore:
    """Test backup restore logging."""

    def test_log_backup_restore_success(self, logger, temp_log_dir):
        """Test logging successful restore."""
        backup_path = temp_log_dir / "restore_backup.db"

        logger.log_backup_restore(
            backup_path=backup_path,
            success=True,
            duration_seconds=5.5
        )

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Restore succeeded" in content
        assert "Duration: 5.50s" in content

    def test_log_backup_restore_failure(self, logger, temp_log_dir):
        """Test logging failed restore."""
        backup_path = temp_log_dir / "failed_restore.db"

        logger.log_backup_restore(
            backup_path=backup_path,
            success=False,
            error_message="Corrupted backup file"
        )

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Restore failed" in content
        assert "Error: Corrupted backup file" in content

    def test_log_backup_restore_creates_json_event(self, logger, temp_log_dir):
        """Test that restore creates JSON event."""
        backup_path = temp_log_dir / "backup.db"

        logger.log_backup_restore(
            backup_path=backup_path,
            success=True,
            duration_seconds=10.0
        )

        events = logger.get_recent_events()
        event = events[0]

        assert event['event_type'] == 'restore'
        assert event['status'] == 'success'
        assert event['duration_seconds'] == 10.0


class TestLogBackupCleanup:
    """Test backup cleanup logging."""

    def test_log_backup_cleanup(self, logger):
        """Test logging backup cleanup."""
        logger.log_backup_cleanup(
            deleted_count=5,
            kept_count=25,
            retention_days=30
        )

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Backup cleanup" in content
        assert "Deleted: 5" in content
        assert "Kept: 25" in content
        assert "Retention: 30 days" in content

    def test_log_backup_cleanup_creates_json_event(self, logger):
        """Test that cleanup creates JSON event."""
        logger.log_backup_cleanup(
            deleted_count=10,
            kept_count=20,
            retention_days=30
        )

        events = logger.get_recent_events()
        event = events[0]

        assert event['event_type'] == 'cleanup'
        assert event['metadata']['deleted_count'] == 10
        assert event['metadata']['kept_count'] == 20
        assert event['metadata']['retention_days'] == 30


class TestLogSchedulerEvents:
    """Test scheduler event logging."""

    def test_log_scheduler_start(self, logger):
        """Test logging scheduler start."""
        logger.log_scheduler_start()

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Scheduler started" in content

    def test_log_scheduler_stop(self, logger):
        """Test logging scheduler stop."""
        logger.log_scheduler_stop()

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Scheduler stopped" in content

    def test_log_scheduler_skipped(self, logger):
        """Test logging scheduler skipped backup."""
        logger.log_scheduler_skipped(reason="Already backed up today")

        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Scheduled backup skipped" in content
        assert "Reason: Already backed up today" in content


class TestGetRecentEvents:
    """Test getting recent events from JSON log."""

    def test_get_recent_events_empty(self, logger):
        """Test getting events when log is empty."""
        events = logger.get_recent_events()

        assert events == []

    def test_get_recent_events_single(self, logger, temp_log_dir):
        """Test getting single event."""
        backup_path = temp_log_dir / "backup.db"
        backup_path.write_text("data")

        logger.log_backup_start()

        events = logger.get_recent_events()

        assert len(events) == 1
        assert events[0]['event_type'] == 'start'

    def test_get_recent_events_multiple(self, logger, temp_log_dir):
        """Test getting multiple events."""
        backup_path = temp_log_dir / "backup.db"
        backup_path.write_text("data")

        # Log multiple events
        logger.log_backup_start()
        logger.log_backup_success(backup_path, 1.0, 1024)
        logger.log_backup_verify(backup_path, True, 10)

        events = logger.get_recent_events(count=10)

        assert len(events) == 3
        # Most recent first
        assert events[0]['event_type'] == 'verify'
        assert events[1]['event_type'] == 'success'
        assert events[2]['event_type'] == 'start'

    def test_get_recent_events_respects_count(self, logger, temp_log_dir):
        """Test that count parameter limits results."""
        backup_path = temp_log_dir / "backup.db"
        backup_path.write_text("data")

        # Log 5 events
        for i in range(5):
            logger.log_backup_start()

        events = logger.get_recent_events(count=3)

        assert len(events) == 3


class TestGetStatistics:
    """Test getting statistics from logs."""

    def test_get_statistics_empty(self, logger):
        """Test getting statistics when no events."""
        stats = logger.get_statistics()

        assert stats['total_backups'] == 0
        assert stats['successful_backups'] == 0
        assert stats['failed_backups'] == 0
        assert stats['last_backup'] is None
        assert stats['last_successful_backup'] is None
        assert stats['average_duration_seconds'] == 0.0
        assert stats['total_size_mb'] == 0.0

    def test_get_statistics_with_successes(self, logger, temp_log_dir):
        """Test statistics with successful backups."""
        backup_path = temp_log_dir / "backup.db"
        backup_path.write_text("data")

        # Log 3 successful backups
        logger.log_backup_success(backup_path, 2.0, 1024 * 1024)
        logger.log_backup_success(backup_path, 4.0, 2048 * 1024)
        logger.log_backup_success(backup_path, 6.0, 4096 * 1024)

        stats = logger.get_statistics()

        assert stats['total_backups'] == 3
        assert stats['successful_backups'] == 3
        assert stats['failed_backups'] == 0
        assert stats['average_duration_seconds'] == 4.0  # (2+4+6)/3
        assert stats['total_size_mb'] == 7.0  # (1+2+4) MB

    def test_get_statistics_with_failures(self, logger):
        """Test statistics with failed backups."""
        # Log 2 successful, 1 failed
        logger.log_backup_failure("Error 1")
        logger.log_backup_failure("Error 2")
        logger.log_backup_success(Path("backup.db"), 1.0, 1024)

        stats = logger.get_statistics()

        assert stats['total_backups'] == 3
        assert stats['successful_backups'] == 1
        assert stats['failed_backups'] == 2


class TestClearLogs:
    """Test clearing log files."""

    def test_clear_logs_removes_text_log(self, logger):
        """Test that clear removes text log and old content."""
        logger.log_backup_start()
        logger.flush()

        # Verify log file exists with content
        assert logger.log_file.exists()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            old_content = f.read()
        assert "Backup started" in old_content

        logger.clear_logs()

        # After clear, log file should exist but with only the cleared message
        assert logger.log_file.exists()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            new_content = f.read()

        # Old content should be gone
        assert "Backup started" not in new_content
        # Only the cleared message should remain
        assert "Log files cleared" in new_content

    def test_clear_logs_removes_json_log(self, logger):
        """Test that clear removes JSON log content."""
        logger.log_backup_start()

        # Verify JSON log file exists
        assert logger.json_log_file.exists()

        # Get initial event count
        initial_events = logger.get_recent_events()
        initial_count = len(initial_events)
        assert initial_count > 0

        logger.clear_logs()

        # After clear, JSON log should be empty (no events)
        cleared_events = logger.get_recent_events()
        assert len(cleared_events) == 0

    def test_clear_logs_logs_action(self, logger):
        """Test that clear action is logged."""
        # First, create some log entries
        logger.log_backup_start()
        logger.log_scheduler_start()

        # Clear logs (this will delete files and log the clear action)
        logger.clear_logs()

        # After clear, log file is re-created with clear message
        assert logger.log_file.exists()
        logger.flush()
        with open(logger.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Log files cleared" in content


class TestBackupEvent:
    """Test BackupEvent dataclass."""

    def test_backup_event_creation(self):
        """Test creating BackupEvent."""
        event = BackupEvent(
            timestamp="2024-01-27T10:00:00",
            event_type="success",
            backup_type="manual",
            backup_path="backup.db",
            size_bytes=1024,
            duration_seconds=5.0,
            status="success"
        )

        assert event.timestamp == "2024-01-27T10:00:00"
        assert event.event_type == "success"
        assert event.backup_type == "manual"
        assert event.size_bytes == 1024

    def test_backup_event_serialization(self):
        """Test BackupEvent can be serialized to dict."""
        event = BackupEvent(
            timestamp="2024-01-27T10:00:00",
            event_type="success",
            backup_type="manual"
        )

        from dataclasses import asdict
        event_dict = asdict(event)

        assert event_dict['timestamp'] == "2024-01-27T10:00:00"
        assert event_dict['event_type'] == "success"
        assert event_dict['backup_type'] == "manual"
