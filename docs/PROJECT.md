# PROJECT SPECIFICATIONS: WAREHOUSE EMPLOYEE MANAGEMENT SYSTEM

## 1. Project Purpose

The Warehouse EMS is a specialized desktop application designed to centralize employee administrative data, track safety certifications (CACES), monitor medical compliance, and manage training records. The system is engineered to operate on a shared network environment, providing a single source of truth while ensuring data integrity through controlled write access.

## 2. Technical Stack

- **Project Management:** `uv` for dependency resolution, virtual environment management, and packaging.
- **Language:** Python 3.14+.
- **Database:** SQLite with Write-Ahead Logging (WAL) enabled for optimized network performance.
- **ORM:** Peewee (Micro-ORM) for Object-Oriented data mapping and migration management.
- **Interface:** Flet (Flutter-based GUI for Python) for the desktop application.
- **Excel Integration:** OpenPyXL or XlsxWriter for generating dynamic, formatted reports.

## 3. Data Architecture and Models

The system follows an Object-Oriented Programming (OOP) pattern where each entity is represented by a model class.

### 3.1 Employee Model

- `id`: Internal UUID (Primary Key).
- `external_id`: Manual reference for WMS synchronization.
- `first_name` / `last_name`: Legal identification.
- `current_status`: Enumeration (active, inactive).
- `workspace`: Physical assignment area.
- `role`: Job function.
- `contract_type`: Enumeration (CDI, CDD, Interim, Alternance).
- `entry_date`: Date of hiring.
- `avatar_path`: Reference to local image file.

### 3.2 Certification Models (CACES, Medical, Training)

- **CACES:** Type (kind), completion date, automated expiration date calculation, and link to digital document.
- **MedicalVisit:** Visit type (initial, periodic, recovery), date, expiration date, result (fit, unfit, restricted), and link to digital document.
- **OnlineTraining:** Title, completion date, validity duration, and link to certificate.

### 3.3 System Models

- **AppLock:** Internal locking mechanism with `id`, `hostname`, `locked_at`, and `last_heartbeat` fields for concurrent access control.
- **SchemaMetadata:** Version tracking for database migrations with `version` (INT) and `applied_at` timestamp.

## 4. Concurrency and Network Deployment

The application is designed for deployment on a shared network drive. To prevent database corruption and concurrent write conflicts, the following protocols are mandatory:

### 4.1 Single-Editor Locking Mechanism

- **Locking Logic:** The system implements a database-backed locking mechanism using a dedicated `AppLock` table in SQLite. This approach is more reliable than file-based locks on network shares and prevents race conditions through transactional operations.
- **Heartbeat System:** The active editor writes a heartbeat every 30 seconds to the `last_heartbeat` field. If the heartbeat is older than the configured timeout, the lock is considered stale.
- **Access Control:** Upon startup, the application checks for active locks in the database. If a valid lock exists, the application initializes in Read-Only mode.
- **Session Security:** Users may only enter Edit Mode if no other active lock is detected.
- **Stale Lock Detection:** A lock is considered stale after a configurable period of inactivity (default: 15 minutes, configurable in `config.json`). The system allows a manual override to release stale locks after user confirmation.

### 4.2 Database Integrity

- **WAL Mode:** Write-Ahead Logging is mandatory to allow multiple readers even during a write transaction.
- **Atomic Transactions:** All database operations are wrapped in ACID-compliant transactions to prevent data loss during network instability.

## 5. Functional Requirements

### 5.1 File Management

The system acts as a document repository. When a certificate or document is added:

1.  The file is copied to a standardized local directory within the project structure.
2.  The file is automatically renamed using a standardized convention (e.g., `DOC_TYPE_NAME_DATE.pdf`).
3.  The relative path is stored in the SQLite database to ensure portability.

### 5.2 Alert System

Alerts are triggered based on expiration dates:

- **Application UI:** Visual indicators (color-coded badges) for items expiring within 30, 60, or 90 days.
- **Excel Exports:** Conditional formatting applied to cells to highlight non-compliance or upcoming expirations.

### 5.3 Excel Reporting

Reports are generated on demand. These reports serve as a manual fallback and a snapshot for administrative audits. They must reflect the current state of the database, including calculated status fields.

## 6. Project Structure and Bootstrapping

A bootstrapper utility will be provided to generate a new, empty project instance.

### 6.1 Directory Hierarchy

- `[Project_Name]/`
  - `.venv/` (Managed by `uv`)
  - `data/` (Contains the `.db` file)
  - `documents/` (Subdirectories: `caces/`, `medical/`, `training/`, `avatars/`)
  - `exports/` (Default location for generated Excel files)
  - `logs/` (Application logs with automatic rotation, max 5MB per file, retains last 3 files)
  - `src/` (Source code and binary resources)
  - `config.json` (Thresholds, role definitions, lock timeout, export filename template, and WMS mapping)

### 6.2 Deployment Process

1.  **Generation:** Run the bootstrapper to create the folder structure and initialize the database.
2.  **Configuration:** Define specific roles and alert thresholds in the configuration file.
3.  **Compilation:** The source code is compiled into a standalone executable using **PyInstaller** for distribution on the network drive. No local Python installation is required for end-users.

### 6.3 Build and Distribution

- **Build Tool:** PyInstaller is used to package the application into a single executable.
- **Bootstrapper:** The bootstrapper script is separate from the compiled application and is used only by administrators to create new project instances.
- **Distribution:** The compiled executable is placed in the shared network folder alongside the project structure (data/, documents/, etc.).
- **Updates:** To update the application, replace the executable with the new version. The database and document folders remain intact.

## 7. Configuration File Structure

The `config.json` file contains customizable settings:

```json
{
  "alert_thresholds_days": [30, 60, 90],
  "lock_timeout_minutes": 15,
  "export_filename_template": "employees_export_{date}.xlsx",
  "roles": ["Préparateur", "Réceptionnaire", "Cariste"],
  "workspaces": ["Quai", "Zone A", "Zone B", "Bureau"],
  "log_level": "INFO"
}
```

## 8. Future Enhancements

Potential features considered for future versions:

- **WMS Integration:** Two-way synchronization with external Warehouse Management Systems using the `external_id` field.
- **Multi-User Authentication:** Role-based access control with different permission levels (admin, editor, viewer).
- **REST API:** External API for programmatic access and integration with other tools.
- **Offline Mode:** Local caching with automatic synchronization when network connectivity is restored.
- **Advanced Reporting:** PDF report generation, custom dashboards, and analytics charts.
- **Email Notifications:** Automated email alerts for upcoming expirations and compliance requirements.
- **Document OCR:** Automatic text extraction from uploaded certificates for pre-filling form fields.
