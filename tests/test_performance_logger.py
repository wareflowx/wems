"""Tests for performance logging module."""

import time
import pytest
from unittest.mock import patch

from utils.performance_logger import (
    log_execution_time,
    log_db_query,
    performance_context,
    PerformanceStats,
    track_performance,
    log_all_performance_stats,
    SLOW_QUERY_THRESHOLD,
    SLOW_FUNCTION_THRESHOLD,
    CRITICAL_THRESHOLD,
)


class TestLogExecutionTime:
    """Tests for log_execution_time decorator."""

    def test_log_execution_time_fast_function(self, caplog):
        """Test logging a fast function."""

        @log_execution_time()
        def fast_function():
            return "result"

        with caplog.at_level(logging.INFO):
            result = fast_function()
            assert result == "result"
            assert len(caplog.records) > 0

    def test_log_execution_time_slow_function(self, caplog):
        """Test logging a slow function."""

        @log_execution_time(threshold_ms=10)
        def slow_function():
            time.sleep(0.02)  # 20ms
            return "result"

        with caplog.at_level(logging.INFO):
            result = slow_function()
            assert result == "result"
            # Should only log because it exceeds threshold
            assert len(caplog.records) > 0

    def test_log_execution_time_below_threshold(self):
        """Test that functions below threshold are not logged."""

        @log_execution_time(threshold_ms=1000)
        def fast_function():
            return "result"

        # This should not trigger logging (too fast)
        result = fast_function()
        assert result == "result"

    def test_log_execution_time_with_args(self, caplog):
        """Test logging with function arguments."""

        @log_execution_time(log_args=True)
        def function_with_args(a, b, c=None):
            return a + b

        with caplog.at_level(logging.INFO):
            result = function_with_args(1, 2, c=3)
            assert result == 3

    def test_log_execution_time_custom_name(self, caplog):
        """Test logging with custom function name."""

        @log_execution_time(func_name="custom_name")
        def original_name():
            pass

        with caplog.at_level(logging.INFO):
            original_name()
            # Check that custom name was used
            assert any("custom_name" in record.message for record in caplog.records)

    def test_log_execution_time_exception_handling(self):
        """Test that timing works even if function raises exception."""

        @log_execution_time()
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()


class TestLogDbQuery:
    """Tests for log_db_query decorator."""

    def test_log_db_query_select(self, caplog):
        """Test logging SELECT query."""

        @log_db_query("SELECT")
        def mock_query():
            time.sleep(0.001)
            return [1, 2, 3]  # Mock 3 rows

        with caplog.at_level(logging.INFO):
            result = mock_query()
            assert result == [1, 2, 3]
            assert len(caplog.records) > 0

    def test_log_db_query_slow_query(self, caplog):
        """Test logging slow query detection."""

        @log_db_query("SELECT", threshold_ms=10)
        def slow_query():
            time.sleep(0.02)  # 20ms
            return [1, 2, 3]

        with caplog.at_level(logging.WARNING):
            result = slow_query()
            assert result == [1, 2, 3]
            # Should log as WARNING for slow query
            assert any("Slow" in record.message for record in caplog.records)

    def test_log_db_query_insert(self):
        """Test logging INSERT query."""

        @log_db_query("INSERT")
        def mock_insert():
            time.sleep(0.001)
            return 1  # Mock rows affected

        result = mock_insert()
        assert result == 1

    def test_log_db_query_empty_result(self):
        """Test logging query that returns no rows."""

        @log_db_query("SELECT")
        def empty_query():
            return []

        result = empty_query()
        assert result == []


class TestPerformanceContext:
    """Tests for performance_context context manager."""

    def test_performance_context(self, caplog):
        """Test timing code block with context manager."""

        with caplog.at_level(logging.INFO):
            with performance_context("test_operation"):
                time.sleep(0.001)

            assert len(caplog.records) > 0
            assert any("test_operation" in record.message for record in caplog.records)

    def test_performance_context_with_context(self, caplog):
        """Test context manager with additional context."""

        with caplog.at_level(logging.INFO):
            with performance_context("data_processing", record_count=100):
                pass

            # Check that operation was logged
            assert len(caplog.records) > 0
            assert any("data_processing" in record.message for record in caplog.records)

    def test_performance_context_exception(self):
        """Test that timing works even if exception raised."""

        with pytest.raises(ValueError):
            with performance_context("failing_operation"):
                time.sleep(0.001)
                raise ValueError("Test error")


class TestPerformanceStats:
    """Tests for PerformanceStats class."""

    def test_performance_stats_initialization(self):
        """Test stats initialization."""
        stats = PerformanceStats("test_operation")
        assert stats.operation_name == "test_operation"
        assert stats.count == 0
        assert stats.total_duration_ms == 0.0

    def test_performance_stats_record(self):
        """Test recording performance measurements."""
        stats = PerformanceStats("test_operation")
        stats.record(100.0)
        stats.record(200.0)
        stats.record(300.0)

        assert stats.count == 3
        assert stats.total_duration_ms == 600.0
        assert stats.min_duration_ms == 100.0
        assert stats.max_duration_ms == 300.0

    def test_performance_stats_get_stats(self):
        """Test getting statistics dictionary."""
        stats = PerformanceStats("test_operation")
        stats.record(100.0)
        stats.record(200.0)

        stat_dict = stats.get_stats()
        assert stat_dict["operation"] == "test_operation"
        assert stat_dict["count"] == 2
        assert stat_dict["avg_ms"] == 150.0
        assert stat_dict["min_ms"] == 100.0
        assert stat_dict["max_ms"] == 200.0
        assert stat_dict["total_ms"] == 300.0

    def test_performance_stats_empty(self):
        """Test stats when no measurements recorded."""
        stats = PerformanceStats("test_operation")
        stat_dict = stats.get_stats()

        assert stat_dict["count"] == 0
        assert stat_dict["avg_ms"] == 0
        assert stat_dict["min_ms"] == 0
        assert stat_dict["max_ms"] == 0

    def test_performance_stats_log_summary(self, caplog):
        """Test logging performance summary."""

        stats = PerformanceStats("test_operation")
        stats.record(100.0)
        stats.record(200.0)

        with caplog.at_level(logging.INFO):
            stats.log_summary()
            assert len(caplog.records) > 0
            assert any("Performance summary" in record.message for record in caplog.records)


class TestTrackPerformance:
    """Tests for performance tracking utilities."""

    def test_track_performance(self):
        """Test getting or creating performance tracker."""
        stats1 = track_performance("operation1")
        stats2 = track_performance("operation1")
        stats3 = track_performance("operation2")

        # Should return same instance for same operation
        assert stats1 is stats2
        assert stats1 is not stats3

    def test_track_performance_record(self):
        """Test recording to tracked performance."""
        stats = track_performance("new_operation")
        stats.record(150.0)

        stat_dict = stats.get_stats()
        assert stat_dict["count"] == 1
        assert stat_dict["total_ms"] == 150.0

    def test_log_all_performance_stats(self, caplog):
        """Test logging all performance statistics."""
        stats1 = track_performance("op1")
        stats1.record(100.0)
        stats1.record(200.0)

        stats2 = track_performance("op2")
        stats2.record(50.0)

        with caplog.at_level(logging.INFO):
            log_all_performance_stats()
            # Should log summaries for both operations
            assert len(caplog.records) >= 2


# Test thresholds
def test_thresholds():
    """Test that threshold constants are set correctly."""
    assert SLOW_QUERY_THRESHOLD == 1000
    assert SLOW_FUNCTION_THRESHOLD == 500
    assert CRITICAL_THRESHOLD == 5000


# Import logging for caplog
import logging
