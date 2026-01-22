"""Performance monitoring utilities.

This module provides decorators and utilities for monitoring
application performance, including:
- Function execution time tracking
- Database query performance
- Slow operation detection
- Performance statistics aggregation
"""

import functools
import time
from typing import Callable, Optional, Any
from contextlib import contextmanager

from utils.logging_config import log_performance, get_logger


logger = get_logger(__name__)


# Performance thresholds (in milliseconds)
SLOW_QUERY_THRESHOLD = 1000  # 1 second
SLOW_FUNCTION_THRESHOLD = 500  # 500ms
CRITICAL_THRESHOLD = 5000  # 5 seconds


def log_execution_time(
    func_name: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
    threshold_ms: Optional[int] = None,
) -> Callable:
    """
    Decorator to log function execution time.

    Args:
        func_name: Custom function name for logging (default: actual function name)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        threshold_ms: Only log if execution exceeds this threshold (None = always log)

    Example:
        @log_execution_time(threshold_ms=100)
        def slow_function():
            time.sleep(0.2)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            name = func_name or f"{func.__module__}.{func.__name__}"
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                # Check threshold
                if threshold_ms is None or duration_ms >= threshold_ms:
                    context = {}
                    if log_args:
                        context["func_args"] = str(args)[:200]  # Truncate long args
                        context["func_kwargs"] = str(kwargs)[:200]
                    if log_result and 'result' in locals():
                        context["result"] = str(result)[:200]

                    # Determine severity
                    if duration_ms >= CRITICAL_THRESHOLD:
                        log_performance(name, duration_ms, severity="CRITICAL", **context)
                    elif duration_ms >= SLOW_FUNCTION_THRESHOLD:
                        log_performance(name, duration_ms, severity="SLOW", **context)
                    else:
                        log_performance(name, duration_ms, **context)

        return wrapper

    return decorator


def log_db_query(
    query_type: str,
    threshold_ms: int = SLOW_QUERY_THRESHOLD,
) -> Callable:
    """
    Decorator to log database query performance.

    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        threshold_ms: Threshold for slow query detection

    Example:
        @log_db_query("SELECT")
        def get_employees():
            return Employee.select()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                row_count = None

                # Try to get row count for SELECT queries
                if query_type == "SELECT" and hasattr(result, "__len__"):
                    try:
                        row_count = len(result)
                    except Exception:
                        row_count = None

                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                context = {"query_type": query_type}
                if 'row_count' in locals() and row_count is not None:
                    context["row_count"] = row_count

                # Log slow queries with warning
                if duration_ms >= threshold_ms:
                    logger.warning(
                        f"Slow {query_type} query: {func.__name__} took {duration_ms:.2f}ms",
                        extra={"action": "slow_query", "duration_ms": duration_ms, **context},
                    )
                else:
                    log_performance(func.__name__, duration_ms, **context)

        return wrapper

    return decorator


@contextmanager
def performance_context(operation_name: str, **context):
    """
    Context manager for timing arbitrary code blocks.

    Args:
        operation_name: Name of the operation being timed
        **context: Additional context to log

    Example:
        with performance_context("data_processing", record_count=100):
            process_data(data)
    """

    start_time = time.perf_counter()
    try:
        yield
    finally:
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        log_performance(operation_name, duration_ms, **context)


class PerformanceStats:
    """Track performance statistics for operations."""

    def __init__(self, operation_name: str):
        """
        Initialize performance stats tracker.

        Args:
            operation_name: Name of the operation to track
        """
        self.operation_name = operation_name
        self.count = 0
        self.total_duration_ms = 0.0
        self.min_duration_ms = float("inf")
        self.max_duration_ms = 0.0

    def record(self, duration_ms: float):
        """
        Record a performance measurement.

        Args:
            duration_ms: Duration in milliseconds
        """
        self.count += 1
        self.total_duration_ms += duration_ms
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)

    def get_stats(self) -> dict:
        """
        Get performance statistics.

        Returns:
            Dictionary with stats (count, avg, min, max, total)
        """
        if self.count == 0:
            return {
                "operation": self.operation_name,
                "count": 0,
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "total_ms": 0,
            }

        return {
            "operation": self.operation_name,
            "count": self.count,
            "avg_ms": self.total_duration_ms / self.count,
            "min_ms": self.min_duration_ms,
            "max_ms": self.max_duration_ms,
            "total_ms": self.total_duration_ms,
        }

    def log_summary(self):
        """Log performance summary."""
        stats = self.get_stats()
        logger.info(
            f"Performance summary for {self.operation_name}: "
            f"{stats['count']} operations, "
            f"avg {stats['avg_ms']:.2f}ms, "
            f"min {stats['min_ms']:.2f}ms, "
            f"max {stats['max_ms']:.2f}ms",
            extra={"action": "performance_summary", **stats},
        )


def track_performance(operation_name: str) -> PerformanceStats:
    """
    Get or create a performance tracker for an operation.

    Args:
        operation_name: Name of the operation

    Returns:
        PerformanceStats instance
    """
    # Simple in-memory tracking
    # In production, consider using a more robust solution
    if not hasattr(track_performance, "_stats"):
        track_performance._stats = {}

    if operation_name not in track_performance._stats:
        track_performance._stats[operation_name] = PerformanceStats(operation_name)

    return track_performance._stats[operation_name]


def log_all_performance_stats():
    """Log summaries for all tracked operations."""
    if not hasattr(track_performance, "_stats"):
        return

    for stats in track_performance._stats.values():
        if stats.count > 0:
            stats.log_summary()
