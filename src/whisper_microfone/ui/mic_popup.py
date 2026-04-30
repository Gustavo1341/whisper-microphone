"""Mini janela flutuante de microfone — estilo Win+H.

Abre via Ctrl+Alt+Shift+Q. Clique no botão central para gravar/parar.
Fecha automaticamente após transcrever.
"""
from __future__ import annotations

import math

from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, Slot
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QIcon, QPixmap, QMouseEvent
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QLabel, QWidget

from whisper_microfone.engine import Engine

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
_BG             = "#1E1E1E"
_BTN_IDLE       = "#C084FC"   # roxo claro
_BTN_RECORDING  = "#FF3B30"   # vermelho
_BTN_PROCESSING = "#FF9500"   # laranja
_ICON_COLOR     = "#FFFFFF"
_TOOLTIP_BG     = "#2C2C2E"
_TOOLTIP_FG     = "#FFFFFF"

_POPUP_W  = 180
_POPUP_H  = 80
_BTN_SIZE = 52
_ANIM_MS  = 80


def _make_mic_icon(color: str, size: int = 28) -> QIcon:
    """Ícone de microfone desenhado com QPainter."""
    px = QPixmap(size, size)
    px.fill(QColor(0, 0, 0, 0))
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(c))

    # Corpo do microfone
    body_w, body_h = size * 0.36, size * 0.52
    bx = (size - body_w) / 2
    by = size * 0.04
    p.drawRoundedRect(QRectF(bx, by, body_w, body_h), body_w / 2, body_w / 2)

    # Arco (suporte)
    pen = QPen(c)
    pen.setWidthF(size * 0.09)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    arc_rect = QRectF(size * 0.18, size * 0.26, size * 0.64, size * 0.48)
    p.drawArc(arc_rect, 0, -180 * 16)

    # Haste
    cx = size / 2
    p.drawLine(QRectF(cx, size * 0.72, 0, size * 0.18).topLeft(),
               QRectF(cx, size * 0.72, 0, size * 0.18).bottomLeft().__class__(cx, size * 0.90))

    # Base
    pen2 = QPen(c)
    pen2.setWidthF(size * 0.09)
    pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen2)
    p.drawLine(QRectF(size * 0.30, size * 0.90, size * 0.40, 0).topLeft(),
               QRectF(size * 0.30, size * 0.90, size * 0.40, 0).topRight())

    p.end()
    return QIcon(px)


def _dots_icon(color: str, size: int = 28, angle: int = 0) -> QIcon:
    """Três pontos pulsantes para o estado de gravação ativa."""
    px = QPixmap(size, size)
    px.fill(QColor(0, 0, 0, 0))
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)

    base_r = size * 0.095
    for i, cx_ratio in enumerate([0.28, 0.50, 0.72]):
        pulse = 0.75 + 0.25 * ((math.sin(math.radians(angle + i * 120)) + 1) / 2)
        r = base_r * pulse
        cy = size / 2
        cx = size * cx_ratio
        alpha = int(180 + 75 * pulse)
        c = QColor(color)
        c.setAlpha(alpha)
        p.setBrush(QBrush(c))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))

    p.end()
    return QIcon(px)


# ---------------------------------------------------------------------------
# Tooltip balão
# ---------------------------------------------------------------------------
class _Balloon(QLabel):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"""
            QLabel {{
                background: {_TOOLTIP_BG};
                color: {_TOOLTIP_FG};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()

    def show_text(self, text: str) -> None:
        self.setText(text)
        self.adjustSize()
        # Centraliza acima do popup
        parent = self.parent()
        if parent:
            pw = parent.width()
            x = (pw - self.width()) // 2
            self.move(x, -self.height() - 6)
        self.show()


# ---------------------------------------------------------------------------
# MicButton
# ---------------------------------------------------------------------------
class _MicButton(QPushButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(_BTN_SIZE, _BTN_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._state = "idle"
        self._angle = 0
        self._apply_style(_BTN_IDLE)
        self.setIcon(_make_mic_icon(_ICON_COLOR))
        self.setIconSize(self.size() * 0.52)

    def set_state(self, state: str, angle: int = 0) -> None:
        self._state = state
        self._angle = angle
        if state == "recording":
            self._apply_style(_BTN_RECORDING)
            self.setIcon(_dots_icon(_ICON_COLOR, angle=angle))
        elif state == "transcribing":
            self._apply_style(_BTN_PROCESSING)
            self.setIcon(_make_mic_icon(_ICON_COLOR))
        else:
            self._apply_style(_BTN_IDLE)
            self.setIcon(_make_mic_icon(_ICON_COLOR))
        self.setIconSize(self.size() * 0.52)

    def _apply_style(self, color: str) -> None:
        half = _BTN_SIZE // 2
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: {half}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {QColor(color).lighter(115).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(color).darker(110).name()};
            }}
        """)


# ---------------------------------------------------------------------------
# MicPopup
# ---------------------------------------------------------------------------
class MicPopup(QDialog):
    """Mini janela flutuante de microfone estilo Win+H."""

    def __init__(self, engine: Engine, parent: QWidget | None = None) -> None:
        super().__init__(
            parent,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool,
        )
        self._engine = engine
        self._drag_pos: QPoint | None = None
        self._angle = 0

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(_POPUP_W, _POPUP_H)

        self._build_ui()
        self._position_bottom_center()

        # Timer de animação
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(_ANIM_MS)
        self._anim_timer.timeout.connect(self._tick)

        # Conecta sinais do engine
        engine.state_changed.connect(self._on_state)
        engine.transcribed.connect(self._on_transcribed)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QDialog {{
                background: {_BG};
                border-radius: 16px;
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 0, 14, 0)
        root.setSpacing(0)

        # Botão esquerdo (config — placeholder)
        self._btn_cfg = QPushButton("⚙")
        self._btn_cfg.setFixedSize(28, 28)
        self._btn_cfg.setFlat(True)
        self._btn_cfg.setStyleSheet("color: #8E8E93; font-size: 16px; border: none; background: transparent;")
        self._btn_cfg.setCursor(Qt.CursorShape.PointingHandCursor)

        # Botão central (microfone)
        self._mic_btn = _MicButton()
        self._mic_btn.clicked.connect(self._on_mic_clicked)

        # Botão direito (fechar)
        self._btn_close = QPushButton("✕")
        self._btn_close.setFixedSize(28, 28)
        self._btn_close.setFlat(True)
        self._btn_close.setStyleSheet("color: #8E8E93; font-size: 13px; border: none; background: transparent;")
        self._btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_close.clicked.connect(self._close_safe)

        root.addWidget(self._btn_cfg, 0, Qt.AlignmentFlag.AlignVCenter)
        root.addStretch()
        root.addWidget(self._mic_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        root.addStretch()
        root.addWidget(self._btn_close, 0, Qt.AlignmentFlag.AlignVCenter)

        # Balão de tooltip (filho do popup, posicionado acima)
        self._balloon = _Balloon(self)

    # ------------------------------------------------------------------
    # Posicionamento
    # ------------------------------------------------------------------

    def _position_bottom_center(self) -> None:
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.availableGeometry()
            x = sg.center().x() - self.width() // 2
            y = sg.bottom() - self.height() - 48
            self.move(x, y)

    # ------------------------------------------------------------------
    # Drag para mover
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------

    def _on_mic_clicked(self) -> None:
        self._engine.toggle_recording()

    def _on_state(self, state: str) -> None:
        if state == "recording":
            self._balloon.show_text("Ouvindo...")
            self._anim_timer.start()
        elif state == "transcribing":
            self._balloon.show_text("Processando...")
            self._anim_timer.stop()
            self._mic_btn.set_state("transcribing")
        else:
            self._balloon.hide()
            self._anim_timer.stop()
            self._mic_btn.set_state("idle")

    def _on_transcribed(self, _text: str, _meta: dict) -> None:
        QTimer.singleShot(300, self._close_safe)

    def _tick(self) -> None:
        self._angle = (self._angle + 40) % 360
        self._mic_btn.set_state("recording", self._angle)

    def _close_safe(self) -> None:
        if self._engine._recorder.is_recording:
            self._engine.toggle_recording()
        self.hide()

    # ------------------------------------------------------------------
    # Toggle público
    # ------------------------------------------------------------------

    @Slot()
    def toggle(self) -> None:
        if self.isVisible():
            self._close_safe()
        else:
            self._position_bottom_center()
            self.show()
            self.raise_()
            # Não roubar foco — o campo onde o usuário estava digitando deve
            # permanecer ativo para que a injeção funcione após transcrever.
            if not self._engine._recorder.is_recording:
                self._engine.toggle_recording()
