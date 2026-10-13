"""Main window implementation for GharBeka Phase 4.

Contains the application layout, sidebar navigation, monitor illustration,
hero controller card, subscription cards, status feedback, dialog hooks,
Windows DisplayController, and RecoveryManager with automatic timers & global hotkeys.
"""

import os
from ctypes import wintypes
from PySide6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    Property,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QLinearGradient,
    QPainterPath,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QButtonGroup,
    QDialog,
    QMessageBox,
)

from src.styles import (
    MAIN_STYLE_SHEET,
    BG_CARD,
    BORDER_MUTED,
    BORDER_ACCENT,
    PURPLE_PRIMARY,
    BLUE_ELECTRIC,
    SUCCESS_GREEN,
    WARNING_AMBER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
)
from src.dialogs import SubscriptionDialog, CheckoutDialog, SettingsDialog
from src.display_controller import DisplayController, DMDO_DEFAULT, DMDO_90
from src.recovery_manager import RecoveryManager
from src.runtime import load_settings, save_settings, logger


class MonitorIllustrationWidget(QWidget):
    """Custom-drawn modern desktop monitor widget.

    Renders a bezel-less display, stand, base, and mock screen content.
    Supports animated or instant simulation rotation angle (0, 90, 180, 270 degrees).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rotation_angle: float = 0.0
        self._anim: QPropertyAnimation | None = None
        self.setMinimumSize(380, 270)
        self.setMaximumHeight(330)

    @Property(float)
    def rotation_angle(self) -> float:
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, angle: float) -> None:
        self._rotation_angle = float(angle) % 360.0
        self.update()

    def set_rotation_angle(self, angle: float, animated: bool = True) -> None:
        """Update simulation rotation angle with optional animation."""
        target = float(angle)
        if animated:
            self._anim = QPropertyAnimation(self, b"rotation_angle")
            self._anim.setDuration(300)
            self._anim.setStartValue(self._rotation_angle)
            self._anim.setEndValue(target)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.start()
        else:
            self.rotation_angle = target

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = float(self.width())
        height = float(self.height())
        center_x = width / 2.0

        # --- Draw Stand Base and Neck ---
        base_width = 140.0
        base_height = 12.0
        base_y = height - 22.0
        neck_width = 28.0
        neck_top = base_y - 42.0

        # Stand neck with metallic vertical gradient
        neck_gradient = QLinearGradient(
            center_x - neck_width / 2, neck_top, center_x + neck_width / 2, neck_top
        )
        neck_gradient.setColorAt(0.0, QColor("#1e253e"))
        neck_gradient.setColorAt(0.5, QColor("#3f4c78"))
        neck_gradient.setColorAt(1.0, QColor("#1e253e"))
        painter.setBrush(QBrush(neck_gradient))
        painter.setPen(QPen(QColor(BORDER_MUTED), 1))
        painter.drawRoundedRect(
            QRectF(center_x - neck_width / 2, neck_top, neck_width, 44.0), 4, 4
        )

        # Stand base with glossy top border
        base_rect = QRectF(
            center_x - base_width / 2, base_y, base_width, base_height
        )
        base_grad = QLinearGradient(
            center_x, base_y, center_x, base_y + base_height
        )
        base_grad.setColorAt(0.0, QColor("#38436c"))
        base_grad.setColorAt(1.0, QColor("#121626"))
        painter.setBrush(QBrush(base_grad))
        painter.setPen(QPen(QColor("#475569"), 1))
        painter.drawRoundedRect(base_rect, 6, 6)

        # --- Draw Monitor Housing ---
        mon_w = min(480.0, max(320.0, width - 60.0))
        mon_h = 195.0
        mon_x = center_x - mon_w / 2.0
        mon_y = 12.0
        outer_rect = QRectF(mon_x, mon_y, mon_w, mon_h)

        # Outer bezel with gradient fill and subtle accent stroke
        bezel_grad = QLinearGradient(mon_x, mon_y, mon_x, mon_y + mon_h)
        bezel_grad.setColorAt(0.0, QColor("#191f33"))
        bezel_grad.setColorAt(1.0, QColor("#0f121e"))
        painter.setBrush(QBrush(bezel_grad))
        painter.setPen(QPen(QColor("#38436c"), 1.5))
        painter.drawRoundedRect(outer_rect, 12, 12)

        # Power LED Dot on Bottom Bezel Right
        led_x = mon_x + mon_w - 24.0
        led_y = mon_y + mon_h - 10.0
        painter.setBrush(QBrush(QColor(BLUE_ELECTRIC)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(led_x, led_y), 2.5, 2.5)

        # Screen inner glass
        screen_margin = 10.0
        screen_rect = QRectF(
            mon_x + screen_margin,
            mon_y + screen_margin,
            mon_w - (screen_margin * 2),
            mon_h - (screen_margin * 2) - 8.0,
        )

        screen_grad = QLinearGradient(
            screen_rect.topLeft(), screen_rect.bottomRight()
        )
        screen_grad.setColorAt(0.0, QColor("#080a10"))
        screen_grad.setColorAt(1.0, QColor("#121628"))
        painter.setBrush(QBrush(screen_grad))
        painter.setPen(QPen(QColor("#242b45"), 1))
        painter.drawRoundedRect(screen_rect, 8, 8)

        # Clip inside screen glass for display graphics
        painter.save()
        screen_path = QPainterPath()
        screen_path.addRoundedRect(screen_rect, 8, 8)
        painter.setClipPath(screen_path)

        # Dynamic screen background glass glow
        glow_grad = QLinearGradient(
            screen_rect.left(), screen_rect.top(),
            screen_rect.right(), screen_rect.bottom()
        )
        glow_grad.setColorAt(0.0, QColor(27, 33, 56, 180))
        glow_grad.setColorAt(1.0, QColor(11, 14, 23, 240))
        painter.setBrush(QBrush(glow_grad))
        painter.drawRect(screen_rect)

        # Transform for rotated screen simulation inside monitor glass
        screen_center = screen_rect.center()
        painter.translate(screen_center)
        painter.rotate(self._rotation_angle)

        # Draw mock OS window inside display
        mock_w = screen_rect.width() * 0.84
        mock_h = screen_rect.height() * 0.74
        mock_rect = QRectF(-mock_w / 2, -mock_h / 2, mock_w, mock_h)

        mock_brush = QBrush(QColor("#181e30"))
        painter.setBrush(mock_brush)
        painter.setPen(QPen(QColor(BORDER_ACCENT), 1.5))
        painter.drawRoundedRect(mock_rect, 7, 7)

        # Window title bar
        title_bar_h = 18.0
        title_rect = QRectF(
            mock_rect.left(), mock_rect.top(), mock_rect.width(), title_bar_h
        )
        painter.setBrush(QBrush(QColor("#232b45")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(title_rect, 7, 7)

        # Window dots
        dot_y = mock_rect.top() + 9.0
        dot_colors = ["#ef4444", "#f59e0b", "#10b981"]
        for i, color_hex in enumerate(dot_colors):
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.drawEllipse(
                QPointF(mock_rect.left() + 12.0 + (i * 11.0), dot_y), 3.5, 3.5
            )

        # Window Title Text
        painter.setPen(QPen(QColor(TEXT_MUTED)))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.drawText(
            QRectF(
                mock_rect.left() + 50.0,
                mock_rect.top() + 1.0,
                mock_rect.width() - 60.0,
                16.0,
            ),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "GharBeka Control Hub",
        )

        # Mock Dashboard Content inside screen
        side_bar_w = mock_rect.width() * 0.25
        side_rect = QRectF(
            mock_rect.left(),
            mock_rect.top() + title_bar_h,
            side_bar_w,
            mock_rect.height() - title_bar_h,
        )
        painter.setBrush(QBrush(QColor("#121626")))
        painter.drawRect(side_rect)

        # Content lines inside sidebar
        painter.setPen(QPen(QColor("#38436c"), 2))
        for line_i in range(3):
            ly = mock_rect.top() + title_bar_h + 12.0 + (line_i * 12.0)
            painter.drawLine(
                QPointF(mock_rect.left() + 8.0, ly),
                QPointF(mock_rect.left() + side_bar_w - 10.0, ly),
            )

        # Chart/Data bars in main content area
        content_left = mock_rect.left() + side_bar_w + 10.0
        content_w = mock_rect.width() - side_bar_w - 20.0
        painter.setPen(QPen(QColor("#3f4c78"), 2))
        painter.drawLine(
            QPointF(content_left, mock_rect.top() + title_bar_h + 14.0),
            QPointF(
                content_left + content_w * 0.8,
                mock_rect.top() + title_bar_h + 14.0,
            ),
        )

        # Stat cards graphics
        stat_bar_y = mock_rect.top() + title_bar_h + 24.0
        painter.setBrush(QBrush(QColor(PURPLE_PRIMARY)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            QRectF(content_left, stat_bar_y, content_w * 0.6, 6.0), 3, 3
        )

        painter.setBrush(QBrush(QColor(BLUE_ELECTRIC)))
        painter.drawRoundedRect(
            QRectF(content_left, stat_bar_y + 10.0, content_w * 0.4, 6.0), 3, 3
        )

        # Dynamic Angle Indicator Badge on simulated screen
        int_angle = int(round(self._rotation_angle)) % 360
        if int_angle == 0:
            badge_bg = QColor(16, 185, 129, 220)
            angle_text = "0° • OPTIMAL LEVEL"
        else:
            badge_bg = QColor(245, 158, 11, 220)
            angle_text = f"{int_angle}° • TILT DETECTED"

        badge_w = mock_rect.width() * 0.76
        badge_rect = QRectF(
            -badge_w / 2, mock_rect.bottom() - 24.0, badge_w, 18.0
        )
        painter.setBrush(QBrush(badge_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(badge_rect, 9, 9)

        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, angle_text)

        painter.restore()

        # Watermark label on bottom bezel
        painter.setPen(QPen(QColor(TEXT_MUTED)))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(
            QRectF(mon_x, mon_y + mon_h - 13.0, mon_w, 11.0),
            Qt.AlignmentFlag.AlignCenter,
            "GHARBEKA SIMULATION DISPLAY • HIGH PRECISION",
        )


class GharBekaMainWindow(QMainWindow):
    """Main application window for GharBeka Phase 4."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GharBeka — Screen Unrotation Suite")
        self.setMinimumSize(960, 680)
        self.resize(1080, 760)

        # Display Controller & Recovery Manager Instances
        self.display_controller = DisplayController()
        self.recovery_manager = RecoveryManager(self.display_controller, self)

        # Application State (Safety guarantee: Display Mode ALWAYS defaults to SIMULATION)
        self._is_rotated: bool = False
        self._subscription_tier: str = "Free"
        self._display_mode: str = "SIMULATION"

        # Load persisted user settings
        user_cfg = load_settings()
        self._sound_enabled: bool = bool(user_cfg.get("sound_enabled", False))
        self._animations_enabled: bool = bool(user_cfg.get("animations_enabled", True))
        self.recovery_manager.set_timeout_seconds(int(user_cfg.get("timeout_seconds", 60)))

        # Tracked Modal Dialog Instances
        self._active_subscription_dialog: SubscriptionDialog | None = None
        self._active_settings_dialog: SettingsDialog | None = None
        self._active_checkout_dialog: CheckoutDialog | None = None

        self._init_ui()
        self._connect_recovery_signals()
        self._setup_shortcuts()
        self.setStyleSheet(MAIN_STYLE_SHEET)

    def _setup_shortcuts(self) -> None:
        """Setup secondary in-app emergency shortcut fallback."""
        self._shortcut_emergency = QShortcut(
            QKeySequence("Ctrl+Alt+Shift+R"), self, self.emergency_recovery
        )

    def showEvent(self, event) -> None:  # noqa: N802
        """Register global Win32 hotkey when main window displays."""
        super().showEvent(event)
        if not self.recovery_manager.hotkey_registered and self.display_controller.is_windows():
            try:
                hwnd = int(self.winId())
                self.recovery_manager.register_global_hotkey(hwnd)
            except Exception:
                pass

    def nativeEvent(self, eventType, message) -> tuple[bool, int]:  # noqa: N802
        """Handle Win32 WM_HOTKEY events for global emergency shortcut."""
        if eventType in (b"windows_generic_MSG", "windows_generic_MSG"):
            try:
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == 0x0312:  # WM_HOTKEY
                    self.emergency_recovery()
                    return True, 0
            except Exception:
                pass
        return super().nativeEvent(eventType, message)

    def closeEvent(self, event) -> None:  # noqa: N802
        """Perform best-effort display recovery on application exit."""
        logger.info("Application closing: running cleanup and recovery check")
        if self.recovery_manager.is_real_rotation_active:
            dev_name = self.display_controller.get_primary_device_name()
            logger.info("Application exiting with active physical rotation; restoring '%s'", dev_name)
            self.display_controller.restore_original_orientation(dev_name)

        self.recovery_manager.unregister_global_hotkey()
        self.recovery_manager.stop_countdown()
        save_settings({
            "sound_enabled": self._sound_enabled,
            "animations_enabled": self._animations_enabled,
            "timeout_seconds": self.recovery_manager.timeout_seconds,
        })
        super().closeEvent(event)

    def _connect_recovery_signals(self) -> None:
        """Connect RecoveryManager signals to UI update slots."""
        self.recovery_manager.countdown_tick.connect(self._on_countdown_tick)
        self.recovery_manager.recovery_completed.connect(self._on_recovery_completed)

    def _on_countdown_tick(self, remaining: int) -> None:
        """Update UI with active auto-recovery countdown."""
        mode_str = "Physical Screen" if self._display_mode == "REAL" else "Simulated Screen"
        self.status_indicator.setText(
            f"● Screen Rotated (90°) — Auto-Recovery in {remaining}s"
        )
        self.status_indicator.setStyleSheet(
            f"color: {WARNING_AMBER}; background-color: rgba(245, 158, 11, 0.18); "
            f"border: 1px solid {WARNING_AMBER};"
        )

        self.feedback_banner.setText(
            f"⏱️ {mode_str} is rotated. Automatic safety recovery countdown active: "
            f"**{remaining}s remaining**. Press 'UNROTATE MY SCREEN', 'EMERGENCY RECOVERY', or Ctrl+Alt+Shift+R to level now."
        )

    def _on_recovery_completed(self, success: bool, message: str) -> None:
        """Update UI following automatic or emergency recovery execution."""
        if success:
            self._is_rotated = False
            self.btn_retry_recovery.setVisible(False)
            self.monitor_widget.set_rotation_angle(0, animated=self._animations_enabled)
            self.status_indicator.setText("● Display Ready — Screen is straight (0°)")
            self._update_status_indicator_style(is_rotated=False)
            self.feedback_banner.setText(
                f"✨ [Recovery Completed] {message}"
            )
        else:
            self.btn_retry_recovery.setVisible(True)
            self.status_indicator.setText("● Recovery Failed — Action Required")
            self.status_indicator.setStyleSheet(
                "color: #ef4444; background-color: rgba(239, 68, 68, 0.2); "
                "border: 1px solid #ef4444;"
            )
            self.feedback_banner.setText(
                f"⚠️ RECOVERY FAILED! {message}\n"
                "Manual Instructions: Press Win+I → System → Display → Orientation → Landscape. "
                "Or click 'Retry Recovery' below."
            )

    @property
    def subscription_tier(self) -> str:
        return self._subscription_tier

    @property
    def display_mode(self) -> str:
        return self._display_mode

    def set_display_mode(self, mode: str) -> None:
        """Set application operation mode ('SIMULATION' or 'REAL')."""
        self._display_mode = mode if mode in ("SIMULATION", "REAL") else "SIMULATION"
        if self._display_mode == "REAL":
            self.sim_mode_badge.setText("Real Display Mode Active")
            self.sim_mode_badge.setStyleSheet(
                f"background-color: rgba(56, 189, 248, 0.2); color: {BLUE_ELECTRIC}; "
                f"border: 1px solid {BLUE_ELECTRIC}; border-radius: 14px; padding: 5px 12px; font-size: 11px; font-weight: 700;"
            )
            self.sim_pill_title.setText("MODE: REAL DISPLAY")
            self.feedback_banner.setText(
                "⚡ [Real Display Mode Active] Physical monitor rotation enabled via Windows user32 APIs."
            )
        else:
            self.sim_mode_badge.setText("Simulation Mode Active")
            self.sim_mode_badge.setStyleSheet(
                f"background-color: rgba(56, 189, 248, 0.15); color: {BLUE_ELECTRIC}; "
                f"border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 5px 12px; font-size: 11px; font-weight: 700;"
            )
            self.sim_pill_title.setText("MODE: SIMULATION")
            self.feedback_banner.setText(
                "Hardware-safe Simulation Mode active. Physical screen drivers are locked."
            )

    @property
    def sound_enabled(self) -> bool:
        return self._sound_enabled

    def set_sound_enabled(self, enabled: bool) -> None:
        self._sound_enabled = enabled
        save_settings({
            "sound_enabled": self._sound_enabled,
            "animations_enabled": self._animations_enabled,
            "timeout_seconds": self.recovery_manager.timeout_seconds,
        })

    @property
    def animations_enabled(self) -> bool:
        return self._animations_enabled

    def set_animations_enabled(self, enabled: bool) -> None:
        self._animations_enabled = enabled
        save_settings({
            "sound_enabled": self._sound_enabled,
            "animations_enabled": self._animations_enabled,
            "timeout_seconds": self.recovery_manager.timeout_seconds,
        })

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = self._create_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Main Content Area with Scroll
        content_area = self._create_content_area()
        root_layout.addWidget(content_area, 1)

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget(self)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 20)
        layout.setSpacing(16)

        # Brand header
        brand_container = QVBoxLayout()
        brand_container.setSpacing(4)

        logo_label = QLabel("GHARBEKA", sidebar)
        logo_label.setObjectName("LogoText")
        brand_container.addWidget(logo_label)

        tagline_label = QLabel(
            "We Rotate Problems.\nYou Pay to Unrotate Them.", sidebar
        )
        tagline_label.setObjectName("TaglineText")
        tagline_label.setWordWrap(True)
        brand_container.addWidget(tagline_label)

        layout.addLayout(brand_container)

        # Divider
        divider = QFrame(sidebar)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_MUTED};")
        layout.addWidget(divider)

        # Navigation group
        self.nav_button_group = QButtonGroup(sidebar)
        self.nav_button_group.setExclusive(True)

        self.btn_nav_dashboard = QPushButton("  ⚡  Dashboard", sidebar)
        self.btn_nav_dashboard.setProperty("class", "nav-item")
        self.btn_nav_dashboard.setCheckable(True)
        self.btn_nav_dashboard.setChecked(True)
        self.btn_nav_dashboard.clicked.connect(
            lambda: self._on_nav_clicked("Dashboard")
        )
        self.nav_button_group.addButton(self.btn_nav_dashboard)
        layout.addWidget(self.btn_nav_dashboard)

        self.btn_nav_plans = QPushButton("  💎  Premium Plans", sidebar)
        self.btn_nav_plans.setProperty("class", "nav-item")
        self.btn_nav_plans.setCheckable(True)
        self.btn_nav_plans.clicked.connect(
            lambda: self._on_nav_clicked("Premium Plans")
        )
        self.nav_button_group.addButton(self.btn_nav_plans)
        layout.addWidget(self.btn_nav_plans)

        self.btn_nav_settings = QPushButton("  ⚙️  Settings", sidebar)
        self.btn_nav_settings.setProperty("class", "nav-item")
        self.btn_nav_settings.setCheckable(True)
        self.btn_nav_settings.clicked.connect(
            lambda: self._on_nav_clicked("Settings")
        )
        self.nav_button_group.addButton(self.btn_nav_settings)
        layout.addWidget(self.btn_nav_settings)

        layout.addStretch()

        # Sidebar Mode Status Pill
        sim_pill = QFrame(sidebar)
        sim_pill.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {BORDER_MUTED}; "
            f"border-radius: 10px; padding: 12px;"
        )
        sim_layout = QVBoxLayout(sim_pill)
        sim_layout.setContentsMargins(6, 6, 6, 6)
        sim_layout.setSpacing(4)

        self.sim_pill_title = QLabel("MODE: SIMULATION", sim_pill)
        self.sim_pill_title.setStyleSheet(
            f"color: {BLUE_ELECTRIC}; font-size: 11px; font-weight: 800;"
        )
        sim_pill_desc = QLabel(
            "Auto-recovery timer active.\nDefaults to simulation.", sim_pill
        )
        sim_pill_desc.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; line-height: 1.3;"
        )
        sim_layout.addWidget(self.sim_pill_title)
        sim_layout.addWidget(sim_pill_desc)

        layout.addWidget(sim_pill)

        return sidebar

    def _create_content_area(self) -> QWidget:
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content_widget = QWidget(self.scroll_area)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(22)

        # 1. Main Header
        header_layout = self._create_header_section()
        layout.addLayout(header_layout)

        # 2. Hero Card (Monitor & Primary Action Buttons)
        self.hero_card = self._create_hero_card()
        layout.addWidget(self.hero_card)

        # 3. Status Feedback Banner
        self.feedback_banner = QLabel(
            "Display Ready: Click 'ROTATE MY SCREEN' to simulate or apply rotation.",
            content_widget,
        )
        self.feedback_banner.setObjectName("FeedbackBanner")
        self.feedback_banner.setWordWrap(True)
        layout.addWidget(self.feedback_banner)

        # 4. Retry Recovery Button (Hidden by default, shown on recovery error)
        self.btn_retry_recovery = QPushButton("🔄 Retry Recovery Now", content_widget)
        self.btn_retry_recovery.setProperty("class", "btn-dialog-danger")
        self.btn_retry_recovery.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_retry_recovery.setVisible(False)
        self.btn_retry_recovery.clicked.connect(self.emergency_recovery)
        layout.addWidget(self.btn_retry_recovery)

        # 5. Subscription Cards
        self.pricing_section = self._create_subscription_section()
        layout.addWidget(self.pricing_section)

        # 6. Footer
        footer_layout = self._create_footer()
        layout.addLayout(footer_layout)

        self.scroll_area.setWidget(content_widget)
        return self.scroll_area

    def _create_header_section(self) -> QHBoxLayout:
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 6)
        header_layout.setSpacing(16)

        title_container = QVBoxLayout()
        title_container.setSpacing(6)

        title = QLabel("Welcome to GharBeka", self)
        title.setObjectName("HeaderTitle")
        title.setWordWrap(True)
        title_container.addWidget(title)

        subtitle = QLabel(
            "We Rotate Problems. You Pay to Unrotate Them.", self
        )
        subtitle.setObjectName("HeaderSubtitle")
        subtitle.setWordWrap(True)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container, 1)

        badge_container = QVBoxLayout()
        badge_container.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )
        badge_container.setSpacing(6)

        parody_badge = QLabel("PARODY SOFTWARE • SATIRE ONLY", self)
        parody_badge.setObjectName("ParodyBadge")
        badge_container.addWidget(parody_badge)

        self.sim_mode_badge = QLabel("Simulation Mode Active", self)
        self.sim_mode_badge.setObjectName("SimulationBadge")
        self.sim_mode_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        badge_container.addWidget(self.sim_mode_badge)

        header_layout.addLayout(badge_container)
        return header_layout

    def _create_hero_card(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "dashboard-card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 22, 28, 24)
        card_layout.setSpacing(18)

        # Card header bar
        top_bar = QHBoxLayout()
        card_title = QLabel("Display Orientation Console", card)
        card_title.setObjectName("CardTitle")
        top_bar.addWidget(card_title)
        top_bar.addStretch()

        mode_label = QLabel("⚡ Hardware-Safe Engine", card)
        mode_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; font-weight: 600;"
        )
        top_bar.addWidget(mode_label)
        card_layout.addLayout(top_bar)

        # Monitor Illustration
        self.monitor_widget = MonitorIllustrationWidget(card)
        card_layout.addWidget(self.monitor_widget)

        # Status Indicator
        status_container = QHBoxLayout()
        status_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_indicator = QLabel("● Display Ready — Screen is straight", card)
        self.status_indicator.setObjectName("StatusIndicator")
        self._update_status_indicator_style(is_rotated=False)
        status_container.addWidget(self.status_indicator)
        card_layout.addLayout(status_container)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_rotate = QPushButton("ROTATE MY SCREEN", card)
        self.btn_rotate.setObjectName("RotateButton")
        self.btn_rotate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rotate.clicked.connect(self._on_rotate_clicked)
        button_layout.addWidget(self.btn_rotate)

        self.btn_unrotate = QPushButton("UNROTATE MY SCREEN", card)
        self.btn_unrotate.setObjectName("UnrotateButton")
        self.btn_unrotate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_unrotate.clicked.connect(self._on_unrotate_clicked)
        button_layout.addWidget(self.btn_unrotate)

        card_layout.addLayout(button_layout)
        return card

    def _create_subscription_section(self) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        section_title = QLabel("Subscription Plans (Satire Pricing)", container)
        section_title.setObjectName("CardTitle")
        layout.addWidget(section_title)

        section_desc = QLabel(
            "Choose a tier to ensure your monitor never stays sideways permanently. No real payments are processed.",
            container,
        )
        section_desc.setObjectName("CardDescription")
        section_desc.setWordWrap(True)
        layout.addWidget(section_desc)

        plans_grid = QGridLayout()
        plans_grid.setSpacing(18)
        plans_grid.setColumnStretch(0, 1)
        plans_grid.setColumnStretch(1, 1)
        plans_grid.setColumnStretch(2, 1)

        # Plan 1: Free
        free_card, self.btn_free_plan = self._build_plan_card(
            title="Free Tier",
            price="৳0",
            period="forever free",
            features=[
                "Accidental 90° rotation risk",
                "Manual neck tilting support",
                "Community unrotation prayers",
                "Basic horizontal contemplation",
            ],
            btn_text="Current Plan",
            btn_class="plan-btn-current",
            highlighted=False,
            is_current=True,
        )
        plans_grid.addWidget(free_card, 0, 0)

        # Plan 2: Premium (Highlighted)
        premium_card, self.btn_premium_plan = self._build_plan_card(
            title="Premium",
            badge="MOST POPULAR (SATIRE)",
            price="৳499",
            period="per month",
            features=[
                "1-Click Unrotate simulation",
                "Anti-dizziness screen leveling",
                "Priority orientation recovery",
                "Digital certificate of levelness",
            ],
            btn_text="Upgrade to Premium",
            btn_class="plan-btn-upgrade",
            highlighted=True,
            is_current=False,
        )
        plans_grid.addWidget(premium_card, 0, 1)

        # Plan 3: Enterprise
        enterprise_card, self.btn_enterprise_plan = self._build_plan_card(
            title="Enterprise",
            price="৳4,999",
            period="per month",
            features=[
                "Unlimited simulated flips",
                "Dedicated on-call neck chiropractor",
                "24/7 Screen leveling SLA",
                "Custom 45° bespoke angle insurance",
            ],
            btn_text="Contact Sales",
            btn_class="plan-btn-enterprise",
            highlighted=False,
            is_current=False,
        )
        plans_grid.addWidget(enterprise_card, 0, 2)

        layout.addLayout(plans_grid)
        return container

    def _build_plan_card(
        self,
        title: str,
        price: str,
        period: str,
        features: list[str],
        btn_text: str,
        btn_class: str,
        highlighted: bool = False,
        badge: str | None = None,
        is_current: bool = False,
    ) -> tuple[QFrame, QPushButton]:
        card = QFrame(self)
        card.setProperty(
            "class",
            "pricing-card-highlighted" if highlighted else "pricing-card",
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(12)

        badge_slot = QWidget(card)
        badge_slot.setFixedHeight(24)
        badge_layout = QHBoxLayout(badge_slot)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(0)

        if badge:
            badge_label = QLabel(badge, badge_slot)
            badge_label.setStyleSheet(
                f"color: {PURPLE_PRIMARY}; font-size: 10px; font-weight: 800; "
                f"background: rgba(139, 92, 246, 0.18); border: 1px solid rgba(139, 92, 246, 0.4); "
                f"border-radius: 4px; padding: 2px 8px;"
            )
            badge_layout.addWidget(badge_label)
            badge_layout.addStretch()

        layout.addWidget(badge_slot)

        title_label = QLabel(title, card)
        title_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700;"
        )
        layout.addWidget(title_label)

        price_box = QHBoxLayout()
        price_box.setSpacing(4)
        price_box.setAlignment(Qt.AlignmentFlag.AlignBottom)

        price_label = QLabel(price, card)
        price_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 28px; font-weight: 800;"
        )
        price_box.addWidget(price_label)

        period_label = QLabel(f"/{period}", card)
        period_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; margin-bottom: 4px;"
        )
        price_box.addWidget(period_label)
        price_box.addStretch()
        layout.addLayout(price_box)

        card_divider = QFrame(card)
        card_divider.setFrameShape(QFrame.Shape.HLine)
        card_divider.setStyleSheet(f"color: {BORDER_MUTED}; margin: 4px 0px;")
        layout.addWidget(card_divider)

        feat_container = QVBoxLayout()
        feat_container.setSpacing(8)
        for item in features:
            item_label = QLabel(f"✔  {item}", card)
            item_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 12px; line-height: 1.3;"
            )
            item_label.setWordWrap(True)
            feat_container.addWidget(item_label)
        layout.addLayout(feat_container)

        layout.addStretch(1)

        btn = QPushButton(btn_text, card)
        btn.setProperty("class", btn_class)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if is_current:
            btn.setEnabled(False)
        btn.clicked.connect(
            lambda _, p=title, pr=price: self._on_plan_clicked(p, pr)
        )
        layout.addWidget(btn)

        return card, btn

    def _create_footer(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 4)
        layout.setSpacing(10)

        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_MUTED};")
        layout.addWidget(divider)

        footer_text = QLabel(
            "GharBeka v0.4.0-phase4 • Satire & Safety Disclaimer: "
            "GharBeka is a humorous conceptual parody. Automatic recovery and Ctrl+Alt+Shift+R shortcut keep your screen safe.",
            self,
        )
        footer_text.setObjectName("FooterText")
        footer_text.setWordWrap(True)
        footer_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_text)

        return layout

    def _update_status_indicator_style(self, is_rotated: bool) -> None:
        if is_rotated:
            self.status_indicator.setText("● Rotation Applied — Screen is rotated (90°)")
            self.status_indicator.setStyleSheet(
                f"color: {WARNING_AMBER}; background-color: rgba(245, 158, 11, 0.15); "
                f"border: 1px solid rgba(245, 158, 11, 0.4);"
            )
        else:
            self.status_indicator.setText("● Display Ready — Screen is straight (0°)")
            self.status_indicator.setStyleSheet(
                f"color: {SUCCESS_GREEN}; background-color: rgba(16, 185, 129, 0.15); "
                f"border: 1px solid rgba(16, 185, 129, 0.4);"
            )

    # --- Session Subscription Tier & State Management ---

    def set_subscription_tier(self, tier: str) -> None:
        """Update session subscription tier and reflect in UI."""
        self._subscription_tier = tier
        if tier == "Premium":
            self.btn_free_plan.setText("Downgrade to Free")
            self.btn_free_plan.setEnabled(True)
            self.btn_free_plan.setProperty("class", "plan-btn-enterprise")
            self.btn_free_plan.setStyle(self.btn_free_plan.style())

            self.btn_premium_plan.setText("Active Plan")
            self.btn_premium_plan.setEnabled(False)
            self.btn_premium_plan.setProperty("class", "plan-btn-current")
            self.btn_premium_plan.setStyle(self.btn_premium_plan.style())

            self.feedback_banner.setText(
                "🎉 [Premium Active] Subscription upgraded to Premium Tier! "
                "You now have 1-click screen unrotation unlocked."
            )
            self.feedback_banner.setStyleSheet(
                f"background-color: rgba(139, 92, 246, 0.18); color: {TEXT_PRIMARY}; "
                f"border: 1px solid rgba(139, 92, 246, 0.5); border-radius: 10px; padding: 12px 16px;"
            )
        else:
            self._subscription_tier = "Free"
            self.btn_free_plan.setText("Current Plan")
            self.btn_free_plan.setEnabled(False)
            self.btn_free_plan.setProperty("class", "plan-btn-current")
            self.btn_free_plan.setStyle(self.btn_free_plan.style())

            self.btn_premium_plan.setText("Upgrade to Premium")
            self.btn_premium_plan.setEnabled(True)
            self.btn_premium_plan.setProperty("class", "plan-btn-upgrade")
            self.btn_premium_plan.setStyle(self.btn_premium_plan.style())

            self.feedback_banner.setText(
                "Returned to Free Tier. Display controls are active in simulation mode."
            )
            self.feedback_banner.setStyleSheet(
                f"background-color: {BG_CARD}; color: {TEXT_PRIMARY}; "
                f"border: 1px solid {BORDER_MUTED}; border-radius: 10px; padding: 12px 16px;"
            )

    def reset_to_free_tier(self) -> None:
        """Reset subscription tier to Free for testing."""
        self.set_subscription_tier("Free")

    # --- Dialog Openers ---

    def _show_dialog(self, dialog: QDialog) -> None:
        """Display dialog modally in interactive GUI or non-blockingly in test suite."""
        if (
            os.environ.get("PYTEST_CURRENT_TEST")
            or os.environ.get("QT_QPA_PLATFORM") == "offscreen"
        ):
            dialog.show()
        else:
            dialog.exec()

    def open_subscription_dialog(self) -> SubscriptionDialog:
        """Open the parody subscription dialog without duplicating."""
        if (
            self._active_subscription_dialog is not None
            and self._active_subscription_dialog.isVisible()
        ):
            self._active_subscription_dialog.raise_()
            self._active_subscription_dialog.activateWindow()
            return self._active_subscription_dialog

        dialog = SubscriptionDialog(self)
        self._active_subscription_dialog = dialog
        dialog.finished.connect(self._on_subscription_dialog_finished)
        self._show_dialog(dialog)
        return dialog

    def _on_subscription_dialog_finished(self, result: int) -> None:
        self._active_subscription_dialog = None

    def open_checkout_dialog(self, plan_name: str = "Premium") -> CheckoutDialog:
        """Open fictional checkout simulation dialog without duplicating."""
        if (
            self._active_checkout_dialog is not None
            and self._active_checkout_dialog.isVisible()
        ):
            self._active_checkout_dialog.raise_()
            self._active_checkout_dialog.activateWindow()
            return self._active_checkout_dialog

        dialog = CheckoutDialog(self, plan_name=plan_name)
        self._active_checkout_dialog = dialog
        dialog.finished.connect(self._on_checkout_dialog_finished)
        self._show_dialog(dialog)
        return dialog

    def _on_checkout_dialog_finished(self, result: int) -> None:
        self._active_checkout_dialog = None

    def open_settings_dialog(self) -> SettingsDialog:
        """Open settings dialog without duplicating."""
        if (
            self._active_settings_dialog is not None
            and self._active_settings_dialog.isVisible()
        ):
            self._active_settings_dialog.raise_()
            self._active_settings_dialog.activateWindow()
            return self._active_settings_dialog

        dialog = SettingsDialog(self)
        self._active_settings_dialog = dialog
        dialog.finished.connect(self._on_settings_dialog_finished)
        self._show_dialog(dialog)
        return dialog

    def _on_settings_dialog_finished(self, result: int) -> None:
        self._active_settings_dialog = None
        self.btn_nav_dashboard.setChecked(True)

    def _confirm_physical_rotation(self, device_name: str) -> bool:
        """Show confirmation prompt before applying physical screen rotation."""
        if (
            os.environ.get("PYTEST_CURRENT_TEST")
            or os.environ.get("QT_QPA_PLATFORM") == "offscreen"
        ):
            return True

        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Icon.Warning)
        confirm.setWindowTitle("Confirm Physical Display Rotation — GharBeka")
        confirm.setText(
            f"⚠️ Confirm Physical Display Rotation\n\n"
            f"Are you sure you want to rotate physical display '{device_name}' to 90° Portrait?\n\n"
            f"Your physical Windows desktop display orientation will change immediately."
        )
        confirm.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirm.setDefaultButton(QMessageBox.StandardButton.No)
        return confirm.exec() == QMessageBox.StandardButton.Yes

    def emergency_recovery(self) -> None:
        """Emergency recovery: bypasses subscription checks and restores original display mode."""
        self.recovery_manager.stop_countdown()
        success, msg = self.recovery_manager.perform_recovery(mode=self._display_mode, source="EMERGENCY_ACTION")

        if success:
            self._is_rotated = False
            self.btn_retry_recovery.setVisible(False)
            self.monitor_widget.set_rotation_angle(0, animated=False)
            self.status_indicator.setText("● Display Ready — Emergency Recovery Applied (0°)")
            self._update_status_indicator_style(is_rotated=False)
            self.feedback_banner.setText(
                f"🛠️ [Emergency Recovery Applied] {msg}"
            )
        else:
            self.btn_retry_recovery.setVisible(True)
            self.status_indicator.setText("● Recovery Failed — Action Required")
            self.status_indicator.setStyleSheet(
                "color: #ef4444; background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444;"
            )
            self.feedback_banner.setText(
                f"⚠️ RECOVERY FAILED! {msg}\n"
                "Manual Instructions: Press Win+I → System → Display → Orientation → Landscape. "
                "Or click 'Retry Recovery' below."
            )

        if self._sound_enabled:
            QApplication.beep()

        if (
            self._active_subscription_dialog is not None
            and self._active_subscription_dialog.isVisible()
        ):
            self._active_subscription_dialog.accept()

    # --- Interaction Handlers ---

    def _on_rotate_clicked(self) -> None:
        """Handle ROTATE MY SCREEN in Simulation or Real Display Mode."""
        dev_name = self.display_controller.get_primary_device_name()

        if self._display_mode == "REAL":
            if not self.display_controller.is_windows():
                self.status_indicator.setText("● Rotation Failed (Windows Required)")
                self.status_indicator.setStyleSheet(
                    "color: #ef4444; background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4);"
                )
                self.feedback_banner.setText("Rotation Failed: Real Display Mode requires Microsoft Windows.")
                return

            try:
                curr_orient = self.display_controller.get_display_orientation(dev_name)
            except Exception as e:
                self.status_indicator.setText("● Rotation Failed (Device Error)")
                self.feedback_banner.setText(f"Rotation Failed: {e}")
                return

            if curr_orient == DMDO_90 or self._is_rotated:
                self.feedback_banner.setText(
                    f"Rotation Skipped: Physical display '{dev_name}' is already at 90° Portrait."
                )
                return

            supported, reason = self.display_controller.is_orientation_supported(dev_name, DMDO_90)
            if not supported:
                self.status_indicator.setText("● Rotation Failed (Unsupported Mode)")
                self.status_indicator.setStyleSheet(
                    "color: #ef4444; background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4);"
                )
                self.feedback_banner.setText(
                    f"Rotation Failed: Target orientation 90° is unsupported on '{dev_name}': {reason}"
                )
                return

            if not self._confirm_physical_rotation(dev_name):
                self.feedback_banner.setText("Physical display rotation canceled by user.")
                return

            success, msg = self.display_controller.rotate_display(dev_name, DMDO_90)
            if success:
                self._is_rotated = True
                self.monitor_widget.set_rotation_angle(90, animated=self._animations_enabled)
                self.recovery_manager.start_countdown(mode="REAL", device_name=dev_name)
                if self._sound_enabled:
                    QApplication.beep()
            else:
                self.status_indicator.setText("● Rotation Failed — Driver rejected request")
                self.status_indicator.setStyleSheet(
                    "color: #ef4444; background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4);"
                )
                self.feedback_banner.setText(f"Rotation Failed: {msg}")
        else:
            # Simulation Mode
            if self._is_rotated:
                self.feedback_banner.setText(
                    "⚠️ [Simulation Mode] Screen is already rotated at 90°! "
                    "Click 'UNROTATE MY SCREEN' or upgrade to Premium to restore level view."
                )
                self.feedback_banner.setStyleSheet(
                    f"background-color: rgba(245, 158, 11, 0.15); color: {TEXT_PRIMARY}; "
                    f"border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 10px; padding: 12px 16px;"
                )
                return

            self._is_rotated = True
            self.monitor_widget.set_rotation_angle(90, animated=self._animations_enabled)
            self.recovery_manager.start_countdown(mode="SIMULATION", device_name=dev_name)
            if self._sound_enabled:
                QApplication.beep()

    def _on_unrotate_clicked(self) -> None:
        """Handle UNROTATE MY SCREEN in Simulation or Real Display Mode."""
        dev_name = self.display_controller.get_primary_device_name()
        if self._display_mode == "REAL" and self.display_controller.is_windows():
            try:
                curr_orient = self.display_controller.get_display_orientation(dev_name)
            except Exception:
                curr_orient = DMDO_DEFAULT

            if curr_orient == DMDO_DEFAULT and not self._is_rotated:
                self.feedback_banner.setText(
                    f"Display Ready: Physical screen '{dev_name}' is already at 0° straight."
                )
                return
        else:
            if not self._is_rotated:
                self.feedback_banner.setText(
                    "✨ [Simulation Mode] Screen is already straight (0°). No unrotation needed."
                )
                return

        if self._subscription_tier == "Free":
            self.open_subscription_dialog()
        else:
            success, msg = self.recovery_manager.perform_recovery(source="PREMIUM_UNROTATE")
            if success:
                self._is_rotated = False
                self.monitor_widget.set_rotation_angle(0, animated=self._animations_enabled)
                self.status_indicator.setText("● Display Ready — Screen is straight (0°)")
                self._update_status_indicator_style(is_rotated=False)
                self.feedback_banner.setText(f"✨ Unrotate Successful: {msg}")
                if self._sound_enabled:
                    QApplication.beep()
            else:
                self.status_indicator.setText("● Unrotate Failed")
                self.feedback_banner.setText(f"Unrotate Failed: {msg}")

    def _on_plan_clicked(self, plan_name: str, price: str) -> None:
        """Handle subscription plan button interactions."""
        if plan_name == "Free Tier":
            self.reset_to_free_tier()
        else:
            self.open_checkout_dialog(plan_name)

    def _on_nav_clicked(self, nav_name: str) -> None:
        """Sidebar navigation handler."""
        if nav_name == "Dashboard":
            self.scroll_area.verticalScrollBar().setValue(0)
            self.btn_nav_dashboard.setChecked(True)
            self.feedback_banner.setText(
                "Navigated to Dashboard. Display controls are active."
            )
        elif nav_name == "Premium Plans":
            self.scroll_area.ensureWidgetVisible(self.pricing_section)
            self.btn_nav_plans.setChecked(True)
            self.feedback_banner.setText(
                "Navigated to Premium Plans. Browse our satirical unrotation offerings below."
            )
        elif nav_name == "Settings":
            self.open_settings_dialog()
