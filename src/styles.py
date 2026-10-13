"""Qt Style Sheets (QSS) and theme constants for GharBeka.

Modern SaaS dark aesthetic with charcoal surfaces, purple and electric-blue accents.
"""

# Color Palette Constants
BG_DARK = "#0b0e17"
BG_SIDEBAR = "#111422"
BG_CARD = "#161b2e"
BG_CARD_ELEVATED = "#1f2642"
BG_HOVER = "#273052"

BORDER_MUTED = "#2b3456"
BORDER_ACCENT = "#8b5cf6"
BORDER_CYAN = "#0ea5e9"

TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#cbd5e1"
TEXT_MUTED = "#94a3b8"

PURPLE_PRIMARY = "#8b5cf6"
PURPLE_HOVER = "#7c3aed"
PURPLE_DARK = "#6d28d9"

BLUE_ELECTRIC = "#38bdf8"
CYAN_ACCENT = "#22d3ee"

SUCCESS_GREEN = "#10b981"
WARNING_AMBER = "#f59e0b"

MAIN_STYLE_SHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
}}

QWidget#CentralWidget {{
    background-color: {BG_DARK};
}}

/* Sidebar */
QWidget#Sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER_MUTED};
}}

QLabel#LogoText {{
    color: {TEXT_PRIMARY};
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}

QLabel#TaglineText {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 500;
    line-height: 1.3;
}}

QPushButton.nav-item {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 600;
    text-align: left;
    padding: 11px 16px;
    border-radius: 8px;
    border: 1px solid transparent;
}}

QPushButton.nav-item:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_MUTED};
}}

QPushButton.nav-item:checked, QPushButton.nav-item[active="true"] {{
    background-color: {BG_CARD_ELEVATED};
    color: {BLUE_ELECTRIC};
    border: 1px solid {BORDER_ACCENT};
    font-weight: 700;
}}

/* Scroll Area */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: {BG_DARK};
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER_MUTED};
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {PURPLE_PRIMARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Badges */
QLabel#ParodyBadge {{
    background-color: rgba(139, 92, 246, 0.18);
    color: {PURPLE_PRIMARY};
    border: 1px solid rgba(139, 92, 246, 0.45);
    border-radius: 14px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}}

QLabel#SimulationBadge {{
    background-color: rgba(56, 189, 248, 0.15);
    color: {BLUE_ELECTRIC};
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}}

/* Hero & General Cards */
QFrame.dashboard-card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_MUTED};
    border-radius: 16px;
}}

QFrame.pricing-card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_MUTED};
    border-radius: 14px;
}}

QFrame.pricing-card-highlighted {{
    background-color: {BG_CARD_ELEVATED};
    border: 2px solid {PURPLE_PRIMARY};
    border-radius: 14px;
}}

/* Titles & Text */
QLabel#HeaderTitle {{
    color: {TEXT_PRIMARY};
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    padding: 2px 0px;
}}

QLabel#HeaderSubtitle {{
    color: {TEXT_SECONDARY};
    font-size: 14px;
    font-weight: 500;
}}

QLabel#CardTitle {{
    color: {TEXT_PRIMARY};
    font-size: 17px;
    font-weight: 700;
}}

QLabel#CardDescription {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
    line-height: 1.4;
}}

/* Status Indicator */
QLabel#StatusIndicator {{
    font-size: 13px;
    font-weight: 700;
    padding: 8px 18px;
    border-radius: 20px;
}}

/* Buttons */
QPushButton#RotateButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURPLE_PRIMARY}, stop:1 {PURPLE_DARK});
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.8px;
    padding: 12px 28px;
    min-height: 20px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}}

QPushButton#RotateButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 {PURPLE_HOVER});
    border: 1px solid {BLUE_ELECTRIC};
}}

QPushButton#RotateButton:pressed {{
    background-color: {PURPLE_DARK};
}}

QPushButton#UnrotateButton {{
    background-color: rgba(56, 189, 248, 0.1);
    color: {BLUE_ELECTRIC};
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.8px;
    padding: 12px 28px;
    min-height: 20px;
    border-radius: 10px;
    border: 1px solid {BLUE_ELECTRIC};
}}

QPushButton#UnrotateButton:hover {{
    background-color: rgba(56, 189, 248, 0.2);
    color: #ffffff;
    border: 1px solid #7dd3fc;
}}

QPushButton#UnrotateButton:pressed {{
    background-color: rgba(56, 189, 248, 0.3);
}}

/* Pricing Buttons */
QPushButton.plan-btn-current {{
    background-color: {BG_HOVER};
    color: {TEXT_MUTED};
    font-size: 13px;
    font-weight: 700;
    min-height: 20px;
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid {BORDER_MUTED};
}}

QPushButton.plan-btn-upgrade {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURPLE_PRIMARY}, stop:1 {BLUE_ELECTRIC});
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    min-height: 20px;
    padding: 10px 16px;
    border-radius: 8px;
    border: none;
}}

QPushButton.plan-btn-upgrade:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 #67e8f9);
}}

QPushButton.plan-btn-enterprise {{
    background-color: transparent;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    font-weight: 700;
    min-height: 20px;
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid {BORDER_MUTED};
}}

QPushButton.plan-btn-enterprise:hover {{
    background-color: {BG_HOVER};
    border: 1px solid {BLUE_ELECTRIC};
}}

/* Feedback message bar */
QLabel#FeedbackBanner {{
    background-color: {BG_CARD_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_MUTED};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.4;
}}

/* Footer */
QLabel#FooterText {{
    color: {TEXT_MUTED};
    font-size: 12px;
    line-height: 1.4;
}}

/* Dialogs */
QDialog {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
}}

QFrame.dialog-card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_MUTED};
    border-radius: 12px;
}}

QPushButton.btn-dialog-primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURPLE_PRIMARY}, stop:1 {PURPLE_DARK});
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}}

QPushButton.btn-dialog-primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 {PURPLE_HOVER});
}}

QPushButton.btn-dialog-secondary {{
    background-color: rgba(56, 189, 248, 0.1);
    color: {BLUE_ELECTRIC};
    font-size: 13px;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid {BLUE_ELECTRIC};
}}

QPushButton.btn-dialog-secondary:hover {{
    background-color: rgba(56, 189, 248, 0.2);
    color: #ffffff;
}}

QPushButton.btn-dialog-danger {{
    background-color: rgba(245, 158, 11, 0.15);
    color: {WARNING_AMBER};
    font-size: 13px;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid {WARNING_AMBER};
}}

QPushButton.btn-dialog-danger:hover {{
    background-color: rgba(245, 158, 11, 0.3);
}}

QPushButton.btn-dialog-close {{
    background-color: transparent;
    color: {TEXT_MUTED};
    font-size: 13px;
    font-weight: 600;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid {BORDER_MUTED};
}}

QPushButton.btn-dialog-close:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QCheckBox {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {BORDER_MUTED};
    background-color: {BG_CARD};
}}

QCheckBox::indicator:checked {{
    background-color: {PURPLE_PRIMARY};
    border-color: {PURPLE_PRIMARY};
}}
"""
