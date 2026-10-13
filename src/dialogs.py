"""Modal dialogs for GharBeka Phase 4.

Includes Subscription Parody Dialog, Fictional Checkout Dialog, and Settings Dialog
with Mode Selection, Recovery Timeout configuration, and Global Shortcut Status.
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QMessageBox,
)

from src.runtime import save_settings


class SubscriptionDialog(QDialog):
    """Parody subscription tier dialog displayed when screen unrotation is requested on Free tier."""

    def __init__(self, main_window: QWidget) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("YOUR SCREEN IS CROOKED! — GharBeka")
        self.setModal(True)
        self.setMinimumWidth(520)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        # Header Badge
        badge = QLabel("⚠️ SIMULATED TILT DETECTED (90°)", self)
        badge.setObjectName("ParodyBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(badge)

        # Title & Messages
        title = QLabel("YOUR SCREEN IS CROOKED!", self)
        title.setObjectName("DialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        msg_box = QFrame(self)
        msg_box.setProperty("class", "dialog-card")
        msg_layout = QVBoxLayout(msg_box)
        msg_layout.setContentsMargins(16, 14, 16, 14)
        msg_layout.setSpacing(6)

        line1 = QLabel("Want your screen straight again?", msg_box)
        line1.setStyleSheet("color: #f8fafc; font-size: 15px; font-weight: 700;")
        line1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_layout.addWidget(line1)

        line2 = QLabel("Sorry. Straightness is a premium feature.", msg_box)
        line2.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: 600;")
        line2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_layout.addWidget(line2)

        layout.addWidget(msg_box)

        # Tier Cards
        tiers_frame = QFrame(self)
        tiers_frame.setProperty("class", "dialog-card")
        tiers_layout = QVBoxLayout(tiers_frame)
        tiers_layout.setContentsMargins(16, 14, 16, 14)
        tiers_layout.setSpacing(10)

        prem_info = QLabel(
            "💎  Premium Tier — ৳499/month\n"
            "    • 1-Click Unrotate simulation & Anti-dizziness algorithm",
            tiers_frame,
        )
        prem_info.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.4;")
        tiers_layout.addWidget(prem_info)

        ent_info = QLabel(
            "🏢  Enterprise Tier — ৳4,999/month\n"
            "    • 24/7 Dedicated neck chiropractor SLA & bespoke angle insurance",
            tiers_frame,
        )
        ent_info.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.4;")
        tiers_layout.addWidget(ent_info)

        layout.addWidget(tiers_frame)

        # Action Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_upgrade = QPushButton("UPGRADE TO PREMIUM", self)
        self.btn_upgrade.setProperty("class", "btn-dialog-primary")
        self.btn_upgrade.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upgrade.clicked.connect(self._on_upgrade_clicked)
        btn_layout.addWidget(self.btn_upgrade)

        self.btn_demo = QPushButton("TRY PREMIUM DEMO", self)
        self.btn_demo.setProperty("class", "btn-dialog-secondary")
        self.btn_demo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_demo.clicked.connect(self._on_demo_clicked)
        btn_layout.addWidget(self.btn_demo)

        self.btn_emergency = QPushButton("EMERGENCY RECOVERY", self)
        self.btn_emergency.setProperty("class", "btn-dialog-danger")
        self.btn_emergency.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_emergency.clicked.connect(self._on_emergency_clicked)
        btn_layout.addWidget(self.btn_emergency)

        self.btn_close = QPushButton("CLOSE", self)
        self.btn_close.setProperty("class", "btn-dialog-close")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # Satire Disclaimer
        disclaimer = QLabel(
            "GharBeka Satire Demonstration • Emergency Recovery is free and un-gated.",
            self,
        )
        disclaimer.setStyleSheet("color: #94a3b8; font-size: 11px;")
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(disclaimer)

    def _on_upgrade_clicked(self) -> None:
        if self.main_window.open_checkout_dialog("Premium"):
            self.accept()

    def _on_demo_clicked(self) -> None:
        if self.main_window.open_checkout_dialog("Premium Demo"):
            self.accept()

    def _on_emergency_clicked(self) -> None:
        self.main_window.emergency_recovery()
        self.accept()


class CheckoutDialog(QDialog):
    """Fictional checkout simulation dialog."""

    def __init__(self, main_window: QWidget, plan_name: str = "Premium") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.plan_name = plan_name
        self.setWindowTitle("Simulated SaaS Checkout — GharBeka")
        self.setModal(True)
        self.setMinimumWidth(460)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Fictional Checkout Simulation", self)
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #f8fafc;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            f"Upgrading to {self.plan_name} Tier (Satire Mode)", self
        )
        subtitle.setStyleSheet("font-size: 13px; color: #cbd5e1;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Summary box
        summary_card = QFrame(self)
        summary_card.setProperty("class", "dialog-card")
        s_layout = QVBoxLayout(summary_card)
        s_layout.setContentsMargins(18, 16, 18, 16)
        s_layout.setSpacing(8)

        item_label = QLabel(
            f"Item: GharBeka Unrotation Suite ({self.plan_name})", summary_card
        )
        item_label.setStyleSheet("color: #f8fafc; font-weight: 600; font-size: 13px;")
        s_layout.addWidget(item_label)

        price_label = QLabel("Subtotal: ৳499.00 / month", summary_card)
        price_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        s_layout.addWidget(price_label)

        discount_label = QLabel(
            "Satire Discount: -৳499.00 (100% Mock)", summary_card
        )
        discount_label.setStyleSheet(
            "color: #10b981; font-size: 12px; font-weight: 600;"
        )
        s_layout.addWidget(discount_label)

        total_label = QLabel("Total Due Today: ৳0.00", summary_card)
        total_label.setStyleSheet(
            "color: #38bdf8; font-size: 16px; font-weight: 800;"
        )
        s_layout.addWidget(total_label)

        layout.addWidget(summary_card)

        # Safety Disclaimer Box
        safety_card = QFrame(self)
        safety_card.setStyleSheet(
            "background-color: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); "
            "border-radius: 8px; padding: 10px;"
        )
        sf_layout = QVBoxLayout(safety_card)
        sf_layout.setContentsMargins(10, 8, 10, 8)
        sf_text = QLabel(
            "🔒 SATIRE DEMONSTRATION ONLY\n"
            "No payment information requested or stored. Clicking Confirm Demo will grant "
            "session-only Premium status.",
            safety_card,
        )
        sf_text.setStyleSheet("color: #cbd5e1; font-size: 11px; line-height: 1.3;")
        sf_text.setWordWrap(True)
        sf_layout.addWidget(sf_text)
        layout.addWidget(safety_card)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        self.btn_confirm = QPushButton("CONFIRM DEMO", self)
        self.btn_confirm.setProperty("class", "btn-dialog-primary")
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.clicked.connect(self._on_confirm)
        btn_box.addWidget(self.btn_confirm)

        self.btn_cancel = QPushButton("CANCEL", self)
        self.btn_cancel.setProperty("class", "btn-dialog-close")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_box.addWidget(self.btn_cancel)

        layout.addLayout(btn_box)

    def _on_confirm(self) -> None:
        self.main_window.set_subscription_tier("Premium")
        self.accept()

    def _on_cancel(self) -> None:
        self.reject()


class SettingsDialog(QDialog):
    """Application settings dialog with Mode Selection, Recovery Timeout, and Hotkey Status."""

    def __init__(self, main_window: QWidget) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Settings — GharBeka")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("GharBeka Settings & Safety Controls", self)
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        card = QFrame(self)
        card.setProperty("class", "dialog-card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(14)

        # 1. Operation Mode Selection Group
        mode_hdr = QLabel("Display Controller Mode:", card)
        mode_hdr.setStyleSheet("color: #cbd5e1; font-weight: 700; font-size: 13px;")
        card_layout.addWidget(mode_hdr)

        self.mode_group = QButtonGroup(card)

        self.rad_sim = QRadioButton("Simulation Mode (Hardware Safe)", card)
        self.rad_sim.setStyleSheet("color: #f8fafc; font-size: 13px;")
        self.mode_group.addButton(self.rad_sim)
        card_layout.addWidget(self.rad_sim)

        self.rad_real = QRadioButton("Real Display Mode (Physical Windows Monitor)", card)
        self.rad_real.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: 600;")
        self.mode_group.addButton(self.rad_real)
        card_layout.addWidget(self.rad_real)

        if getattr(self.main_window, "display_mode", "SIMULATION") == "REAL":
            self.rad_real.setChecked(True)
        else:
            self.rad_sim.setChecked(True)

        self.rad_real.toggled.connect(self._on_real_mode_toggled)

        # Divider
        divider1 = QFrame(card)
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setStyleSheet("color: #2b3456;")
        card_layout.addWidget(divider1)

        # 2. Recovery Timeout Selector
        timeout_box = QHBoxLayout()
        timeout_lbl = QLabel("Auto-Recovery Timeout:", card)
        timeout_lbl.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 13px;")

        self.combo_timeout = QComboBox(card)
        self.combo_timeout.addItems([
            "15 seconds (Fast)",
            "30 seconds",
            "60 seconds (Default)",
            "120 seconds",
        ])
        # Map timeout to index
        curr_to = self.main_window.recovery_manager.timeout_seconds
        to_map = {15: 0, 30: 1, 60: 2, 120: 3}
        self.combo_timeout.setCurrentIndex(to_map.get(curr_to, 2))
        self.combo_timeout.currentIndexChanged.connect(self._on_timeout_changed)

        timeout_box.addWidget(timeout_lbl)
        timeout_box.addStretch()
        timeout_box.addWidget(self.combo_timeout)
        card_layout.addLayout(timeout_box)

        # 3. Global Emergency Hotkey Status
        hotkey_box = QHBoxLayout()
        hotkey_lbl = QLabel("Global Emergency Shortcut:", card)
        hotkey_lbl.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 13px;")

        reg_status = (
            "Active (Ctrl+Alt+Shift+R)"
            if self.main_window.recovery_manager.hotkey_registered
            else "Inactive / Local Fallback Only"
        )
        self.hotkey_val = QLabel(reg_status, card)
        self.hotkey_val.setStyleSheet(
            "color: #10b981; font-weight: 700; font-size: 12px;"
            if self.main_window.recovery_manager.hotkey_registered
            else "color: #94a3b8; font-size: 12px;"
        )
        hotkey_box.addWidget(hotkey_lbl)
        hotkey_box.addStretch()
        hotkey_box.addWidget(self.hotkey_val)
        card_layout.addLayout(hotkey_box)

        # Divider
        divider2 = QFrame(card)
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setStyleSheet("color: #2b3456;")
        card_layout.addWidget(divider2)

        # 4. Primary Target Display
        dev_name = self.main_window.display_controller.get_primary_device_name()
        dev_box = QHBoxLayout()
        dev_label = QLabel("Primary Display Device:", card)
        dev_label.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 13px;")
        dev_val = QLabel(dev_name, card)
        dev_val.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 13px;")
        dev_box.addWidget(dev_label)
        dev_box.addStretch()
        dev_box.addWidget(dev_val)
        card_layout.addLayout(dev_box)

        # 5. Current Subscription Tier & Reset Button
        tier_box = QHBoxLayout()
        tier_label = QLabel("Subscription Tier:", card)
        tier_label.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 13px;")
        self.tier_val = QLabel(f"{self.main_window.subscription_tier} Tier", card)
        self.tier_val.setStyleSheet("color: #8b5cf6; font-weight: 700; font-size: 13px;")
        tier_box.addWidget(tier_label)
        tier_box.addStretch()
        tier_box.addWidget(self.tier_val)
        card_layout.addLayout(tier_box)

        self.btn_reset_free = QPushButton("Reset to Free Tier", card)
        self.btn_reset_free.setProperty("class", "btn-dialog-close")
        self.btn_reset_free.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_free.setEnabled(self.main_window.subscription_tier != "Free")
        self.btn_reset_free.clicked.connect(self._on_reset_free)
        card_layout.addWidget(self.btn_reset_free)

        # Divider
        divider3 = QFrame(card)
        divider3.setFrameShape(QFrame.Shape.HLine)
        divider3.setStyleSheet("color: #2b3456;")
        card_layout.addWidget(divider3)

        # Checkboxes
        self.chk_sound = QCheckBox(
            "Enable Sound Effects (System Beep on actions)", card
        )
        self.chk_sound.setChecked(self.main_window.sound_enabled)
        self.chk_sound.toggled.connect(self.main_window.set_sound_enabled)
        card_layout.addWidget(self.chk_sound)

        self.chk_anim = QCheckBox("Enable UI Rotation Animations", card)
        self.chk_anim.setChecked(self.main_window.animations_enabled)
        self.chk_anim.toggled.connect(self.main_window.set_animations_enabled)
        card_layout.addWidget(self.chk_anim)

        layout.addWidget(card)

        # Safety Notice Box
        safety_card = QFrame(self)
        safety_card.setStyleSheet(
            "background-color: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); "
            "border-radius: 8px; padding: 10px;"
        )
        sf_layout = QVBoxLayout(safety_card)
        sf_layout.setContentsMargins(10, 8, 10, 8)
        sf_text = QLabel(
            "🛡️ Safety System Notice: When a real screen rotation occurs, an automatic recovery countdown starts. "
            "If unconfirmed before the timer reaches 0, the screen automatically restores to its original mode. "
            "Pressing Ctrl+Alt+Shift+R or Emergency Recovery immediately levels the screen.",
            safety_card,
        )
        sf_text.setStyleSheet("color: #cbd5e1; font-size: 11px; line-height: 1.3;")
        sf_text.setWordWrap(True)
        sf_layout.addWidget(sf_text)
        layout.addWidget(safety_card)

        # Close Button
        self.btn_close = QPushButton("CLOSE", self)
        self.btn_close.setProperty("class", "btn-dialog-close")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        layout.addWidget(self.btn_close)

    def _on_timeout_changed(self, index: int) -> None:
        timeout_vals = [15, 30, 60, 120]
        selected = timeout_vals[index] if index < len(timeout_vals) else 60
        self.main_window.recovery_manager.set_timeout_seconds(selected)
        save_settings({
            "sound_enabled": self.main_window.sound_enabled,
            "animations_enabled": self.main_window.animations_enabled,
            "timeout_seconds": selected,
        })

    def _on_real_mode_toggled(self, checked: bool) -> None:
        if checked:
            if (
                os.environ.get("PYTEST_CURRENT_TEST")
                or os.environ.get("QT_QPA_PLATFORM") == "offscreen"
            ):
                self.main_window.set_display_mode("REAL")
                return

            confirm = QMessageBox(self)
            confirm.setIcon(QMessageBox.Icon.Warning)
            confirm.setWindowTitle("Confirm Real Display Mode — GharBeka")
            confirm.setText(
                "⚠️ Enable Real Display Mode?\n\n"
                "This mode will execute actual Windows display API calls to physically rotate "
                "your monitor display orientation.\n\n"
                "• Please save your work in all open applications first.\n"
                "• Emergency recovery remains accessible in the app.\n\n"
                "Are you sure you want to enable Real Display Mode?"
            )
            confirm.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            confirm.setDefaultButton(QMessageBox.StandardButton.No)

            res = confirm.exec()
            if res == QMessageBox.StandardButton.Yes:
                self.main_window.set_display_mode("REAL")
            else:
                self.rad_sim.setChecked(True)
                self.main_window.set_display_mode("SIMULATION")
        else:
            self.main_window.set_display_mode("SIMULATION")

    def _on_reset_free(self) -> None:
        self.main_window.reset_to_free_tier()
        self.tier_val.setText(f"{self.main_window.subscription_tier} Tier")
        self.btn_reset_free.setEnabled(False)
