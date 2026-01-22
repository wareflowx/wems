"""Business logic calculations for Employee entity."""

from datetime import date

from dateutil.relativedelta import relativedelta

from employee.models import Employee


def calculate_seniority(employee: Employee) -> int:
    """
    Calculate employee seniority in complete years.

    Uses hire_date (entry_date) and handles leap years correctly.
    Returns 0 if no date available or if employee hasn't started yet.

    Args:
        employee: Employee instance

    Returns:
        Number of complete years since entry_date

    Examples:
        >>> from datetime import date
        >>> emp = Employee(entry_date=date(2020, 1, 15))
        >>> # If today is 2026-01-16, seniority = 6 years
        >>> calculate_seniority(emp)
        6
    """
    if not employee.entry_date:
        return 0

    # Use relativedelta for accurate year calculation (handles leap years)
    years_diff = relativedelta(date.today(), employee.entry_date).years

    # Return 0 if entry_date is in the future
    if years_diff < 0:
        return 0

    return years_diff


def calculate_compliance_score(employee: Employee) -> dict:
    """
    Calculate overall compliance score (0-100).

    Scoring system:
    - Valid item: +100 points
    - Critical (expiring < 30 days): -30 points
    - Expired: -100 points
    - Final score: weighted average of all items

    Args:
        employee: Employee instance

    Returns:
        Dictionary with:
        - score: Overall compliance score (0-100)
        - total_items: Total number of compliance items
        - valid_items: Number of valid items
        - critical_items: Number of critical items
        - expired_items: Number of expired items

    Examples:
        >>> score = calculate_compliance_score(employee)
        >>> print(f"Compliance: {score['score']}/100")
        >>> print(f"Expired items: {score['expired_items']}")
    """
    items = []
    total_score = 0
    valid_count = 0
    critical_count = 0
    expired_count = 0

    # Check CACES certifications
    for caces in employee.caces:
        if caces.is_expired:
            items.append(-100)
            expired_count += 1
        elif caces.status == "critical":
            items.append(-30)
            critical_count += 1
        else:
            items.append(100)
            valid_count += 1

    # Check medical visits
    for visit in employee.medical_visits:
        if visit.is_expired:
            items.append(-100)
            expired_count += 1
        elif visit.days_until_expiration < 30:
            items.append(-30)
            critical_count += 1
        else:
            items.append(100)
            valid_count += 1

    # Check online trainings (only if they expire)
    for training in employee.trainings:
        if not training.expires:
            # Permanent trainings don't affect score
            continue

        if training.is_expired:
            items.append(-100)
            expired_count += 1
        elif training.days_until_expiration < 30:
            items.append(-30)
            critical_count += 1
        else:
            items.append(100)
            valid_count += 1

    # Calculate final score
    total_items = len(items)

    if total_items == 0:
        # No compliance items - return neutral score
        return {
            "score": 100,
            "total_items": 0,
            "valid_items": 0,
            "critical_items": 0,
            "expired_items": 0,
        }

    # Calculate average score and normalize to 0-100
    avg_score = sum(items) / total_items

    # Map from [-100, 100] to [0, 100]
    # -100 -> 0, 0 -> 50, 100 -> 100
    normalized_score = int((avg_score + 100) / 2)

    # Clamp to 0-100 range
    normalized_score = max(0, min(100, normalized_score))

    return {
        "score": normalized_score,
        "total_items": total_items,
        "valid_items": valid_count,
        "critical_items": critical_count,
        "expired_items": expired_count,
    }


def get_compliance_status(employee: Employee) -> str:
    """
    Determine overall compliance status.

    Returns:
        'critical': Has expired items
        'warning': Has items expiring soon (< 30 days) but no expired items
        'compliant': All items valid

    Args:
        employee: Employee instance

    Examples:
        >>> status = get_compliance_status(employee)
        >>> if status == 'critical':
        ...     print("Immediate action required!")
    """
    has_expired = False
    has_critical = False

    # Check CACES
    for caces in employee.caces:
        if caces.is_expired:
            has_expired = True
            break
        elif caces.status == "critical":
            has_critical = True

    # Check medical visits
    if not has_expired:
        for visit in employee.medical_visits:
            if visit.is_expired:
                has_expired = True
                break
            elif visit.days_until_expiration < 30:
                has_critical = True

    # Check trainings
    if not has_expired:
        for training in employee.trainings:
            if not training.expires:
                continue
            if training.is_expired:
                has_expired = True
                break
            elif training.days_until_expiration < 30:
                has_critical = True

    if has_expired:
        return "critical"
    elif has_critical:
        return "warning"
    else:
        return "compliant"


def calculate_next_actions(employee: Employee) -> list:
    """
    Get prioritized list of required actions.

    Returns:
        List of action dictionaries:
        [
            {
                'type': 'caces' | 'medical' | 'training',
                'priority': 'urgent' | 'high' | 'normal',
                'item': model_instance,
                'description': str,
                'days_until': int
            }
        ]
        Sorted by priority (urgent first) and days_until.

    Args:
        employee: Employee instance

    Examples:
        >>> actions = calculate_next_actions(employee)
        >>> for action in actions:
        ...     print(f"{action['priority']}: {action['description']}")
    """
    actions = []

    # Check CACES
    for caces in employee.caces:
        days = caces.days_until_expiration

        if days < 0:
            priority = "urgent"
            description = f"Renew CACES {caces.kind} (expired {abs(days)} days ago)"
        elif days < 30:
            priority = "urgent"
            description = f"Renew CACES {caces.kind} (expires in {days} days)"
        elif days < 60:
            priority = "high"
            description = f"Plan CACES {caces.kind} renewal (expires in {days} days)"
        elif days < 90:
            priority = "normal"
            description = f"CACES {caces.kind} expires in {days} days"
        else:
            continue  # No action needed yet

        actions.append(
            {
                "type": "caces",
                "priority": priority,
                "item": caces,
                "description": description,
                "days_until": days,
            }
        )

    # Check medical visits
    for visit in employee.medical_visits:
        days = visit.days_until_expiration

        if days < 0:
            priority = "urgent"
            description = f"Schedule medical visit (expired {abs(days)} days ago)"
        elif days < 30:
            priority = "urgent"
            description = f"Schedule medical visit (expires in {days} days)"
        elif days < 60:
            priority = "high"
            description = f"Plan medical visit (expires in {days} days)"
        elif days < 90:
            priority = "normal"
            description = f"Medical visit expires in {days} days"
        else:
            continue

        actions.append(
            {
                "type": "medical",
                "priority": priority,
                "item": visit,
                "description": description,
                "days_until": days,
            }
        )

    # Check trainings
    for training in employee.trainings:
        if not training.expires:
            continue

        days = training.days_until_expiration

        if days is None:
            continue

        if days < 0:
            priority = "urgent"
            description = f"Renew training '{training.title}' (expired {abs(days)} days ago)"
        elif days < 30:
            priority = "urgent"
            description = f"Renew training '{training.title}' (expires in {days} days)"
        elif days < 60:
            priority = "high"
            description = f"Plan training renewal '{training.title}' (expires in {days} days)"
        elif days < 90:
            priority = "normal"
            description = f"Training '{training.title}' expires in {days} days"
        else:
            continue

        actions.append(
            {
                "type": "training",
                "priority": priority,
                "item": training,
                "description": description,
                "days_until": days,
            }
        )

    # Sort by priority (urgent > high > normal) then by days_until
    priority_order = {"urgent": 0, "high": 1, "normal": 2}
    actions.sort(key=lambda a: (priority_order[a["priority"]], a["days_until"]))

    return actions


def days_until_next_action(employee: Employee) -> int:
    """
    Calculate days until next required action.

    Returns:
        Days until earliest expiration, or 9999 if no actions needed

    Args:
        employee: Employee instance

    Examples:
        >>> days = days_until_next_action(employee)
        >>> if days < 30:
        ...     print(f"Action needed in {days} days")
    """
    min_days = None

    # Check CACES
    for caces in employee.caces:
        days = caces.days_until_expiration
        if min_days is None or days < min_days:
            min_days = days

    # Check medical visits
    for visit in employee.medical_visits:
        days = visit.days_until_expiration
        if min_days is None or days < min_days:
            min_days = days

    # Check trainings
    for training in employee.trainings:
        if not training.expires or training.days_until_expiration is None:
            continue
        days = training.days_until_expiration
        if min_days is None or days < min_days:
            min_days = days

    if min_days is None:
        return 9999  # No actions needed

    return max(0, min_days)


def calculate_age(employee: Employee) -> int | None:
    """
    Calculate employee age from birth_date.

    Returns None if birth_date not available.

    Args:
        employee: Employee instance

    Returns:
        Age in complete years, or None if birth_date not set

    Examples:
        >>> age = calculate_age(employee)
        >>> if age:
        ...     print(f"Employee is {age} years old")
    """
    # Note: birth_date field doesn't exist yet in Employee model
    # This function is a placeholder for future implementation
    # When birth_date is added to the model, uncomment:

    # if not employee.birth_date:
    #     return None
    # return relativedelta(date.today(), employee.birth_date).years

    return None
