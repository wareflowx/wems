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
class Icons:
    """Centralized icon name constants."""

    # Navigation
    HOME = ft.icons.HOME
    DASHBOARD = ft.icons.DASHBOARD_OUTLINE
    PEOPLE = ft.icons.PEOPLE_OUTLINE
    PERSON = ft.icons.PERSON_OUTLINE
    SETTINGS = ft.icons.SETTINGS_OUTLINE

    # Actions
    ADD = ft.icons.ADD
    EDIT = ft.icons.EDIT_OUTLINE
    DELETE = ft.icons.DELETE_OUTLINE
    SAVE = ft.icons.SAVE
    CANCEL = ft.icons.CLOSE
    SEARCH = ft.icons.SEARCH
    FILTER = ft.icons.FILTER_LIST
    REFRESH = ft.icons.REFRESH
    DOWNLOAD = ft.icons.DOWNLOAD
    UPLOAD = ft.icons.UPLOAD
    EXPORT = ft.icons.FILE_EXPORT
    IMPORT = ft.icons.FILE_IMPORT

    # Communication
    EMAIL = ft.icons.EMAIL_OUTLINE
    PHONE = ft.icons.PHONE
    NOTIFICATION = ft.icons.NOTIFICATIONS_OUTLINE
    WARNING = ft.icons.WARNING
    ERROR = ft.icons.ERROR
    INFO = ft.icons.INFO
    SUCCESS = ft.icons.CHECK_CIRCLE
    CHECK = ft.icons.CHECK
    CLOSE_CIRCLE = ft.icons.CANCEL

    # Files
    FILE = ft.icons.INSERT_DRIVE_FILE_OUTLINE
    FOLDER = ft.icons.FOLDER_OUTLINE
    DOCUMENT = ft.icons.DESCRIPTION_OUTLINE
    PDF = ft.icons.PICTURE_AS_PDF
    IMAGE = ft.icons.IMAGE_OUTLINE

    # Status
    ACTIVE = ft.icons.CHECK_CIRCLE_OUTLINE
    INACTIVE = ft.icons.CANCEL_OUTLINE
    PENDING = ft.icons.PENDING
    LOADING = ft.icons.LOADING

    # Navigation arrows
    ARROW_BACK = ft.icons.ARROW_BACK
    ARROW_FORWARD = ft.icons.ARROW_FORWARD
    CHEVRON_RIGHT = ft.icons.CHEVRON_RIGHT
    EXPAND_MORE = ft.icons.EXPAND_MORE
    EXPAND_LESS = ft.icons.EXPAND_LESS

    # Calendar
    CALENDAR = ft.icons.CALENDAR_MONTH
    TODAY = ft.icons.TODAY
    DATE_RANGE = ft.icons.DATE_RANGE

    # Business
    BUSINESS = ft.icons.BUSINESS_OUTLINE
    WORK = ft.icons.WORK_OUTLINE
    ASSIGNMENT = ft.icons.ASSIGNMENT_OUTLINE
    BADGE = ft.icons.BADGE_OUTLINE
    CERTIFICATE = ft.icons.CERTIFICATE
    SCHOOL = ft.icons.SCHOOL
    MEDICAL = ft.icons.MEDICAL_SERVICES

    # UI elements
    MENU = ft.icons.MENU
    MORE_VERT = ft.icons.MORE_VERT
    FULLSCREEN = ft.icons.FULLSCREEN
    VIEW_LIST = ft.icons.VIEW_LIST
    VIEW_MODULE = ft.icons.VIEW_MODULE
    GRID_VIEW = ft.icons.GRID_VIEW
    TABLE_ROWS = ft.icons.TABLE_ROWS

    # Visibility
    VISIBILITY = ft.icons.VISIBILITY
    VISIBILITY_OFF = ft.icons.VISIBILITY_OFF
    EYE = ft.icons.VISIBILITY_OUTLINE
    EYE_OFF = ft.icons.VISIBILITY_OFF_OUTLINE
