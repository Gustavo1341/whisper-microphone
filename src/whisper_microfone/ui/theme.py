from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


class AppTheme:
    """Design system dark-mode para o Whisper Microfone."""

    # Paleta de cores
    BG_PRIMARY: str = "#0d0e11"
    BG_SECONDARY: str = "#111318"
    BG_CARD: str = "#181a20"
    BG_CARD2: str = "#1c1e25"

    TEXT_PRIMARY: str = "rgba(255,255,255,0.90)"
    TEXT_SECONDARY: str = "rgba(255,255,255,0.48)"

    ACCENT: str = "#0071E3"
    ACCENT_HOVER: str = "#0077ED"
    ACCENT_PRESSED: str = "#005BBE"

    # Estados do engine
    RECORDING: str = "#FF3B30"
    TRANSCRIBING: str = "#FF9500"
    READY: str = "#34C759"
    PAUSED: str = "#8E8E93"
    ERROR: str = "#FF3B30"
    SUCCESS: str = "#34C759"
    WARNING: str = "#FF9500"

    BORDER: str = "rgba(255,255,255,0.08)"

    # Tipografia
    FONT_FAMILY: str = '"Segoe UI", "Helvetica Neue", sans-serif'
    FONT_SIZE_BASE: int = 14
    FONT_SIZE_SMALL: int = 12
    FONT_SIZE_LARGE: int = 20

    # Layout
    SIDEBAR_WIDTH: int = 220
    CARD_RADIUS: str = "12px"
    CARD_RADIUS_INT: int = 12

    # Estado → cor
    STATE_COLOR: dict[str, str] = {
        "idle":         READY,
        "recording":    RECORDING,
        "transcribing": TRANSCRIBING,
        "paused":       PAUSED,
        "error":        ERROR,
    }

    @staticmethod
    def build_stylesheet() -> str:
        t = AppTheme
        return f"""
/* ── Base ──────────────────────────────────────────────────────────── */
QMainWindow, QDialog, QWidget {{
    background-color: {t.BG_PRIMARY};
    color: {t.TEXT_PRIMARY};
    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: {t.FONT_SIZE_BASE}px;
}}

/* ── Sidebar frame ──────────────────────────────────────────────────── */
QFrame#sidebar {{
    background-color: {t.BG_PRIMARY};
    border: none;
    border-right: 1px solid {t.BORDER};
}}

/* ── Labels ─────────────────────────────────────────────────────────── */
QLabel {{
    color: {t.TEXT_PRIMARY};
    background: transparent;
}}

QLabel[secondary="true"] {{
    color: {t.TEXT_SECONDARY};
    font-size: {t.FONT_SIZE_SMALL}px;
}}

/* ── Botão primário ─────────────────────────────────────────────────── */
QPushButton {{
    background-color: {t.ACCENT};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: {t.FONT_SIZE_BASE}px;
    font-weight: 500;
}}

QPushButton:hover {{ background-color: {t.ACCENT_HOVER}; }}
QPushButton:pressed {{ background-color: {t.ACCENT_PRESSED}; }}
QPushButton:disabled {{
    background-color: {t.BG_CARD2};
    color: {t.TEXT_SECONDARY};
}}

/* ── Botão flat (secundário / nav) ──────────────────────────────────── */
QPushButton[flat="true"] {{
    background-color: transparent;
    color: {t.TEXT_SECONDARY};
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: {t.FONT_SIZE_BASE}px;
    font-weight: 400;
    text-align: left;
}}

QPushButton[flat="true"]:hover {{
    background-color: {t.BORDER};
    color: {t.TEXT_PRIMARY};
}}

QPushButton[flat="true"][selected="true"] {{
    background-color: rgba(255,255,255,0.08);
    color: {t.TEXT_PRIMARY};
    font-weight: 500;
}}

QPushButton[flat="true"][selected="true"]:hover {{
    background-color: rgba(255,255,255,0.12);
}}

/* ── Inputs ─────────────────────────────────────────────────────────── */
QLineEdit, QComboBox {{
    background-color: {t.BG_CARD};
    color: {t.TEXT_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: {t.FONT_SIZE_BASE}px;
    selection-background-color: {t.ACCENT};
}}

QLineEdit:focus, QComboBox:focus {{
    border-color: {t.ACCENT};
    outline: none;
}}

QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{ width: 10px; height: 10px; }}

QComboBox QAbstractItemView {{
    background-color: {t.BG_CARD};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    selection-background-color: {t.ACCENT};
    selection-color: #FFFFFF;
    color: {t.TEXT_PRIMARY};
    padding: 4px;
}}

/* ── SpinBox ────────────────────────────────────────────────────────── */
QSpinBox {{
    background-color: {t.BG_CARD};
    color: {t.TEXT_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: {t.FONT_SIZE_BASE}px;
}}

QSpinBox:focus {{ border-color: {t.ACCENT}; }}
QSpinBox::up-button, QSpinBox::down-button {{ width: 18px; border: none; }}

/* ── CheckBox ───────────────────────────────────────────────────────── */
QCheckBox {{
    color: {t.TEXT_PRIMARY};
    font-size: {t.FONT_SIZE_SMALL}px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {t.BORDER};
    background: {t.BG_CARD};
}}

QCheckBox::indicator:checked {{
    background: {t.ACCENT};
    border-color: {t.ACCENT};
}}

/* ── Tabela ─────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {t.BG_SECONDARY};
    alternate-background-color: {t.BG_CARD};
    color: {t.TEXT_PRIMARY};
    border: none;
    gridline-color: transparent;
    font-size: {t.FONT_SIZE_BASE}px;
}}

QTableWidget::item {{ padding: 6px 12px; border: none; }}
QTableWidget::item:selected {{
    background-color: {t.ACCENT};
    color: #FFFFFF;
}}

QHeaderView::section {{
    background-color: {t.BG_SECONDARY};
    color: {t.TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {t.BORDER};
    padding: 6px 12px;
    font-size: {t.FONT_SIZE_SMALL}px;
    font-weight: 500;
}}

/* ── Scrollbar minimalista ──────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.12);
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(255,255,255,0.24);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none; height: 0; width: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: rgba(255,255,255,0.12);
    border-radius: 3px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: rgba(255,255,255,0.24);
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none; height: 0; width: 0;
}}

/* ── Tooltip ────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {t.BG_CARD};
    color: {t.TEXT_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {t.FONT_SIZE_SMALL}px;
}}

/* ── Cards ──────────────────────────────────────────────────────────── */
QFrame[card="true"] {{
    background-color: {t.BG_CARD};
    border: 1px solid {t.BORDER};
    border-radius: {t.CARD_RADIUS};
}}

/* ── Separadores ────────────────────────────────────────────────────── */
QFrame[separator="true"] {{
    background-color: {t.BORDER};
    max-height: 1px;
    border: none;
}}

/* ── StackedWidget / área de conteúdo ───────────────────────────────── */
QStackedWidget {{ background-color: {t.BG_SECONDARY}; }}

/* ── Menu (tray) ────────────────────────────────────────────────────── */
QMenu {{
    background-color: {t.BG_CARD};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    padding: 4px;
    color: {t.TEXT_PRIMARY};
}}
QMenu::item {{
    padding: 6px 20px;
    border-radius: 4px;
    font-size: 13px;
}}
QMenu::item:selected {{
    background-color: rgba(255,255,255,0.08);
}}
QMenu::item:disabled {{
    color: {t.TEXT_SECONDARY};
}}
QMenu::separator {{
    height: 1px;
    background: {t.BORDER};
    margin: 4px 0;
}}

/* ── Slider ─────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    background: {t.BG_CARD2};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {t.ACCENT};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {t.ACCENT};
    border-radius: 2px;
}}
"""

    @staticmethod
    def apply(app: QApplication) -> None:
        app.setStyle("Fusion")
        app.setStyleSheet(AppTheme.build_stylesheet())

        font = QFont()
        font.setFamilies(["Segoe UI", "Helvetica Neue"])
        font.setPixelSize(AppTheme.FONT_SIZE_BASE)
        app.setFont(font)
