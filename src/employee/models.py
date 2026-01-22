"""Employee data models using Peewee ORM."""

import uuid
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from peewee import *

from database.connection import database
from employee.constants import (
    CACES_VALIDITY_YEARS,
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
    current_status = CharField()  # Enum: 'active', 'inactive'
    workspace = CharField()
    role = CharField()
    contract_type = CharField()  # Enum: 'CDI', 'CDD', 'Interim', 'Alternance'

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
        return (date.today() - self.entry_date).days // 365

    @property
    def is_active(self) -> bool:
        """Convenience boolean for active status."""
        return self.current_status == EmployeeStatus.ACTIVE

    # ========== CLASS METHODS (QUERIES) ==========

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

    class Meta:
        database = database
        table_name = "caces"
        indexes = (
            (("employee", "expiration_date"), False),  # Composite index
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration (negative if already expired)."""
        return (self.expiration_date - date.today()).days

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
    result = CharField()  # 'fit', 'unfit', 'fit_with_restrictions'

    # Document
    document_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = "medical_visits"
        indexes = ((("employee", "expiration_date"), False),)

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_expired(self) -> bool:
        """Check if medical clearance is expired."""
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration."""
        return (self.expiration_date - date.today()).days

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

    class Meta:
        database = database
        table_name = "online_trainings"
        indexes = ((("employee", "expiration_date"), False),)

    # ========== COMPUTED PROPERTIES ==========

    @property
    def expires(self) -> bool:
        """Does this training expire?"""
        return self.validity_months is not None

    @property
    def is_expired(self) -> bool:
        """Check if training is expired (only if it expires)."""
        if not self.expires:
            return False
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int | None:
        """Days until expiration, or None if permanent."""
        if not self.expires:
            return None
        return (self.expiration_date - date.today()).days

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

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if self.expiration_date is None and self.validity_months is not None:
            self.expiration_date = self.calculate_expiration(self.completion_date, self.validity_months)

    def save(self, force_insert=False, only=None):
        """Override save to calculate expiration_date automatically."""
        self.before_save()
        return super().save(force_insert=force_insert, only=only)
