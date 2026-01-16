# Simple Employee Manager - Development Roadmap

**Version:** 1.0
**Last Updated:** January 16, 2026
**Current Status:** 40% Complete

---

## Executive Summary

The Simple Employee Manager is a warehouse employee management desktop application designed for tracking safety certifications (CACES), medical compliance visits, and online training records. This roadmap outlines the development path from the current state (40% complete) to a fully functional production application.

**Current Progress:**
- ✅ Complete: Data models, database infrastructure, test framework
- ⏳ In Progress: Business logic layer
- ❌ Not Started: Export, utilities, UI

**Estimated Timeline:** 6-8 weeks for full application (3-4 weeks for core functionality without UI)

---

## Current Status Overview

### ✅ Completed (40%)

**Data Layer:**
- Employee, Caces, MedicalVisit, OnlineTraining models with Peewee ORM
- AppLock model for concurrent access control
- SQLite database with WAL mode for network performance
- Automatic expiration calculations with leap year handling
- CASCADE delete relationships

**Test Infrastructure:**
- pytest configuration with in-memory SQLite
- Comprehensive fixtures for all models
- 38 passing tests (model tests + integration tests)
- Database binding and cleanup

**Documentation:**
- PROJECT.md, MODELS.md, MODEL_TESTS.md, PROJECT_STRUCTURE.md
- Complete design documentation with rationale

### ❌ Missing (60%)

**Empty Modules:**
- `src/employee/queries.py` - Complex multi-table queries
- `src/employee/calculations.py` - Business logic calculations
- `src/employee/validators.py` - Custom validators
- `src/lock/manager.py` - Heartbeat timer and lock management
- `src/export/` - Excel export functionality
- `src/utils/` - File operations, config, logging
- `src/ui/` - Flet desktop interface

---

## Development Phases

## 🔴 Phase 1: Complete Employee Module (Week 1-2)

**Priority:** CRITICAL
**Goal:** Implement business logic layer for alerts and compliance tracking
**Dependencies:** None (models are complete)

### 1.1 Implement `src/employee/queries.py`

**Objective:** Create optimized queries for dashboard and alerts

**Functions to Implement:**

```python
def get_employees_with_expiring_items(days=30):
    """
    Get employees with certifications expiring within X days.

    Returns:
        List of employees with expiring CACES, medical visits, or trainings
        Prefetch related items to avoid N+1 queries
    """

def get_employees_with_expired_caces():
    """Get employees with expired CACES certifications."""

def get_employees_with_expired_medical_visits():
    """Get employees with expired medical visits."""

def get_unfit_employees():
    """Get employees with unfit medical status."""

def get_dashboard_statistics():
    """
    Calculate aggregated statistics for dashboard.

    Returns:
        {
            'total_employees': int,
            'active_employees': int,
            'expiring_caces': int,
            'expiring_visits': int,
            'unfit_employees': int
        }
    """

def get_expiring_items_by_type(days=30):
    """
    Get expiring items grouped by type.

    Returns:
        Dict with employee_id as key, lists of expiring items as values
    """
```

**Technical Considerations:**
- Use `prefetch()` to avoid N+1 query problems
- Use `join()` for multi-table queries
- Add database indexes on `(employee_id, expiration_date)`
- Return model instances, not dicts (for ORM flexibility)

**Testing:**
- Test query returns correct employee counts
- Test prefetch eliminates N+1 queries
- Test edge cases (no expiring items, all expired, etc.)
- Time-dependent tests with `freezegun` library

**Acceptance Criteria:**
- [ ] All functions implemented and documented
- [ ] Unit tests for each query function
- [ ] Performance tests (query execution time < 100ms for 1000 employees)
- [ ] Integration tests with real data

---

### 1.2 Implement `src/employee/calculations.py`

**Objective:** Implement business logic for compliance scoring and alerts

**Functions to Implement:**

```python
def calculate_seniority(employee) -> int:
    """
    Calculate employee seniority in complete years.

    Uses hire_date or entry_date, handles leap years correctly.
    Returns 0 if no date available.
    """

def calculate_compliance_score(employee) -> dict:
    """
    Calculate overall compliance score (0-100).

    Scoring:
    - Valid item: +100 points
    - Critical (expiring soon): -30 points
    - Expired: -100 points
    - Final score: weighted average

    Returns:
        {
            'score': float (0-100),
            'total_items': int,
            'valid_items': int,
            'critical_items': int,
            'expired_items': int
        }
    """

def get_compliance_status(employee) -> str:
    """
    Determine overall compliance status.

    Returns:
        'critical': Has expired items
        'warning': Has items expiring soon (< 30 days)
        'compliant': All items valid
    """

def calculate_next_actions(employee) -> list:
    """
    Get prioritized list of required actions.

    Returns:
        [
            {
                'type': 'renewal' | 'visit' | 'training',
                'priority': 'urgent' | 'high' | 'normal',
                'item': model_instance,
                'description': str
            }
        ]
    """

def days_until_next_action(employee) -> int:
    """
    Calculate days until next required action.

    Returns:
        Days until earliest expiration, or 9999 if no actions needed
    """

def calculate_age(employee) -> int | None:
    """
    Calculate employee age from birth_date.

    Returns None if birth_date not available.
    """
```

**Technical Considerations:**
- Use `dateutil.relativedelta` for accurate year calculations
- Handle missing/None values gracefully
- Cache expensive calculations if needed
- Return simple data types (dict, list, str) for JSON serialization

**Testing:**
- Test seniority calculation with various hire dates
- Test compliance scoring with different item combinations
- Test status determination (critical/warning/compliant)
- Test action prioritization
- Time-dependent tests with `freezegun`

**Acceptance Criteria:**
- [ ] All functions implemented and documented
- [ ] Unit tests for each calculation function
- [ ] Tests with realistic scenarios
- [ ] Edge case handling (missing dates, no items, etc.)

---

## 🔴 Phase 2: Lock Manager Heartbeat (Week 2)

**Priority:** CRITICAL
**Goal:** Implement background heartbeat mechanism for lock management
**Dependencies:** AppLock model (complete)
**Estimated Duration:** 1 week

### 📊 Current State Analysis

**✅ Already Implemented (AppLock Model):**

The `AppLock` model in `src/lock/models.py` already provides:
- ✅ Computed properties (`is_stale`, `age_seconds`, `heartbeat_age_seconds`)
- ✅ Class methods (`acquire()`, `release()`, `refresh_heartbeat()`, `get_active_lock()`)
- ✅ Stale lock detection logic (2-minute timeout)
- ✅ Owner validation (hostname + pid)

**❌ Missing (LockManager):**

**Empty file:** `src/lock/manager.py` - Only contains docstring

---

### 2.1 Implement `src/lock/manager.py`

**Objective:** Create `LockManager` class that automatically maintains lock via background heartbeat thread.

#### Architecture Overview

```
Application Start
        ↓
LockManager.acquire_lock()
        ↓
   AppLock.acquire()
   - Check existing lock
   - Remove if stale
   - Create new lock
        ↓
   _start_heartbeat()
   - Create threading.Thread(daemon=True)
   - Start background thread
        ↓
   Background Thread Loop (every 30s)
   - refresh_heartbeat()
   - Handle errors gracefully
   - Check stop_event
        ↓
Application Work
        ↓
LockManager.release_lock()
        ↓
   _stop_heartbeat()
   - Signal thread to stop
   - Wait for graceful shutdown
   - AppLock.release()
```

#### Detailed Class Specification

```python
import threading
import time
import socket
import os
from datetime import datetime, timedelta

from lock.models import AppLock


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

    # ========== INITIALIZATION ==========

    def __init__(self, hostname: str, username: str | None, pid: int):
        """
        Initialize lock manager with process identification.

        Args:
            hostname: Machine name (use socket.gethostname())
            username: Optional user name (use os.environ.get('USERNAME'))
            pid: Process ID (use os.getpid())

        Process Identification Sources:
            ```python
            import socket
            import os

            hostname = socket.gethostname()  # Machine name
            username = os.environ.get('USERNAME') or os.environ.get('USER')
            pid = os.getpid()  # Current process ID
            ```
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
        self._heartbeat_interval = 30  # seconds
        self._lost_lock_event = threading.Event()  # Signals lock loss
        self._last_successful_refresh: float | None = None

        # Application-level acquisition lock (prevents race conditions)
        self._acquisition_lock = threading.Lock()

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

        Thread Safety:
            - Uses _acquisition_lock to prevent concurrent acquisition attempts
            - Database transaction ensures atomic lock creation
        """
        with self._acquisition_lock:  # Prevent race conditions
            # Use existing acquire() logic from AppLock model
            self._lock = AppLock.acquire(
                hostname=self.hostname,
                username=self.username,
                pid=self.pid
            )

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

        Thread Safety:
            - Only succeeds if hostname and pid match
            - Guarantees heartbeat stops even if release fails
        """
        # Stop heartbeat first
        self._stop_heartbeat()

        # Release lock
        if self._lock:
            success = AppLock.release(
                hostname=self.hostname,
                pid=self.pid
            )
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

        Usage:
            ```python
            # In main thread, periodically check:
            if not manager.check_lock_health():
                logger.critical("Lock verification failed!")
                # Take action: save work, alert user, etc.
            ```
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

        Error Handling:
        - Database errors: Log and retry (up to 3 times)
        - Lock loss: Set lost_lock_event and exit
        - Unexpected errors: Log, wait, and continue

        Shutdown Behavior:
        - Checks stop_event every second (not every 30s)
        - Guarantees prompt response to shutdown request
        - Cleans up resources in finally block
        """
        logger.debug(f"Heartbeat thread started for {self.hostname}")

        retry_count = 0
        max_retries = 3

        try:
            while not self._stop_event.is_set():
                try:
                    # Attempt to refresh heartbeat
                    success = AppLock.refresh_heartbeat(
                        self.hostname,
                        self.pid
                    )

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
                        wait_time = min(2 ** retry_count, 10)
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
            name=f"Heartbeat-{self.hostname}-{self.pid}"
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

        Timeout Handling:
        - If thread doesn't stop in 5s, logs warning
        - Thread reference cleared to prevent further use
        - Note: Python threads cannot be forcibly killed
        """
        if not self._heartbeat_thread or not self._heartbeat_thread.is_alive():
            return

        # Signal thread to stop
        self._stop_event.set()

        # Wait for graceful shutdown
        self._heartbeat_thread.join(timeout=5.0)

        # Verify thread stopped
        if self._heartbeat_thread.is_alive():
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
            return (active is not None and
                    active.hostname == self.hostname and
                    active.process_id == self.pid)
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

        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value if exception occurred
            exc_tb: Exception traceback if exception occurred

        Returns:
            False (don't suppress exceptions)
        """
        self.release_lock()
        return False  # Don't suppress any exceptions
```

#### Risk Analysis and Mitigation Strategies

##### Risk 1: Deadlock of Heartbeat Thread

**Problem:** Thread blocks indefinitely on database operation.

**Recommended Solution: Timeout + Retry**

```python
# In _heartbeat_loop, handle database locks:
try:
    success = AppLock.refresh_heartbeat(self.hostname, self.pid)
except Exception as e:
    if "database is locked" in str(e).lower():
        logger.warning(f"DB locked, retrying: {e}")
        self._stop_event.wait(timeout=1.0)  # Wait 1s
        continue
    else:
        logger.error(f"Heartbeat error: {e}")
```

**Why this works:**
- Robust to temporary SQLite locks
- Thread doesn't crash on transient errors
- Automatic recovery with retry logic

---

##### Risk 2: Thread Zombie / Memory Leak

**Problem:** Thread continues running after lock release.

**Recommended Solution: Two-Phase Shutdown + Frequent Checks**

```python
# In _heartbeat_loop, check stop_event frequently:
while not self._stop_event.is_set():
    # ... heartbeat work ...

    # Instead of: time.sleep(30)
    # Do this for responsive shutdown:
    for _ in range(30):  # 30 seconds
        if self._stop_event.is_set():
            break
        time.sleep(1)

# In _stop_heartbeat, with finally block:
try:
    # ... shutdown logic ...
finally:
    logger.debug("Heartbeat cleanup complete")
    self._heartbeat_thread = None
```

**Combined with Context Manager:**

```python
# Usage guarantees cleanup:
with LockManager('host', None, 1234) as lock:
    # ... work ...
# Heartbeat guaranteed to stop here, even on exception
```

**Why this works:**
- Frequent stop_event checks → responsive shutdown
- finally block → guaranteed cleanup
- Context manager → exception-safe

---

##### Risk 3: Race Condition on Lock Acquisition

**Problem:** Two processes acquire lock simultaneously.

**Recommended Solution: Database Transaction + Application Lock**

```python
# In acquire_lock:
with self._acquisition_lock:  # Application-level lock
    # Only one thread/process can execute this at a time

    # AppLock.acquire() uses database transaction:
    with database.atomic():
        # Check for active lock
        active = AppLock.get_active_lock()
        if active and not active.is_stale:
            raise RuntimeError(f"Lock held by {active.hostname}")

        # Delete stale if exists
        if active:
            active.delete_instance()

        # Create new lock (atomic in transaction)
        return AppLock.create(...)
```

**Defense in Depth:**
1. Application-level lock (`_acquisition_lock`) - prevents internal races
2. Database transaction - guarantees atomicity
3. Stale check - automatic cleanup of old locks

---

##### Risk 4: Silent Lock Loss

**Problem:** Heartbeat fails silently, application thinks it still has lock.

**Recommended Solution: Health Check + Lost Lock Event**

```python
# In LockManager, add:
def check_lock_health(self) -> bool:
    """Check from main thread if we still have the lock."""
    if self._lost_lock_event.is_set():
        return False

    lock = AppLock.get_active_lock()
    if not lock or lock.hostname != self.hostname:
        return False
    return True

# In _heartbeat_loop, detect loss:
if not success:
    logger.critical("Lost lock during heartbeat!")
    self._lost_lock_event.set()  # Notify main thread
    break
```

**Main Thread Monitoring:**

```python
# Optional: Start watchdog in main thread
def start_watchdog(self):
    """Monitor lock health from main thread."""
    def watchdog():
        while self.has_lock:
            if not self.check_lock_health():
                logger.critical("Lock verification failed!")
                # Take action: alert user, save work, etc.
                break
            time.sleep(15)  # Check every 15 seconds

    threading.Thread(target=watchdog, daemon=True).start()
```

---

##### Risk 5: Database Corruption on Crash

**Solution: WAL Mode (Already Configured)**

```python
# In database/connection.py:
database.execute_sql('PRAGMA journal_mode=WAL')
database.execute_sql('PRAGMA synchronous=NORMAL')
```

**Why WAL Mode is Sufficient:**
- Isolates writes to separate -wal file
- If crash occurs, -wal file is ignored on restart
- No corruption of main database file
- Automatic recovery on next open

**Optional Integrity Check:**

```python
def verify_database_integrity():
    """Check database integrity on startup."""
    try:
        result = database.execute_sql('PRAGMA integrity_check').fetchone()
        if result[0] != 'ok':
            logger.critical(f"Database corruption: {result}")
            return False
        return True
    except Exception as e:
        logger.critical(f"Cannot verify database: {e}")
        return False
```

---

#### Risk Mitigation Summary

| Risk | Solution | Complexity | Effectiveness |
|------|----------|------------|--------------|
| Deadlock heartbeat | Timeout (5s) + Retry | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Thread zombie | 2-phase shutdown + frequent checks | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Race condition | Transaction + app lock | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Silent lock loss | Health check + lost event | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Corruption DB | WAL mode (already done) | ⭐ | ⭐⭐⭐⭐⭐ |

---

#### Configuration Parameters

**Hardcoded Values (with rationale):**

```python
# Heartbeat interval: 30 seconds
# - Frequent enough to detect crashes quickly
# - Not too aggressive for network shares
# - 4 missed heartbeats = 2 minute timeout

HEARTBEAT_INTERVAL = 30  # seconds

# Stale timeout: 2 minutes (in AppLock model)
# - 4 x heartbeat_interval = tolerance margin
# - Quick crash detection
# - Allows for network hiccups

TIMEOUT_MINUTES = 2

# Shutdown timeout: 5 seconds
# - Enough time for graceful shutdown
# - Doesn't block process exit
# - Thread is daemon anyway

SHUTDOWN_TIMEOUT = 5.0  # seconds

# Retry configuration
MAX_RETRIES = 3  # Before giving up
BASE_RETRY_DELAY = 1.0  # seconds (exponential backoff)
```

---

#### Technical Considerations

**Thread Management:**
- Use `threading.Thread` with `daemon=True` (won't block process exit)
- Use `threading.Event` for thread-safe shutdown signal
- Thread name includes hostname/pid for debugging
- Check `stop_event` every second (not every 30s) for responsive shutdown

**Thread Safety:**
- Application-level lock (`_acquisition_lock`) prevents concurrent acquisitions
- Peewee handles per-thread database connections automatically
- WAL mode allows concurrent reads during writes
- Use `threading.Event` for inter-thread communication

**Error Handling:**
- Background thread catches all exceptions (log but continue)
- Retry logic for transient errors (database locks)
- Lost lock event signals main thread of failures
- finally block guarantees cleanup

**Performance:**
- Heartbeat thread is lightweight (simple UPDATE every 30s)
- Daemon thread doesn't block process exit
- Minimal CPU usage (mostly sleeping/waiting)
- No blocking of main thread

---

#### Testing Strategy

**Unit Tests:**

```python
def test_lock_manager_initialization():
    """Should initialize with process identification."""
    manager = LockManager(hostname='test-host', username='test-user', pid=12345)
    assert manager.hostname == 'test-host'
    assert manager.username == 'test-user'
    assert manager.pid == 12345
    assert manager.has_lock == False

def test_acquire_lock_success():
    """Should acquire lock and start heartbeat."""
    manager = LockManager(hostname='test', username=None, pid=9999)
    lock = manager.acquire_lock()

    assert lock.hostname == 'test'
    assert manager.has_lock == True
    assert manager._heartbeat_thread.is_alive()

def test_release_lock():
    """Should release lock and stop heartbeat."""
    manager = LockManager(hostname='test', username=None, pid=9999)
    manager.acquire_lock()
    manager.release_lock()

    assert manager.has_lock == False
    assert manager._heartbeat_thread is None or not manager._heartbeat_thread.is_alive()
    assert AppLock.get_active_lock() == None

def test_context_manager():
    """Should support 'with' statement for guaranteed cleanup."""
    with LockManager('test', None, 9999) as lock:
        assert lock.hostname == 'test'
        assert manager.has_lock == True

    # Lock automatically released
    assert AppLock.get_active_lock() == None

def test_cannot_override_active_lock():
    """Should raise error if lock is active."""
    manager1 = LockManager(hostname='host1', username=None, pid=1111)
    manager2 = LockManager(hostname='host2', username=None, pid=2222)

    manager1.acquire_lock()

    with pytest.raises(RuntimeError):
        manager2.acquire_lock()
```

**Heartbeat Tests:**

```python
def test_heartbeat_refreshes():
    """Should refresh heartbeat every 30 seconds."""
    manager = LockManager(hostname='test', username=None, pid=9999)
    lock = manager.acquire_lock()

    initial_heartbeat = lock.last_heartbeat

    # Wait for heartbeat refresh
    time.sleep(35)

    # Reload from database
    lock_reloaded = AppLock.get_active_lock()
    assert lock_reloaded.last_heartbeat > initial_heartbeat

def test_heartbeat_stops_on_release():
    """Heartbeat thread should stop when lock is released."""
    manager = LockManager(hostname='test', username=None, pid=9999)
    manager.acquire_lock()

    thread = manager._heartbeat_thread
    manager.release_lock()

    # Thread should stop within 5 seconds
    thread.join(timeout=5.0)
    assert not thread.is_alive()
```

**Stale Lock Tests:**

```python
def test_stale_lock_cleanup():
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

def test_concurrent_lock_acquisition():
    """Only one process should acquire the lock."""
    import concurrent.futures

    managers = [
        LockManager(hostname=f'host{i}', username=None, pid=i)
        for i in range(5)
    ]

    locks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(lambda m: m.acquire_lock(), m)
            for m in managers
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                lock = future.result(timeout=5)
                locks.append(lock)
            except RuntimeError:
                pass  # Expected for all but one

    assert len(locks) == 1
```

**Thread Safety Tests:**

```python
def test_heartbeat_continues_after_exception():
    """Heartbeat should continue after transient errors."""
    # This test would mock database errors
    # and verify heartbeat continues
    pass

def test_graceful_shutdown():
    """Thread should shutdown cleanly when stop_event is set."""
    manager = LockManager(hostname='test', username=None, pid=9999)
    manager.acquire_lock()

    # Request shutdown
    manager._stop_event.set()

    # Thread should stop within heartbeat interval
    manager._heartbeat_thread.join(timeout=35)
    assert not manager._heartbeat_thread.is_alive()
```

**Integration Tests:**

```python
def test_full_lifecycle():
    """Test complete lock lifecycle."""
    manager = LockManager(hostname='test', username='alice', pid=12345)

    # 1. Acquire
    lock = manager.acquire_lock()
    assert lock.hostname == 'test'
    assert manager.has_lock == True

    # 2. Use lock (heartbeat refreshes)
    time.sleep(35)
    lock.refresh()
    assert lock.last_heartbeat > lock.locked_at

    # 3. Release
    success = manager.release_lock()
    assert success == True
    assert manager.has_lock == False
    assert AppLock.get_active_lock() == None

def test_process_crash_recovery():
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
```

---

#### Acceptance Criteria

**Implementation:**
- [ ] LockManager class implemented with all methods
- [ ] Heartbeat refreshes every 30 seconds automatically
- [ ] Lock doesn't go stale while manager is active
- [ ] Stale locks are automatically removed on acquisition
- [ ] Thread-safe operations (using _acquisition_lock)
- [ ] Context manager support (`__enter__` / `__exit__`)

**Error Handling:**
- [ ] Background thread handles database errors gracefully
- [ ] Retry logic for transient errors (max 3 retries)
- [ ] Lost lock detection via `_lost_lock_event`
- [ ] Health check method (`check_lock_health()`)

**Thread Management:**
- [ ] Heartbeat thread starts on lock acquisition
- [ ] Heartbeat thread stops on lock release
- [ ] Thread checks stop_event frequently (every 1s)
- [ ] Thread marked as daemon (won't block process exit)
- [ ] Graceful shutdown with 5-second timeout

**Testing:**
- [ ] Unit tests for all public methods
- [ ] Tests for heartbeat refresh timing
- [ ] Tests for stale lock cleanup
- [ ] Tests for concurrent acquisition
- [ ] Tests for thread lifecycle
- [ ] Tests for context manager usage
- [ ] Integration tests for full lifecycle
- [ ] Tests simulating process crashes

**Documentation:**
- [ ] Comprehensive docstrings for all methods
- [ ] Usage examples in docstrings
- [ ] Comments explaining thread safety considerations
- [ ] Error handling documented

---

## 🟡 Phase 3: Utils Module (Week 3-4)

**Priority:** HIGH
**Goal:** Implement file operations, configuration, and logging
**Dependencies:** None

### 3.1 Implement `src/utils/files.py`

**Objective:** Handle document file operations

**Functions to Implement:**

```python
def copy_document_to_storage(
    source_path: Path,
    category: str,  # 'caces', 'medical', 'training'
    employee: Employee,
    document_date: date,
    title: str
) -> Path:
    """
    Copy uploaded document to standardized storage location.

    Storage structure:
        documents/{category}/{employee_id}_{date}_{sanitized_title}.{ext}

    Returns:
        Path to stored file
    """

def sanitize_filename(filename: str) -> str:
    """
    Remove/rename unsafe characters from filename.

    Removes: ../.., special chars, leading/trailing spaces
    Replaces spaces with underscores
    Keeps: letters, numbers, hyphens, underscores, dots
    """

def generate_document_name(
    category: str,
    employee: Employee,
    document_date: date,
    title: str
) -> str:
    """
    Generate standardized document name.

    Format: {external_id}_{category}_{YYYYMMDD}_{title}.{ext}
    """

def ensure_directory_exists(path: Path) -> None:
    """Create directory if it doesn't exist."""

def validate_file_type(file: Path, allowed_extensions: list[str]) -> bool:
    """
    Validate file has allowed extension.

    Returns True if valid, False otherwise.
    """
```

**Testing:**
- Test file copying with various scenarios
- Test filename sanitization
- Test document name generation
- Test directory creation
- Test file type validation
- Test error handling (permission errors, missing files)

**Acceptance Criteria:**
- [ ] All functions implemented
- [ ] Handles network file system gracefully
- [ ] Prevents directory traversal attacks
- [ ] Clear error messages
- [ ] Comprehensive tests

---

### 3.2 Implement `src/utils/config.py`

**Objective:** Load and validate application configuration

**Functions to Implement:**

```python
def load_config(config_path: Path = Path("config.json")) -> dict:
    """
    Load configuration from JSON file.

    Returns config dict or defaults if file missing.
    """

def get_alert_thresholds(config: dict) -> dict:
    """
    Get alert thresholds from config.

    Returns:
        {
            'critical_days': int,  # default 7
            'warning_days': int,    # default 30
            'caces_warning_months': int,  # default 6
            'visit_warning_months': int   # default 6
        }
    """

def get_lock_timeout(config: dict) -> int:
    """Get lock timeout in minutes (default 2)."""

def get_roles(config: dict) -> list[str]:
    """Get list of valid roles or defaults."""

def get_workspaces(config: dict) -> list[str]:
    """Get list of valid workspaces or defaults."""

def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    Validate configuration values.

    Returns:
        (is_valid, list_of_errors)
    """
```

**Config.json Structure:**
```json
{
  "alerts": {
    "critical_days": 7,
    "warning_days": 30
  },
  "lock": {
    "timeout_minutes": 2,
    "heartbeat_interval_seconds": 30
  },
  "organization": {
    "roles": ["Cariste", "Préparateur", "Magasinier"],
    "workspaces": ["Quai", "Zone A", "Zone B", "Bureau"]
  }
}
```

**Testing:**
- Test loading with valid config
- Test loading with missing config (use defaults)
- Test loading with invalid JSON (handle gracefully)
- Test validation with various config values
- Test default values when config missing

**Acceptance Criteria:**
- [ ] Loads config.json with proper error handling
- [ ] Provides sensible defaults when config missing
- [ ] Validates config values
- [ ] Clear error messages for invalid config
- [ ] Tests for all scenarios

---

### 3.3 Implement `src/utils/log.py`

**Objective:** Setup application logging

**Functions to Implement:**

```python
def setup_logger(
    name: str = "employee_manager",
    level: str = "INFO",
    log_file: Path | None = None
) -> logging.Logger:
    """
    Setup logger with rotating file handler.

    Features:
    - RotatingFileHandler (max 5MB, keep 3 files)
    - Console handler for debugging
    - Formatter with timestamp, level, module, message
    - Application lifecycle logging

    Returns configured logger instance.
    """

def log_application_start(logger):
    """Log application startup with system info."""

def log_application_stop(logger):
    """Log application shutdown."""

def log_lock_acquired(logger, lock):
    """Log when lock is acquired."""

def log_lock_released(logger, lock):
    """Log when lock is released."""
```

**Logging Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages (expiring items, etc.)
- ERROR: Error events (lock failures, file errors, etc.)
- CRITICAL: Critical failures (database corruption, etc.)

**Testing:**
- Test logger creation
- Test file rotation (simulate large logs)
- Test log output format
- Test console vs file logging

**Acceptance Criteria:**
- [ ] Logger setup function implemented
- [ ] RotatingFileHandler configured
- [ ] Console handler for debugging
- [ ] Proper log format
- [ ] Application lifecycle logging functions
- [ ] Tests for logging functionality

---

## 🟡 Phase 4: Excel Export (Week 4-5)

**Priority:** HIGH
**Goal:** Implement Excel export with conditional formatting
**Dependencies:** Models, calculations, queries

### 4.1 Implement `src/export/templates.py`

**Objective:** Define Excel column definitions and styles

**Constants to Define:**

```python
# Column definitions for employee export
EMPLOYEE_COLUMNS = [
    {'key': 'external_id', 'header': 'ID WMS', 'width': 15},
    {'key': 'full_name', 'header': 'Nom Complet', 'width': 25},
    {'key': 'workspace', 'header': 'Zone', 'width': 15},
    {'key': 'role', 'header': 'Poste', 'width': 20},
    {'key': 'contract_type', 'header': 'Contrat', 'width': 12},
    {'key': 'entry_date', 'header': 'Date Entrée', 'width': 15},
    {'key': 'seniority', 'header': 'Ancienneté', 'width': 12},
    {'key': 'status', 'header': 'Statut', 'width': 15},
]

# Column definitions for CACES
CACES_COLUMNS = [
    {'key': 'kind', 'header': 'Type CACES', 'width': 15},
    {'key': 'completion_date', 'header': 'Date Obtention', 'width': 15},
    {'key': 'expiration_date', 'header': 'Date Expiration', 'width': 15},
    {'key': 'days_until_expiration', 'header': 'Jours Restants', 'width': 15},
    {'key': 'status', 'header': 'Statut', 'width': 12},
    {'key': 'document_path', 'header': 'Document', 'width': 40},
]

# Cell styles
HEADER_STYLE = {
    'font': {'bold': True, 'size': 12, 'color': 'FFFFFF'},
    'fill': {'fgColor': '4472C4', 'bgColor': '4472C4'},
    'alignment': {'horizontal': 'center', 'vertical': 'center'},
    'border': 1
}

CRITICAL_STYLE = {
    'font': {'bold': True, 'color': 'FFFFFF'},
    'fill': {'fgColor': 'C0504D', 'bgColor': 'C0504D'},
    'border': 1
}

WARNING_STYLE = {
    'font': {'bold': True, 'color': '000000'},
    'fill': {'fgColor': 'FFEB9C', 'bgColor': 'FFEB9C'},
    'border': 1
}

VALID_STYLE = {
    'font': {'color': '000000'},
    'fill': {'fgColor': 'C6EFCE', 'bgColor': 'C6EFCE'},
    'border': 1
}

def get_column_widths(columns: list) -> list:
    """Extract widths from column definitions."""

def get_style_for_status(status: str) -> dict:
    """Return cell style based on status value."""
```

**Acceptance Criteria:**
- [ ] Column definitions for all entity types
- [ ] Cell style definitions
- [ ] Helper functions implemented
- [ ] Consistent naming conventions

---

### 4.2 Implement `src/export/excel.py`

**Objective:** Generate Excel reports with conditional formatting

**Functions to Implement:**

```python
def export_employees_to_excel(
    output_path: Path,
    employees: list[Employee],
    include_caces: bool = True,
    include_visits: bool = True,
    include_trainings: bool = True
) -> None:
    """
    Export employees to Excel file.

    Creates workbook with multiple sheets:
    - Summary: Overview statistics
    - Employees: Employee data
    - CACES: Certification details (if include_caces)
    - Medical Visits: Visit details (if include_visits)
    - Trainings: Training details (if include_trainings)
    """

def create_summary_sheet(workbook, stats: dict):
    """
    Create summary sheet with key metrics.

    Metrics:
    - Total employees
    - Active employees
    - Expiring items (by category)
    - Unfit employees
    """

def create_employees_sheet(workbook, employees: list[Employee]):
    """
    Create employee data sheet with headers.

    Apply conditional formatting based on status.
    """

def create_caces_sheet(workbook, employees: list[Employee]):
    """
    Create CACES details sheet.

    One row per CACES, grouped by employee.
    Apply conditional formatting (red for expired, orange for critical).
    """

def create_medical_visits_sheet(workbook, employees: list[Employee]):
    """
    Create medical visits sheet.

    Apply conditional formatting based on fitness status.
    """

def create_trainings_sheet(workbook, employees: list[Employee]):
    """
    Create trainings sheet.

    Apply conditional formatting for expiring trainings.
    """

def apply_conditional_formatting(worksheet, data: list, column_configs: list):
    """
    Apply conditional formatting based on values.

    Rules:
    - status = 'expired' → red background
    - status = 'critical' → orange background
    - status = 'warning' → yellow background
    - status = 'valid' → green background
    - days_until_expiration < 0 → red background
    """

def save_workbook(workbook, path: Path) -> None:
    """Save workbook to file with error handling."""
```

**Technical Considerations:**
- Use `openpyxl` library
- Apply styles to ranges for performance (not cell-by-cell)
- Handle large datasets (stream if needed)
- Auto-adjust column widths
- Add freeze panes for headers
- Include last updated timestamp

**Testing:**
- Test Excel generation with sample data
- Test conditional formatting correctness
- Test with large datasets (100+ employees)
- Test file permissions and error handling
- Validate generated Excel files manually

**Acceptance Criteria:**
- [ ] All export functions implemented
- [ ] Multiple sheets created correctly
- [ ] Conditional formatting works
- [ ] Styles applied properly
- [ ] Handles errors gracefully
- [ ] Comprehensive tests
- [ ] Generated files validated manually

---

## 🟢 Phase 5: Validators (Week 5)

**Priority:** MEDIUM
**Goal:** Implement custom Peewee validators
**Dependencies:** Models (complete)

### 5.1 Implement `src/employee/validators.py`

**Objective:** Add custom validation logic

**Validators to Implement:**

```python
def validate_external_id(value: str) -> bool:
    """
    Validate external ID format.

    Rules:
    - Must be unique
    - Format: WMS-XXXX or similar
    - Alphanumeric with limited special chars
    """

def validate_entry_date(value: date) -> bool:
    """
    Validate entry date is not in future.

    Raises ValueError if date > today.
    """

def validate_caces_kind(value: str) -> bool:
    """
    Validate CACES kind is in allowed list.

    Must be in CACES_TYPES constant.
    """

def validate_visit_type(value: str) -> bool:
    """
    Validate visit type is in allowed list.

    Must be in ['initial', 'periodic', 'recovery'].
    """

def validate_visit_result(value: str, visit_type: str) -> bool:
    """
    Validate visit result is appropriate for visit type.

    Rules:
    - 'recovery' visits can be: 'fit', 'unfit', 'restrictions'
    - Other visits can be: 'fit', 'unfit', 'restrictions'
    - Must be appropriate for visit type
    """

class UniqueValidator:
    """
    Custom Peewee validator for uniqueness.

    Usage:
        external_id = CharField(unique=True, validators=[UniqueValidator()])
    """

class DateRangeValidator:
    """
    Validate date is within acceptable range.

    Usage:
        entry_date = DateField(validators=[DateRangeValidator(min=date(2020, 1, 1))])
    """
```

**Testing:**
- Test each validator function
- Test Peewee integration
- Test error messages

**Acceptance Criteria:**
- [ ] All validators implemented
- [ ] Peewee integration works
- [ ] Clear error messages
- [ ] Tests for validation rules

---

## 🟢 Phase 6: CLI for Testing (Week 5-6)

**Priority:** MEDIUM
**Goal:** Create temporary CLI for testing before UI
**Dependencies:** All core modules (queries, calculations, export)

### 6.1 Implement Basic CLI

**Location:** `src/main.py` or new `src/cli.py`

**Commands to Implement:**

```python
# Employee commands
python main.py add-employee
python main.py list-employees
python main.py show-employee <id>

# Certification commands
python main.py add-caces <employee_id>
python main.py add-visit <employee_id>
python main.py add-training <employee_id>

# Reporting commands
python main.py check-alerts
python main.py export-excel <output_path>
python main.py dashboard

# Lock commands
python main.py acquire-lock
python main.py release-lock
python main.py lock-status
```

**CLI Framework:** Use `argparse` or `click`

**Features:**
- Interactive prompts for data entry
- Table formatting for output (use `tabulate`)
- Progress indicators for long operations
- Error handling with clear messages

**Testing:**
- Manual testing of all commands
- Integration tests for CLI flows

**Acceptance Criteria:**
- [ ] All commands implemented
- [ ] Interactive prompts work
- [ ] Output formatting is clear
- [ ] Error handling is robust
- [ ] All features can be tested through CLI

---

## ⚪ Phase 7: Flet UI (Week 7+)

**Priority:** LOW
**Goal:** Build desktop application interface
**Dependencies:** All core modules complete

### 7.1 UI Architecture

**Technology:** Flet (Python Flutter)

**Key Views to Implement:**

1. **Main Application Window**
   - Menu bar
   - Status bar (lock status, user info)
   - Main content area

2. **Employee List View**
   - Table of employees with filtering
   - Status indicators (compliant, warning, critical)
   - Quick actions (view, edit, delete)
   - Search functionality

3. **Employee Detail View**
   - Employee information
   - Tabs: CACES, Medical Visits, Trainings
   - Add/Edit/Delete related items
   - Document upload

4. **Documents View**
   - File picker for uploads
   - Document list by category
   - Preview functionality
   - Batch operations

5. **Alerts Dashboard**
   - Employees with expiring items
   - Color-coded by severity
   - Filter by type
   - Export reports

6. **Settings Dialog**
   - Configuration
   - Database location
   - Alert thresholds
   - Role/workspace management

**UI Features:**
- Responsive layout
- Keyboard shortcuts
- Dark/light theme
- Context menus
- Progress indicators
- Error dialogs

**Acceptance Criteria:**
- [ ] All views implemented
- [ ] Navigation works smoothly
- [ ] Data operations functional
- [ ] Alerts display correctly
- [ ] Export works from UI
- [ ] Lock management integrated
- [ ] Manual testing complete

---

## Testing Strategy

### Unit Tests
- Each module function has unit tests
- Mock dependencies for isolation
- Edge cases covered

### Integration Tests
- Test module interactions
- Test database operations
- Test complex queries

### End-to-End Tests
- Test complete workflows (add employee → add CACES → export)
- Test CLI commands
- Test UI flows

### Performance Tests
- Test with 1000+ employees
- Test query performance
- Test export speed

### Time-Dependent Tests
- Use `freezegun` library
- Test expiration calculations
- Test date-based queries

---

## Success Criteria

### Phase Completion Criteria

**Phase 1 (Employee Module):**
- [ ] queries.py: All functions implemented and tested
- [ ] calculations.py: All functions implemented and tested
- [ ] Tests: >80% code coverage
- [ ] Performance: Queries <100ms for 1000 employees

**Phase 2 (Lock Manager):**
- [ ] manager.py: Heartbeat working correctly
- [ ] Tests: Thread safety verified
- [ ] Locks don't go stale when held
- [ ] Stale locks cleaned up automatically

**Phase 3 (Utils):**
- [ ] files.py: All file operations working
- [ ] config.py: Config loading with defaults
- [ ] log.py: Rotating logs working
- [ ] Tests: All scenarios covered

**Phase 4 (Excel Export):**
- [ ] excel.py: All exports working
- [ ] templates.py: All templates defined
- [ ] Tests: Generated files validated
- [ ] Performance: Export 1000 employees <10 seconds

**Phase 5 (Validators):**
- [ ] validators.py: All validators working
- [ ] Integration: Peewee validators functional
- [ ] Tests: Validation rules enforced

**Phase 6 (CLI):**
- [ ] CLI: All commands functional
- [ ] Testing: All features testable via CLI

**Phase 7 (UI):**
- [ ] UI: All views functional
- [ ] Testing: Manual testing complete
- [ ] Performance: Responsive UI

### Project Completion Criteria

**Must Have:**
- [ ] All core modules implemented (Phases 1-5)
- [ ] CLI functional for testing
- [ ] Excel export working
- [ ] Lock manager with heartbeat
- [ ] >80% test coverage
- [ ] Documentation updated

**Should Have:**
- [ ] Flet UI implemented
- [ ] User manual written
- [ ] Installation package created
- [ ] Performance benchmarks

**Nice to Have:**
- [ ] Advanced reporting
- [ ] Data import from Excel
- [ ] Email notifications
- [ ] Automated backups

---

## Timeline Estimates

| Phase | Duration | Dependencies | Completeness |
|-------|----------|--------------|--------------|
| Phase 1: Employee Module | 1-2 weeks | None | +30% |
| Phase 2: Lock Manager | 1 week | Phase 1 | +10% |
| Phase 3: Utils | 1-2 weeks | None | +10% |
| Phase 4: Excel Export | 1-2 weeks | Phase 1, Phase 3 | +15% |
| Phase 5: Validators | 1 week | Phase 1 | +5% |
| Phase 6: CLI | 1 week | Phases 1-5 | +5% |
| Phase 7: UI | 2-3 weeks | Phases 1-6 | +25% |
| **TOTAL** | **6-8 weeks** | | **100%** |

**Core Functionality (Phases 1-4):** 3-4 weeks
**Full Application (Phases 1-6):** 4-5 weeks (CLI-based testing)
**Complete Application (Phases 1-7):** 6-8 weeks (with UI)

---

## Risk Assessment

### Technical Risks

**High Risk:**
- Thread safety in LockManager heartbeat
- Database performance on network share
- Date calculation bugs (leap years, timezones)

**Mitigation:**
- Extensive testing of thread operations
- Database indexing, query optimization, prefetch
- Use `relativedelta`, `freezegun` for time tests

### Schedule Risks

**Potential Delays:**
- Excel export complexity (conditional formatting)
- Flet UI learning curve
- Integration testing time

**Mitigation:**
- Start with simple exports, add formatting later
- Consider simpler UI toolkit if Flet proves difficult
- Allocate buffer time for testing

---

## Next Steps

**Immediate Action (This Week):**
1. Implement `employee/queries.py`
   - Start with get_employees_with_expiring_items()
   - Add prefetch to avoid N+1 queries
   - Write tests

2. Implement `employee/calculations.py`
   - Start with calculate_compliance_score()
   - Add status determination logic
   - Write tests with freezegun

**Success Metrics:**
- All queries return correct results
- Calculations match business rules
- Tests pass with >80% coverage
- Ready for Phase 2 (Lock Manager)

---

## Questions?

For clarifications on implementation details, refer to:
- `docs/MODELS.md` - Model design documentation
- `docs/MODEL_TESTS.md` - Testing strategy
- `docs/PROJECT.md` - Project requirements

**Last Updated:** January 16, 2026
**Maintained By:** Development Team
