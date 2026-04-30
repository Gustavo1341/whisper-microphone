"""System tray icon e menu para o Whisper Microfone.

Design minimalista Apple-style com ícones gerados programaticamente via QPainter.
Animação de loading/recording via QTimer não-bloqueante.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QIcon, QPixmap, QPen, QBrush
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMainWindow

from whisper_microfone.config.schemas import FullConfig
from whisper_microfone.engine import Engine

# ---------------------------------------------------------------------------
# Constantes de cor (Apple Human Interface Guidelines)
# ---------------------------------------------------------------------------
_COLOR_IDLE_COLD = QColor("#8E8E93")
_COLOR_IDLE_WARM = QColor("#34C759")
_COLOR_LOADING = QColor("#0071E3")
_COLOR_RECORDING = QColor("#FF3B30")
_COLOR_TRANSCRIBING = QColor("#FF9500")
_COLOR_PAUSED = QColor("#8E8E93")
_COLOR_ERROR = QColor("#FF3B30")
_COLOR_TRANSPARENT = QColor(0, 0, 0, 0)

# Tamanhos
_ICON_SIZE = 32          # renderizar em 2× para HiDPI
_ANIMATION_INTERVAL_MS = 100  # 10 fps — leve o suficiente para o system tray

# Tooltips por estado
_TOOLTIPS: dict[str, str] = {
    "idle_cold": "Pronto",
    "idle_warm": "Pronto",
    "loading": "Carregando IA...",
    "recording": "Ouvindo...",
    "transcribing": "Processando...",
    "paused": "Pausado",
    "error": "Erro",
}

# Estados que exigem animação
_ANIMATED_STATES = frozenset({"loading", "recording"})

# Stylesheet do menu Apple-style
_MENU_STYLESHEET = """
QMenu {
    background: #FFFFFF;
    border: 1px solid rgba(0,0,0,0.12);
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
    color: #1D1D1F;
    font-size: 13px;
}
QMenu::item:selected {
    background: #F5F5F7;
}
QMenu::item:disabled {
    color: #8E8E93;
}
QMenu::separator {
    height: 1px;
    background: rgba(0,0,0,0.08);
    margin: 4px 0;
}
"""


# ---------------------------------------------------------------------------
# Geração programática de ícones
# ---------------------------------------------------------------------------

def _make_icon(state: str, angle: int = 0) -> QIcon:
    """Gera um QIcon para o estado dado.

    Renderiza em 32×32 para HiDPI e escala para 16×16 em monitores normais.
    O parâmetro *angle* é usado apenas nos estados animados (loading, recording).
    """
    size = _ICON_SIZE
    pixmap = QPixmap(size, size)
    pixmap.fill(_COLOR_TRANSPARENT)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Área de desenho com margem de 1px para evitar clipping do antialiasing
    margin = 1.5
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    center_x = size / 2.0
    center_y = size / 2.0
    radius = (size / 2.0) - margin

    if state == "idle_cold":
        # Círculo vazio (outline) cinza
        pen = QPen(_COLOR_IDLE_COLD)
        pen.setWidthF(2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

    elif state == "idle_warm":
        # Círculo preenchido verde
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(_COLOR_IDLE_WARM))
        painter.drawEllipse(rect)

    elif state == "loading":
        # Arco (setor) animado azul girando
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(_COLOR_LOADING.darker(130)))
        painter.drawEllipse(rect)

        # Setor de 120° que rotaciona
        pen = QPen(_COLOR_LOADING)
        pen.setWidthF(3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Qt mede em 1/16 de grau; sentido anti-horário do eixo X positivo
        start_angle = (90 - angle) * 16   # parte do topo e avança com o ângulo
        span_angle = 120 * 16             # arco de 120°
        painter.drawArc(rect, start_angle, span_angle)

    elif state == "recording":
        # Círculo vermelho pulsante: oscila entre 70% e 100% da área
        pulse_ratio = 0.70 + 0.30 * _pulse_factor(angle)
        r = radius * pulse_ratio
        pulse_rect = QRectF(
            center_x - r, center_y - r, 2 * r, 2 * r
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(_COLOR_RECORDING))
        painter.drawEllipse(pulse_rect)

    elif state == "transcribing":
        # Círculo preenchido laranja
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(_COLOR_TRANSCRIBING))
        painter.drawEllipse(rect)

    elif state == "paused":
        # Círculo cinza com dois retângulos verticais (ícone de pausa)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(_COLOR_PAUSED))
        painter.drawEllipse(rect)

        # Dois retângulos brancos para o símbolo de pausa
        bar_color = QColor("#FFFFFF")
        painter.setBrush(QBrush(bar_color))
        bar_h = size * 0.40
        bar_w = size * 0.12
        bar_y = center_y - bar_h / 2
        gap = size * 0.08
        left_x = center_x - gap / 2 - bar_w
        right_x = center_x + gap / 2

        painter.drawRoundedRect(
            QRectF(left_x, bar_y, bar_w, bar_h), 1.0, 1.0
        )
        painter.drawRoundedRect(
            QRectF(right_x, bar_y, bar_w, bar_h), 1.0, 1.0
        )

    elif state == "error":
        # Círculo vermelho com ✕ branco
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(_COLOR_ERROR))
        painter.drawEllipse(rect)

        pen = QPen(QColor("#FFFFFF"))
        pen.setWidthF(2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        cross_margin = size * 0.28
        painter.drawLine(
            QRectF(cross_margin, cross_margin,
                   size - 2 * cross_margin, size - 2 * cross_margin).topLeft(),
            QRectF(cross_margin, cross_margin,
                   size - 2 * cross_margin, size - 2 * cross_margin).bottomRight(),
        )
        painter.drawLine(
            QRectF(cross_margin, cross_margin,
                   size - 2 * cross_margin, size - 2 * cross_margin).topRight(),
            QRectF(cross_margin, cross_margin,
                   size - 2 * cross_margin, size - 2 * cross_margin).bottomLeft(),
        )

    painter.end()
    return QIcon(pixmap)


def _pulse_factor(angle: int) -> float:
    """Fator de escala pulsante [0..1] derivado do ângulo acumulado.

    O ângulo incrementa 36°/tick (100 ms × 36 = 3.6 s por ciclo completo),
    produzindo uma pulsação suave sem depender de math.sin externo.
    """
    import math
    return (math.sin(math.radians(angle)) + 1.0) / 2.0


# ---------------------------------------------------------------------------
# SystemTray
# ---------------------------------------------------------------------------

class SystemTray(QSystemTrayIcon):
    """Ícone de bandeja do sistema com menu Apple-style e animação de estado.

    Args:
        engine: Instância de Engine que emite sinais de estado.
        main_window: Janela principal — exibida ao clicar no ícone.
        config: Configuração completa do app (reservado para extensões futuras).
    """

    def __init__(
        self,
        engine: Engine,
        main_window: QMainWindow,
        config: FullConfig,  # noqa: ARG002 — mantido na assinatura para extensibilidade
    ) -> None:
        super().__init__()

        self._engine = engine
        self._main_window = main_window
        self._current_state = "idle_cold"
        self._angle = 0

        # Ícone inicial
        self.setIcon(_make_icon("idle_cold"))
        self.setToolTip(_TOOLTIPS["idle_cold"])

        # Timer de animação (não iniciado até necessário)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(_ANIMATION_INTERVAL_MS)
        self._anim_timer.timeout.connect(self._tick_animation)

        # Menu
        self._build_menu()

        # Conexões com engine
        engine.state_changed.connect(self.update_state)
        engine.error_occurred.connect(
            lambda msg: self.show_notification("Erro", msg)
        )

        # Clique simples no ícone da bandeja → exibe janela principal
        self.activated.connect(self._on_activated)

        self.setVisible(True)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menu = QMenu()
        menu.setStyleSheet(_MENU_STYLESHEET)

        # Mostrar janela
        action_show = QAction("Mostrar janela", menu)
        action_show.triggered.connect(self._show_window)
        menu.addAction(action_show)

        menu.addSeparator()

        # Toggle ativo/pausado
        self._action_pause = QAction("Pausado", menu)
        self._action_pause.setCheckable(True)
        self._action_pause.setChecked(False)
        self._action_pause.triggered.connect(self._toggle_pause)
        menu.addAction(self._action_pause)

        menu.addSeparator()

        # Carregar modelo
        action_load = QAction("Carregar modelo", menu)
        action_load.triggered.connect(self._engine.load_model)
        menu.addAction(action_load)

        # Descarregar modelo
        action_unload = QAction("Descarregar modelo", menu)
        action_unload.triggered.connect(self._engine.unload_model)
        menu.addAction(action_unload)

        menu.addSeparator()

        # Sair
        action_quit = QAction("Sair", menu)
        action_quit.triggered.connect(self._quit)
        menu.addAction(action_quit)

        self.setContextMenu(menu)

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def update_state(self, state: str) -> None:
        """Atualiza ícone e tooltip conforme novo estado do engine.

        Inicia ou para o timer de animação conforme necessário.
        """
        self._current_state = state

        tooltip = _TOOLTIPS.get(state, state)
        self.setToolTip(tooltip)

        if state in _ANIMATED_STATES:
            if not self._anim_timer.isActive():
                self._angle = 0
                self._anim_timer.start()
            # O ícone será atualizado pelo próximo tick do timer
        else:
            if self._anim_timer.isActive():
                self._anim_timer.stop()
            self.setIcon(_make_icon(state))

        # Sincroniza o checkable do menu
        self._action_pause.setChecked(state == "paused")

    def show_notification(self, title: str, message: str) -> None:
        """Exibe uma notificação balloon no system tray."""
        self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    # ------------------------------------------------------------------
    # Slots privados
    # ------------------------------------------------------------------

    def _tick_animation(self) -> None:
        """Avança o ângulo de animação e regenera o ícone."""
        self._angle = (self._angle + 36) % 360
        self.setIcon(_make_icon(self._current_state, self._angle))

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Clique simples no ícone exibe a janela principal."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self) -> None:
        self._main_window.show()
        self._main_window.raise_()
        self._main_window.activateWindow()

    def _toggle_pause(self, checked: bool) -> None:
        if checked:
            self._engine.pause()
        else:
            self._engine.resume()

    def _quit(self) -> None:
        from PySide6.QtWidgets import QApplication
        self._engine.stop()
        QApplication.quit()
