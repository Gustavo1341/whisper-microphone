from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
_COLOR_BG = "#FFFFFF"
_COLOR_TITLE = "#6E6E73"
_COLOR_TEXT = "#1D1D1F"
_COLOR_EMPTY = "#6E6E73"
_COLOR_FOOTER = "#6E6E73"

_FONT_TITLE = 11
_FONT_TEXT = 14
_FONT_FOOTER = 11

_MAX_LINES = 4


class TranscriptionCard(QFrame):
    """Card Apple-style exibindo a última transcrição com metadados."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._show_empty()

    def _build_ui(self) -> None:
        self.setObjectName("TranscriptionCard")
        self.setStyleSheet(
            """
            QFrame#TranscriptionCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
            """
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Título
        self._title_label = QLabel("ÚLTIMA TRANSCRIÇÃO")
        self._title_label.setStyleSheet(
            f"color: {_COLOR_TITLE}; font-size: {_FONT_TITLE}px; font-weight: 500;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
            " letter-spacing: 0.5px;"
        )
        layout.addWidget(self._title_label)

        # Texto da transcrição
        self._text_label = QLabel()
        self._text_label.setWordWrap(True)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addWidget(self._text_label)

        # Rodapé: idioma + latência
        self._footer_label = QLabel()
        self._footer_label.setStyleSheet(
            f"color: {_COLOR_FOOTER}; font-size: {_FONT_FOOTER}px;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
        )
        self._footer_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._footer_label)

    def _show_empty(self) -> None:
        self._text_label.setText("Nenhuma transcrição ainda")
        self._text_label.setStyleSheet(
            f"color: {_COLOR_EMPTY}; font-size: {_FONT_TEXT}px; font-style: italic;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
        )
        self._footer_label.setText("")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_transcription(self, text: str, metadata: dict) -> None:
        """Atualiza o card com nova transcrição e metadados.

        Args:
            text: Texto transcrito.
            metadata: Dicionário com chaves opcionais:
                - latency_ms (float): latência em milissegundos.
                - language (str): idioma detectado/configurado.
                - duration_ms (float): duração do áudio em ms.
        """
        if not text:
            self._show_empty()
            return

        # Limita a exibição a _MAX_LINES linhas truncando por caracteres
        lines = text.splitlines()
        if len(lines) > _MAX_LINES:
            display_text = "\n".join(lines[:_MAX_LINES]) + "…"
        else:
            display_text = text

        self._text_label.setText(display_text)
        self._text_label.setStyleSheet(
            f"color: {_COLOR_TEXT}; font-size: {_FONT_TEXT}px;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
        )

        # Rodapé
        parts: list[str] = []
        language = metadata.get("language", "")
        if language and language != "auto":
            parts.append(language.upper())

        latency_ms = metadata.get("latency_ms")
        if latency_ms is not None:
            parts.append(f"{latency_ms:.0f} ms")

        duration_ms = metadata.get("duration_ms")
        if duration_ms is not None:
            parts.append(f"{duration_ms / 1000:.1f}s áudio")

        self._footer_label.setText("  ·  ".join(parts))
