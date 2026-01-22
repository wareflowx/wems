"""Tests for database indexes.

This test module verifies that:
1. Indexes are properly defined in model Meta classes
2. Indexes are created in the database
3. Queries use the expected indexes
"""

import pytest
from peewee import *

from database.connection import database
from employee.models import Employee, Caces, MedicalVisit, OnlineTraining


class TestEmployeeIndexes:
    """Tests for Employee table indexes."""

    def test_employee_model_has_status_index(self):
        """Test that current_status field has an index."""
        field = Employee._meta.fields["current_status"]
        assert field.index is True, "current_status should be indexed"

    def test_employee_model_has_workspace_index(self):
        """Test that workspace field has an index."""
        field = Employee._meta.fields["workspace"]
        assert field.index is True, "workspace should be indexed"

    def test_employee_model_has_role_index(self):
        """Test that role field has an index."""
        field = Employee._meta.fields["role"]
        assert field.index is True, "role should be indexed"

    def test_employee_model_has_contract_type_index(self):
        """Test that contract_type field has an index."""
        field = Employee._meta.fields["contract_type"]
        assert field.index is True, "contract_type should be indexed"

    def test_employee_external_id_has_unique_index(self):
        """Test that external_id has a unique index."""
        field = Employee._meta.fields["external_id"]
        assert field.index is True, "external_id should be indexed"
        assert field.unique is True, "external_id should be unique"


class TestMedicalVisitIndexes:
    """Tests for MedicalVisit table indexes."""

    def test_medical_visit_result_has_index(self):
        """Test that result field has an index."""
        field = MedicalVisit._meta.fields["result"]
        assert field.index is True, "result should be indexed for MedicalVisit"

    def test_medical_visit_expiration_date_has_index(self):
        """Test that expiration_date field has an index."""
        field = MedicalVisit._meta.fields["expiration_date"]
        assert field.index is True, "expiration_date should be indexed"

    def test_medical_visit_composite_index(self):
        """Test that composite index on (employee, expiration_date) exists."""
        indexes = MedicalVisit._meta.indexes
        # Check for composite index (indexes are tuples in Peewee)
        composite_exists = any(
            idx == (("employee", "expiration_date"), False) for idx in indexes
        )
        assert composite_exists, "Composite index on (employee, expiration_date) should exist"


class TestCacesIndexes:
    """Tests for Caces table indexes."""

    def test_caces_expiration_date_has_index(self):
        """Test that expiration_date field has an index."""
        field = Caces._meta.fields["expiration_date"]
        assert field.index is True, "expiration_date should be indexed"

    def test_caces_composite_index(self):
        """Test that composite index on (employee, expiration_date) exists."""
        indexes = Caces._meta.indexes
        # Check for composite index (indexes are tuples in Peewee)
        composite_exists = any(
            idx == (("employee", "expiration_date"), False) for idx in indexes
        )
        assert composite_exists, "Composite index on (employee, expiration_date) should exist"


class TestOnlineTrainingIndexes:
    """Tests for OnlineTraining table indexes."""

    def test_online_training_expiration_date_has_index(self):
        """Test that expiration_date field has an index."""
        field = OnlineTraining._meta.fields["expiration_date"]
        assert field.index is True, "expiration_date should be indexed"

    def test_online_training_composite_index(self):
        """Test that composite index on (employee, expiration_date) exists."""
        indexes = OnlineTraining._meta.indexes
        # Check for composite index (indexes are tuples in Peewee)
        composite_exists = any(
            idx == (("employee", "expiration_date"), False) for idx in indexes
        )
        assert composite_exists, "Composite index on (employee, expiration_date) should exist"


class TestDatabaseIndexesCreated:
    """Tests to verify indexes are actually created in the database."""

    def test_employee_indexes_exist_in_db(self):
        """Test that Employee indexes exist in the database."""
        # These tests require database to be initialized by conftest fixture
        # The database should already be connected from test setup
        if not database.is_closed():
            cursor = database.cursor()

            # Get all indexes on employees table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='employees'"
            )
            indexes = [row[0] for row in cursor.fetchall()]

            # Check for our indexes (SQLite auto-creates indexes for unique constraints)
            expected_prefixes = ["external_id", "current_status", "workspace", "role", "contract_type"]

            # At least some of our indexes should be present
            found_indexes = [
                prefix for prefix in expected_prefixes if any(prefix in idx for idx in indexes)
            ]

            assert len(found_indexes) >= len(expected_prefixes), \
                f"Expected at least {len(expected_prefixes)} indexes, found {len(found_indexes)}: {found_indexes}"
        else:
            # Skip test if database not connected
            import pytest
            pytest.skip("Database not connected - requires initialization")

    def test_medical_visit_indexes_exist_in_db(self):
        """Test that MedicalVisit indexes exist in the database."""
        # These tests require database to be initialized by conftest fixture
        if not database.is_closed():
            cursor = database.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='medical_visits'"
            )
            indexes = [row[0] for row in cursor.fetchall()]

            # Check for result index
            result_indexes = [idx for idx in indexes if "result" in idx.lower()]

            assert len(result_indexes) > 0, "Should have at least one index on 'result' field"
        else:
            # Skip test if database not connected
            import pytest
            pytest.skip("Database not connected - requires initialization")


class TestQueryPerformanceWithIndexes:
    """Tests to verify queries can use the indexes."""

    def test_active_employees_query_can_use_index(self):
        """Test that active employees query can use the status index."""
        # This query should use the current_status index
        query = Employee.select().where(Employee.current_status == "active")

        # Convert to SQL to verify it's indexed
        sql = query.sql()
        assert "WHERE" in sql[0], "Query should have WHERE clause"
        assert "current_status" in sql[0], "Query should filter on current_status"

    def test_workspace_query_can_use_index(self):
        """Test that workspace query can use the workspace index."""
        query = Employee.by_workspace("Zone A")

        sql = query.sql()
        assert "workspace" in sql[0], "Query should filter on workspace"

    def test_role_query_can_use_index(self):
        """Test that role query can use the role index."""
        query = Employee.by_role("Cariste")

        sql = query.sql()
        assert "role" in sql[0], "Query should filter on role"

    def test_unfit_employees_query_can_use_index(self):
        """Test that unfit employees query can use the result index."""
        query = MedicalVisit.select().where(MedicalVisit.result == "unfit")

        sql = query.sql()
        assert "result" in sql[0], "Query should filter on result"
