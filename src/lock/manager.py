"""Lock acquisition, heartbeat, and release management."""

import os
import socket
import threading
import time

from lock.models import AppLock


# Simple logger for now (will be replaced in Phase 3)
class Logger:
    """Simple placeholder logger."""

    def debug(self, msg):
        pass  # Suppress debug messages for cleaner output

    def info(self, msg):
        print(f"[INFO] {msg}")

    def warning(self, msg):
        print(f"[WARNING] {msg}")

    def error(self, msg):
        print(f"[ERROR] {msg}")

    def critical(self, msg):
        print(f"[CRITICAL] {msg}")


logger = Logger()


class LockManager:
    """
    Manages application lock with automatic heartbeat refresh.

    Responsibilities:
    - Acquire application lock (with stale cleanup)
    - Maintain lock alive via background heartbeat thread
    - Release lock when done
    - Handle errors gracefully in background thread

    Thread Safety:
    - Uses threading.Event for thread-safe shutdown
    - Background thread marked as daemon (won't block process exit)
    - Database operations protected by Peewee's connection handling
    - Application-level lock for acquisition safety

    Usage Example:
        manager = LockManager(hostname='PC-01', username='alice', pid=12345)
        try:
            lock = manager.acquire_lock()
            print(f"Lock acquired: {lock.hostname}")
            # Do work...
            time.sleep(300)  # 5 minutes
        finally:
            manager.release_lock()
            print("Lock released")

    Context Manager Usage:
        with LockManager('PC-01', 'alice', 12345) as lock:
            # Work here...
            pass
        # Lock automatically released
    """

    # Class-level acquisition lock (shared across all instances)
    _acquisition_lock = threading.Lock()

    # ========== INITIALIZATION ==========

    def __init__(self, hostname: str, username: str | None, pid: int, heartbeat_interval: int = 30):
        """
        Initialize lock manager with process identification.

        Args:
            hostname: Machine name (use socket.gethostname())
            username: Optional user name (use os.environ.get('USERNAME'))
            pid: Process ID (use os.getpid())
            heartbeat_interval: Seconds between heartbeat refreshes (default: 30)
        """
        self.hostname = hostname
        self.username = username
        self.pid = pid

        # Lock reference
        self._lock: AppLock | None = None

        # Thread management
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_event = threading.Event()  # Thread-safe shutdown signal

        # Heartbeat configuration
        self._heartbeat_interval = heartbeat_interval  # seconds (configurable for testing)
        self._lost_lock_event = threading.Event()  # Signals lock loss
        self._last_successful_refresh: float | None = None

    # ========== PUBLIC METHODS ==========

    def acquire_lock(self) -> AppLock:
        """
        Acquire application lock and start heartbeat thread.

        Process:
        1. Check for existing active lock (using application lock for safety)
        2. Remove stale locks if present
        3. Create new lock record (atomic in transaction)
        4. Start background heartbeat thread

        Returns:
            AppLock instance representing acquired lock

        Raises:
            RuntimeError: If lock is already held by active process
        """
        with LockManager._acquisition_lock:  # Prevent race conditions (class-level lock)
            # Use existing acquire() logic from AppLock model
            self._lock = AppLock.acquire(hostname=self.hostname, username=self.username, pid=self.pid)

        # Start heartbeat thread after successful acquisition
        self._start_heartbeat()

        return self._lock

    def release_lock(self) -> bool:
        """
        Release lock and stop heartbeat thread.

        Process:
        1. Signal heartbeat thread to stop
        2. Wait for graceful shutdown (max 5 seconds)
        3. Release lock in database (if owned by caller)
        4. Clean up thread references

        Returns:
            True if lock was released, False if not owned by caller
        """
        # Stop heartbeat first
        self._stop_heartbeat()

        # Release lock
        if self._lock:
            success = AppLock.release(hostname=self.hostname, pid=self.pid)
            self._lock = None
            return success

        return False

    def check_lock_health(self) -> bool:
        """
        Check from main thread if we still have the lock.

        Can be called periodically from main thread to detect
        silent lock loss (heartbeat failures, etc.).

        Returns:
            True if lock is still held, False otherwise
        """
        # Check if lock loss was detected
        if self._lost_lock_event.is_set():
            return False

        # Verify lock still exists in database
        try:
            lock = AppLock.get_active_lock()
            if not lock or lock.hostname != self.hostname or lock.process_id != self.pid:
                return False
            return True
        except Exception:
            return False

    # ========== BACKGROUND HEARTBEAT ==========

    def _heartbeat_loop(self):
        """
        Background thread that refreshes heartbeat every 30 seconds.

        Responsibilities:
        - Refresh heartbeat timestamp in database
        - Handle errors gracefully (log but continue)
        - Detect lock loss (refresh returns False)
        - Stop when stop_event is set
        - Clean up in finally block
        """
        logger.debug(f"Heartbeat thread started for {self.hostname}")

        retry_count = 0
        max_retries = 3

        try:
            while not self._stop_event.is_set():
                try:
                    # Attempt to refresh heartbeat
                    success = AppLock.refresh_heartbeat(self.hostname, self.pid)

                    if not success:
                        # Lock was lost (stolen, deleted, etc.)
                        logger.critical(f"Lost lock for {self.hostname}!")
                        self._lost_lock_event.set()
                        break

                    # Reset retry counter on success
                    retry_count = 0
                    self._last_successful_refresh = time.time()

                except Exception as e:
                    # Error handling with retry logic
                    retry_count += 1

                    error_msg = str(e).lower()

                    if "database is locked" in error_msg or "locked" in error_msg:
                        # SQLite busy - wait and retry
                        logger.warning(f"DB locked, retrying (attempt {retry_count}/{max_retries})")

                        if retry_count >= max_retries:
                            logger.critical("Max retries reached, stopping heartbeat")
                            self._lost_lock_event.set()
                            break

                        # Exponential backoff: 1s, 2s, 4s, max 10s
                        wait_time = min(2**retry_count, 10)
                        self._stop_event.wait(timeout=wait_time)
                        continue
                    else:
                        # Other error - log and continue
                        logger.error(f"Heartbeat error: {e}")

                        if retry_count >= max_retries:
                            logger.critical("Max retries reached, stopping heartbeat")
                            self._lost_lock_event.set()
                            break

                # Wait for next heartbeat interval
                # Check stop_event every second for responsive shutdown
                for _ in range(self._heartbeat_interval):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)

        finally:
            # Guaranteed cleanup
            logger.debug(f"Heartbeat thread stopping for {self.hostname}")
            self._heartbeat_thread = None

    def _start_heartbeat(self):
        """
        Start background heartbeat timer thread.

        Thread Configuration:
        - daemon=True: Won't block process exit
        - target=_heartbeat_loop: Main loop function
        - Name: Human-readable for debugging
        """
        self._stop_event.clear()
        self._lost_lock_event.clear()

        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,  # Critical: won't block process exit
            name=f"Heartbeat-{self.hostname}-{self.pid}",
        )

        self._heartbeat_thread.start()
        logger.debug(f"Heartbeat thread started for {self.hostname}")

    def _stop_heartbeat(self):
        """
        Stop background heartbeat timer thread.

        Shutdown Process:
        1. Set stop_event to signal thread
        2. Wait for thread to finish (max 5 seconds)
        3. Verify thread stopped
        4. Log warning if thread didn't stop gracefully
        """
        if not self._heartbeat_thread or not self._heartbeat_thread.is_alive():
            return

        # Signal thread to stop
        self._stop_event.set()

        # Store thread reference before it might be cleared
        thread = self._heartbeat_thread

        # Wait for graceful shutdown
        thread.join(timeout=5.0)

        # Verify thread stopped (use stored reference)
        if thread.is_alive():
            logger.error(
                f"Heartbeat thread for {self.hostname} did not stop gracefully. "
                "Thread reference cleared, but thread may still be running."
            )
            # Clear reference to prevent accidental reuse
            self._heartbeat_thread = None
        else:
            logger.debug(f"Heartbeat thread stopped successfully for {self.hostname}")

    # ========== PROPERTIES ==========

    @property
    def has_lock(self) -> bool:
        """
        Check if this process currently holds the lock.

        Returns:
            True if lock is active and owned by this process, False otherwise
        """
        if not self._lock:
            return False

        # Verify lock still exists in database
        try:
            active = AppLock.get_active_lock()
            return active is not None and active.hostname == self.hostname and active.process_id == self.pid
        except Exception:
            return False

    # ========== CONTEXT MANAGER SUPPORT ==========

    def __enter__(self):
        """
        Support for 'with' statement.

        Guarantees lock release even if exception occurs.

        Returns:
            Acquired AppLock instance
        """
        self._lock = self.acquire_lock()
        return self._lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Guaranteed cleanup when exiting context.

        Returns:
            False (don't suppress exceptions)
        """
        self.release_lock()
        return False  # Don't suppress any exceptions


# ========== HELPER FUNCTIONS ==========


def get_process_info() -> tuple[str, str | None, int]:
    """
    Get process identification information.

    Returns:
        Tuple of (hostname, username, pid)

    Usage:
        hostname, username, pid = get_process_info()
        manager = LockManager(hostname, username, pid)
    """
    hostname = socket.gethostname()
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    pid = os.getpid()
    return hostname, username, pid
