# PHASE 1: DATA MODEL & MIGRATION (DETAILED)

## 📋 OVERVIEW

**Objective**: Add contact information fields (phone, email) to the Employee model and migrate the existing database schema.

**Duration**: 2 hours
**Complexity**: Low
**Dependencies**: Phase 0 complete
**Deliverables**: Updated Employee model, working migration script, validated database changes

---

## 🎯 DETAILED TASKS

### Task 1.1: Update Employee Model

#### 1.1.1. Current Employee Model Analysis

**Location**: `src/employee/models.py`

**Current Structure:**
```python
class Employee(Model):
    # Primary Key
    id = UUIDField(primary_key=True, default=uuid.uuid4)

    # Identification
    external_id = CharField(null=True, index=True, unique=True)
    first_name = CharField()
    last_name = CharField()

    # Employment Status
    current_status = CharField()  # Enum: 'active', 'inactive'
    workspace = CharField()
    role = CharField()
    contract_type = CharField()  # Enum: 'CDI', 'CDD', 'Interim', 'Alternance'

    # Employment Dates
    entry_date = DateField()

    # Optional
    avatar_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
```

**Observation**: The model already has `phone` and `email` fields added (from Phase 0 preparation).

**Verification:**
```python
# Run this to verify
from src.employee.models import Employee
import inspect

# Get all fields
fields = Employee._meta.fields
field_names = [f.name for f in fields]

print("Current Employee fields:")
for name in field_names:
    print(f"  - {name}")

# Check if phone and email exist
assert 'phone' in field_names, "phone field missing"
assert 'email' in field_names, "email field missing"

print("\n[OK] phone and email fields exist")
```

**Expected Output:**
```
Current Employee fields:
  - id
  - external_id
  - first_name
  - last_name
  - current_status
  - workspace
  - role
  - contract_type
  - entry_date
  - avatar_path
  - phone          <-- NEW
  - email          <-- NEW
  - created_at
  - updated_at

[OK] phone and email fields exist
```

#### 1.1.2. Field Specifications

**Phone Field:**
```python
phone = CharField(null=True)
```

**Specifications:**
- **Type**: CharField (string storage)
- **Nullability**: `null=True` (optional, not required)
- **Max Length**: Default (255 chars in Peewee/SQLite)
- **Index**: No (not needed for lookups currently)
- **Unique**: No (multiple employees can share contact info)
- **Validation**: Application-level (format validation in UI)
- **Storage Format**: Free text (allows international formats)

**Rationale for CharField over Integer:**
- Phone numbers can have formats: "06 12 34 56 78", "+33 6 12 34 56 78", "0612345678"
- International formats with country codes
- Extensions: "06 12 34 56 78 ext. 123"
- Leading zeros matter
- Spaces, dashes, parentheses for readability

**Email Field:**
```python
email = CharField(null=True)
```

**Specifications:**
- **Type**: CharField (string storage)
- **Nullability**: `null=True` (optional, not required)
- **Max Length**: Default (255 chars - sufficient for email addresses)
- **Index**: No (not needed for lookups currently)
- **Unique**: No (multiple employees can share email in some cases)
- **Validation**: Application-level (email format validation in UI)
- **Storage Format**: Plain text email address

**Rationale for CharField:**
- Email is fundamentally a string
- Need to preserve exact format (case sensitivity for local part)
- Maximum length of 255 is RFC 5321 compliant (254 chars max for emails)

**Why Both Optional?**
- Not all employees may have contact information
- Historical data may be incomplete
- Some employees might not have company email/phone
- Privacy concerns for some roles

#### 1.1.3. Validation Strategy

**Model-Level Validation:**

Current Employee model has validation hooks:
```python
def before_save(self):
    """Validation logic using Peewee hooks."""
    # ... existing validation ...
```

**Decision: No Database-Level Validation**

**Rationale:**
- Contact info is optional - no strict validation needed at model level
- Format validation happens in UI forms (user-friendly error messages)
- Database stores raw input - flexibility for international formats
- Validation logic stays in presentation layer (forms), not business logic

**UI-Level Validation (Future Phase 3):**

```python
# In forms/employee_form.py (Phase 3)
import re

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format."""
    if not email:
        return (True, "")  # Empty is OK (optional field)

    # Basic email regex (RFC 5322 simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return (True, "")
    else:
        return (False, "Format d'email invalide")

def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone format."""
    if not phone:
        return (True, "")  # Empty is OK (optional field)

    # Remove spaces and common formatting for basic check
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Basic check: 10-15 digits, can start with +
    if re.match(r'^\+?\d{10,15}$', cleaned):
        return (True, "")
    else:
        return (False, "Format de téléphone invalide")
```

#### 1.1.4. Model Method Updates

**No Updates Needed**

**Existing methods remain unchanged:**
- `full_name` property - unchanged
- `seniority` property - unchanged
- `is_active` property - unchanged
- `active()` classmethod - unchanged
- `inactive()` classmethod - unchanged

**Why?**
- New fields are optional metadata
- They don't affect business logic
- No computed properties needed for phone/email
- No queries need to filter by these fields (yet)

**Future Enhancements (Optional V2):**
```python
# NOT implementing in Phase 1, but documenting for future

@classmethod
def by_email(cls, email: str):
    """Get employee by email address."""
    return cls.select().where(cls.email == email)

@classmethod
def by_phone(cls, phone: str):
    """Get employee by phone number."""
    return cls.select().where(cls.phone == phone)

def has_contact_info(self) -> bool:
    """Check if employee has any contact information."""
    return bool(self.email or self.phone)

def get_primary_contact(self) -> str:
    """Get primary contact method (email preferred)."""
    return self.email or self.phone or "No contact info"
```

---

### Task 1.2: Create Migration Script

#### 1.2.1. Migration Strategy Options

**Option A: Peewee Migrate (Recommended)**

**Pros:**
- Peewee-native
- Version control friendly
- Easy to rollback
- Supports multiple databases

**Cons:**
- Requires `peewee-migrate` dependency
- More setup required

**Option B: Manual SQL Script (Chosen for V1)**

**Pros:**
- No additional dependencies
- Simple and direct
- Easy to understand
- Works with Peewee

**Cons:**
- Manual rollback
- Database-specific (SQLite)
- Less sophisticated versioning

**Decision: Use Manual SQL Script for V1**

**Rationale:**
- Simpler for single-table change
- No additional dependencies
- Easy to execute and test
- Can upgrade to Peewee Migrate in V2 if needed

#### 1.2.2. Manual Migration Script

**File**: `scripts/migrate_add_contacts.py`

**Complete Script:**
```python
#!/usr/bin/env python
"""
Manual SQLite migration for adding contact fields to Employee table.

This script adds phone and email columns to the employees table.

Usage:
    python scripts/migrate_add_contacts.py

Rollback:
    python scripts/migrate_add_contacts.py --rollback
"""

import sqlite3
import sys
from pathlib import Path


def migrate(db_path: str, dry_run: bool = False):
    """
    Add phone and email columns to employees table.

    Args:
        db_path: Path to SQLite database file
        dry_run: If True, show SQL without executing
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Start transaction
    cursor.execute("BEGIN TRANSACTION")

    try:
        # Get current schema
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {', '.join(columns)}")

        # Check if phone column exists
        phone_exists = "phone" in columns
        email_exists = "email" in columns

        # Add phone column
        if not phone_exists:
            sql_phone = "ALTER TABLE employees ADD COLUMN phone TEXT"
            if dry_run:
                print(f"\n[DRY RUN] Would execute: {sql_phone}")
            else:
                cursor.execute(sql_phone)
                print("\n[OK] Column 'phone' added")
        else:
            print("\n[SKIP] Column 'phone' already exists")

        # Add email column
        if not email_exists:
            sql_email = "ALTER TABLE employees ADD COLUMN email TEXT"
            if dry_run:
                print(f"[DRY RUN] Would execute: {sql_email}")
            else:
                cursor.execute(sql_email)
                print("[OK] Column 'email' added")
        else:
            print("[SKIP] Column 'email' already exists")

        # Verify new schema
        cursor.execute("PRAGMA table_info(employees)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\nNew columns: {', '.join(new_columns)}")

        # Commit transaction
        if not dry_run:
            conn.commit()
            print("\n[OK] Migration committed successfully")
        else:
            conn.rollback()
            print("\n[OK] Dry run complete (no changes made)")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise

    finally:
        conn.close()


def rollback(db_path: str, dry_run: bool = False):
    """
    Rollback migration by removing phone and email columns.

    WARNING: SQLite doesn't support DROP COLUMN directly.
    This requires recreating the table.

    Args:
        db_path: Path to SQLite database file
        dry_run: If True, show SQL without executing
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Start transaction
    cursor.execute("BEGIN TRANSACTION")

    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]

        phone_exists = "phone" in columns
        email_exists = "email" in columns

        if not phone_exists and not email_exists:
            print("[SKIP] Columns don't exist, nothing to rollback")
            conn.rollback()
            return

        print("\n[WARN] SQLite DROP COLUMN limitation detected")
        print("[INFO] To rollback, you need to:")
        print("  1. Export data excluding phone/email")
        print("  2. Drop the employees table")
        print("  3. Recreate table without phone/email")
        print("  4. Import data back")
        print("\n[RECOMMENDATION] Use database backup instead:")
        print("  1. Restore from: employee_manager.db.backup")
        print("  2. Or use git to revert changes")

        # Show SQL for manual rollback
        print("\n[INFO] Manual rollback SQL (for reference):")

        # Get CREATE TABLE statement
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='employees'")
        create_sql = cursor.fetchone()[0]
        print(f"\nCurrent schema:\n{create_sql}")

        if dry_run:
            print("\n[DRY RUN] Rollback not executed")

        conn.rollback()

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Rollback failed: {e}")
        raise

    finally:
        conn.close()


def backup_database(db_path: str) -> str:
    """
    Create backup of database before migration.

    Args:
        db_path: Path to database file

    Returns:
        Path to backup file
    """
    import shutil
    from datetime import datetime

    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"\n[INFO] Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print(f"[OK] Backup created: {backup_path}")

    return backup_path


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate database: Add phone and email columns")
    parser.add_argument("--db", default="employee_manager.db", help="Path to database file")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL without executing")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration")
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser.add_argument("--no-backup", action="store_true", help="Skip automatic backup")

    args = parser.parse_args()

    db_path = args.db

    # Check if database exists
    if not Path(db_path).exists():
        print(f"[ERROR] Database file not found: {db_path}")
        return 1

    # Create backup unless explicitly skipped
    if not args.no_backup and not args.rollback and not args.dry_run:
        backup_database(db_path)

    # Run migration or rollback
    if args.rollback:
        print("=" * 50)
        print(" ROLLBACK MIGRATION")
        print("=" * 50)
        rollback(db_path, args.dry_run)
    else:
        print("=" * 50)
        print(" MIGRATE DATABASE")
        print("=" * 50)
        migrate(db_path, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

#### 1.2.3. Migration Script Features

**Safe Migration Practices:**

1. **Automatic Backup**
   - Creates timestamped backup before migration
   - Backup format: `employee_manager.db.backup_YYYYMMDD_HHMMSS`
   - Can be disabled with `--no-backup` flag

2. **Idempotent Execution**
   - Checks if columns exist before adding
   - Safe to run multiple times
   - Won't fail if columns already exist

3. **Dry Run Mode**
   - `--dry-run` flag shows SQL without executing
   - Useful for testing and validation
   - No database changes made

4. **Transaction Support**
   - Uses SQLite transactions
   - Automatic rollback on error
   - Data integrity guaranteed

5. **Rollback Support**
   - `--rollback` flag for rollback operations
   - Warns about SQLite limitations
   - Recommends backup restoration

**Usage Examples:**

```bash
# Normal migration with automatic backup
python scripts/migrate_add_contacts.py

# Dry run (show what would be done)
python scripts/migrate_add_contacts.py --dry-run

# Specify custom database path
python scripts/migrate_add_contacts.py --db data/employee_manager.db

# Migration without backup
python scripts/migrate_add_contacts.py --no-backup

# Rollback (manual process explained)
python scripts/migrate_add_contacts.py --rollback
```

#### 1.2.4. Alternative: Peewee Migrate Approach

**For Future Reference (V2)**

If using Peewee Migrate:

```python
# File: src/database/migrations/001_add_employee_contacts.py
"""Migration: Add phone and email to Employee table."""

from peewee import *
from playhouse.migrate import *

# Database connection (from your config)
database = SqliteDatabase('employee_manager.db')
migrator = SqliteMigrator(database)


def upgrade():
    """Add phone and email columns to employees table."""
    migrate(
        migrator.add_column('employees', 'phone', CharField(null=True)),
        migrator.add_column('employees', 'email', CharField(null=True)),
    )


def downgrade():
    """Remove phone and email columns from employees table."""
    migrate(
        migrator.drop_column('employees', 'phone'),
        migrator.drop_column('employees', 'email'),
    )
```

**To use Peewee Migrate:**

```bash
# Install peewee-migrate
pip install peewee-migrate

# Run migration
python -m peewee_migrate migrate --database=employee_manager.db

# Rollback
python -m peewee_migrate rollback --database=employee_manager.db
```

---

### Task 1.3: Test Migration

#### 1.3.1. Test Database Setup

**Create Test Database:**

```python
# File: scripts/create_test_db.py
"""Create a test database for migration testing."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from database.connection import init_database
from employee.models import Employee, Caces, MedicalVisit
from datetime import date

def create_test_database(db_path: str = "test_employee.db"):
    """Create a test database with sample data."""
    # Remove existing test database
    if Path(db_path).exists():
        Path(db_path).unlink()

    # Initialize database
    init_database(Path(db_path))

    # Create sample employees
    employees = [
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "current_status": "active",
            "workspace": "Zone A",
            "role": "Cariste",
            "contract_type": "CDI",
            "entry_date": date(2024, 1, 15),
        },
        {
            "first_name": "Marie",
            "last_name": "Martin",
            "current_status": "active",
            "workspace": "Zone B",
            "role": "Préparateur de commandes",
            "contract_type": "CDD",
            "entry_date": date(2024, 3, 1),
        },
        {
            "first_name": "Pierre",
            "last_name": "Bernard",
            "current_status": "inactive",
            "workspace": "Zone A",
            "role": "Magasinier",
            "contract_type": "Interim",
            "entry_date": date(2023, 6, 15),
        },
    ]

    for emp_data in employees:
        Employee.create(**emp_data)

    print(f"[OK] Test database created: {db_path}")
    print(f"[OK] Created {len(employees)} test employees")

    return db_path

if __name__ == "__main__":
    create_test_database()
```

#### 1.3.2: Migration Test Suite

**File**: `scripts/test_migration.py`

```python
#!/usr/bin/env python
"""Test migration script."""

import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, 'src')

from database.connection import init_database
from employee.models import Employee


def test_migration(db_path: str = "test_employee.db"):
    """Test that migration was successful."""
    print("=" * 50)
    print(" TESTING MIGRATION")
    print("=" * 50)

    # Initialize database
    init_database(Path(db_path))

    # Test 1: Check columns exist
    print("\n[Test 1] Checking columns...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(employees)")
    columns = [row[1] for row in cursor.fetchall()]

    assert "phone" in columns, "Column 'phone' not found"
    assert "email" in columns, "Column 'email' not found"
    print("[OK] Columns 'phone' and 'email' exist")

    conn.close()

    # Test 2: Query employee with Peewee
    print("\n[Test 2] Querying employees...")
    employees = Employee.select()
    count = employees.count()
    print(f"[OK] Queried {count} employees")

    # Test 3: Access phone and email fields
    print("\n[Test 3] Accessing new fields...")
    for emp in employees:
        # Should not raise AttributeError
        _ = emp.phone
        _ = emp.email
    print("[OK] Can access phone and email fields")

    # Test 4: Create employee with contact info
    print("\n[Test 4] Creating employee with contact info...")
    test_emp = Employee.create(
        first_name="Test",
        last_name="User",
        current_status="active",
        workspace="Zone C",
        role="Testeur",
        contract_type="CDI",
        entry_date="2024-01-01",
        phone="06 12 34 56 78",
        email="test@example.com"
    )
    print(f"[OK] Created employee with phone: {test_emp.phone}, email: {test_emp.email}")

    # Test 5: Update employee with contact info
    print("\n[Test 5] Updating employee with contact info...")
    test_emp.phone = "06 98 76 54 32"
    test_emp.email = "updated@example.com"
    test_emp.save()
    test_emp = Employee.get_by_id(test_emp.id)
    assert test_emp.phone == "06 98 76 54 32"
    assert test_emp.email == "updated@example.com"
    print("[OK] Updated phone and email successfully")

    # Test 6: NULL values work
    print("\n[Test 6] Testing NULL values...")
    test_emp.phone = None
    test_emp.email = None
    test_emp.save()
    test_emp = Employee.get_by_id(test_emp.id)
    assert test_emp.phone is None
    assert test_emp.email is None
    print("[OK] NULL values work correctly")

    # Test 7: Query with filters
    print("\n[Test 7] Querying with contact filters...")
    with_phone = Employee.select().where(Employee.phone.is_null(False))
    count_with_phone = with_phone.count()
    print(f"[OK] {count_with_phone} employees with phone")

    with_email = Employee.select().where(Employee.email.is_null(False))
    count_with_email = with_email.count()
    print(f"[OK] {count_with_email} employees with email")

    print("\n" + "=" * 50)
    print(" [OK] ALL MIGRATION TESTS PASSED")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(test_migration())
```

#### 1.3.3. Test Execution Plan

**Pre-Migration Tests:**

```bash
# 1. Create test database
python scripts/create_test_db.py

# 2. Verify test database works
python -c "
import sys
sys.path.insert(0, 'src')
from database.connection import init_database
from employee.models import Employee
from pathlib import Path

init_database(Path('test_employee.db'))
count = Employee.select().count()
print(f'Employees in test DB: {count}')
"

# 3. Backup original database (if exists)
cp employee_manager.db employee_manager.db.backup_original 2>/dev/null || true
```

**Migration Tests:**

```bash
# 4. Dry run migration
python scripts/migrate_add_contacts.py --db test_employee.db --dry-run

# Expected output:
# Current columns: id, external_id, first_name, ...
# [DRY RUN] Would execute: ALTER TABLE employees ADD COLUMN phone TEXT
# [DRY RUN] Would execute: ALTER TABLE employees ADD COLUMN email TEXT

# 5. Actual migration
python scripts/migrate_add_contacts.py --db test_employee.db

# Expected output:
# Current columns: id, external_id, first_name, ...
# [OK] Column 'phone' added
# [OK] Column 'email' added
# New columns: id, ..., phone, email, ...
# [OK] Migration committed successfully
```

**Post-Migration Tests:**

```bash
# 6. Run test suite
python scripts/test_migration.py

# Expected output:
# [Test 1] Checking columns...
# [OK] Columns 'phone' and 'email' exist
# [Test 2] Querying employees...
# [OK] Queried 3 employees
# [Test 3] Accessing new fields...
# [OK] Can access phone and email fields
# ...
# [OK] ALL MIGRATION TESTS PASSED

# 7. Verify idempotency (run migration again)
python scripts/migrate_add_contacts.py --db test_employee.db

# Expected output:
# Current columns: id, ..., phone, email, ...
# [SKIP] Column 'phone' already exists
# [SKIP] Column 'email' already exists
# New columns: id, ..., phone, email, ...
# [OK] Migration committed successfully

# 8. Test rollback strategy
# (Just show the SQL, don't actually rollback)
python scripts/migrate_add_contacts.py --db test_employee.db --rollback --dry-run
```

---

### Task 1.4: Document Migration Process

#### 1.4.1. Migration Documentation

**File**: `docs/MIGRATION_GUIDE.md`

```markdown
# Database Migration Guide

## Adding Phone and Email Fields to Employee Table

This document describes the migration process for adding contact information fields to the employees table.

### What Changed

Two new optional columns added to the `employees` table:
- `phone` (TEXT, NULL) - Employee phone number
- `email` (TEXT, NULL) - Employee email address

### When to Run

Run this migration:
- **Before**: Starting Phase 2 (UI Structure)
- **After**: Completing Phase 0 (Preparation)
- **Prerequisite**: Database backup completed

### Migration Steps

#### 1. Backup Database

**Automatic Backup:**
```bash
python scripts/migrate_add_contacts.py
```
This automatically creates: `employee_manager.db.backup_YYYYMMDD_HHMMSS`

**Manual Backup:**
```bash
cp employee_manager.db employee_manager.db.backup
```

#### 2. Run Migration

**Option A: Automatic Backup + Migration**
```bash
python scripts/migrate_add_contacts.py
```

**Option B: Dry Run First**
```bash
# See what will be done
python scripts/migrate_add_contacts.py --dry-run
# Then run actual migration
python scripts/migrate_add_contacts.py
```

**Option C: Custom Database Path**
```bash
python scripts/migrate_add_contacts.py --db /path/to/database.db
```

#### 3. Verify Migration

**Run Tests:**
```bash
python scripts/test_migration.py
```

**Manual Verification:**
```bash
sqlite3 employee_manager.db
> PRAGMA table_info(employees);
-- Should show phone and email columns

> SELECT COUNT(*) FROM employees;
-- Should return same count as before migration

> .quit
```

### Rollback Process

If migration fails or causes issues:

**Option A: Restore from Backup**
```bash
# List backups
ls -la employee_manager.db.backup_*

# Restore from latest backup
cp employee_manager.db.backup_YYYYMMDD_HHMMSS employee_manager.db
```

**Option B: Use Git (if database is tracked)**
```bash
# Check if database is in git
git ls-files | grep employee_manager.db

# If tracked, restore from git
git checkout HEAD -- employee_manager.db
```

**Option C: Manual Rollback (Not Recommended)**
```bash
# This will explain what to do
python scripts/migrate_add_contacts.py --rollback
```

### Verification Checklist

- [ ] Backup created (automatic or manual)
- [ ] Migration script ran without errors
- [ ] Test suite passes (`python scripts/test_migration.py`)
- [ ] Phone column exists in employees table
- [ ] Email column exists in employees table
- [ ] Existing employee records unaffected
- [ ] Can create new employee with phone/email
- [ ] Can update employee phone/email
- [ ] NULL values work correctly
- [ ] Application still connects to database

### Troubleshooting

**Issue: "Database is locked"**
- **Cause**: Another process has the database open
- **Solution**: Close all applications using the database
- **Command**: Check for open connections: `lsof employee_manager.db` (Linux/Mac) or `handle employee_manager.db` (Windows)

**Issue: "Column already exists"**
- **Cause**: Migration already ran
- **Solution**: This is normal, migration is idempotent
- **Verification**: Check that phone and email columns exist and contain data

**Issue: "No such table: employees"**
- **Cause**: Database not initialized
- **Solution**: Run database initialization first
- **Command**: See database setup documentation

**Issue: "Migration fails with constraint error"**
- **Cause**: Data integrity constraint violated
- **Solution**: Restore from backup and investigate data
- **Command**: Check data quality before re-running migration

### Next Steps

After successful migration:
1. ✅ Verify all tests pass
2. ✅ Test application startup
3. ✅ Create one test employee with contact info
4. ✅ Proceed to Phase 2 (UI Structure)

### References

- SQLite ALTER TABLE: https://www.sqlite.org/lang_altertable.html
- Peewee Documentation: https://docs.peewee-orm.com/
- Project Phase Planning: `docs/DEVELOPMENT_PLAN.md`
```

#### 1.4.2. Update README

**File**: `README.md` (or create `README_MIGRATION.md`)

**Add Migration Section:**

```markdown
## Database Migrations

### Adding Contact Fields (January 2025)

Migration adds `phone` and `email` columns to the `employees` table.

**Status**: ✅ Complete

**How to Migrate:**
```bash
python scripts/migrate_add_contacts.py
```

**For more details**, see: `docs/MIGRATION_GUIDE.md`
```

---

### Task 1.5: Edge Cases & Considerations

#### 1.5.1. Data Integrity

**Existing Data:**

Migration must NOT affect existing employee records:
- Existing employees should have `phone = NULL` and `email = NULL`
- No data loss or corruption
- All existing queries continue to work
- No constraints violated

**Verification:**
```python
# Before migration
before_count = Employee.select().count()

# After migration
after_count = Employee.select().count()

assert before_count == after_count, "Employee count changed!"
```

#### 1.5.2. Concurrent Access

**Lock Manager Consideration:**

The project has a lock manager (`src/lock/models.py`) to prevent concurrent writes.

**Migration Impact:**
- Lock manager unaffected (different table)
- AppLocks table not modified
- Multi-user safety preserved

**Testing Concurrent Access:**
```python
# This should still work after migration
from lock.models import AppLock
from state.app_state import AppState

# Acquire lock
app_state = AppState()
lock_acquired = app_state.lock_manager.acquire_lock(
    "test_user",
    "migration_test"
)

# Do database operation
Employee.select().count()

# Release lock
app_state.lock_manager.release_lock()
```

#### 1.5.3. Performance Impact

**Adding Columns Impact:**

- **Storage**: Minimal (only NULL values initially)
- **Query Speed**: No impact (columns not indexed)
- **Insert Speed**: No significant impact (2 extra fields, optional)
- **Update Speed**: No significant impact (only if phone/email updated)

**Measurement:**
```python
import time

# Measure query time before migration
start = time.time()
employees = Employee.select()
list(employees)  # Force evaluation
before_time = time.time() - start

# After migration
start = time.time()
employees = Employee.select()
list(employees)
after_time = time.time() - start

# Should be roughly the same
diff = abs(after_time - before_time)
assert diff < 0.1, f"Query performance degraded by {diff}s"
```

#### 1.5.4. Backward Compatibility

**Code Compatibility:**

**Old code that doesn't use phone/email:**
```python
# This still works (phone and email are optional/NULL)
emp = Employee.get_by_id(emp_id)
print(emp.full_name)
# No need to access phone or email
```

**New code that uses phone/email:**
```python
# This works in both old and new database
emp = Employee.get_by_id(emp_id)
if hasattr(emp, 'phone'):  # Check if field exists
    print(emp.phone or "No phone")
```

**Forward Compatibility:**
- Phone/email fields can be indexed in future (for search)
- Validation rules can be added in future
- Constraints can be added in future (UNIQUE, NOT NULL)
- Default values can be set (though not recommended)

#### 1.5.5. Application Compatibility

**Existing Controllers:**

**EmployeeController** (`src/controllers/employee_controller.py`):
```python
# These methods don't need changes
def get_employee_by_id(self, emp_id):
    return Employee.get_by_id(emp_id)

def get_employee_details(self, emp_id):
    # Returns Employee object
    # New fields (phone, email) accessible but not required
    return Employee.get_by_id(emp_id)
```

**DashboardController** (`src/controllers/dashboard_controller.py`):
```python
# These methods don't need changes
def get_statistics(self):
    # Returns counts, not affected by new fields
    stats = {
        'total_employees': Employee.select().count(),
        # ... other stats
    }
    return stats
```

**AlertsController** (`src/controllers/alerts_controller.py`):
```python
# These methods don't need changes
def get_alerts(self, alert_type, days):
    # Filters by expiration, not affected by phone/email
    # ...
```

**Conclusion**: All existing controllers remain compatible.

---

### Task 1.6: Validation & Signoff

#### 1.6.1. Pre-Migration Checklist

**Environment:**
- [ ] Python 3.14+ installed
- [ ] All dependencies installed (`uv sync` completed)
- [ ] Database file exists (`employee_manager.db`)
- [ ] Application not running (close all instances)

**Backup:**
- [ ] Automatic backup will be created
- [ ] OR manual backup created: `employee_manager.db.backup`
- [ ] Backup verified (can open and query)

**Code:**
- [ ] Employee model updated with phone/email fields
- [ ] Migration script created (`scripts/migrate_add_contacts.py`)
- [ ] Test script created (`scripts/test_migration.py`)
- [ ] Documentation created (`docs/MIGRATION_GUIDE.md`)

**Testing:**
- [ ] Test database created and works
- [ ] Migration tested on test database
- [ ] All migration tests pass
- [ ] Rollback procedure tested

---

#### 1.6.2. Post-Migration Checklist

**Migration Success:**
- [ ] Migration script ran without errors
- [ ] Backup created successfully
- [ ] Phone column exists in database
- [ ] Email column exists in database
- [ ] Existing employee records unchanged
- [ ] Employee count matches pre-migration count

**Functionality:**
- [ ] Can create employee with phone
- [ ] Can create employee with email
- [ ] Can create employee without phone/email
- [ ] Can update employee phone
- [ ] Can update employee email
- [ ] Can set phone/email to NULL
- [ ] Can query employees with phone filter
- [ ] Can query employees with email filter

**Application:**
- [ ] Application starts without errors
- [ ] Can connect to database
- [ ] Can query employees
- [ ] Can create new employee
- [ ] Can update existing employee
- [ ] Lock manager still works
- [ ] All existing features work

**Testing:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Migration test suite passes
- [ ] Manual testing completed

---

#### 1.6.3. Signoff Criteria

**Migration is complete when:**

1. ✅ **Database Schema Updated**
   - `employees` table has `phone` column
   - `employees` table has `email` column
   - Columns are TEXT type and nullable
   - No constraints violated

2. ✅ **Data Integrity Preserved**
   - All existing employees intact
   - Employee count unchanged
   - No data corruption
   - All existing queries work

3. ✅ **Application Compatibility**
   - Application connects to database
   - All controllers work
   - All existing features work
   - No breaking changes

4. ✅ **Testing Complete**
   - Migration script tested
   - Rollback procedure tested
   - Test suite passes
   - Manual testing successful

5. ✅ **Documentation Complete**
   - Migration guide created
   - README updated
   - Troubleshooting guide written
   - Changelog updated

---

## 📊 PHASE 1 SUMMARY

### Tasks Completed Checklist

- [x] 1.1.1: Current Employee model analyzed
- [x] 1.1.2: Field specifications defined
- [x] 1.1.3: Validation strategy documented
- [x] 1.1.4: Model method updates reviewed
- [x] 1.2.1: Migration strategy evaluated
- [x] 1.2.2: Manual migration script designed
- [x] 1.2.3: Migration script features defined
- [x] 1.2.4: Peewee migrate alternative documented
- [x] 1.3.1: Test database setup planned
- [x] 1.3.2: Migration test suite designed
- [x] 1.3.3: Test execution plan documented
- [x] 1.4.1: Migration documentation planned
- [x] 1.4.2: README updates planned
- [x] 1.5.1: Data integrity considerations documented
- [x] 1.5.2: Concurrent access impact analyzed
- [x] 1.5.3: Performance impact analyzed
- [x] 1.5.4: Backward compatibility verified
- [x] 1.5.5: Application compatibility verified
- [x] 1.6.1: Pre-migration checklist created
- [x] 1.6.2: Post-migration checklist created
- [x] 1.6.3: Signoff criteria defined

### Deliverables

1. **Migration Script** (`scripts/migrate_add_contacts.py`)
   - Adds phone and email columns
   - Automatic backup creation
   - Idempotent execution
   - Dry run mode
   - Rollback guidance

2. **Test Script** (`scripts/test_migration.py`)
   - 7 comprehensive tests
   - Validates all functionality
   - Tests edge cases
   - Verifies data integrity

3. **Test Database Setup** (`scripts/create_test_db.py`)
   - Creates test database
   - Populates sample data
   - Isolated from production

4. **Documentation** (`docs/MIGRATION_GUIDE.md`)
   - Step-by-step instructions
   - Troubleshooting guide
   - Rollback procedures
   - Verification checklist

### Time Estimate: 2 Hours

| Task | Duration |
|------|----------|
| Review Employee model | 15 min |
| Create migration script | 30 min |
| Create test scripts | 30 min |
| Test migration | 30 min |
| Document process | 20 min |
| Validation & signoff | 15 min |
| **Total** | **2 hours** |

---

## 🚀 NEXT STEPS (Phase 2)

Once Phase 1 is validated and complete:

1. **Verify database migration** on production database
2. **Test all existing functionality** still works
3. **Create test employee** with contact information
4. **Proceed to Phase 2** (UI Structure)

**Proceed to Phase 2 when all Phase 1 tasks are complete and validated.**
