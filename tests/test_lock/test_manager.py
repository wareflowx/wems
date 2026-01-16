"""Tests for Lock Manager."""

import pytest
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from lock.models import AppLock
from lock.manager import LockManager, get_process_info


class TestLockManagerInitialization:
    """Tests for LockManager initialization."""

    def test_initialization_with_parameters(self, db):
        """Should initialize with process identification."""
        manager = LockManager(hostname='test-host', username='test-user', pid=12345)

        assert manager.hostname == 'test-host'
        assert manager.username == 'test-user'
        assert manager.pid == 12345
        assert manager.has_lock == False
        assert manager._lock is None
        assert manager._heartbeat_thread is None

    def test_initialization_with_nullable_username(self, db):
        """Should accept None for username."""
        manager = LockManager(hostname='test-host', username=None, pid=12345)

        assert manager.hostname == 'test-host'
        assert manager.username is None
        assert manager.pid == 12345


class TestLockManagerAcquisition:
    """Tests for lock acquisition and release."""

    def test_acquire_lock_success(self, db):
        """Should acquire lock and start heartbeat."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        lock = manager.acquire_lock()

        assert lock.hostname == 'test-host'
        assert lock.process_id == 9999
        assert manager.has_lock == True
        assert manager._heartbeat_thread is not None
        assert manager._heartbeat_thread.is_alive()

    def test_acquire_lock_starts_heartbeat(self, db):
        """Should start heartbeat thread when acquiring lock."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        assert manager._heartbeat_thread is not None
        assert manager._heartbeat_thread.is_alive()
        assert manager._stop_event.is_set() == False

    def test_release_lock(self, db):
        """Should release lock and stop heartbeat."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()
        manager.release_lock()

        assert manager.has_lock == False
        assert manager._heartbeat_thread is None or not manager._heartbeat_thread.is_alive()
        assert AppLock.get_active_lock() == None

    def test_release_lock_stops_heartbeat(self, db):
        """Heartbeat thread should stop when lock is released."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        thread = manager._heartbeat_thread
        manager.release_lock()

        # Thread should stop within 5 seconds
        thread.join(timeout=5.0)
        assert not thread.is_alive()

    def test_cannot_override_active_lock(self, db):
        """Should raise error if lock is active."""
        manager1 = LockManager(hostname='host1', username=None, pid=1111)
        manager2 = LockManager(hostname='host2', username=None, pid=2222)

        manager1.acquire_lock()

        with pytest.raises(RuntimeError, match="Lock is held by"):
            manager2.acquire_lock()

        # Cleanup
        manager1.release_lock()

    def test_release_only_by_owner(self, db):
        """Only lock owner should be able to release."""
        manager1 = LockManager(hostname='host1', username=None, pid=1111)
        manager2 = LockManager(hostname='host2', username=None, pid=2222)

        manager1.acquire_lock()

        # manager2 cannot release manager1's lock
        success = manager2.release_lock()
        assert success == False

        # manager1 can still release
        success = manager1.release_lock()
        assert success == True


class TestStaleLockCleanup:
    """Tests for automatic stale lock removal."""

    def test_stale_lock_cleanup_on_acquire(self, db):
        """Should remove stale locks on acquire."""
        # Create old lock
        old_lock = AppLock.create(
            hostname='old-host',
            username='old-user',
            process_id=1111
        )
        # Manually make it stale (5 minutes old)
        old_lock.last_heartbeat = datetime.now() - timedelta(minutes=5)
        old_lock.save()

        # Acquire new lock
        manager = LockManager(hostname='new-host', username=None, pid=2222)
        lock = manager.acquire_lock()

        # Old lock should be deleted
        assert AppLock.select().where(AppLock.hostname == 'old-host').count() == 0
        assert lock.hostname == 'new-host'

        # Cleanup
        manager.release_lock()


class TestHeartbeat:
    """Tests for heartbeat functionality."""

    def test_heartbeat_refreshes_timestamp(self, db):
        """Should refresh heartbeat timestamp every 30 seconds."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        lock = manager.acquire_lock()

        initial_heartbeat = lock.last_heartbeat

        # Wait for heartbeat refresh
        time.sleep(35)

        # Reload from database
        lock_reloaded = AppLock.get_active_lock()
        assert lock_reloaded is not None
        assert lock_reloaded.last_heartbeat > initial_heartbeat

        # Cleanup
        manager.release_lock()

    def test_heartbeat_continues_during_work(self, db):
        """Heartbeat should continue while lock is held."""
        # Use shorter heartbeat interval for testing
        manager = LockManager(hostname='test-host', username=None, pid=9999,
                              heartbeat_interval=2)
        lock = manager.acquire_lock()

        # Get lock from database to see updated heartbeat
        time.sleep(1)
        lock_reloaded = AppLock.get_active_lock()
        timestamp1 = lock_reloaded.last_heartbeat

        time.sleep(2)
        lock_reloaded = AppLock.get_active_lock()
        timestamp2 = lock_reloaded.last_heartbeat

        # Heartbeat should have refreshed
        assert timestamp2 > timestamp1

        # Cleanup
        manager.release_lock()


class TestContextManager:
    """Tests for context manager support."""

    def test_context_manager_acquire(self, db):
        """Should acquire lock when entering context."""
        with LockManager('test-host', None, 9999) as lock:
            assert lock.hostname == 'test-host'
            assert lock.process_id == 9999

    def test_context_manager_release_on_exit(self, db):
        """Should release lock when exiting context."""
        with LockManager('test-host', None, 9999) as lock:
            pass  # Do nothing

        # Lock should be released
        assert AppLock.get_active_lock() == None

    def test_context_manager_release_on_exception(self, db):
        """Should release lock even if exception occurs."""
        class CustomException(Exception):
            pass

        with pytest.raises(CustomException):
            with LockManager('test-host', None, 9999) as lock:
                raise CustomException("Test exception")

        # Lock should still be released
        assert AppLock.get_active_lock() == None


class TestHealthCheck:
    """Tests for health check functionality."""

    def test_health_check_returns_true_when_active(self, db):
        """Should return True when lock is active."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        assert manager.check_lock_health() == True

        # Cleanup
        manager.release_lock()

    def test_health_check_returns_false_when_no_lock(self, db):
        """Should return False when no lock."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)

        assert manager.check_lock_health() == False

    def test_health_check_returns_false_after_release(self, db):
        """Should return False after lock is released."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()
        manager.release_lock()

        assert manager.check_lock_health() == False


class TestGracefulShutdown:
    """Tests for graceful thread shutdown."""

    def test_thread_stops_when_stop_event_set(self, db):
        """Thread should shutdown cleanly when stop_event is set."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        # Store thread reference before it might be cleared
        thread = manager._heartbeat_thread

        # Request shutdown
        manager._stop_event.set()

        # Thread should stop within heartbeat interval
        thread.join(timeout=35)
        assert not thread.is_alive()

    def test_thread_responsive_to_shutdown(self, db):
        """Thread should respond quickly to shutdown request."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        # Mark start time
        start_time = time.time()

        # Request shutdown
        manager._stop_event.set()

        # Wait for thread to stop
        manager._heartbeat_thread.join(timeout=5.0)

        # Should stop within a few seconds (not after 30s)
        elapsed = time.time() - start_time
        assert elapsed < 5.0


class TestConcurrency:
    """Tests for concurrent access scenarios."""

    def test_concurrent_lock_acquisition(self, db):
        """Only one process should acquire the lock."""
        managers = [
            LockManager(hostname=f'host{i}', username=None, pid=i)
            for i in range(5)
        ]

        locks = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(lambda m: m.acquire_lock(), m)
                for m in managers
            ]

            for future in as_completed(futures):
                try:
                    lock = future.result(timeout=5)
                    locks.append(lock)
                except RuntimeError:
                    pass  # Expected for all but one

        assert len(locks) == 1

        # Cleanup
        if locks:
            # Find the manager that got the lock
            for manager in managers:
                if manager._lock == locks[0]:
                    manager.release_lock()
                    break

    def test_sequential_acquisition_and_release(self, db):
        """Multiple managers should be able to acquire lock sequentially."""
        manager1 = LockManager(hostname='host1', username=None, pid=1111)
        manager2 = LockManager(hostname='host2', username=None, pid=2222)

        # Manager1 acquires
        lock1 = manager1.acquire_lock()
        assert lock1.hostname == 'host1'

        # Manager1 releases
        manager1.release_lock()
        assert AppLock.get_active_lock() == None

        # Manager2 can now acquire
        lock2 = manager2.acquire_lock()
        assert lock2.hostname == 'host2'

        # Cleanup
        manager2.release_lock()


class TestLostLockDetection:
    """Tests for lost lock detection."""

    def test_lost_lock_event_set_on_refresh_failure(self, db):
        """Should set lost_lock_event when refresh fails."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        # Manually delete the lock to simulate loss
        AppLock.delete().where(AppLock.hostname == 'test-host').execute()

        # Wait for heartbeat to detect loss
        time.sleep(35)

        # Lost lock event should be set
        assert manager._lost_lock_event.is_set()

    def test_health_check_detects_lost_lock(self, db):
        """Health check should detect lost lock."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)
        manager.acquire_lock()

        # Manually delete the lock
        AppLock.delete().where(AppLock.hostname == 'test-host').execute()

        # Health check should return False
        assert manager.check_lock_health() == False


class TestGetProcessInfo:
    """Tests for get_process_info helper function."""

    def test_get_process_info_returns_tuple(self):
        """Should return tuple of (hostname, username, pid)."""
        hostname, username, pid = get_process_info()

        assert isinstance(hostname, str)
        assert len(hostname) > 0
        assert isinstance(username, (str, type(None)))
        assert isinstance(pid, int)
        assert pid > 0


class TestFullLifecycle:
    """Integration tests for complete lock lifecycle."""

    def test_full_lifecycle(self, db):
        """Test complete lock lifecycle."""
        manager = LockManager(hostname='test-host', username='alice', pid=12345)

        # 1. Acquire
        lock = manager.acquire_lock()
        assert lock.hostname == 'test-host'
        assert manager.has_lock == True

        # 2. Use lock (heartbeat refreshes automatically)
        time.sleep(2)
        # Reload from database to see updated heartbeat
        lock_reloaded = AppLock.get_active_lock()
        assert lock_reloaded is not None
        assert lock_reloaded.last_heartbeat >= lock.locked_at

        # 3. Release
        success = manager.release_lock()
        assert success == True
        assert manager.has_lock == False
        assert AppLock.get_active_lock() == None

    def test_process_crash_recovery(self, db):
        """Stale locks should be automatically cleaned up."""
        # Simulate crash: create lock without heartbeat
        lock = AppLock.create(
            hostname='crashed-host',
            username='victim',
            process_id=9999
        )

        # Make it stale
        lock.last_heartbeat = datetime.now() - timedelta(minutes=5)
        lock.save()

        # New manager should be able to acquire lock
        manager = LockManager(hostname='recovery-host', username='recovery', pid=5000)
        new_lock = manager.acquire_lock()

        assert new_lock.hostname == 'recovery-host'
        assert AppLock.get_active_lock().hostname == 'recovery-host'

        # Cleanup
        manager.release_lock()

    def test_multiple_cycles(self, db):
        """Should handle multiple acquire/release cycles."""
        manager = LockManager(hostname='test-host', username=None, pid=9999)

        for i in range(3):
            lock = manager.acquire_lock()
            assert lock.hostname == 'test-host'

            time.sleep(0.5)  # Simulate some work

            manager.release_lock()
            assert AppLock.get_active_lock() == None
