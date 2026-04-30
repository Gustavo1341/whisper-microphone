from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


class AppTheme:
    """Design system Apple-style para o Whisper Microfone.

    Todas as constantes de cor e tipografia ficam aqui — nenhum valor
    hardcoded em outros módulos de UI.
    """

    # ------------------------------------------------------------------
    # Paleta de cores
    # ------------------------------------------------------------------
    BG_PRIMARY: str = "#FFFFFF"
    BG_SECONDARY: str = "#F5F5F7"
    BG_TERTIARY: str = "#E8E8ED"

    TEXT_PRIMARY: str = "#1D1D1F"
    TEXT_SECONDARY: str = "#6E6E73"

    ACCENT: str = "#0071E3"
    ACCENT_HOVER: str = "#0077ED"
    ACCENT_PRESSED: str = "#005BBE"

    # Estados do engine
    RECORDING: str = "#FF3B30"
    TRANSCRIBING: str = "#FF9500"
    READY_WARM: str = "#34C759"
    READY_COLD: str = "#6E6E73"
    LOADING: str = "#0071E3"
    PAUSED: str = "#8E8E93"
    ERROR: str = "#FF3B30"

    BORDER: str = "rgba(0, 0, 0, 0.08)"

    # ------------------------------------------------------------------
    # Tipografia
    # ------------------------------------------------------------------
    FONT_FAMILY: str = (
        '"SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", sans-serif'
    )
    # Tamanhos em pontos (pt), compatível com QFont
    FONT_SIZE_BASE: int = 14
    FONT_SIZE_SMALL: int = 12
    FONT_SIZE_LARGE: int = 20

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    SIDEBAR_WIDTH: int = 220
    CARD_RADIUS: int = 12

    # ------------------------------------------------------------------
    # Estado → cor (mapa auxiliar para widgets dinâmicos)
    # ------------------------------------------------------------------
    STATE_COLOR: dict[str, str] = {
        "idle_warm": READY_WARM,
        "idle_cold": READY_COLD,
        "loading": LOADING,
        "recording": RECORDING,
        "transcribing": TRANSCRIBING,
        "paused": PAUSED,
        "error": ERROR,
    }

    # ------------------------------------------------------------------
    # QSS completo
    # ------------------------------------------------------------------
    @staticmethod
    def build_stylesheet() -> str:
        t = AppTheme
        return f"""
/* ── Base ──────────────────────────────────────────────────────────── */
QMainWindow,
QDialog,
QWidget {{
    background-color: {t.BG_PRIMARY};
    color: {t.TEXT_PRIMARY};
    font-family: "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", sans-serif;
    font-size: {t.FONT_SIZE_BASE}px;
}}

/* ── Sidebar frame ──────────────────────────────────────────────────── */
QFrame#sidebar {{
    background-color: {t.BG_SECONDARY};
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

QPushButton:hover {{
    background-color: {t.ACCENT_HOVER};
}}

QPushButton:pressed {{
    background-color: {t.ACCENT_PRESSED};
}}

QPushButton:disabled {{
    background-color: {t.BG_TERTIARY};
    color: {t.TEXT_SECONDARY};
}}

/* ── Botão flat (secundário / nav) ──────────────────────────────────── */
QPushButton[flat="true"] {{
    background-color: transparent;
    color: {t.TEXT_PRIMARY};
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: {t.FONT_SIZE_BASE}px;
    font-weight: 400;
    text-align: left;
}}

QPushButton[flat="true"]:hover {{
    background-color: {t.BG_TERTIARY};
}}

QPushButton[flat="true"]:pressed {{
    background-color: {t.BG_TERTIARY};
}}

/* Item de nav selecionado (pill azul) */
QPushButton[flat="true"][selected="true"] {{
    background-color: {t.ACCENT};
    color: #FFFFFF;
    font-weight: 500;
}}

QPushButton[flat="true"][selected="true"]:hover {{
    background-color: {t.ACCENT_HOVER};
}}

/* ── Inputs ─────────────────────────────────────────────────────────── */
QLineEdit,
QComboBox {{
    background-color: {t.BG_SECONDARY};
    color: {t.TEXT_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: {t.FONT_SIZE_BASE}px;
    selection-background-color: {t.ACCENT};
}}

QLineEdit:focus,
QComboBox:focus {{
    border-color: {t.ACCENT};
    outline: none;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {t.BG_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    selection-background-color: {t.ACCENT};
    selection-color: #FFFFFF;
    padding: 4px;
}}

/* ── Tabela ─────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {t.BG_PRIMARY};
    alternate-background-color: {t.BG_SECONDARY};
    color: {t.TEXT_PRIMARY};
    border: none;
    gridline-color: transparent;
    font-size: {t.FONT_SIZE_BASE}px;
}}

QTableWidget::item {{
    padding: 6px 12px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {t.ACCENT};
    color: #FFFFFF;
}}

QHeaderView::section {{
    background-color: {t.BG_PRIMARY};
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
    background: {t.BG_TERTIARY};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t.TEXT_SECONDARY};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
    height: 0;
    width: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {t.BG_TERTIARY};
    border-radius: 3px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {t.TEXT_SECONDARY};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: none;
    height: 0;
    width: 0;
}}

/* ── Tooltip ────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {t.TEXT_PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {t.FONT_SIZE_SMALL}px;
}}

/* ── Cards ──────────────────────────────────────────────────────────── */
QFrame[card="true"] {{
    background-color: {t.BG_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: {t.CARD_RADIUS}px;
}}

/* ── Separadores ────────────────────────────────────────────────────── */
QFrame[separator="true"] {{
    background-color: {t.BORDER};
    max-height: 1px;
    border: none;
}}

/* ── Stackedwidget / área de conteúdo ───────────────────────────────── */
QStackedWidget {{
    background-color: {t.BG_PRIMARY};
}}
"""

    @staticmethod
    def apply(app: QApplication) -> None:
        """Aplica o design system completo à QApplication."""
        app.setStyle("Fusion")
        app.setStyleSheet(AppTheme.build_stylesheet())

        font = QFont()
        font.setFamilies(
            ["SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI"]
        )
        font.setPixelSize(AppTheme.FONT_SIZE_BASE)
        app.setFont(font)


# ---------------------------------------------------------------------------
# Verificação visual — abre janela de amostra
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    app = QApplication(sys.argv)
    AppTheme.apply(app)

    win = QWidget()
    win.setWindowTitle("AppTheme — Amostra de estilos")
    win.resize(500, 400)

    root = QVBoxLayout(win)
    root.setContentsMargins(24, 24, 24, 24)
    root.setSpacing(16)

    root.addWidget(QLabel("Texto primário — tamanho base"))

    lbl_sec = QLabel("Texto secundário — tamanho pequeno")
    lbl_sec.setProperty("secondary", True)
    lbl_sec.style().unpolish(lbl_sec)
    lbl_sec.style().polish(lbl_sec)
    root.addWidget(lbl_sec)

    sep = QFrame()
    sep.setProperty("separator", True)
    root.addWidget(sep)

    btn_row = QHBoxLayout()
    btn_primary = QPushButton("Botão primário")
    btn_flat = QPushButton("Botão flat")
    btn_flat.setFlat(True)
    btn_selected = QPushButton("Nav selecionado")
    btn_selected.setFlat(True)
    btn_selected.setProperty("selected", True)
    btn_row.addWidget(btn_primary)
    btn_row.addWidget(btn_flat)
    btn_row.addWidget(btn_selected)
    root.addLayout(btn_row)

    line = QLineEdit()
    line.setPlaceholderText("Campo de texto...")
    root.addWidget(line)

    combo = QComboBox()
    combo.addItems(["Opção 1", "Opção 2", "Opção 3"])
    root.addWidget(combo)

    root.addStretch()
    win.show()
    sys.exit(app.exec())
