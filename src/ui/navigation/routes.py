"""Route definitions for application views.

Centralized route mapping for all application views.
"""


class Routes:
    """Application route constants."""

    DASHBOARD = "/"
    EMPLOYEES = "/employees"
    EMPLOYEE_DETAIL = "/employee/:id"
    EMPLOYEE_CREATE = "/employee/create"
    EMPLOYEE_EDIT = "/employee/:id/edit"
    ALERTS = "/alerts"
    DOCUMENTS = "/documents"
    SETTINGS = "/settings"


# View builder mapping
ROUTE_VIEWS = {}


def register_view(route: str, view_builder):
    """
    Register a view builder for a route.

    Args:
        route: Route path (use :param for dynamic segments)
        view_builder: Callable that builds the view, receives (page, **params)
    """
    ROUTE_VIEWS[route] = view_builder


def get_view_builder(route: str):
    """
    Get the view builder for a route.

    Args:
        route: Route path

    Returns:
        View builder callable or None
    """
    # Try exact match first
    if route in ROUTE_VIEWS:
        return ROUTE_VIEWS[route]

    # Try pattern matching for dynamic routes
    for pattern, builder in ROUTE_VIEWS.items():
        if ":id" in pattern or ":param" in pattern:
            # Extract pattern parts
            pattern_parts = pattern.strip("/").split("/")
            route_parts = route.strip("/").split("/")

            if len(pattern_parts) == len(route_parts):
                # Check if non-param parts match
                match = True
                params = {}
                for p, r in zip(pattern_parts, route_parts):
                    if p.startswith(":"):
                        # Extract parameter
                        param_name = p.lstrip(":")
                        params[param_name] = r
                    elif p != r:
                        match = False
                        break

                if match:
                    # Return a wrapper that injects params
                    def build_with_params(page, **kwargs):
                        return builder(page, **{**params, **kwargs})

                    return build_with_params

    return None
