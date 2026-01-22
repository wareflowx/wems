"""Complex database queries for Employee entity."""

from datetime import date, timedelta

from peewee import prefetch

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining


def get_employees_with_expiring_items(days=30):
    """
    Get employees with certifications expiring within X days.

    Args:
        days: Number of days to look ahead (default: 30)

    Returns:
        List of Employee objects with prefetched related items.
        Each employee has caces, medical_visits, and trainings loaded
        to avoid N+1 queries.

    Examples:
        >>> employees = get_employees_with_expiring_items(days=30)
        >>> for emp in employees:
        ...     for caces in emp.caces:
        ...         if caces.status in ['critical', 'warning']:
        ...             print(f"{emp.full_name}: {caces.kind} expires in {caces.days_until_expiration} days")
    """
    threshold = date.today() + timedelta(days=days)

    # Collect employee IDs from all three sources
    employee_ids = set()

    # Get employees with expiring CACES
    caces_employees = (
        Employee.select(Employee.id)
        .join(Caces)
        .where((Caces.expiration_date >= date.today()) & (Caces.expiration_date <= threshold))
    )
    employee_ids.update(emp.id for emp in caces_employees)

    # Get employees with expiring medical visits
    visit_employees = (
        Employee.select(Employee.id)
        .join(MedicalVisit)
        .where((MedicalVisit.expiration_date >= date.today()) & (MedicalVisit.expiration_date <= threshold))
    )
    employee_ids.update(emp.id for emp in visit_employees)

    # Get employees with expiring trainings
    training_employees = (
        Employee.select(Employee.id)
        .join(OnlineTraining)
        .where(
            (OnlineTraining.expiration_date.is_null(False))
            & (OnlineTraining.expiration_date >= date.today())
            & (OnlineTraining.expiration_date <= threshold)
        )
    )
    employee_ids.update(emp.id for emp in training_employees)

    if not employee_ids:
        return []

    # Get all unique employees
    all_employees = Employee.select().where(Employee.id.in_(employee_ids))

    # Prefetch related items to avoid N+1 queries
    employees_with_prefetch = prefetch(all_employees, Caces, MedicalVisit, OnlineTraining)

    return list(employees_with_prefetch)


def get_employees_with_expired_caces():
    """
    Get employees with expired CACES certifications.

    Returns:
        List of Employee objects with prefetched expired CACES.

    Examples:
        >>> employees = get_employees_with_expired_caces()
        >>> for emp in employees:
        ...     for caces in emp.caces:
        ...         if caces.is_expired:
        ...             print(f"{emp.full_name}: {caces.kind} expired on {caces.expiration_date}")
    """
    # Get employees with expired CACES
    employees = Employee.select().join(Caces).where(Caces.expiration_date < date.today()).distinct()

    # Prefetch CACES to avoid N+1 queries
    employees_with_prefetch = prefetch(employees, Caces)

    return list(employees_with_prefetch)


def get_employees_with_expired_medical_visits():
    """
    Get employees with expired medical visits.

    Returns:
        List of Employee objects with prefetched expired medical visits.

    Examples:
        >>> employees = get_employees_with_expired_medical_visits()
        >>> for emp in employees:
        ...     for visit in emp.medical_visits:
        ...         if visit.is_expired:
        ...             print(f"{emp.full_name}: Medical visit expired on {visit.expiration_date}")
    """
    # Get employees with expired medical visits
    employees = Employee.select().join(MedicalVisit).where(MedicalVisit.expiration_date < date.today()).distinct()

    # Prefetch medical visits to avoid N+1 queries
    employees_with_prefetch = prefetch(employees, MedicalVisit)

    return list(employees_with_prefetch)


def get_unfit_employees():
    """
    Get employees with unfit medical status.

    Returns:
        List of Employee objects with prefetched medical visits.
        Only includes employees whose most recent medical visit
        has result='unfit'.

    Examples:
        >>> employees = get_unfit_employees()
        >>> for emp in employees:
        ...     print(f"{emp.full_name} is currently unfit for work")
    """
    # Get employees with unfit medical visits (most recent first)
    unfit_query = (
        MedicalVisit.select(MedicalVisit.employee)
        .where(MedicalVisit.result == "unfit")
        .order_by(MedicalVisit.visit_date.desc())
        .distinct()
    )

    # Get employees from unfit visits
    employee_ids = [visit.employee.id for visit in unfit_query]

    if not employee_ids:
        return []

    # Get full employee objects
    employees = Employee.select().where(Employee.id.in_(employee_ids))

    # Prefetch medical visits to avoid N+1 queries
    employees_with_prefetch = prefetch(employees, MedicalVisit)

    return list(employees_with_prefetch)


def get_dashboard_statistics():
    """
    Calculate aggregated statistics for dashboard.

    Returns:
        Dictionary with key metrics:
        - total_employees: Total number of employees
        - active_employees: Number of active employees
        - expiring_caces: Number of CACES expiring within 30 days
        - expiring_visits: Number of medical visits expiring within 30 days
        - unfit_employees: Number of employees with unfit status

    Examples:
        >>> stats = get_dashboard_statistics()
        >>> print(f"Active employees: {stats['active_employees']}")
        >>> print(f"Expiring CACES: {stats['expiring_caces']}")
    """
    today = date.today()
    threshold_30_days = today + timedelta(days=30)

    # Total employees
    total_employees = Employee.select().count()

    # Active employees
    active_employees = Employee.select().where(Employee.current_status == "active").count()

    # Expiring CACES (within 30 days)
    expiring_caces = (
        Caces.select().where((Caces.expiration_date >= today) & (Caces.expiration_date <= threshold_30_days)).count()
    )

    # Expiring medical visits (within 30 days)
    expiring_visits = (
        MedicalVisit.select()
        .where((MedicalVisit.expiration_date >= today) & (MedicalVisit.expiration_date <= threshold_30_days))
        .count()
    )

    # Unfit employees (most recent visit is unfit)
    unfit_employees = MedicalVisit.select().where(MedicalVisit.result == "unfit").count()

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "expiring_caces": expiring_caces,
        "expiring_visits": expiring_visits,
        "unfit_employees": unfit_employees,
    }


def get_expiring_items_by_type(days=30):
    """
    Get expiring items grouped by type and employee.

    Args:
        days: Number of days to look ahead (default: 30)

    Returns:
        Dictionary mapping employee_id to lists of expiring items:
        {
            employee_id: {
                'employee': Employee,
                'caces': [Caces, ...],
                'medical_visits': [MedicalVisit, ...],
                'trainings': [OnlineTraining, ...]
            }
        }
        Only includes employees who have at least one expiring item.

    Examples:
        >>> items = get_expiring_items_by_type(days=30)
        >>> for emp_id, data in items.items():
        ...     emp = data['employee']
        ...     print(f"{emp.full_name}:")
        ...     for caces in data['caces']:
        ...         print(f"  - CACES {caces.kind} expires in {caces.days_until_expiration} days")
    """
    threshold = date.today() + timedelta(days=days)
    today = date.today()

    result = {}

    # Get expiring CACES
    expiring_caces = Caces.select().where((Caces.expiration_date >= today) & (Caces.expiration_date <= threshold))

    for caces in expiring_caces:
        emp_id = caces.employee.id
        if emp_id not in result:
            result[emp_id] = {
                "employee": caces.employee,
                "caces": [],
                "medical_visits": [],
                "trainings": [],
            }
        result[emp_id]["caces"].append(caces)

    # Get expiring medical visits
    expiring_visits = MedicalVisit.select().where(
        (MedicalVisit.expiration_date >= today) & (MedicalVisit.expiration_date <= threshold)
    )

    for visit in expiring_visits:
        emp_id = visit.employee.id
        if emp_id not in result:
            result[emp_id] = {
                "employee": visit.employee,
                "caces": [],
                "medical_visits": [],
                "trainings": [],
            }
        result[emp_id]["medical_visits"].append(visit)

    # Get expiring trainings
    expiring_trainings = OnlineTraining.select().where(
        (OnlineTraining.expiration_date.is_null(False))
        & (OnlineTraining.expiration_date >= today)
        & (OnlineTraining.expiration_date <= threshold)
    )

    for training in expiring_trainings:
        emp_id = training.employee.id
        if emp_id not in result:
            result[emp_id] = {
                "employee": training.employee,
                "caces": [],
                "medical_visits": [],
                "trainings": [],
            }
        result[emp_id]["trainings"].append(training)

    return result
