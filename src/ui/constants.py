"""Design tokens and constants for consistent UI styling.

This module defines all design tokens including spacing, typography,
colors, and other visual properties used throughout the application.
"""

from enum import Enum


class Spacing(Enum):
    """Spacing tokens for consistent margins and padding."""
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


class BorderRadius(Enum):
    """Border radius tokens for consistent corner rounding."""
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    FULL = 9999  # For pills/circles


class FontSize(Enum):
    """Font size tokens following Material Design typography scale."""
    DISPLAY_LARGE = 57
    DISPLAY_MEDIUM = 45
    DISPLAY_SMALL = 36
    HEADLINE_LARGE = 32
    HEADLINE_MEDIUM = 28
    HEADLINE_SMALL = 24
    TITLE_LARGE = 22
    TITLE_MEDIUM = 16
    TITLE_SMALL = 14
    BODY_LARGE = 16
    BODY_MEDIUM = 14
    BODY_SMALL = 12
    LABEL_LARGE = 14
    LABEL_MEDIUM = 12
    LABEL_SMALL = 11


class IconSize(Enum):
    """Icon size tokens."""
    XS = 16
    SM = 20
    MD = 24
    LG = 32
    XL = 48


class Breakpoint(Enum):
    """Responsive breakpoints."""
    XS = 576
    SM = 768
    MD = 992
    LG = 1200
    XL = 1400


# Layout constants
MAX_CONTENT_WIDTH = 1200
SIDEBAR_WIDTH = 250
NAVBAR_HEIGHT = 56
APPBAR_HEIGHT = 64

# Animation durations (in milliseconds)
ANIMATION_FAST = 150
ANIMATION_NORMAL = 300
ANIMATION_SLOW = 500

# Z-index layers
Z_NAVBAR = 100
Z_DROPDOWN = 200
Z_MODAL = 300
Z_TOOLTIP = 400
Z_SNACKBAR = 500
