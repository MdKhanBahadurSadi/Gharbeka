"""Main window implementation for GharBeka.

Contains the application layout, sidebar navigation, monitor illustration,
hero controller card, subscription cards, and status feedback.
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QLinearGradient,
    QPainterPath,
)
from PySide6.QtWidgets import (
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


class MonitorIllustrationWidget(QWidget):
    """Custom-drawn modern desktop monitor widget.

    Renders a bezel-less display, stand, base, and mock screen content.
    Supports a simulated rotation angle (0, 90, 180, 270 degrees) locally.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rotation_angle: int = 0
        self.setMinimumSize(380, 270)
        self.setMaximumHeight(330)

    @property
    def rotation_angle(self) -> int:
        return self._rotation_angle

    def set_rotation_angle(self, angle: int) -> None:
        """Update simulation rotation angle and redraw."""
        self._rotation_angle = angle % 360
        self.update()

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
            center_x - neck_width / 2, neck_top,
            center_x + neck_width / 2, neck_top
        )
        neck_gradient.setColorAt(0.0, QColor("#1e253e"))
        neck_gradient.setColorAt(0.5, QColor("#3f4c78"))
        neck_gradient.setColorAt(1.0, QColor("#1e253e"))
        painter.setBrush(QBrush(neck_gradient))
        painter.setPen(QPen(QColor(BORDER_MUTED), 1))
        painter.drawRoundedRect(
            QRectF(center_x - neck_width / 2, neck_top, neck_width, 44.0),
            4, 4
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
        # Left sidebar column
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
            QPointF(content_left + content_w * 0.8, mock_rect.top() + title_bar_h + 14.0),
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
        if self._rotation_angle == 0:
            badge_bg = QColor(16, 185, 129, 220)
            angle_text = "0° • OPTIMAL LEVEL"
        else:
            badge_bg = QColor(245, 158, 11, 220)
            angle_text = f"{self._rotation_angle}° • TILT DETECTED"

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
    """Main application window for Phase 1 of GharBeka."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GharBeka — Screen Unrotation Suite (Simulation)")
        self.setMinimumSize(960, 680)
        self.resize(1080, 760)

        self._is_rotated: bool = False

        self._init_ui()
        self.setStyleSheet(MAIN_STYLE_SHEET)

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

        # Sidebar Simulation Pill
        sim_pill = QFrame(sidebar)
        sim_pill.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {BORDER_MUTED}; "
            f"border-radius: 10px; padding: 12px;"
        )
        sim_layout = QVBoxLayout(sim_pill)
        sim_layout.setContentsMargins(6, 6, 6, 6)
        sim_layout.setSpacing(4)

        sim_pill_title = QLabel("MODE: SIMULATION", sim_pill)
        sim_pill_title.setStyleSheet(
            f"color: {BLUE_ELECTRIC}; font-size: 11px; font-weight: 800;"
        )
        sim_pill_desc = QLabel(
            "Hardware changes locked.\nNo actual OS rotation.", sim_pill
        )
        sim_pill_desc.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; line-height: 1.3;"
        )
        sim_layout.addWidget(sim_pill_title)
        sim_layout.addWidget(sim_pill_desc)

        layout.addWidget(sim_pill)

        return sidebar

    def _create_content_area(self) -> QWidget:
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content_widget = QWidget(scroll_area)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(22)

        # 1. Main Header
        header_layout = self._create_header_section()
        layout.addLayout(header_layout)

        # 2. Hero Card (Monitor & Primary Action Buttons)
        hero_card = self._create_hero_card()
        layout.addWidget(hero_card)

        # 3. Status Feedback Banner
        self.feedback_banner = QLabel(
            "Ready: Click 'ROTATE MY SCREEN' to simulate rotation, or 'UNROTATE MY SCREEN' to level it.",
            content_widget,
        )
        self.feedback_banner.setObjectName("FeedbackBanner")
        self.feedback_banner.setWordWrap(True)
        layout.addWidget(self.feedback_banner)

        # 4. Subscription Cards
        pricing_section = self._create_subscription_section()
        layout.addWidget(pricing_section)

        # 5. Footer
        footer_layout = self._create_footer()
        layout.addLayout(footer_layout)

        scroll_area.setWidget(content_widget)
        return scroll_area

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

        sim_mode_badge = QLabel("Simulation Mode Active", self)
        sim_mode_badge.setObjectName("SimulationBadge")
        sim_mode_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        badge_container.addWidget(sim_mode_badge)

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

        mode_label = QLabel("⚡ Hardware-Safe Simulation", card)
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

        self.status_indicator = QLabel("● Screen is straight", card)
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
        free_card = self._build_plan_card(
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
        premium_card = self._build_plan_card(
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
        enterprise_card = self._build_plan_card(
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
    ) -> QFrame:
        card = QFrame(self)
        card.setProperty(
            "class",
            "pricing-card-highlighted" if highlighted else "pricing-card",
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(12)

        # Badge container slot for uniform alignment across all cards
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

        # Separator Line inside card
        card_divider = QFrame(card)
        card_divider.setFrameShape(QFrame.Shape.HLine)
        card_divider.setStyleSheet(f"color: {BORDER_MUTED}; margin: 4px 0px;")
        layout.addWidget(card_divider)

        # Features list
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
        else:
            btn.clicked.connect(
                lambda _, p=title, pr=price: self._on_plan_clicked(p, pr)
            )
        layout.addWidget(btn)

        return card

    def _create_footer(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 4)
        layout.setSpacing(10)

        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_MUTED};")
        layout.addWidget(divider)

        footer_text = QLabel(
            "GharBeka v0.1.0-alpha • Satire & Parody Disclaimer: "
            "GharBeka is a humorous conceptual parody. No actual Windows screen rotation or financial charges occur.",
            self,
        )
        footer_text.setObjectName("FooterText")
        footer_text.setWordWrap(True)
        footer_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_text)

        return layout

    def _update_status_indicator_style(self, is_rotated: bool) -> None:
        if is_rotated:
            self.status_indicator.setText("● Screen is rotated (90° Simulation)")
            self.status_indicator.setStyleSheet(
                f"color: {WARNING_AMBER}; background-color: rgba(245, 158, 11, 0.15); "
                f"border: 1px solid rgba(245, 158, 11, 0.4);"
            )
        else:
            self.status_indicator.setText("● Screen is straight")
            self.status_indicator.setStyleSheet(
                f"color: {SUCCESS_GREEN}; background-color: rgba(16, 185, 129, 0.15); "
                f"border: 1px solid rgba(16, 185, 129, 0.4);"
            )

    # --- Interaction Handlers ---

    def _on_rotate_clicked(self) -> None:
        """Simulate screen rotation without touching OS settings."""
        self._is_rotated = True
        self.monitor_widget.set_rotation_angle(90)
        self._update_status_indicator_style(is_rotated=True)
        self.feedback_banner.setText(
            "⚠️ [Simulation Mode] Screen rotated to 90°! "
            "Notice your neck tilting? Upgrade to Premium (৳499) to unrotate, or click 'UNROTATE MY SCREEN'."
        )
        self.feedback_banner.setStyleSheet(
            f"background-color: rgba(245, 158, 11, 0.12); color: {TEXT_PRIMARY}; "
            f"border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 10px; padding: 12px 16px;"
        )

    def _on_unrotate_clicked(self) -> None:
        """Simulate unrotating back to 0 degrees."""
        self._is_rotated = False
        self.monitor_widget.set_rotation_angle(0)
        self._update_status_indicator_style(is_rotated=False)
        self.feedback_banner.setText(
            "✨ [Simulation Mode] Screen successfully unrotated to 0° straight! "
            "Equilibrium restored. That will be ৳0 on your current satirical plan."
        )
        self.feedback_banner.setStyleSheet(
            f"background-color: rgba(16, 185, 129, 0.12); color: {TEXT_PRIMARY}; "
            f"border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 10px; padding: 12px 16px;"
        )

    def _on_plan_clicked(self, plan_name: str, price: str) -> None:
        """Simulate plan selection with polite parody feedback."""
        self.feedback_banner.setText(
            f"💳 [Satire Mode] Selected {plan_name} plan ({price}/month). "
            f"Payment processing is disabled in Simulation mode."
        )
        self.feedback_banner.setStyleSheet(
            f"background-color: rgba(139, 92, 246, 0.15); color: {TEXT_PRIMARY}; "
            f"border: 1px solid rgba(139, 92, 246, 0.4); border-radius: 10px; padding: 12px 16px;"
        )

    def _on_nav_clicked(self, nav_name: str) -> None:
        """Visual feedback for sidebar navigation."""
        if nav_name == "Dashboard":
            self.feedback_banner.setText(
                "Navigated to Dashboard. Display controls are active in simulation mode."
            )
        elif nav_name == "Premium Plans":
            self.feedback_banner.setText(
                "Navigated to Premium Plans. Browse our satirical unrotation offerings below."
            )
        elif nav_name == "Settings":
            self.feedback_banner.setText(
                "Navigated to Settings: All physical screen rotation drivers are safely mocked."
            )
