"""Automated tests for GharBeka Phase 1 Foundation & UI."""

import os
import sys
import pytest
from PySide6.QtWidgets import QApplication

# Ensure offscreen rendering for headless testing environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main_window import GharBekaMainWindow, MonitorIllustrationWidget
from src.styles import MAIN_STYLE_SHEET


@pytest.fixture(scope="session")
def qapp():
    """Ensure a QApplication instance exists for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def window(qapp):
    """Fixture providing a fresh GharBekaMainWindow instance."""
    win = GharBekaMainWindow()
    return win


def test_main_window_initialization(window):
    """Test window title, initial dimensions and basic layout initialization."""
    assert "GharBeka" in window.windowTitle()
    assert window.minimumWidth() >= 960
    assert window.minimumHeight() >= 680
    assert window.centralWidget() is not None


def test_styles_loaded():
    """Verify QSS stylesheet is non-empty and contains key classes."""
    assert len(MAIN_STYLE_SHEET) > 0
    assert "QMainWindow" in MAIN_STYLE_SHEET
    assert "dashboard-card" in MAIN_STYLE_SHEET
    assert "RotateButton" in MAIN_STYLE_SHEET
    assert "UnrotateButton" in MAIN_STYLE_SHEET


def test_monitor_widget_rotation():
    """Verify MonitorIllustrationWidget handles rotation updates correctly."""
    widget = MonitorIllustrationWidget()
    assert widget.rotation_angle == 0

    widget.set_rotation_angle(90)
    assert widget.rotation_angle == 90

    widget.set_rotation_angle(450)  # 450 % 360 == 90
    assert widget.rotation_angle == 90

    widget.set_rotation_angle(0)
    assert widget.rotation_angle == 0


def test_initial_screen_status(window):
    """Verify initial screen status indicator reads 'Screen is straight'."""
    assert "Screen is straight" in window.status_indicator.text()
    assert window.monitor_widget.rotation_angle == 0


def test_rotate_button_click(window):
    """Verify clicking ROTATE MY SCREEN updates simulation state and feedback."""
    window.btn_rotate.click()

    assert window.monitor_widget.rotation_angle == 90
    assert "rotated" in window.status_indicator.text().lower()
    assert "90°" in window.status_indicator.text()
    assert "Simulation Mode" in window.feedback_banner.text()


def test_unrotate_button_click(window):
    """Verify clicking UNROTATE MY SCREEN restores straight orientation."""
    # First rotate
    window.btn_rotate.click()
    assert window.monitor_widget.rotation_angle == 90

    # Then unrotate
    window.btn_unrotate.click()
    assert window.monitor_widget.rotation_angle == 0
    assert "Screen is straight" in window.status_indicator.text()
    assert "successfully unrotated" in window.feedback_banner.text().lower()


def test_navigation_feedback(window):
    """Verify clicking sidebar navigation updates feedback."""
    window.btn_nav_plans.click()
    assert "Premium Plans" in window.feedback_banner.text()

    window.btn_nav_settings.click()
    assert "Settings" in window.feedback_banner.text()

    window.btn_nav_dashboard.click()
    assert "Dashboard" in window.feedback_banner.text()


def test_plan_buttons_feedback(window):
    """Verify clicking subscription plan buttons triggers satire notice without charging."""
    window._on_plan_clicked("Premium", "৳499")
    assert "Premium" in window.feedback_banner.text()
    assert "Satire" in window.feedback_banner.text()
    assert "disabled" in window.feedback_banner.text().lower()


def test_window_resizing(window):
    """Verify window resizes cleanly to standard desktop resolutions."""
    for width, height in [(960, 680), (1280, 800), (1920, 1080)]:
        window.resize(width, height)
        assert window.width() == width
        assert window.height() == height
