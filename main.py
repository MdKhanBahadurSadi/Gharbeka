"""Entry point for the GharBeka desktop application.

GharBeka: 'We Rotate Problems. You Pay to Unrotate Them.'
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from src.main_window import GharBekaMainWindow


def main() -> int:
    """Initialize and run the GharBeka desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName("GharBeka")
    app.setOrganizationName("GharBeka Labs")

    # Set default modern clean font
    app_font = QFont("Segoe UI", 10)
    app.setFont(app_font)

    window = GharBekaMainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
