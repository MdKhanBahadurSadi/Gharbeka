"""Runtime utilities for GharBeka: resource resolution, logging, settings, and error handling.

Handles frozen PyInstaller environments (sys._MEIPASS) and standard development mode.
"""

from __future__ import annotations

import configparser
import logging
import os
import sys
from pathlib import Path
from typing import Any

LOGGER_NAME = "GharBeka"
logger = logging.getLogger(LOGGER_NAME)


def is_frozen() -> bool:
    """Return True if running in a PyInstaller bundled executable."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_base_dir() -> Path:
    """Get the base directory for bundled assets or local development."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def get_asset_path(filename: str) -> Path:
    """Resolve an asset path reliably across frozen and normal environments."""
    asset_path = get_base_dir() / "assets" / filename
    if asset_path.exists():
        return asset_path
    # Fallback check next to executable or script
    local_path = Path(sys.executable).parent / "assets" / filename
    if local_path.exists():
        return local_path
    return asset_path


def get_user_data_dir() -> Path:
    """Get user-writable data directory for logs and configuration.

    Uses %LOCALAPPDATA%\\GharBeka on Windows, or ~/.local/share/GharBeka on other OS.
    Honors GHARBEKA_DATA_DIR environment variable for custom/test locations.
    """
    custom_dir = os.environ.get("GHARBEKA_DATA_DIR")
    if custom_dir:
        data_dir = Path(custom_dir)
    elif os.environ.get("PYTEST_CURRENT_TEST"):
        import tempfile
        data_dir = Path(tempfile.gettempdir()) / "GharBeka_test_run"
    else:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            data_dir = Path(local_app_data) / "GharBeka"
        else:
            data_dir = Path.home() / ".gharbeka"

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        fallback = Path(os.environ.get("TEMP", "/tmp")) / "GharBeka"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

    return data_dir


def get_log_file_path() -> Path:
    """Get path to the persistent diagnostic log file."""
    return get_user_data_dir() / "gharbeka.log"


def get_settings_file_path() -> Path:
    """Get path to the user settings INI file."""
    return get_user_data_dir() / "settings.ini"


def setup_logging() -> Path:
    """Configure structured diagnostic logging to file and standard stream."""
    log_file = get_log_file_path()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if called multiple times
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except OSError:
        pass

    # Add console stream handler if running with an attached console
    if sys.stderr is not None and hasattr(sys.stderr, "write"):
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    logger.info("=" * 60)
    logger.info("GharBeka Desktop Application Startup")
    logger.info("Version: 1.0.0")
    logger.info("Frozen Executable: %s", is_frozen())
    logger.info("Executable Path: %s", sys.executable)
    logger.info("Base Resource Directory: %s", get_base_dir())
    logger.info("Log File: %s", log_file)
    logger.info("=" * 60)

    install_exception_hook()
    return log_file


def _global_exception_handler(exctype, value, tb):
    """Handle uncaught exceptions by logging them and optionally showing a GUI alert."""
    import traceback

    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    logger.critical("Uncaught Exception:\n%s", error_msg)

    # If PySide6 is imported and QApplication exists, show a non-fatal error dialog
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        app = QApplication.instance()
        if app is not None:
            QMessageBox.critical(
                None,
                "GharBeka — Unexpected Error",
                f"An unexpected error occurred:\n\n{value}\n\n"
                f"Diagnostic log: {get_log_file_path()}\n"
                "Please check the log file for technical details.",
            )
    except Exception:
        pass

    sys.__excepthook__(exctype, value, tb)


def install_exception_hook() -> None:
    """Install global exception hook to capture unhandled errors into logs."""
    sys.excepthook = _global_exception_handler


# Default Settings
DEFAULT_SETTINGS: dict[str, Any] = {
    "sound_enabled": False,
    "animations_enabled": True,
    "timeout_seconds": 60,
    # Note: display_mode is strictly ephemeral and starts at SIMULATION for user safety
}


def load_settings() -> dict[str, Any]:
    """Load user settings from user-writable configuration file."""
    settings = dict(DEFAULT_SETTINGS)
    ini_path = get_settings_file_path()

    if not ini_path.exists():
        return settings

    config = configparser.ConfigParser()
    try:
        config.read(str(ini_path), encoding="utf-8")
        if "Settings" in config:
            sec = config["Settings"]
            settings["sound_enabled"] = sec.getboolean(
                "sound_enabled", fallback=DEFAULT_SETTINGS["sound_enabled"]
            )
            settings["animations_enabled"] = sec.getboolean(
                "animations_enabled", fallback=DEFAULT_SETTINGS["animations_enabled"]
            )
            settings["timeout_seconds"] = sec.getint(
                "timeout_seconds", fallback=DEFAULT_SETTINGS["timeout_seconds"]
            )
            logger.info("Loaded user settings from %s", ini_path)
    except Exception as e:
        logger.warning("Could not read settings from %s: %s", ini_path, e)

    return settings


def save_settings(settings: dict[str, Any]) -> bool:
    """Save user settings to user-writable configuration file."""
    ini_path = get_settings_file_path()
    config = configparser.ConfigParser()
    config["Settings"] = {
        "sound_enabled": str(bool(settings.get("sound_enabled", False))),
        "animations_enabled": str(bool(settings.get("animations_enabled", True))),
        "timeout_seconds": str(int(settings.get("timeout_seconds", 60))),
    }

    try:
        with open(ini_path, "w", encoding="utf-8") as f:
            config.write(f)
        logger.info("Saved user settings to %s", ini_path)
        return True
    except Exception as e:
        logger.warning("Could not save settings to %s: %s", ini_path, e)
        return False
