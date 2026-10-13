"""Entry point for the GharBeka desktop application.

GharBeka: 'We Rotate Problems. You Pay to Unrotate Them.'
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont, QIcon

from src.main_window import GharBekaMainWindow
from src.runtime import setup_logging, get_asset_path, logger


def main() -> int:
    """Initialize and run the GharBeka desktop application."""
    log_file = setup_logging()
    logger.info("Initializing GharBeka application")

    app = QApplication(sys.argv)
    app.setApplicationName("GharBeka")
    app.setOrganizationName("GharBeka Labs")

    # Set application icon if present
    icon_path = get_asset_path("icon.ico")
    if not icon_path.exists():
        icon_path = get_asset_path("icon.png")

    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)

    # Set default modern clean font
    app_font = QFont("Segoe UI", 10)
    app.setFont(app_font)

    try:
        window = GharBekaMainWindow()
        if icon_path.exists():
            window.setWindowIcon(QIcon(str(icon_path)))
        window.show()
    except Exception as exc:
        logger.critical("Fatal error initializing main window: %s", exc, exc_info=True)
        QMessageBox.critical(
            None,
            "GharBeka — Startup Failure",
            f"Failed to start GharBeka:\n\n{exc}\n\n"
            f"Please review the diagnostic log file at:\n{log_file}",
        )
        return 1

    logger.info("Entering Qt main event loop")
    exit_code = app.exec()
    logger.info("Exiting application with code %d", exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
