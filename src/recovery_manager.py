"""Automatic Recovery Manager for GharBeka Phase 4.

Manages recovery countdown timers, automatic restoration, state tracking,
and global emergency hotkey registration via Win32 user32 APIs.
"""

import ctypes
from typing import Any
from PySide6.QtCore import QObject, QTimer, Signal


# Win32 Hotkey Constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
VK_R = 0x52  # 'R'
HOTKEY_ID_GHARBEKA = 0x4742  # 'GB'
WM_HOTKEY = 0x0312


class RecoveryManager(QObject):
    """Manages display recovery timers, state tracking, and emergency restoration."""

    # Signals
    countdown_tick = Signal(int)
    recovery_triggered = Signal(str, str)
    recovery_completed = Signal(bool, str)

    def __init__(self, display_controller: Any, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.display_controller = display_controller

        self._timeout_seconds: int = 60
        self._remaining_seconds: int = 60
        self._is_timer_running: bool = False
        self._current_mode: str = "SIMULATION"
        self._target_device: str | None = None
        self._is_real_rotation_active: bool = False
        self._is_simulated_rotation_active: bool = False
        self._recovery_error: str | None = None

        self._hotkey_registered: bool = False
        self._hotkey_hwnd: int | None = None

        # Countdown Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_timer_tick)

    @property
    def timeout_seconds(self) -> int:
        return self._timeout_seconds

    def set_timeout_seconds(self, seconds: int) -> None:
        """Update default recovery timeout (valid range: 5 to 300 seconds)."""
        if 5 <= seconds <= 300:
            self._timeout_seconds = seconds
            if not self._is_timer_running:
                self._remaining_seconds = seconds

    @property
    def remaining_seconds(self) -> int:
        return self._remaining_seconds

    @property
    def is_timer_running(self) -> bool:
        return self._is_timer_running

    @property
    def is_real_rotation_active(self) -> bool:
        return self._is_real_rotation_active

    @property
    def is_simulated_rotation_active(self) -> bool:
        return self._is_simulated_rotation_active

    @property
    def recovery_error(self) -> str | None:
        return self._recovery_error

    @property
    def hotkey_registered(self) -> bool:
        return self._hotkey_registered

    # --- Timer Controls ---

    def start_countdown(
        self, mode: str = "SIMULATION", device_name: str | None = None
    ) -> None:
        """Start or restart the automatic recovery countdown."""
        self.stop_countdown()

        self._current_mode = mode if mode in ("SIMULATION", "REAL") else "SIMULATION"
        self._target_device = (
            device_name or self.display_controller.get_primary_device_name()
        )

        if self._current_mode == "REAL":
            self._is_real_rotation_active = True
            self._is_simulated_rotation_active = False
        else:
            self._is_simulated_rotation_active = True
            self._is_real_rotation_active = False

        self._recovery_error = None
        self._remaining_seconds = self._timeout_seconds
        self._is_timer_running = True

        self.timer.start(1000)
        self.countdown_tick.emit(self._remaining_seconds)

    def stop_countdown(self) -> None:
        """Stop active countdown timer without triggering recovery."""
        if self.timer.isActive():
            self.timer.stop()
        self._is_timer_running = False

    def _on_timer_tick(self) -> None:
        """Called every second by QTimer."""
        if not self._is_timer_running:
            return

        self._remaining_seconds -= 1
        self.countdown_tick.emit(self._remaining_seconds)

        if self._remaining_seconds <= 0:
            self.stop_countdown()
            self.recovery_triggered.emit(self._current_mode, "AUTOMATIC_TIMEOUT")
            self.perform_recovery(source="AUTOMATIC_TIMEOUT")

    # --- Recovery Execution ---

    def perform_recovery(
        self, mode: str | None = None, source: str = "EMERGENCY_ACTION"
    ) -> tuple[bool, str]:
        """Perform display orientation recovery in real or simulation mode."""
        self.stop_countdown()
        recovery_mode = mode or self._current_mode
        dev_name = (
            self._target_device
            or self.display_controller.get_primary_device_name()
        )

        if recovery_mode == "REAL" and self.display_controller.is_windows():
            success, msg = self.display_controller.restore_original_orientation(
                dev_name
            )
            if success:
                self._is_real_rotation_active = False
                self._recovery_error = None
                self.recovery_completed.emit(
                    True, f"Real display mode for '{dev_name}' restored."
                )
                return True, f"Real display mode for '{dev_name}' restored."
            else:
                self._recovery_error = msg
                self.recovery_completed.emit(
                    False, f"Real display recovery failed: {msg}"
                )
                return False, f"Real display recovery failed: {msg}"
        else:
            self._is_simulated_rotation_active = False
            self._recovery_error = None
            self.recovery_completed.emit(
                True, "Simulation display orientation restored to 0°."
            )
            return True, "Simulation display orientation restored to 0°."

    def cancel_and_reset(self) -> None:
        """Stop timers and reset rotation tracking flags."""
        self.stop_countdown()
        self._is_real_rotation_active = False
        self._is_simulated_rotation_active = False
        self._recovery_error = None

    # --- Win32 Global Hotkey Integration ---

    def register_global_hotkey(self, window_handle: int) -> tuple[bool, str]:
        """Register Ctrl+Alt+Shift+R global emergency hotkey via Win32 API."""
        if not self.display_controller.is_windows():
            return False, "Global Windows hotkey requires Microsoft Windows."

        user32 = getattr(ctypes.windll, "user32", None)
        if user32 is None:
            return False, "user32.dll unavailable."

        self.unregister_global_hotkey()

        self._hotkey_hwnd = window_handle
        res = user32.RegisterHotKey(
            window_handle,
            HOTKEY_ID_GHARBEKA,
            MOD_CONTROL | MOD_ALT | MOD_SHIFT | MOD_NOREPEAT,
            VK_R,
        )

        if res:
            self._hotkey_registered = True
            return True, "Registered global emergency shortcut: Ctrl+Alt+Shift+R"
        else:
            self._hotkey_registered = False
            return (
                False,
                "Shortcut Ctrl+Alt+Shift+R is currently in use by another application.",
            )

    def unregister_global_hotkey(self) -> None:
        """Unregister global emergency hotkey on shutdown."""
        if self._hotkey_registered and self._hotkey_hwnd is not None:
            user32 = getattr(ctypes.windll, "user32", None)
            if user32 is not None:
                user32.UnregisterHotKey(self._hotkey_hwnd, HOTKEY_ID_GHARBEKA)
            self._hotkey_registered = False
            self._hotkey_hwnd = None
