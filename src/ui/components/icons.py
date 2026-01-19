"""Icon components with consistent styling.

Provides a wrapper around Flet icons with consistent sizing and styling.
Maps commonly used icons to named constants.
"""

import flet as ft
from ui.constants import IconSize
from ui.theme import AppTheme


class AppIcon(ft.Icon):
    """
    A styled icon component with consistent defaults.

    Args:
        icon_name: Flet icon name (e.g., ft.icons.HOME)
        size: Icon size from IconSize enum or custom int
        color: Icon color (uses theme primary if None)
        **kwargs: Additional ft.Icon properties
    """

    def __init__(
        self,
        icon_name: str,
        size: int = IconSize.MD.value,
        color: str = None,
        **kwargs
    ):
        super().__init__(
            name=icon_name,
            size=size,
            color=color or AppTheme.PRIMARY,
            **kwargs
        )


# Named icon mappings for commonly used icons
# Icons are accessed via ft.icons.Icons enum
class Icons:
    """Centralized icon name constants."""

    # Navigation
    HOME = ft.icons.Icons.HOME
    DASHBOARD = ft.icons.Icons.DASHBOARD
    PEOPLE = ft.icons.Icons.PEOPLE
    PERSON = ft.icons.Icons.PERSON
    SETTINGS = ft.icons.Icons.SETTINGS

    # Actions
    ADD = ft.icons.Icons.ADD
    EDIT = ft.icons.Icons.EDIT
    DELETE = ft.icons.Icons.DELETE
    SAVE = ft.icons.Icons.SAVE
    CANCEL = ft.icons.Icons.CLOSE
    SEARCH = ft.icons.Icons.SEARCH
    FILTER = ft.icons.Icons.FILTER_LIST
    REFRESH = ft.icons.Icons.REFRESH
    DOWNLOAD = ft.icons.Icons.DOWNLOAD
    UPLOAD = ft.icons.Icons.UPLOAD
    EXPORT = ft.icons.Icons.DOWNLOAD  # Use download icon for export
    IMPORT = ft.icons.Icons.UPLOAD  # Use upload icon for import

    # Communication
    EMAIL = ft.icons.Icons.EMAIL
    PHONE = ft.icons.Icons.PHONE
    NOTIFICATION = ft.icons.Icons.NOTIFICATIONS
    WARNING = ft.icons.Icons.WARNING
    ERROR = ft.icons.Icons.ERROR
    INFO = ft.icons.Icons.INFO
    SUCCESS = ft.icons.Icons.CHECK_CIRCLE
    CHECK = ft.icons.Icons.CHECK
    CLOSE_CIRCLE = ft.icons.Icons.CANCEL

    # Files
    FILE = ft.icons.Icons.INSERT_DRIVE_FILE
    FOLDER = ft.icons.Icons.FOLDER
    DOCUMENT = ft.icons.Icons.DESCRIPTION
    PDF = ft.icons.Icons.PICTURE_AS_PDF
    IMAGE = ft.icons.Icons.IMAGE

    # Status
    ACTIVE = ft.icons.Icons.CHECK_CIRCLE
    INACTIVE = ft.icons.Icons.CANCEL
    PENDING = ft.icons.Icons.PENDING
    LOADING = ft.icons.Icons.REFRESH  # Use refresh for loading

    # Navigation arrows
    ARROW_BACK = ft.icons.Icons.ARROW_BACK
    ARROW_FORWARD = ft.icons.Icons.ARROW_FORWARD
    CHEVRON_RIGHT = ft.icons.Icons.CHEVRON_RIGHT
    EXPAND_MORE = ft.icons.Icons.EXPAND_MORE
    EXPAND_LESS = ft.icons.Icons.EXPAND_LESS

    # Calendar
    CALENDAR = ft.icons.Icons.CALENDAR_MONTH
    TODAY = ft.icons.Icons.TODAY
    DATE_RANGE = ft.icons.Icons.DATE_RANGE

    # Business
    BUSINESS = ft.icons.Icons.BUSINESS
    WORK = ft.icons.Icons.WORK
    ASSIGNMENT = ft.icons.Icons.ASSIGNMENT
    BADGE = ft.icons.Icons.BADGE
    CERTIFICATE = ft.icons.Icons.VERIFIED
    SCHOOL = ft.icons.Icons.SCHOOL
    MEDICAL = ft.icons.Icons.LOCAL_HOSPITAL

    # UI elements
    MENU = ft.icons.Icons.MENU
    MORE_VERT = ft.icons.Icons.MORE_VERT
    FULLSCREEN = ft.icons.Icons.FULLSCREEN
    VIEW_LIST = ft.icons.Icons.VIEW_LIST
    VIEW_MODULE = ft.icons.Icons.VIEW_MODULE
    GRID_VIEW = ft.icons.Icons.GRID_VIEW
    TABLE_ROWS = ft.icons.Icons.TABLE_ROWS

    # Visibility
    VISIBILITY = ft.icons.Icons.VISIBILITY
    VISIBILITY_OFF = ft.icons.Icons.VISIBILITY_OFF
    EYE = ft.icons.Icons.VISIBILITY
    EYE_OFF = ft.icons.Icons.VISIBILITY_OFF
