"""Comprehensive Automated Tests for GharBeka Phase 5 Integration & Reliability."""

import os
import sys
import ctypes
import inspect
from unittest.mock import MagicMock, patch
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QCloseEvent

# Ensure offscreen rendering for headless testing environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main_window import GharBekaMainWindow, MonitorIllustrationWidget
from src.display_controller import (
    DisplayController,
    DEVMODEW,
    DISP_CHANGE_SUCCESSFUL,
    DISP_CHANGE_FAILED,
    DISP_CHANGE_BADMODE,
    DMDO_DEFAULT,
    DMDO_90,
)
from src.recovery_manager import RecoveryManager
from src import main_window, dialogs, styles, display_controller, recovery_manager


@pytest.fixture(scope="session")
def qapp():
    """Ensure a QApplication instance exists for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# Isolate runtime data directory during automated test execution
import tempfile
os.environ["GHARBEKA_DATA_DIR"] = os.path.join(tempfile.gettempdir(), "GharBeka_pytest_isolated")


@pytest.fixture
def window(qapp):
    """Fixture providing a fresh GharBekaMainWindow instance in safe Simulation mode."""
    win = GharBekaMainWindow()
    win.set_animations_enabled(False)  # Speed up unit test transitions
    win.recovery_manager.set_timeout_seconds(60)
    return win


# --- Phase 1 & 2 Core UI Tests ---

def test_main_window_initialization(window):
    """Test window title, initial dimensions and basic layout initialization."""
    assert "GharBeka" in window.windowTitle()
    assert window.minimumWidth() >= 960
    assert window.minimumHeight() >= 680
    assert window.centralWidget() is not None
    assert window.subscription_tier == "Free"
    assert window.display_mode == "SIMULATION"


def test_styles_loaded():
    """Verify QSS stylesheet is non-empty and contains key classes."""
    assert len(styles.MAIN_STYLE_SHEET) > 0
    assert "QMainWindow" in styles.MAIN_STYLE_SHEET
    assert "dashboard-card" in styles.MAIN_STYLE_SHEET
    assert "RotateButton" in styles.MAIN_STYLE_SHEET
    assert "UnrotateButton" in styles.MAIN_STYLE_SHEET


def test_monitor_widget_rotation():
    """Verify MonitorIllustrationWidget handles rotation updates correctly."""
    widget = MonitorIllustrationWidget()
    assert widget.rotation_angle == 0.0

    widget.set_rotation_angle(90, animated=False)
    assert widget.rotation_angle == 90.0

    widget.set_rotation_angle(450, animated=False)
    assert widget.rotation_angle == 90.0

    widget.set_rotation_angle(0, animated=False)
    assert widget.rotation_angle == 0.0


def test_rotate_simulated_screen(window):
    """Workflow A: Rotating the simulated screen."""
    assert window.monitor_widget.rotation_angle == 0.0
    window.btn_rotate.click()

    assert window.monitor_widget.rotation_angle == 90.0
    assert "rotated" in window.status_indicator.text().lower()


def test_prevent_redundant_rotation(window):
    """Workflow A: Preventing redundant rotation."""
    window.btn_unrotate.click()
    assert window.monitor_widget.rotation_angle == 0.0

    window.btn_rotate.click()
    assert window.monitor_widget.rotation_angle == 90.0

    window.btn_rotate.click()
    assert window.monitor_widget.rotation_angle == 90.0
    assert "already rotated" in window.feedback_banner.text().lower()


def test_subscription_dialog_open_close(window):
    """Workflow A: Opening and closing the subscription dialog."""
    window.btn_rotate.click()
    window.btn_unrotate.click()

    dialog = window._active_subscription_dialog
    assert dialog is not None
    assert dialog.isVisible()

    dialog.btn_close.click()
    assert window._active_subscription_dialog is None
    assert window.monitor_widget.rotation_angle == 90.0


def test_workflow_a_simulation_full_lifecycle(window):
    """Workflow A Complete Lifecycle Integration Test."""
    assert window.display_mode == "SIMULATION"

    # 1. Rotate
    window.btn_rotate.click()
    assert window.monitor_widget.rotation_angle == 90.0
    assert window.recovery_manager.is_timer_running

    # 2. Open subscription dialog on Free tier
    window.btn_unrotate.click()
    sub_dialog = window._active_subscription_dialog
    assert sub_dialog is not None

    # 3. Cancel dialog
    sub_dialog.btn_close.click()
    assert window._active_subscription_dialog is None
    assert window.monitor_widget.rotation_angle == 90.0

    # 4. Trigger Emergency Recovery
    window.emergency_recovery()
    assert window.monitor_widget.rotation_angle == 0.0
    assert not window.recovery_manager.is_timer_running


def test_workflow_b_premium_demo_full_lifecycle(window):
    """Workflow B Complete Lifecycle Integration Test."""
    window.btn_rotate.click()
    window.btn_unrotate.click()

    sub_dialog = window._active_subscription_dialog
    assert sub_dialog is not None

    # 1. Open checkout & cancel
    sub_dialog.btn_upgrade.click()
    checkout_dialog = window._active_checkout_dialog
    assert checkout_dialog is not None
    checkout_dialog.btn_cancel.click()

    assert window.subscription_tier == "Free"
    assert window.monitor_widget.rotation_angle == 90.0

    # 2. Open checkout & confirm
    sub_dialog.btn_upgrade.click()
    checkout_dialog = window._active_checkout_dialog
    assert checkout_dialog is not None
    checkout_dialog.btn_confirm.click()

    assert window.subscription_tier == "Premium"

    # 3. Unrotate after upgrade
    window.btn_unrotate.click()
    assert window.monitor_widget.rotation_angle == 0.0


def test_emergency_recovery_bypasses_premium(window):
    """Workflow B/D: Emergency recovery bypasses premium dialog."""
    window.reset_to_free_tier()
    window.btn_rotate.click()
    assert window.monitor_widget.rotation_angle == 90.0

    window.emergency_recovery()
    assert window.monitor_widget.rotation_angle == 0.0
    assert window._active_subscription_dialog is None


# --- Phase 3 & 5 Display Controller Tests ---

def test_display_controller_is_windows():
    ctrl = DisplayController()
    assert isinstance(ctrl.is_windows(), bool)


def test_get_display_devices():
    ctrl = DisplayController()
    devices = ctrl.get_display_devices()
    assert isinstance(devices, list)
    assert len(devices) >= 1


def test_get_display_orientation():
    ctrl = DisplayController()
    mock_user32 = MagicMock()

    def mock_enum_settings(device_name, mode_num, byref_dm):
        dm = DEVMODEW()
        dm.u1.s2.dmDisplayOrientation = DMDO_DEFAULT
        ctypes.memmove(byref_dm, ctypes.byref(dm), ctypes.sizeof(DEVMODEW))
        return 1

    mock_user32.EnumDisplaySettingsW = mock_enum_settings
    with patch.object(ctrl, "get_user32", return_value=mock_user32):
        orient = ctrl.get_display_orientation(r"\\.\DISPLAY1")
        assert orient == DMDO_DEFAULT


def test_is_orientation_supported():
    ctrl = DisplayController()
    mock_user32 = MagicMock()

    def mock_enum_settings(device_name, mode_num, byref_dm):
        dm = DEVMODEW()
        dm.u1.s2.dmDisplayOrientation = DMDO_DEFAULT
        dm.dmPelsWidth = 1920
        dm.dmPelsHeight = 1080
        ctypes.memmove(byref_dm, ctypes.byref(dm), ctypes.sizeof(DEVMODEW))
        return 1

    mock_user32.EnumDisplaySettingsW = mock_enum_settings
    mock_user32.ChangeDisplaySettingsExW.return_value = DISP_CHANGE_SUCCESSFUL

    with patch.object(ctrl, "get_user32", return_value=mock_user32):
        supported, msg = ctrl.is_orientation_supported(r"\\.\DISPLAY1", DMDO_90)
        assert supported is True

        mock_user32.ChangeDisplaySettingsExW.return_value = DISP_CHANGE_BADMODE
        supported_bad, msg_bad = ctrl.is_orientation_supported(r"\\.\DISPLAY1", DMDO_90)
        assert supported_bad is False


def test_rotate_display_success():
    ctrl = DisplayController()
    mock_user32 = MagicMock()

    current_orient = [DMDO_DEFAULT]

    def mock_enum_settings(device_name, mode_num, byref_dm):
        dm = DEVMODEW()
        dm.u1.s2.dmDisplayOrientation = current_orient[0]
        dm.dmPelsWidth = 1920
        dm.dmPelsHeight = 1080
        ctypes.memmove(byref_dm, ctypes.byref(dm), ctypes.sizeof(DEVMODEW))
        return 1

    def mock_change_settings(dev_name, devmode_ptr, hwnd, flags, param):
        current_orient[0] = DMDO_90
        return DISP_CHANGE_SUCCESSFUL

    mock_user32.EnumDisplaySettingsW = mock_enum_settings
    mock_user32.ChangeDisplaySettingsExW = mock_change_settings

    with patch.object(ctrl, "is_windows", return_value=True), \
         patch.object(ctrl, "get_user32", return_value=mock_user32), \
         patch.object(ctrl, "get_display_devices", return_value=[{"device_name": r"\\.\DISPLAY1", "is_primary": True}]):

        success, msg = ctrl.rotate_display(r"\\.\DISPLAY1", DMDO_90)
        assert success is True
        assert "successfully rotated" in msg.lower()


def test_unsupported_orientation():
    ctrl = DisplayController()
    with patch.object(ctrl, "is_windows", return_value=True), \
         patch.object(ctrl, "get_display_devices", return_value=[{"device_name": r"\\.\DISPLAY1", "is_primary": True}]), \
         patch.object(ctrl, "is_orientation_supported", return_value=(False, "Driver rejected mode")):

        success, msg = ctrl.rotate_display(r"\\.\DISPLAY1", DMDO_90)
        assert success is False
        assert "unsupported" in msg.lower()


def test_display_api_failure():
    ctrl = DisplayController()
    mock_user32 = MagicMock()

    def mock_enum_settings(device_name, mode_num, byref_dm):
        dm = DEVMODEW()
        dm.u1.s2.dmDisplayOrientation = DMDO_DEFAULT
        ctypes.memmove(byref_dm, ctypes.byref(dm), ctypes.sizeof(DEVMODEW))
        return 1

    mock_user32.EnumDisplaySettingsW = mock_enum_settings
    mock_user32.ChangeDisplaySettingsExW.return_value = DISP_CHANGE_FAILED

    with patch.object(ctrl, "is_windows", return_value=True), \
         patch.object(ctrl, "get_user32", return_value=mock_user32), \
         patch.object(ctrl, "get_display_devices", return_value=[{"device_name": r"\\.\DISPLAY1", "is_primary": True}]), \
         patch.object(ctrl, "is_orientation_supported", return_value=(True, "OK")):

        success, msg = ctrl.rotate_display(r"\\.\DISPLAY1", DMDO_90)
        assert success is False
        assert "failed" in msg.lower()


def test_invalid_display_selection():
    ctrl = DisplayController()
    with patch.object(ctrl, "is_windows", return_value=True), \
         patch.object(ctrl, "get_display_devices", return_value=[{"device_name": r"\\.\DISPLAY1", "is_primary": True}]):

        success, msg = ctrl.rotate_display(r"\\.\DISPLAY_NONEXISTENT", DMDO_90)
        assert success is False
        assert "no longer connected" in msg.lower()


def test_restore_original_orientation():
    ctrl = DisplayController()
    mock_user32 = MagicMock()

    mock_user32.EnumDisplaySettingsW.return_value = 1
    mock_user32.ChangeDisplaySettingsExW.return_value = DISP_CHANGE_SUCCESSFUL

    with patch.object(ctrl, "is_windows", return_value=True), \
         patch.object(ctrl, "get_user32", return_value=mock_user32), \
         patch.object(ctrl, "get_display_devices", return_value=[{"device_name": r"\\.\DISPLAY1", "is_primary": True}]), \
         patch.object(ctrl, "is_orientation_supported", return_value=(True, "OK")):

        ctrl.rotate_display(r"\\.\DISPLAY1", DMDO_90)
        assert r"\\.\DISPLAY1" in ctrl._saved_original_modes

        success, msg = ctrl.restore_original_orientation(r"\\.\DISPLAY1")
        assert success is True
        assert "successfully restored" in msg.lower()


def test_cancel_rotation_confirmation(window):
    window.set_display_mode("REAL")
    with patch.object(window.display_controller, "is_orientation_supported", return_value=(True, "OK")), \
         patch.object(window, "_confirm_physical_rotation", return_value=False):
        window._on_rotate_clicked()
        assert "canceled by user" in window.feedback_banner.text().lower()


def test_non_windows_platform_behavior():
    ctrl = DisplayController()
    with patch.object(ctrl, "is_windows", return_value=False):
        success, msg = ctrl.rotate_display(r"\\.\DISPLAY1", DMDO_90)
        assert success is False
        assert "Microsoft Windows" in msg


# --- Workflow D: Recovery System Tests ---

def test_recovery_countdown_starts(window):
    """Workflow D: Countdown starts after rotation."""
    assert not window.recovery_manager.is_timer_running
    window.btn_rotate.click()

    assert window.recovery_manager.is_timer_running
    assert window.recovery_manager.remaining_seconds == 60


def test_recovery_countdown_expires(window):
    """Workflow D: Countdown reaches zero and requests recovery."""
    window.btn_rotate.click()
    assert window.recovery_manager.is_timer_running

    window.recovery_manager._remaining_seconds = 1
    window.recovery_manager._on_timer_tick()

    assert not window.recovery_manager.is_timer_running
    assert window.monitor_widget.rotation_angle == 0.0


def test_successful_recovery_stops_timer(window):
    """Workflow D: Successful recovery stops the timer."""
    window.btn_rotate.click()
    assert window.recovery_manager.is_timer_running

    window.emergency_recovery()
    assert not window.recovery_manager.is_timer_running
    assert window.monitor_widget.rotation_angle == 0.0


def test_failed_recovery_shows_warning(window):
    """Workflow D: Failed recovery shows a persistent warning."""
    window.show()
    window.set_display_mode("REAL")

    with patch.object(window.display_controller, "is_windows", return_value=True), \
         patch.object(window.display_controller, "restore_original_orientation", return_value=(False, "Hardware display error")):

        window.emergency_recovery()
        assert not window.btn_retry_recovery.isHidden()
        assert "RECOVERY FAILED" in window.feedback_banner.text()
        assert "Win+I" in window.feedback_banner.text()


def test_prevent_duplicate_timers(window):
    """Workflow D: Duplicate timers are prevented."""
    window.recovery_manager.start_countdown("SIMULATION")
    assert window.recovery_manager.is_timer_running

    window.recovery_manager.start_countdown("SIMULATION")
    assert window.recovery_manager.is_timer_running
    assert window.recovery_manager.remaining_seconds == 60


def test_repeated_recovery_requests_safe(window):
    """Workflow D: Repeated recovery requests do not corrupt state."""
    window.emergency_recovery()
    window.emergency_recovery()
    window.emergency_recovery()

    assert window.monitor_widget.rotation_angle == 0.0
    assert not window.recovery_manager.is_timer_running


def test_simulation_recovery_no_win_api(window):
    """Workflow D: Recovery works in simulation mode without calling Windows APIs."""
    window.set_display_mode("SIMULATION")
    window.btn_rotate.click()

    mock_restore = MagicMock()
    with patch.object(window.display_controller, "restore_original_orientation", mock_restore):
        window.emergency_recovery()
        assert mock_restore.call_count == 0
        assert window.monitor_widget.rotation_angle == 0.0


def test_shutdown_attempts_recovery(window):
    """Workflow D: Normal application shutdown attempts recovery when appropriate."""
    window.set_display_mode("REAL")
    window.recovery_manager._is_real_rotation_active = True

    mock_restore = MagicMock()
    with patch.object(window.display_controller, "restore_original_orientation", mock_restore):
        close_event = QCloseEvent()
        window.closeEvent(close_event)
        assert mock_restore.call_count == 1


def test_shortcut_registration_failure_handling():
    """Workflow D: Shortcut registration failure handled safely."""
    ctrl = DisplayController()
    mgr = RecoveryManager(ctrl)

    mock_user32 = MagicMock()
    mock_user32.RegisterHotKey.return_value = 0

    with patch.object(ctrl, "is_windows", return_value=True), \
         patch("ctypes.windll", create=True) as mock_windll:

        mock_windll.user32 = mock_user32
        success, msg = mgr.register_global_hotkey(12345)
        assert success is False
        assert "currently in use" in msg.lower()


# --- Workflow E: Navigation, Settings & Edge Cases ---

def test_workflow_e_navigation(window):
    """Workflow E: Dashboard and Premium Plans navigation."""
    window.btn_nav_plans.click()
    assert "Premium Plans" in window.feedback_banner.text()

    window.btn_nav_dashboard.click()
    assert "Dashboard" in window.feedback_banner.text()


def test_workflow_e_settings_and_timeout(window):
    """Workflow E: Settings dialog and timeout configuration."""
    window.open_settings_dialog()
    settings_dialog = window._active_settings_dialog
    assert settings_dialog is not None

    # Test timeout change
    settings_dialog.combo_timeout.setCurrentIndex(0)  # 15 seconds
    assert window.recovery_manager.timeout_seconds == 15

    settings_dialog.btn_close.click()
    assert window._active_settings_dialog is None


def test_timeout_bounds_validation():
    """Test timeout bounds validation in RecoveryManager."""
    ctrl = DisplayController()
    mgr = RecoveryManager(ctrl)

    mgr.set_timeout_seconds(2)  # Too small, ignored (<5)
    assert mgr.timeout_seconds == 60

    mgr.set_timeout_seconds(500)  # Too large, ignored (>300)
    assert mgr.timeout_seconds == 60

    mgr.set_timeout_seconds(30)  # Valid
    assert mgr.timeout_seconds == 30


def test_window_resizing(window):
    """Verify window resizes cleanly to standard desktop resolutions."""
    for width, height in [(960, 680), (1280, 800), (1920, 1080)]:
        window.resize(width, height)
        assert window.width() == width
        assert window.height() == height


# --- Workflow F: Phase 6 Packaging & Runtime Tests ---

def test_runtime_paths_and_asset_resolution():
    """Verify resource resolution and user data directories."""
    from src.runtime import get_base_dir, get_asset_path, get_user_data_dir, is_frozen

    assert not is_frozen()
    base_dir = get_base_dir()
    assert base_dir.exists()

    icon_ico = get_asset_path("icon.ico")
    assert icon_ico.exists()
    assert icon_ico.is_file()

    icon_png = get_asset_path("icon.png")
    assert icon_png.exists()
    assert icon_png.is_file()

    user_dir = get_user_data_dir()
    assert user_dir.exists()


def test_runtime_logging_setup():
    """Verify logging configuration generates a valid log file."""
    from src.runtime import setup_logging, get_log_file_path, logger

    log_path = setup_logging()
    assert log_path.exists()
    logger.info("Test log verification event from test suite")

    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Test log verification event" in content


def test_settings_persistence(tmp_path):
    """Verify settings save and load round-trip with safe defaults."""
    from unittest.mock import patch
    from src.runtime import load_settings, save_settings

    fake_ini = tmp_path / "test_settings.ini"
    with patch("src.runtime.get_settings_file_path", return_value=fake_ini):
        defaults = load_settings()
        assert defaults["sound_enabled"] is False
        assert defaults["timeout_seconds"] == 60

        save_success = save_settings({
            "sound_enabled": True,
            "animations_enabled": False,
            "timeout_seconds": 30,
        })
        assert save_success is True

        loaded = load_settings()
        assert loaded["sound_enabled"] is True
        assert loaded["animations_enabled"] is False
        assert loaded["timeout_seconds"] == 30


def test_icon_file_validity():
    """Verify generated ICO and PNG can be loaded by PySide6 without errors."""
    from PySide6.QtGui import QIcon, QPixmap
    from src.runtime import get_asset_path

    ico_path = get_asset_path("icon.ico")
    icon = QIcon(str(ico_path))
    assert not icon.isNull()
    sizes = icon.availableSizes()
    assert len(sizes) >= 1

    png_path = get_asset_path("icon.png")
    pixmap = QPixmap(str(png_path))
    assert not pixmap.isNull()
    assert pixmap.width() == 256
    assert pixmap.height() == 256
