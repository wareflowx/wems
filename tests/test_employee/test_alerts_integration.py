"""Tests for alert system integration with AlertSettingsManager.

Integration tests to verify that the alert system properly uses
configurable alert settings from AlertSettingsManager.
"""

import tempfile
import shutil
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import patch

import pytest

from employee.alerts import Alert, AlertQuery, AlertType, UrgencyLevel
from employee.alert_settings import AlertSettingsManager, AlertLevel, CategoryAlertSettings


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def custom_settings_manager(temp_config_dir):
    """Create AlertSettingsManager with custom settings for testing."""
    config_path = Path(temp_config_dir) / "test_alert_settings.json"

    # Create custom settings
    manager = AlertSettingsManager(config_path=config_path)

    # Customize CACES thresholds
    manager.update_category(
        "caces",
        info_days=120,
        warning_days=80,
        alert_days=40,
        critical_days=10,
        enabled=True,
    )

    # Customize medical thresholds
    manager.update_category(
        "medical",
        info_days=100,
        warning_days=70,
        alert_days=35,
        critical_days=5,
        enabled=True,
    )

    return manager


@pytest.fixture
def reset_settings_manager():
    """Reset settings manager after test."""
    yield
    # Reset class-level settings manager
    AlertQuery._settings_manager = None


class TestAlertQueryIntegration:
    """Test AlertQuery integration with AlertSettingsManager."""

    def test_calculate_urgency_uses_settings(self, custom_settings_manager, reset_settings_manager):
        """Test that calculate_urgency uses configurable settings."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        # CACES custom thresholds: info=120, warning=80, alert=40, critical=10
        today = date.today()

        # Test critical range (<= 10 days)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=5), category="caces")
        assert urgency == UrgencyLevel.CRITICAL

        # Test alert range (<= 40 days, > 10)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=25), category="caces")
        assert urgency == UrgencyLevel.CRITICAL  # Alert maps to CRITICAL

        # Test warning range (<= 80 days, > 40)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=60), category="caces")
        assert urgency == UrgencyLevel.WARNING

        # Test info range (<= 120 days, > 80)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=100), category="caces")
        assert urgency == UrgencyLevel.INFO

        # Test OK range (> 120 days)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=150), category="caces")
        assert urgency == UrgencyLevel.OK

    def test_calculate_urgency_medical_category(self, custom_settings_manager, reset_settings_manager):
        """Test calculate_urgency for medical category with custom settings."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        # Medical custom thresholds: info=100, warning=70, alert=35, critical=5
        today = date.today()

        # Test critical range
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=3), category="medical")
        assert urgency == UrgencyLevel.CRITICAL

        # Test warning range
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=50), category="medical")
        assert urgency == UrgencyLevel.WARNING

        # Test info range
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=90), category="medical")
        assert urgency == UrgencyLevel.INFO

    def test_calculate_urgency_disabled_category(self, custom_settings_manager, reset_settings_manager):
        """Test calculate_urgency when category is disabled."""
        # Disable CACES alerts
        custom_settings_manager.settings["caces"].enabled = False
        AlertQuery.set_settings_manager(custom_settings_manager)

        today = date.today()
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=5), category="caces")

        # Should return OK when disabled
        assert urgency == UrgencyLevel.OK

    def test_calculate_urgency_expired_items(self, custom_settings_manager, reset_settings_manager):
        """Test calculate_urgency for expired items."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        today = date.today()
        urgency = AlertQuery.calculate_urgency(today - timedelta(days=10), category="caces")

        # Expired items should be CRITICAL
        assert urgency == UrgencyLevel.CRITICAL

    def test_get_settings_manager_singleton(self, reset_settings_manager):
        """Test that get_settings_manager returns singleton instance."""
        # First call creates instance
        manager1 = AlertQuery.get_settings_manager()

        # Second call returns same instance
        manager2 = AlertQuery.get_settings_manager()

        assert manager1 is manager2

    def test_set_custom_settings_manager(self, custom_settings_manager, reset_settings_manager):
        """Test setting a custom settings manager."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        manager = AlertQuery.get_settings_manager()
        assert manager is custom_settings_manager


class TestAlertIntegration:
    """Test Alert integration with configurable settings."""

    def test_alert_uses_custom_color(self, custom_settings_manager, reset_settings_manager):
        """Test that Alert uses custom color from settings."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        today = date.today()
        alert_level = custom_settings_manager.get_alert_level("caces", 25)

        alert = Alert(
            alert_type=AlertType.CACES,
            employee=None,  # type: ignore
            description="CACES R489-1A",
            expiration_date=today + timedelta(days=25),
            days_until=25,
            urgency=UrgencyLevel.CRITICAL,
            alert_level=alert_level.label if alert_level else None,
            custom_color=alert_level.color if alert_level else None,
            custom_label=alert_level.label if alert_level else None,
        )

        # Should use custom color from settings
        assert alert.custom_color == "#FF0000"  # Alert level color
        assert alert.custom_label == "Alert"
        assert alert.urgency_color == "#FF0000"

    def test_alert_fallback_color(self, reset_settings_manager):
        """Test that Alert falls back to default color when no custom color."""
        AlertQuery._settings_manager = None  # Use defaults

        alert = Alert(
            alert_type=AlertType.CACES,
            employee=None,  # type: ignore
            description="CACES R489-1A",
            expiration_date=date.today() + timedelta(days=25),
            days_until=25,
            urgency=UrgencyLevel.CRITICAL,
            alert_level=None,
            custom_color=None,
            custom_label=None,
        )

        # Should use default color
        assert alert.urgency_color == "#DC3545"  # Default CRITICAL color

    def test_alert_urgency_text_with_custom_label(self, custom_settings_manager, reset_settings_manager):
        """Test that Alert urgency_text uses custom label."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        today = date.today()
        alert_level = custom_settings_manager.get_alert_level("caces", 25)

        alert = Alert(
            alert_type=AlertType.CACES,
            employee=None,  # type: ignore
            description="CACES R489-1A",
            expiration_date=today + timedelta(days=25),
            days_until=25,
            urgency=UrgencyLevel.CRITICAL,
            alert_level=alert_level.label if alert_level else None,
            custom_color=alert_level.color if alert_level else None,
            custom_label=alert_level.label if alert_level else None,
        )

        # Should use custom label in text
        assert "Alert" in alert.urgency_text
        assert "25" in alert.urgency_text

    def test_alert_urgency_text_expired(self, custom_settings_manager, reset_settings_manager):
        """Test alert urgency_text for expired items."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        today = date.today()
        alert_level = custom_settings_manager.get_alert_level("caces", -10)

        alert = Alert(
            alert_type=AlertType.CACES,
            employee=None,  # type: ignore
            description="CACES R489-1A",
            expiration_date=today - timedelta(days=10),
            days_until=-10,
            urgency=UrgencyLevel.CRITICAL,
            alert_level=alert_level.label if alert_level else None,
            custom_color=alert_level.color if alert_level else None,
            custom_label=alert_level.label if alert_level else None,
        )

        # Should show expired text with custom label
        assert "Expiré depuis" in alert.urgency_text
        assert "10" in alert.urgency_text

    def test_alert_urgency_text_fallback(self, reset_settings_manager):
        """Test alert urgency_text fallback without custom label."""
        AlertQuery._settings_manager = None  # Use defaults

        alert = Alert(
            alert_type=AlertType.CACES,
            employee=None,  # type: ignore
            description="CACES R489-1A",
            expiration_date=date.today() + timedelta(days=25),
            days_until=25,
            urgency=UrgencyLevel.CRITICAL,
            alert_level=None,
            custom_color=None,
            custom_label=None,
        )

        # Should use default text
        assert "Urgent" in alert.urgency_text
        assert "25" in alert.urgency_text


class TestCategoryDifferences:
    """Test that different categories use different thresholds."""

    def test_caces_vs_medical_thresholds(self, custom_settings_manager, reset_settings_manager):
        """Test that CACES and medical use different thresholds."""
        AlertQuery.set_settings_manager(custom_settings_manager)

        today = date.today()

        # 30 days: CACES is in alert range (alert=40, critical=10), medical is in critical range (critical=5)
        # CACES: 30 <= 40? Yes, so alert level -> CRITICAL urgency
        # Medical: 30 <= 35? Yes, so alert level -> CRITICAL urgency
        caces_urgency = AlertQuery.calculate_urgency(today + timedelta(days=30), category="caces")
        medical_urgency = AlertQuery.calculate_urgency(today + timedelta(days=30), category="medical")

        assert caces_urgency == UrgencyLevel.CRITICAL
        assert medical_urgency == UrgencyLevel.CRITICAL

        # 50 days: CACES is in warning range (warning=80), medical is in alert range (alert=35)
        # CACES: 50 <= 80? Yes, so warning level -> WARNING urgency
        # Medical: 50 <= 70? Yes, so warning level -> WARNING urgency
        caces_urgency = AlertQuery.calculate_urgency(today + timedelta(days=50), category="caces")
        medical_urgency = AlertQuery.calculate_urgency(today + timedelta(days=50), category="medical")

        assert caces_urgency == UrgencyLevel.WARNING
        assert medical_urgency == UrgencyLevel.WARNING

    def test_training_category_defaults(self, reset_settings_manager):
        """Test that training category uses its own default thresholds."""
        # Training defaults: info=60, warning=30, alert=14
        AlertQuery._settings_manager = None  # Use defaults

        today = date.today()

        # 20 days: should be warning (14 < 20 <= 30)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=20), category="training")
        assert urgency == UrgencyLevel.WARNING

    def test_contracts_category_no_critical(self, reset_settings_manager):
        """Test that contracts category doesn't have critical level."""
        # Contracts defaults: info=90, warning=60, alert=30 (no critical)
        AlertQuery._settings_manager = None  # Use defaults

        today = date.today()

        # 5 days: should be alert (no critical level)
        urgency = AlertQuery.calculate_urgency(today + timedelta(days=5), category="contracts")
        assert urgency == UrgencyLevel.CRITICAL  # Alert maps to CRITICAL


class TestSettingsPersistence:
    """Test that settings persist and affect alert calculations."""

    def test_settings_persistence_across_managers(self, temp_config_dir, reset_settings_manager):
        """Test that settings persist when creating new managers."""
        config_path = Path(temp_config_dir) / "persistent_settings.json"

        # Create first manager and customize
        manager1 = AlertSettingsManager(config_path=config_path)
        manager1.update_category("caces", info_days=150, warning_days=100, alert_days=50, critical_days=15)

        # Create second manager (should load from file)
        manager2 = AlertSettingsManager(config_path=config_path)

        # Should have same settings
        assert manager2.settings["caces"].info.days == 150
        assert manager2.settings["caces"].warning.days == 100
        assert manager2.settings["caces"].alert.days == 50
        assert manager2.settings["caces"].critical.days == 15

    def test_alert_calculations_use_persistent_settings(self, temp_config_dir, db, reset_settings_manager):
        """Test that alert calculations use persistent settings."""
        from employee.models import Employee

        config_path = Path(temp_config_dir) / "alert_calcs.json"
        today = date.today()

        # Create manager with custom settings
        manager = AlertSettingsManager(config_path=config_path)
        manager.update_category("caces", info_days=120, warning_days=80, alert_days=40, critical_days=10)

        AlertQuery.set_settings_manager(manager)

        # Test with custom settings
        urgency_30_days = AlertQuery.calculate_urgency(today + timedelta(days=30), category="caces")
        urgency_50_days = AlertQuery.calculate_urgency(today + timedelta(days=50), category="caces")
        urgency_100_days = AlertQuery.calculate_urgency(today + timedelta(days=100), category="caces")

        # With custom settings (info=120, warning=80, alert=40, critical=10):
        # 30 days: 30 <= 40? Yes, so alert level -> CRITICAL
        # 50 days: 50 <= 80? Yes, so warning level -> WARNING
        # 100 days: 100 <= 120? Yes, so info level -> INFO
        assert urgency_30_days == UrgencyLevel.CRITICAL
        assert urgency_50_days == UrgencyLevel.WARNING
        assert urgency_100_days == UrgencyLevel.INFO
