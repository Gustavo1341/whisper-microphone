from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from whisper_microfone.config.schemas import FullConfig
from whisper_microfone.engine import Engine
from whisper_microfone.ui.widgets.metric_bar import MetricBar
from whisper_microfone.ui.widgets.status_card import StatusCard
from whisper_microfone.ui.widgets.transcription_card import TranscriptionCard

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
_COLOR_BG = "#F5F5F7"
_COLOR_TEXT_PRIMARY = "#1D1D1F"
_COLOR_TEXT_SECONDARY = "#6E6E73"
_COLOR_ACCENT = "#0071E3"
_COLOR_DESTRUCTIVE = "#FF3B30"

_COLOR_RAM = "#0071E3"
_COLOR_VRAM = "#FF9500"
_COLOR_GPU = "#34C759"
_COLOR_CPU = "#6E6E73"

_FONT_SECTION = 13
_PAGE_PADDING = 32
_SECTION_SPACING = 20
_CARD_SPACING = 12

# RAM display máximo assumido (16 GB) quando vram_total_mb não está disponível
_RAM_MAX_MB = 16384.0


def _fmt_mb(value_mb: float) -> str:
    """Formata MB para exibição: abaixo de 1024 usa MB, acima usa GB."""
    if value_mb >= 1024:
        return f"{value_mb / 1024:.1f} GB"
    return f"{value_mb:.0f} MB"


class HomePage(QWidget):
    """Página principal do Whisper Microfone.

    Exibe estado do engine, consumo de recursos em tempo real e
    a última transcrição recebida.
    """

    def __init__(
        self,
        engine: Engine,
        config: FullConfig,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._engine = engine
        self._config = config
        self._current_state: str = "idle_cold"

        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setObjectName("HomePage")
        self.setStyleSheet(f"QWidget#HomePage {{ background-color: {_COLOR_BG}; }}")

        # Scroll area wrapping o conteúdo
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)

        content = QVBoxLayout(container)
        content.setContentsMargins(
            _PAGE_PADDING, _PAGE_PADDING, _PAGE_PADDING, _PAGE_PADDING
        )
        content.setSpacing(_SECTION_SPACING)

        # --- Status card ---
        self._status_card = StatusCard()
        content.addWidget(self._status_card)

        # --- Botões de controle do modelo ---
        self._btn_load = QPushButton("Carregar modelo")
        self._btn_load.setStyleSheet(self._primary_btn_style())
        self._btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_load.clicked.connect(self._engine.load_model)

        self._btn_unload = QPushButton("Descarregar modelo")
        self._btn_unload.setStyleSheet(self._secondary_btn_style())
        self._btn_unload.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_unload.clicked.connect(self._engine.unload_model)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.addWidget(self._btn_load)
        btn_row.addWidget(self._btn_unload)
        btn_row.addStretch()
        content.addLayout(btn_row)

        # --- Seção de métricas ---
        metrics_label = QLabel("Consumo em tempo real")
        metrics_label.setStyleSheet(
            f"color: {_COLOR_TEXT_PRIMARY}; font-size: {_FONT_SECTION}px;"
            " font-weight: 600;"
            " font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
        )
        content.addWidget(metrics_label)

        metrics_container = QWidget()
        metrics_container.setStyleSheet(
            "background: #FFFFFF; border-radius: 12px;"
            " border: 1px solid rgba(0,0,0,0.08);"
        )
        metrics_layout = QVBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(20, 16, 20, 16)
        metrics_layout.setSpacing(12)

        self._bar_ram = MetricBar("RAM", color=_COLOR_RAM)
        self._bar_vram = MetricBar("VRAM", color=_COLOR_VRAM)
        self._bar_gpu = MetricBar("GPU", color=_COLOR_GPU)
        self._bar_cpu = MetricBar("CPU", color=_COLOR_CPU)

        for bar in (self._bar_ram, self._bar_vram, self._bar_gpu, self._bar_cpu):
            metrics_layout.addWidget(bar)

        content.addWidget(metrics_container)

        # --- Transcrição ---
        self._transcription_card = TranscriptionCard()
        content.addWidget(self._transcription_card)

        content.addStretch()

        # Coloca o scroll no layout raiz da página
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        # Estado inicial dos botões
        self._update_button_visibility("idle_cold")

    # ------------------------------------------------------------------
    # Estilos de botão
    # ------------------------------------------------------------------

    @staticmethod
    def _primary_btn_style() -> str:
        return (
            f"QPushButton {{"
            f"  background-color: {_COLOR_ACCENT};"
            f"  color: #FFFFFF;"
            f"  border: none;"
            f"  border-radius: 8px;"
            f"  padding: 8px 16px;"
            f"  font-size: 13px;"
            f"  font-weight: 500;"
            f"  font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
            f"}}"
            f"QPushButton:hover {{ background-color: #0077ED; }}"
            f"QPushButton:pressed {{ background-color: #0068CC; }}"
            f"QPushButton:disabled {{ background-color: #C7C7CC; }}"
        )

    @staticmethod
    def _secondary_btn_style() -> str:
        return (
            f"QPushButton {{"
            f"  background-color: transparent;"
            f"  color: {_COLOR_DESTRUCTIVE};"
            f"  border: 1px solid {_COLOR_DESTRUCTIVE};"
            f"  border-radius: 8px;"
            f"  padding: 8px 16px;"
            f"  font-size: 13px;"
            f"  font-weight: 500;"
            f"  font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', sans-serif;"
            f"}}"
            f"QPushButton:hover {{ background-color: rgba(255,59,48,0.06); }}"
            f"QPushButton:pressed {{ background-color: rgba(255,59,48,0.12); }}"
            f"QPushButton:disabled {{ color: #C7C7CC; border-color: #C7C7CC; }}"
        )

    # ------------------------------------------------------------------
    # Conexão de sinais
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._engine.state_changed.connect(self._on_state_changed)
        self._engine.transcribed.connect(self._transcription_card.set_transcription)
        self._engine.metrics_updated.connect(self._on_metrics)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_state_changed(self, state: str) -> None:
        self._current_state = state
        self._status_card.set_state(state)
        self._update_button_visibility(state)

    def _update_button_visibility(self, state: str) -> None:
        """Exibe botões conforme o estado atual do engine.

        - "Carregar modelo" visível quando modelo não está carregado/carregando.
        - "Descarregar modelo" visível quando modelo está carregado (idle_warm).
        - Ambos ocultos durante gravação, transcrição ou pausa para evitar
          interrupção acidental de operação em andamento.
        """
        active_states = {"recording", "transcribing"}
        model_loaded = state == "idle_warm"
        model_unloaded = state in {"idle_cold", "error"}
        in_operation = state in active_states

        self._btn_load.setVisible(model_unloaded and not in_operation)
        self._btn_unload.setVisible(model_loaded and not in_operation)

        # Durante carregamento desabilita ambos
        if state == "loading":
            self._btn_load.setVisible(False)
            self._btn_unload.setVisible(False)

    def _on_metrics(self, metrics: object) -> None:
        """Atualiza as quatro MetricBars com os dados mais recentes.

        O parâmetro é o dataclass Metrics emitido por Engine.metrics_updated.
        Usado como `object` na assinatura para compatibilidade com o Signal(object).
        """
        ram_mb: float = getattr(metrics, "ram_mb", 0.0)
        vram_mb: float = getattr(metrics, "vram_mb", 0.0)
        vram_total_mb: float = getattr(metrics, "vram_total_mb", 0.0)
        gpu_percent: float = getattr(metrics, "gpu_percent", 0.0)
        cpu_percent: float = getattr(metrics, "cpu_percent", 0.0)

        # RAM — máximo display fixo em 16 GB
        self._bar_ram.set_value(ram_mb, _RAM_MAX_MB, _fmt_mb(ram_mb))

        # VRAM — usa total real quando disponível
        vram_max = max(vram_total_mb, 1.0)
        vram_label = (
            f"{_fmt_mb(vram_mb)} / {_fmt_mb(vram_total_mb)}"
            if vram_total_mb > 0
            else _fmt_mb(vram_mb)
        )
        self._bar_vram.set_value(vram_mb, vram_max, vram_label)

        # GPU %
        self._bar_gpu.set_value(gpu_percent, 100.0, f"{gpu_percent:.0f}%")

        # CPU %
        self._bar_cpu.set_value(cpu_percent, 100.0, f"{cpu_percent:.0f}%")
