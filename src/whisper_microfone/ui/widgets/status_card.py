from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
_COLOR_BG = "#FFFFFF"
_COLOR_TEXT_PRIMARY = "#1D1D1F"
_COLOR_TEXT_SECONDARY = "#6E6E73"
_COLOR_BORDER = "rgba(0,0,0,0.08)"

_COLOR_RECORDING = "#FF3B30"
_COLOR_TRANSCRIBING = "#FF9500"
_COLOR_READY_WARM = "#34C759"
_COLOR_LOADING = "#0071E3"
_COLOR_PAUSED = "#6E6E73"
_COLOR_READY_COLD = "#6E6E73"
_COLOR_ERROR = "#FF3B30"

_DOT_SIZE = 12
_FONT_STATE = 20
_FONT_SUB = 12

_STATE_MAP: dict[str, tuple[str, str, str]] = {
    # state -> (dot_color, state_text, sub_text)
    "recording":    (_COLOR_RECORDING,    "Ouvindo...",              "Segure para gravar"),
    "idle_warm":    (_COLOR_READY_WARM,   "Pronto",                  "Modelo carregado"),
    "transcribing": (_COLOR_TRANSCRIBING, "Processando...",          "Transcrevendo áudio"),
    "loading":      (_COLOR_LOADING,      "Carregando IA...",        "Aguarde"),
    "paused":       (_COLOR_PAUSED,       "Pausado",                 "PTT desativado"),
    "idle_cold":    (_COLOR_READY_COLD,   "Pronto",                  "Modelo descarregado"),
    "error":        (_COLOR_ERROR,        "Erro",                    "Verifique os logs"),
}
_STATE_FALLBACK = (_COLOR_READY_COLD, "Pronto", "")


class _DotIndicator(QWidget):
    """Círculo colorido de 12 px desenhado com QPainter."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = QColor(_COLOR_READY_COLD)
        self.setFixedSize(_DOT_SIZE, _DOT_SIZE)

    def set_color(self, hex_color: str) -> None:
        self._color = QColor(hex_color)
        self.update()

    def paintEvent(self, _event: object) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)
        painter.drawEllipse(0, 0, _DOT_SIZE, _DOT_SIZE)
        painter.end()


class StatusCard(QFrame):
    """Card Apple-style exibindo o estado atual do engine."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.set_state("idle_cold")

    def _build_ui(self) -> None:
        self.setObjectName("StatusCard")
        self.setStyleSheet(
            """
            QFrame#StatusCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
            """
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(4)

        # Linha superior: dot + estado
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        top_row.setContentsMargins(0, 0, 0, 0)

        self._dot = _DotIndicator()
        top_row.addWidget(self._dot, 0, Qt.AlignmentFlag.AlignVCenter)

        self._state_label = QLabel()
        self._state_label.setStyleSheet(
            f"color: {_COLOR_TEXT_PRIMARY}; font-size: {_FONT_STATE}px; font-weight: 600;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
        )
        top_row.addWidget(self._state_label, 1, Qt.AlignmentFlag.AlignVCenter)

        outer.addLayout(top_row)

        # Subtexto
        self._sub_label = QLabel()
        self._sub_label.setStyleSheet(
            f"color: {_COLOR_TEXT_SECONDARY}; font-size: {_FONT_SUB}px;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
        )
        self._sub_label.setIndent(_DOT_SIZE + 10)  # alinha com o texto do estado
        outer.addWidget(self._sub_label)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_state(self, state: str) -> None:
        """Atualiza o card para refletir o estado informado.

        States reconhecidos: recording, idle_warm, transcribing, loading,
        paused, idle_cold, error. Qualquer outro cai no fallback cinza.
        """
        dot_color, state_text, sub_text = _STATE_MAP.get(state, _STATE_FALLBACK)
        self._dot.set_color(dot_color)
        self._state_label.setText(state_text)
        self._sub_label.setText(sub_text)
