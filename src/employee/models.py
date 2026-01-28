"""Employee data models using Peewee ORM."""

import uuid
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from peewee import (
    AutoField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
    UUIDField,
)

from database.connection import database
from employee.constants import (
    CACES_VALIDITY_YEARS,
    CONTRACT_EXPIRATION_CRITICAL_DAYS,
    CONTRACT_EXPIRATION_WARNING_DAYS,
    TRIAL_PERIOD_WARNING_DAYS,
    VISIT_VALIDITY_YEARS,
    EmployeeStatus,
)


class Employee(Model):
    """Core employee entity with business logic."""

    # Primary Key - UUIDField is native in Peewee
    # In SQLite/MySQL it's stored as VARCHAR, in Postgres as native UUID
    id = UUIDField(primary_key=True, default=uuid.uuid4)

    # Identification
    external_id = CharField(null=True, index=True, unique=True)  # WMS reference
    first_name = CharField()
    last_name = CharField()

    # Employment Status
    current_status = CharField(index=True)  # Enum: 'active', 'inactive'
    workspace = CharField(index=True)
    role = CharField(index=True)
    contract_type = CharField(index=True)  # Enum: 'CDI', 'CDD', 'Interim', 'Alternance'

    # Employment Dates
    entry_date = DateField()

    # Optional
    avatar_path = CharField(null=True)

    # Contact Information
    phone = CharField(null=True)
    email = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    # Soft Delete
    deleted_at = DateTimeField(null=True, index=True)
    deleted_by = CharField(null=True)  # Username who deleted (when auth is added)
    deletion_reason = TextField(null=True)

    class Meta:
        database = database
        table_name = "employees"

    # ========== COMPUTED PROPERTIES ==========

    @property
    def full_name(self) -> str:
        """Complete employee name for display."""
        return f"{self.first_name} {self.last_name}"

    @property
    def seniority(self) -> int:
        """Complete years of service."""
        # Ensure entry_date is a date object (not datetime)
        if isinstance(self.entry_date, datetime):
            entry_date = self.entry_date.date()
        else:
            entry_date = self.entry_date
        return (date.today() - entry_date).days // 365

    @property
    def is_active(self) -> bool:
        """Convenience boolean for active status."""
        return self.current_status == EmployeeStatus.ACTIVE

    @property
    def is_deleted(self) -> bool:
        """Check if employee is soft-deleted."""
        return self.deleted_at is not None

    # ========== CLASS METHODS (QUERIES) ==========

    @classmethod
    def without_deleted(cls):
        """Get all employees excluding soft-deleted ones."""
        return cls.select().where(cls.deleted_at.is_null(True))

    @classmethod
    def deleted(cls):
        """Get all soft-deleted employees."""
        return cls.select().where(cls.deleted_at.is_null(False))

    @classmethod
    def active(cls):
        """Get all active employees."""
        return cls.select().where(cls.current_status == EmployeeStatus.ACTIVE)

    @classmethod
    def inactive(cls):
        """Get all inactive employees."""
        return cls.select().where(cls.current_status == EmployeeStatus.INACTIVE)

    @classmethod
    def by_workspace(cls, workspace: str):
        """Get employees by workspace assignment."""
        return cls.select().where(cls.workspace == workspace)

    @classmethod
    def by_role(cls, role: str):
        """Get employees by job role."""
        return cls.select().where(cls.role == role)

    @classmethod
    def by_contract_type(cls, contract_type: str):
        """Get employees by contract type."""
        return cls.select().where(cls.contract_type == contract_type)

    # Note: Complex multi-table queries like with_expiring_certifications
    # will be implemented in employee/queries.py to avoid circular imports

    # ========== INSTANCE METHODS ==========

    def soft_delete(self, reason: str = None, deleted_by: str = None):
        """
        Mark employee as deleted (soft delete).

        Args:
            reason: Optional reason for deletion
            deleted_by: Optional username who performed the deletion
        """
        self.deleted_at = datetime.now()
        self.deletion_reason = reason
        self.deleted_by = deleted_by
        self.save(only=[Employee.deleted_at, Employee.deletion_reason, Employee.deleted_by])

    def restore(self):
        """Restore a soft-deleted employee."""
        self.deleted_at = None
        self.deletion_reason = None
        self.deleted_by = None
        self.save(only=[Employee.deleted_at, Employee.deletion_reason, Employee.deleted_by])

    def add_caces(self, kind: str, completion_date: date, document_path: str):
        """Create a CACES certification for this employee."""
        return Caces.create(employee=self, kind=kind, completion_date=completion_date, document_path=document_path)

    def add_medical_visit(self, visit_type: str, visit_date: date, result: str, document_path: str):
        """Create a medical visit record for this employee."""
        return MedicalVisit.create(
            employee=self, visit_type=visit_type, visit_date=visit_date, result=result, document_path=document_path
        )

    def add_training(self, title: str, completion_date: date, validity_months: int, certificate_path: str):
        """Create an online training record for this employee."""
        return OnlineTraining.create(
            employee=self,
            title=title,
            completion_date=completion_date,
            validity_months=validity_months,
            certificate_path=certificate_path,
        )

    # ========== HOOKS ==========

    def before_save(self):
        """Validation logic using Peewee hooks."""
        from .validators import (
            UniqueValidator,
            validate_entry_date,
            validate_external_id,
        )
        from .validators import (
            ValidationError as ModelValidationError,
        )

        # Validate external_id format if provided
        if self.external_id:
            try:
                self.external_id = validate_external_id(self.external_id)
            except ModelValidationError as e:
                # Convert to ValueError for Peewee compatibility
                raise ValueError(str(e))

            # Check uniqueness (only if external_id has changed or is new)
            if self.id:
                # Update: exclude current instance
                validator = UniqueValidator(Employee, Employee.external_id, exclude_instance=self)
                try:
                    validator.validate(self.external_id)
                except ModelValidationError as e:
                    raise ValueError(str(e))
            else:
                # New record: check all records
                validator = UniqueValidator(Employee, Employee.external_id)
                try:
                    validator.validate(self.external_id)
                except ModelValidationError as e:
                    raise ValueError(str(e))

        # Validate entry_date
        if self.entry_date:
            try:
                self.entry_date = validate_entry_date(self.entry_date)
            except ModelValidationError as e:
                raise ValueError(str(e))

    def save(self, force_insert=False, only=None):
        """Override save to update updated_at timestamp and validate."""
        self.before_save()
        self.updated_at = datetime.now()
        return super().save(force_insert=force_insert, only=only)


class Caces(Model):
    """
    CACES certification (Certificat d'Aptitude à la Conduite En Sécurité).

    French certification for operating heavy machinery and equipment.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee = ForeignKeyField(Employee, backref="caces", on_delete="CASCADE")

    # Certification Details
    kind = CharField()  # e.g., 'R489-1A', 'R489-1B', 'R489-3', 'R489-4'
    completion_date = DateField()

    # Calculated at creation time
    expiration_date = DateField(index=True)

    # Document
    document_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    # Soft Delete
    deleted_at = DateTimeField(null=True, index=True)
    deleted_by = CharField(null=True)
    deletion_reason = TextField(null=True)

    class Meta:
        database = database
        table_name = "caces"
        indexes = (
            (("employee", "expiration_date"), False),  # Composite index
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_deleted(self) -> bool:
        """Check if CACES is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        # Ensure expiration_date is a date object (not datetime)
        if isinstance(self.expiration_date, datetime):
            expiration_date = self.expiration_date.date()
        else:
            expiration_date = self.expiration_date
        return date.today() > expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration (negative if already expired)."""
        # Ensure expiration_date is a date object (not datetime)
        if isinstance(self.expiration_date, datetime):
            expiration_date = self.expiration_date.date()
        else:
            expiration_date = self.expiration_date
        return (expiration_date - date.today()).days

    @property
    def status(self) -> str:
        """
        Human-readable status.

        Returns:
            'expired': Already expired
            'critical': Expires within 30 days
            'warning': Expires within 60 days
            'valid': More than 60 days remaining
        """
        if self.is_expired:
            return "expired"
        elif self.days_until_expiration < 30:
            return "critical"
        elif self.days_until_expiration < 60:
            return "warning"
        else:
            return "valid"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, kind: str, completion_date: date) -> date:
        """
        Calculate expiration date based on CACES kind.

        Rules:
        - R489-1A, R489-1B, R489-3, R489-4: 5 years validity
        - Other certifications: 10 years validity

        Args:
            kind: CACES certification type
            completion_date: Date when certification was obtained

        Returns:
            Expiration date (handles leap years correctly)
        """
        years = CACES_VALIDITY_YEARS.get(kind, 10)

        # Use relativedelta to handle leap years correctly
        # This is more accurate than timedelta(days=years*365)
        return completion_date + relativedelta(years=years)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get all certifications expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where((cls.expiration_date <= threshold) & (cls.expiration_date >= date.today()))

    @classmethod
    def expired(cls):
        """Get all expired certifications."""
        return cls.select().where(cls.expiration_date < date.today())

    @classmethod
    def by_kind(cls, kind: str):
        """Get certifications by type."""
        return cls.select().where(cls.kind == kind)

    @classmethod
    def without_deleted(cls):
        """Get all CACES excluding soft-deleted ones."""
        return cls.select().where(cls.deleted_at.is_null(True))

    @classmethod
    def deleted(cls):
        """Get all soft-deleted CACES."""
        return cls.select().where(cls.deleted_at.is_null(False))

    # ========== INSTANCE METHODS ==========

    def soft_delete(self, reason: str = None, deleted_by: str = None):
        """
        Mark CACES as deleted (soft delete).

        Args:
            reason: Optional reason for deletion
            deleted_by: Optional username who performed the deletion
        """
        self.deleted_at = datetime.now()
        self.deletion_reason = reason
        self.deleted_by = deleted_by
        self.save(only=[Caces.deleted_at, Caces.deletion_reason, Caces.deleted_by])

    def restore(self):
        """Restore a soft-deleted CACES."""
        self.deleted_at = None
        self.deletion_reason = None
        self.deleted_by = None
        self.save(only=[Caces.deleted_at, Caces.deletion_reason, Caces.deleted_by])

    # ========== HOOKS ==========

    def before_save(self):
        """Validate CACES kind and calculate expiration_date before saving."""
        from .validators import ValidationError as ModelValidationError
        from .validators import validate_caces_kind

        # Validate CACES kind
        if self.kind:
            try:
                self.kind = validate_caces_kind(self.kind)
            except ModelValidationError as e:
                raise ValueError(str(e))

        # Calculate expiration_date if not set
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration(self.kind, self.completion_date)

    def save(self, force_insert=False, only=None):
        """Override save to calculate expiration_date automatically."""
        self.before_save()
        return super().save(force_insert=force_insert, only=only)


class MedicalVisit(Model):
    """
    Occupational health visit record.

    French labor law requires periodic medical examinations for workers.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee = ForeignKeyField(Employee, backref="medical_visits", on_delete="CASCADE")

    # Visit Details
    visit_type = CharField()  # 'initial', 'periodic', 'recovery'
    visit_date = DateField()

    # Calculated expiration
    expiration_date = DateField(index=True)

    # Visit Result
    result = CharField(index=True)  # 'fit', 'unfit', 'fit_with_restrictions'

    # Document
    document_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    # Soft Delete
    deleted_at = DateTimeField(null=True, index=True)
    deleted_by = CharField(null=True)
    deletion_reason = TextField(null=True)

    class Meta:
        database = database
        table_name = "medical_visits"
        indexes = ((("employee", "expiration_date"), False),)

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_deleted(self) -> bool:
        """Check if medical visit is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if medical clearance is expired."""
        # Ensure expiration_date is a date object (not datetime)
        if isinstance(self.expiration_date, datetime):
            expiration_date = self.expiration_date.date()
        else:
            expiration_date = self.expiration_date
        return date.today() > expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration."""
        # Ensure expiration_date is a date object (not datetime)
        if isinstance(self.expiration_date, datetime):
            expiration_date = self.expiration_date.date()
        else:
            expiration_date = self.expiration_date
        return (expiration_date - date.today()).days

    @property
    def is_fit(self) -> bool:
        """Convenience: is employee fit for work?"""
        return self.result == "fit"

    @property
    def has_restrictions(self) -> bool:
        """Does this visit have work restrictions?"""
        return self.result == "fit_with_restrictions"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, visit_type: str, visit_date: date) -> date:
        """
        Calculate medical visit expiration based on type.

        Rules:
        - Initial visit: 2 years
        - Periodic visit: 2 years
        - Recovery visit: 1 year

        Args:
            visit_type: Type of medical visit
            visit_date: Date when visit occurred

        Returns:
            Expiration date (handles leap years correctly)
        """
        years = VISIT_VALIDITY_YEARS.get(visit_type, 2)

        # Use relativedelta to handle leap years correctly
        return visit_date + relativedelta(years=years)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get medical visits expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where((cls.expiration_date <= threshold) & (cls.expiration_date >= date.today()))

    @classmethod
    def unfit_employees(cls):
        """Get employees with unfit medical visits."""
        return Employee.select(Employee, cls).join(cls).where(cls.result == "unfit")

    @classmethod
    def without_deleted(cls):
        """Get all medical visits excluding soft-deleted ones."""
        return cls.select().where(cls.deleted_at.is_null(True))

    @classmethod
    def deleted(cls):
        """Get all soft-deleted medical visits."""
        return cls.select().where(cls.deleted_at.is_null(False))

    # ========== INSTANCE METHODS ==========

    def soft_delete(self, reason: str = None, deleted_by: str = None):
        """
        Mark medical visit as deleted (soft delete).

        Args:
            reason: Optional reason for deletion
            deleted_by: Optional username who performed the deletion
        """
        self.deleted_at = datetime.now()
        self.deletion_reason = reason
        self.deleted_by = deleted_by
        self.save(only=[MedicalVisit.deleted_at, MedicalVisit.deletion_reason, MedicalVisit.deleted_by])

    def restore(self):
        """Restore a soft-deleted medical visit."""
        self.deleted_at = None
        self.deletion_reason = None
        self.deleted_by = None
        self.save(only=[MedicalVisit.deleted_at, MedicalVisit.deletion_reason, MedicalVisit.deleted_by])

    # ========== HOOKS ==========

    def before_save(self):
        """Validate visit consistency and calculate expiration_date before saving."""
        from .validators import ValidationError as ModelValidationError
        from .validators import validate_medical_visit_consistency

        # Validate visit type and result consistency
        if self.visit_type and self.result:
            try:
                self.visit_type, self.result = validate_medical_visit_consistency(self.visit_type, self.result)
            except ModelValidationError as e:
                raise ValueError(str(e))

        # Calculate expiration_date if not set
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration(self.visit_type, self.visit_date)

    def save(self, force_insert=False, only=None):
        """Override save to calculate expiration_date automatically."""
        self.before_save()
        return super().save(force_insert=force_insert, only=only)


class OnlineTraining(Model):
    """
    Online training completion record.

    Some trainings have expiration dates, others are permanent.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee = ForeignKeyField(Employee, backref="trainings", on_delete="CASCADE")

    # Training Details
    title = CharField()
    completion_date = DateField()

    # Validity (NULL = permanent, no expiration)
    validity_months = IntegerField(null=True)

    # Calculated expiration (NULL if permanent)
    expiration_date = DateField(null=True, index=True)

    # Certificate (optional)
    certificate_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    # Soft Delete
    deleted_at = DateTimeField(null=True, index=True)
    deleted_by = CharField(null=True)
    deletion_reason = TextField(null=True)

    class Meta:
        database = database
        table_name = "online_trainings"
        indexes = ((("employee", "expiration_date"), False),)

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_deleted(self) -> bool:
        """Check if training is soft-deleted."""
        return self.deleted_at is not None

    @property
    def expires(self) -> bool:
        """Does this training expire?"""
        return self.validity_months is not None

    @property
    def is_expired(self) -> bool:
        """Check if training is expired (only if it expires)."""
        if not self.expires:
            return False
        # Ensure expiration_date is a date object (not datetime)
        if isinstance(self.expiration_date, datetime):
            expiration_date = self.expiration_date.date()
        else:
            expiration_date = self.expiration_date
        return date.today() > expiration_date

    @property
    def days_until_expiration(self) -> int | None:
        """Days until expiration, or None if permanent."""
        if not self.expires:
            return None
        # Ensure expiration_date is a date object (not datetime)
        if isinstance(self.expiration_date, datetime):
            expiration_date = self.expiration_date.date()
        else:
            expiration_date = self.expiration_date
        return (expiration_date - date.today()).days

    @property
    def status(self) -> str:
        """Human-readable status."""
        if not self.expires:
            return "permanent"
        elif self.is_expired:
            return "expired"
        elif self.days_until_expiration < 30:
            return "critical"
        elif self.days_until_expiration < 60:
            return "warning"
        else:
            return "valid"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, completion_date: date, validity_months: int | None) -> date | None:
        """
        Calculate training expiration date.

        If validity_months is None, training has no expiration (permanent).

        Args:
            completion_date: Date when training was completed
            validity_months: Number of months training is valid, or None for permanent

        Returns:
            Expiration date, or None for permanent trainings
        """
        if validity_months is None:
            return None

        # Use relativedelta for accurate month addition
        return completion_date + relativedelta(months=validity_months)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get trainings expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date.is_null(False))
            & (cls.expiration_date <= threshold)
            & (cls.expiration_date >= date.today())
        )

    @classmethod
    def permanent(cls):
        """Get all permanent (non-expiring) trainings."""
        return cls.select().where(cls.validity_months.is_null(True))

    @classmethod
    def without_deleted(cls):
        """Get all trainings excluding soft-deleted ones."""
        return cls.select().where(cls.deleted_at.is_null(True))

    @classmethod
    def deleted(cls):
        """Get all soft-deleted trainings."""
        return cls.select().where(cls.deleted_at.is_null(False))

    # ========== INSTANCE METHODS ==========

    def soft_delete(self, reason: str = None, deleted_by: str = None):
        """
        Mark training as deleted (soft delete).

        Args:
            reason: Optional reason for deletion
            deleted_by: Optional username who performed the deletion
        """
        self.deleted_at = datetime.now()
        self.deletion_reason = reason
        self.deleted_by = deleted_by
        self.save(only=[OnlineTraining.deleted_at, OnlineTraining.deletion_reason, OnlineTraining.deleted_by])

    def restore(self):
        """Restore a soft-deleted training."""
        self.deleted_at = None
        self.deletion_reason = None
        self.deleted_by = None
        self.save(only=[OnlineTraining.deleted_at, OnlineTraining.deletion_reason, OnlineTraining.deleted_by])

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if self.expiration_date is None and self.validity_months is not None:
            self.expiration_date = self.calculate_expiration(self.completion_date, self.validity_months)

    def save(self, force_insert=False, only=None):
        """Override save to calculate expiration_date automatically."""
        self.before_save()
        return super().save(force_insert=force_insert, only=only)


class Contract(Model):
    """
    Employment contract with complete history tracking.

    Tracks all employee contracts with start/end dates, position,
    salary, department, and evolution over time.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    employee = ForeignKeyField(Employee, backref="contracts", on_delete="CASCADE")

    # Contract Details
    contract_type = CharField(index=True)  # CDI, CDD, Interim, etc.
    start_date = DateField(index=True)
    end_date = DateField(null=True, index=True)  # NULL for CDI (permanent)

    # Trial Period
    trial_period_end = DateField(null=True)

    # Compensation
    gross_salary = DecimalField(max_digits=10, decimal_places=2, null=True)
    weekly_hours = DecimalField(max_digits=4, decimal_places=2, default=35.0)

    # Position and Department
    position = CharField(index=True)  # Job title
    department = CharField(index=True)  # Department
    manager = CharField(null=True)  # Manager's name

    # Status
    status = CharField(default="active")  # active, ended, cancelled, pending
    end_reason = CharField(null=True)  # resignation, termination, completion, etc.

    # Documents
    contract_document_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    created_by = CharField(null=True)
    notes = TextField(null=True)

    class Meta:
        database = database
        table_name = "contracts"
        indexes = (
            (("employee", "start_date"), False),  # Chronological order per employee
            ("end_date", False),  # Expiring contracts
            ("status", False),  # Active contracts
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_current(self) -> bool:
        """
        Check if this is the current active contract.

        A contract is current if:
        - Status is 'active'
        - Start date is today or in the past
        - No end date (CDI) OR end date is in the future
        """
        if self.status != "active":
            return False

        today = date.today()

        # Hasn't started yet
        if self.start_date > today:
            return False

        # Has end date and has passed
        if self.end_date and self.end_date < today:
            return False

        return True

    @property
    def duration_days(self) -> int | None:
        """
        Calculate contract duration in days.

        Returns:
            Duration in days, or None if contract is ongoing (no end_date)
        """
        if not self.end_date:
            return None  # Ongoing (CDI)
        return (self.end_date - self.start_date).days

    @property
    def is_trial_period(self) -> bool:
        """Check if currently in trial period."""
        if not self.trial_period_end:
            return False
        return date.today() <= self.trial_period_end

    @property
    def days_until_trial_end(self) -> int | None:
        """Days until trial period ends, or None if no trial period."""
        if not self.trial_period_end:
            return None
        return (self.trial_period_end - date.today()).days

    @property
    def days_until_expiration(self) -> int | None:
        """
        Days until contract expires.

        Returns:
            Days until expiration, negative if expired, None for CDI (no expiration)
        """
        if not self.end_date:
            return None  # CDI doesn't expire
        return (self.end_date - date.today()).days

    @property
    def is_expiring_soon(self) -> bool:
        """Check if contract expires within warning period."""
        if not self.end_date:
            return False

        days_until = self.days_until_expiration
        return 0 <= days_until <= CONTRACT_EXPIRATION_WARNING_DAYS

    @property
    def is_expiring_critical(self) -> bool:
        """Check if contract expires within critical period."""
        if not self.end_date:
            return False

        days_until = self.days_until_expiration
        return 0 <= days_until <= CONTRACT_EXPIRATION_CRITICAL_DAYS

    @property
    def is_expired(self) -> bool:
        """Check if contract has expired."""
        if not self.end_date:
            return False
        return self.end_date < date.today()

    # ========== CLASS METHODS ==========

    @classmethod
    def active(cls):
        """Get all active contracts."""
        return cls.select().where(cls.status == "active")

    @classmethod
    def expiring_soon(cls, days: int = 90):
        """
        Get contracts expiring within X days.

        Args:
            days: Number of days to look ahead

        Returns:
            Query of contracts expiring soon
        """
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.end_date.is_null(False))
            & (cls.end_date <= threshold)
            & (cls.end_date >= date.today())
            & (cls.status == "active")
        )

    @classmethod
    def expired(cls):
        """Get expired contracts that are still marked as active."""
        return cls.select().where(
            (cls.end_date.is_null(False))
            & (cls.end_date < date.today())
            & (cls.status == "active")
        )

    @classmethod
    def trial_period_ending(cls, days: int = 7):
        """
        Get contracts with trial periods ending soon.

        Args:
            days: Number of days to look ahead

        Returns:
            Query of contracts with trial periods ending soon
        """
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.trial_period_end.is_null(False))
            & (cls.trial_period_end <= threshold)
            & (cls.trial_period_end >= date.today())
            & (cls.status == "active")
        )

    # ========== INSTANCE METHODS ==========

    def end_contract(self, reason: str = None):
        """
        Mark contract as ended.

        Args:
            reason: Optional reason for ending (resignation, termination, etc.)
        """
        self.status = "ended"
        self.end_reason = reason
        if self.end_date is None:
            self.end_date = date.today()
        self.save()

    # ========== HOOKS ==========

    def before_save(self):
        """Validate contract data before saving."""
        from .validators import ValidationError as ModelValidationError
        from .validators import validate_entry_date

        # Validate start_date
        if self.start_date:
            try:
                self.start_date = validate_entry_date(self.start_date)
            except ModelValidationError as e:
                raise ValueError(str(e))

        # Validate end_date if provided
        if self.end_date:
            try:
                self.end_date = validate_entry_date(self.end_date)
            except ModelValidationError as e:
                raise ValueError(str(e))

            # End date must be after start date
            if self.end_date < self.start_date:
                raise ValueError("End date must be after start date")

            # For CDI, end_date should typically be None
            if self.contract_type == "CDI" and self.end_date:
                # Warning but allow it (might be ending the CDI)
                pass

    def save(self, force_insert=False, only=None):
        """Override save to update updated_at timestamp and validate."""
        self.before_save()
        self.updated_at = datetime.now()
        return super().save(force_insert=force_insert, only=only)


class ContractAmendment(Model):
    """
    Contract amendment for tracking changes during contract lifetime.

    Records changes to salary, position, department, hours, etc.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    contract = ForeignKeyField(Contract, backref="amendments", on_delete="CASCADE")

    # Amendment Details
    amendment_date = DateField(index=True)
    amendment_type = CharField()  # salary_change, position_change, etc.
    description = TextField()

    # Change Tracking
    old_field_name = CharField()  # Which field was changed
    old_value = CharField(null=True)  # Previous value
    new_value = CharField(null=True)  # New value

    # Document
    document_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    created_by = CharField(null=True)

    class Meta:
        database = database
        table_name = "contract_amendments"
        indexes = (
            (("contract", "amendment_date"), False),  # Chronological per contract
            ("amendment_type", False),  # By type
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_recent(self) -> bool:
        """Check if amendment was made in the last 30 days."""
        return (date.today() - self.amendment_date).days <= 30

    # ========== CLASS METHODS ==========

    @classmethod
    def by_contract(cls, contract: Contract):
        """Get all amendments for a specific contract."""
        return cls.select().where(cls.contract == contract).order_by(cls.amendment_date.desc())

    @classmethod
    def recent(cls, days: int = 30):
        """Get amendments from the last X days."""
        threshold = date.today() - timedelta(days=days)
        return cls.select().where(cls.amendment_date >= threshold).order_by(cls.amendment_date.desc())

    # ========== HOOKS ==========

    def before_save(self):
        """Validate amendment data before saving."""
        from .validators import ValidationError as ModelValidationError
        from .validators import validate_entry_date

        # Validate amendment_date
        if self.amendment_date:
            try:
                self.amendment_date = validate_entry_date(self.amendment_date)
            except ModelValidationError as e:
                raise ValueError(str(e))

        # Require description
        if not self.description or not self.description.strip():
            raise ValueError("Description is required")

    def save(self, force_insert=False, only=None):
        """Override save to validate before saving."""
        self.before_save()
        return super().save(force_insert=force_insert, only=only)
