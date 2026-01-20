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

---

## Migration Steps

### 1. Backup Database

**Automatic Backup:**
```bash
python scripts/migrate_add_contacts.py
```
This automatically creates: `employee_manager.db.backup_YYYYMMDD_HHMMSS`

**Manual Backup:**
```bash
cp employee_manager.db employee_manager.db.backup
```

### 2. Run Migration

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

### 3. Verify Migration

**Run Tests:**
```bash
# Create test database
python scripts/create_test_db.py

# Run migration tests
python scripts/test_migration.py
```

**Manual Verification:**
```bash
sqlite3 employee_manager.db

> PRAGMA table_info(employees);
-- Should show phone and email columns at the end

> SELECT COUNT(*) FROM employees;
-- Should return same count as before migration

> SELECT first_name, last_name, phone, email FROM employees LIMIT 3;
-- Should show employee data with phone/email (may be NULL)

> .quit
```

---

## Rollback Process

If migration fails or causes issues:

### Option A: Restore from Backup

**List Backups:**
```bash
ls -la employee_manager.db.backup_*
```

**Restore Latest Backup:**
```bash
cp employee_manager.db.backup_YYYYMMDD_HHMMSS employee_manager.db
```

### Option B: Use Git (If Database is Tracked)

```bash
# Check if database is in git
git ls-files | grep employee_manager.db

# If tracked, restore from git
git checkout HEAD -- employee_manager.db
```

### Option C: Manual Rollback (Not Recommended)

```bash
# This will explain what to do
python scripts/migrate_add_contacts.py --rollback
```

**Note:** SQLite doesn't support DROP COLUMN directly. You would need to:
1. Export data excluding phone/email
2. Drop the employees table
3. Recreate table without phone/email
4. Import data back

**Recommendation:** Use backup restoration instead.

---

## Verification Checklist

Use this checklist to verify migration success:

### Pre-Migration
- [ ] Backup created (automatic or manual)
- [ ] Backup file exists and is readable
- [ ] Application not running
- [ ] Migration script reviewed

### Post-Migration
- [ ] Migration script ran without errors
- [ ] Phone column exists in employees table
- [ ] Email column exists in employees table
- [ ] Existing employee records unaffected
- [ ] Employee count matches pre-migration count
- [ ] Can create new employee with phone/email
- [ ] Can update employee phone/email
- [ ] Can set phone/email to NULL
- [ ] Application still connects to database
- [ ] All existing features work

### Testing
- [ ] Migration test suite passes
- [ ] Manual verification successful
- [ ] Application starts without errors
- [ ] Can query employees
- [ ] Can create new employee
- [ ] Can update existing employee

---

## Troubleshooting

### Issue: "Database is locked"

**Cause:** Another process has the database open

**Solution:** Close all applications using the database

**Windows:**
```powershell
# Check for open connections
Get-Process | Where-Object {$_.Path -like "*employee_manager*"}
```

**Linux/Mac:**
```bash
lsof employee_manager.db
```

### Issue: "Column already exists"

**Cause:** Migration already ran

**Solution:** This is normal, migration is idempotent (safe to run multiple times)

**Verification:** Check that phone and email columns exist and contain data

### Issue: "No such table: employees"

**Cause:** Database not initialized

**Solution:** Run database initialization first

**Command:**
```bash
python -c "
import sys
sys.path.insert(0, 'src')
from database.connection import init_database
from pathlib import Path
init_database(Path('employee_manager.db'))
print('Database initialized')
"
```

### Issue: "Migration fails with constraint error"

**Cause:** Data integrity constraint violated

**Solution:** Restore from backup and investigate data

**Command:**
```bash
# Restore backup
cp employee_manager.db.backup_YYYYMMDD_HHMMSS employee_manager.db

# Check data
python -c "
import sys
sys.path.insert(0, 'src')
from employee.models import Employee
from database.connection import init_database
from pathlib import Path

init_database(Path('employee_manager.db'))
for emp in Employee.select():
    print(f'{emp.full_name}: status={emp.current_status}')
"
```

---

## Migration Script Options

### Command-Line Arguments

```
--db PATH          Path to database file (default: employee_manager.db)
--dry-run          Show SQL without executing
--rollback         Show rollback instructions
--backup           Create backup before migration (default)
--no-backup        Skip automatic backup
```

### Examples

**Dry run to see what will happen:**
```bash
python scripts/migrate_add_contacts.py --dry-run
```

**Migrate custom database:**
```bash
python scripts/migrate_add_contacts.py --db /path/to/database.db
```

**Migrate without backup:**
```bash
python scripts/migrate_add_contacts.py --no-backup
```

**Show rollback instructions:**
```bash
python scripts/migrate_add_contacts.py --rollback
```

---

## Testing Migration

### Create Test Database

```bash
python scripts/create_test_db.py
```

This creates `test_employee.db` with 3 sample employees.

### Run Migration on Test Database

```bash
# Dry run first
python scripts/migrate_add_contacts.py --db test_employee.db --dry-run

# Actual migration
python scripts/migrate_add_contacts.py --db test_employee.db
```

### Run Test Suite

```bash
python scripts/test_migration.py --db test_employee.db
```

Expected output:
```
==================================================
 TESTING MIGRATION
==================================================

[Test 1] Checking columns...
[OK] Columns 'phone' and 'email' exist

[Test 2] Querying employees...
[OK] Queried 3 employees

[Test 3] Accessing new fields...
[OK] Can access phone and email fields

[Test 4] Creating employee with contact info...
[OK] Created employee with phone: 06 12 34 56 78, email: test@example.com

[Test 5] Updating employee with contact info...
[OK] Updated phone and email successfully

[Test 6] Testing NULL values...
[OK] NULL values work correctly

[Test 7] Querying with contact filters...
[OK] 1 employees with phone
[OK] 1 employees with email

==================================================
 [OK] ALL MIGRATION TESTS PASSED
==================================================
```

---

## Data Schema

### Before Migration

```
CREATE TABLE employees (
    id TEXT PRIMARY KEY,
    external_id TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    current_status TEXT NOT NULL,
    workspace TEXT NOT NULL,
    role TEXT NOT NULL,
    contract_type TEXT NOT NULL,
    entry_date DATE NOT NULL,
    avatar_path TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### After Migration

```
CREATE TABLE employees (
    id TEXT PRIMARY KEY,
    external_id TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    current_status TEXT NOT NULL,
    workspace TEXT NOT NULL,
    role TEXT NOT NULL,
    contract_type TEXT NOT NULL,
    entry_date DATE NOT NULL,
    avatar_path TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    phone TEXT,              -- NEW COLUMN
    email TEXT               -- NEW COLUMN
);
```

---

## Impact Assessment

### Application Compatibility

**No Changes Required:**
- Employee model works with new fields
- All existing controllers work
- Lock manager unaffected
- All queries work as before

**New Capabilities:**
- Can store phone numbers
- Can store email addresses
- Can query by contact info (future feature)
- Can display contact info in UI (Phase 3+)

### Performance

**Storage:** Minimal impact (only NULL values initially)

**Query Speed:** No impact (columns not indexed)

**Insert Speed:** Negligible impact (2 optional fields)

**Update Speed:** Negligible impact (only when contact info updated)

---

## Next Steps

After successful migration:

1. ✅ Verify all tests pass
2. ✅ Test application startup
3. ✅ Create one test employee with contact info
4. ✅ Proceed to Phase 2 (UI Structure)

### For UI Development (Phase 3+)

The phone and email fields will be used in:
- Employee detail view
- Employee edit form
- Contact information display

---

## References

- **SQLite ALTER TABLE**: https://www.sqlite.org/lang_altertable.html
- **Peewee Documentation**: https://docs.peewee-orm.com/
- **Project Phase Planning**: `docs/DEVELOPMENT_PLAN.md`
- **Phase 1 Detail**: `docs/PHASE_1_DETAILED.md`

---

## Support

If you encounter issues not covered in this guide:

1. Check troubleshooting section above
2. Review Phase 1 detailed documentation
3. Run test suite to diagnose problem
4. Restore from backup if needed

**Last Updated:** January 2025
**Migration Version:** 1.0 (Add phone and email fields)
