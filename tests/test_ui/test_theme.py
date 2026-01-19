"""Tests for theme system and UI components."""

import pytest
from src.ui.constants import Spacing, BorderRadius, FontSize, IconSize, Breakpoint
from src.ui.theme import AppTheme
from src.ui.components.buttons import AppButton, AppIconButton
from src.ui.components.cards import AppCard, StatCard
from src.ui.components.icons import Icons, AppIcon
from src.ui.components.chips import AppChip, AppBadge, StatusBadge
from src.ui.components.inputs import AppTextField, AppDropdown
from src.ui.components.feedback import AppSnackBar, ConfirmDialog


class TestConstants:
    """Test design token constants."""

    def test_spacing_enum(self):
        """Test spacing enum values."""
        assert Spacing.XS.value == 4
        assert Spacing.SM.value == 8
        assert Spacing.MD.value == 16
        assert Spacing.LG.value == 24
        assert Spacing.XL.value == 32

    def test_border_radius_enum(self):
        """Test border radius enum values."""
        assert BorderRadius.SM.value == 8
        assert BorderRadius.MD.value == 12
        assert BorderRadius.LG.value == 16

    def test_font_size_enum(self):
        """Test font size enum has expected values."""
        assert FontSize.BODY_LARGE.value == 16
        assert FontSize.BODY_MEDIUM.value == 14

    def test_icon_size_enum(self):
        """Test icon size enum has expected values."""
        assert IconSize.SM.value == 20
        assert IconSize.MD.value == 24
        assert IconSize.LG.value == 32

    def test_breakpoint_enum(self):
        """Test breakpoint enum values."""
        assert Breakpoint.XS.value == 576
        assert Breakpoint.SM.value == 768
        assert Breakpoint.MD.value == 992


class TestAppTheme:
    """Test AppTheme class."""

    def test_get_light_theme_returns_theme(self):
        """Test get_light_theme returns a ft.Theme object."""
        import flet as ft

        theme = AppTheme.get_light_theme()
        assert isinstance(theme, ft.Theme)
        assert theme.theme_mode.value == "light"

    def test_get_dark_theme_returns_theme(self):
        """Test get_dark_theme returns a ft.Theme object."""
        import flet as ft

        theme = AppTheme.get_dark_theme()
        assert isinstance(theme, ft.Theme)
        assert theme.theme_mode.value == "dark"

    def test_get_button_style_returns_styles(self):
        """Test get_button_style returns button styles."""
        import flet as ft

        primary_style = AppTheme.get_button_style("primary")
        assert isinstance(primary_style, ft.ButtonStyle)

        success_style = AppTheme.get_button_style("success")
        assert isinstance(success_style, ft.ButtonStyle)

        # Test invalid variant defaults to primary
        default_style = AppTheme.get_button_style("invalid")
        assert isinstance(default_style, ft.ButtonStyle)

    def test_semantic_colors_defined(self):
        """Test semantic colors are defined."""
        assert AppTheme.PRIMARY
        assert AppTheme.SUCCESS
        assert AppTheme.WARNING
        assert AppTheme.ERROR
        assert AppTheme.INFO

    def test_get_card_style_returns_dict(self):
        """Test get_card_style returns dictionary."""
        style = AppTheme.get_card_style()
        assert isinstance(style, dict)
        assert "bgcolor" in style
        assert "border_radius" in style
        assert "padding" in style


class TestIcons:
    """Test Icons class."""

    def test_icons_have_values(self):
        """Test icon constants have string values."""
        assert Icons.HOME
        assert Icons.PEOPLE
        assert Icons.SETTINGS
        assert Icons.ADD
        assert Icons.EDIT
        assert Icons.DELETE
        assert Icons.SUCCESS
        assert Icons.WARNING
        assert Icons.ERROR


class TestComponents:
    """Test UI components instantiation."""

    def test_app_icon_creation(self):
        """Test AppIcon can be instantiated."""
        icon = AppIcon(Icons.HOME, size=24)
        assert icon.name == Icons.HOME
        assert icon.size == 24

    def test_app_button_creation(self):
        """Test AppButton can be instantiated."""
        button = AppButton("Click Me", variant="primary")
        assert button.text == "Click Me"

    def test_app_button_with_icon(self):
        """Test AppButton with icon can be created."""
        button = AppButton("Save", icon=Icons.SAVE)
        assert button.content is not None

    def test_app_icon_button_creation(self):
        """Test AppIconButton can be instantiated."""
        button = AppIconButton(Icons.ADD, tooltip="Add")
        assert button.icon == Icons.ADD
        assert button.tooltip == "Add"

    def test_app_card_creation(self):
        """Test AppCard can be instantiated."""
        import flet as ft

        card = AppCard(content=ft.Text("Card content"))
        assert card.content is not None

    def test_app_card_with_title(self):
        """Test AppCard with title can be created."""
        import flet as ft

        card = AppCard(
            content=ft.Text("Content"),
            title="Card Title"
        )
        assert card.content is not None

    def test_stat_card_creation(self):
        """Test StatCard can be instantiated."""
        card = StatCard(
            label="Test Stat",
            value=42,
            icon=Icons.HOME,
            color=ft.Colors.BLUE
        )
        assert card.content is not None

    def test_app_chip_creation(self):
        """Test AppChip can be instantiated."""
        chip = AppChip(label="Filter", selected=False)
        assert chip.label is not None

    def test_app_badge_creation(self):
        """Test AppBadge can be instantiated."""
        badge = AppBadge(text="New", count=5, variant="primary")
        assert badge.content is not None

    def test_status_badge_creation(self):
        """Test StatusBadge can be instantiated."""
        badge = StatusBadge(status="active", variant="active")
        assert badge.content is not None

    def test_app_text_field_creation(self):
        """Test AppTextField can be instantiated."""
        field = AppTextField(label="Test Field")
        assert field.label == "Test Field"

    def test_app_text_field_required(self):
        """Test AppTextField with required flag."""
        field = AppTextField(label="Name", required=True)
        assert " * " in field.label

    def test_app_dropdown_creation(self):
        """Test AppDropdown can be instantiated."""
        options = [("val1", "Value 1"), ("val2", "Value 2")]
        dropdown = AppDropdown(label="Select", options=options)
        assert dropdown.label == "Select"

    def test_app_snack_bar_creation(self):
        """Test AppSnackBar can be instantiated."""
        snackbar = AppSnackBar(message="Test message", variant="info")
        assert snackbar.content is not None

    def test_confirm_dialog_creation(self):
        """Test ConfirmDialog can be instantiated."""
        dialog = ConfirmDialog(
            title="Confirm",
            message="Are you sure?",
        )
        assert dialog.title is not None
        assert dialog.content is not None


class TestFeedbackHelpers:
    """Test feedback helper functions."""

    def test_show_snackbar_function_exists(self):
        """Test show_snackbar helper function exists."""
        from src.ui.components.feedback import show_snackbar
        assert callable(show_snackbar)

    def test_show_confirm_dialog_function_exists(self):
        """Test show_confirm_dialog helper function exists."""
        from src.ui.components.feedback import show_confirm_dialog
        assert callable(show_confirm_dialog)

    def test_show_error_dialog_function_exists(self):
        """Test show_error_dialog helper function exists."""
        from src.ui.components.feedback import show_error_dialog
        assert callable(show_error_dialog)

    def test_show_loading_dialog_function_exists(self):
        """Test show_loading_dialog helper function exists."""
        from src.ui.components.feedback import show_loading_dialog
        assert callable(show_loading_dialog)


@pytest.mark.parametrize("variant", ["primary", "secondary", "success", "warning", "error", "outline"])
def test_all_button_variants_work(variant):
    """Test all button variants can be created."""
    button = AppButton("Test", variant=variant)
    assert button is not None


@pytest.mark.parametrize("variant", ["info", "success", "warning", "error"])
def test_all_snackbar_variants_work(variant):
    """Test all snackbar variants can be created."""
    snackbar = AppSnackBar(message="Test", variant=variant)
    assert snackbar is not None
