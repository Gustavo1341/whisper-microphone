from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QComboBox,
    QCheckBox, QSpinBox, QSizePolicy,
)

from whisper_microfone.engine import Engine
from whisper_microfone.config.schemas import (
    FullConfig, ModelConfig, LifecycleConfig,
    AudioConfig, InjectionConfig,
)

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG_PRIMARY     = "#FFFFFF"
BG_SECONDARY   = "#F5F5F7"
TEXT_PRIMARY   = "#1D1D1F"
TEXT_SECONDARY = "#6E6E73"
ACCENT         = "#0071E3"
BORDER         = "rgba(0,0,0,0.08)"

_STRATEGY_LABELS = [
    "Digitar → Colar",
    "Só colar",
    "Só digitar",
]
_STRATEGY_VALUES = [
    "type_then_paste",
    "paste_only",
    "type_only",
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_card(title: str = "") -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("card")
    card.setStyleSheet("""
        QFrame#card {
            background: #FFFFFF;
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,0.08);
        }
    """)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(12)
    if title:
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            f"font-size: 11px; color: {TEXT_SECONDARY}; letter-spacing: 0.5px;"
        )
        layout.addWidget(lbl)
    return card, layout


def _field_row(label: str, widget: QWidget) -> QHBoxLayout:
    """Label à esquerda + widget à direita, alinhados."""
    row = QHBoxLayout()
    row.setSpacing(12)
    lbl = QLabel(label)
    lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_PRIMARY};")
    lbl.setMinimumWidth(240)
    row.addWidget(lbl)
    row.addWidget(widget)
    row.addStretch()
    return row


def _styled_combo(items: list[str]) -> QComboBox:
    cb = QComboBox()
    cb.addItems(items)
    cb.setMinimumWidth(160)
    cb.setStyleSheet(f"""
        QComboBox {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 13px;
            color: {TEXT_PRIMARY};
            background: {BG_PRIMARY};
        }}
        QComboBox::drop-down {{ border: none; }}
    """)
    return cb


def _styled_spin(min_val: int, max_val: int, step: int = 1) -> QSpinBox:
    sp = QSpinBox()
    sp.setRange(min_val, max_val)
    sp.setSingleStep(step)
    sp.setMinimumWidth(100)
    sp.setStyleSheet(f"""
        QSpinBox {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 13px;
            color: {TEXT_PRIMARY};
            background: {BG_PRIMARY};
        }}
    """)
    return sp


def _styled_check(label: str) -> QCheckBox:
    cb = QCheckBox(label)
    cb.setStyleSheet(f"font-size: 13px; color: {TEXT_PRIMARY};")
    return cb


# ---------------------------------------------------------------------------
# ConfigPage
# ---------------------------------------------------------------------------

class ConfigPage(QWidget):
    def __init__(self, engine: Engine, config: FullConfig) -> None:
        super().__init__()
        self._engine = engine
        self._config = config

        self._build_ui()
        self._populate(config)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {BG_SECONDARY};")

        container = QWidget()
        container.setStyleSheet(f"background: {BG_SECONDARY};")
        self._content = QVBoxLayout(container)
        self._content.setContentsMargins(32, 32, 32, 32)
        self._content.setSpacing(16)
        self._content.setAlignment(Qt.AlignTop)

        self._build_model_card()
        self._build_lifecycle_card()
        self._build_audio_card()
        self._build_injection_card()
        self._build_apply_row()

        self._content.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _build_model_card(self) -> None:
        card, layout = _make_card("Modelo")

        self._cb_model = _styled_combo([
            "tiny", "base", "small ★ recomendado", "medium", "large-v3-turbo",
        ])
        self._cb_compute = _styled_combo(["int8", "int8_float16", "float16"])
        self._cb_device = _styled_combo(["auto", "cuda", "cpu"])
        self._cb_language = _styled_combo(["auto", "pt", "en", "es", "fr", "de"])

        layout.addLayout(_field_row("Modelo", self._cb_model))
        layout.addLayout(_field_row("Tipo de computação", self._cb_compute))
        layout.addLayout(_field_row("Dispositivo", self._cb_device))
        layout.addLayout(_field_row("Idioma de transcrição", self._cb_language))

        self._content.addWidget(card)

    def _build_lifecycle_card(self) -> None:
        card, layout = _make_card("Ciclo de vida")

        self._chk_preload = _styled_check("Carregar modelo ao iniciar")
        self._spin_unload = _styled_spin(0, 3600, 30)
        self._spin_unload.setSuffix(" s")
        self._spin_unload.setSpecialValueText("Nunca")
        self._chk_load_during = _styled_check(
            "Carregar modelo enquanto grava (recomendado)"
        )

        layout.addWidget(self._chk_preload)
        layout.addLayout(
            _field_row("Descarregar após inatividade", self._spin_unload)
        )
        layout.addWidget(self._chk_load_during)

        self._content.addWidget(card)

    def _build_audio_card(self) -> None:
        card, layout = _make_card("Áudio")

        self._spin_min_dur = _styled_spin(100, 5000, 50)
        self._spin_min_dur.setSuffix(" ms")
        self._spin_max_dur = _styled_spin(5, 300, 5)
        self._spin_max_dur.setSuffix(" s")

        layout.addLayout(_field_row("Duração mínima", self._spin_min_dur))
        layout.addLayout(_field_row("Duração máxima", self._spin_max_dur))

        self._content.addWidget(card)

    def _build_injection_card(self) -> None:
        card, layout = _make_card("Injeção de texto")

        self._cb_strategy = _styled_combo(_STRATEGY_LABELS)
        self._chk_capitalize = _styled_check("Capitalizar primeira letra")
        self._chk_trailing = _styled_check("Adicionar espaço ao final")

        layout.addLayout(_field_row("Estratégia", self._cb_strategy))
        layout.addWidget(self._chk_capitalize)
        layout.addWidget(self._chk_trailing)

        self._content.addWidget(card)

    def _build_apply_row(self) -> None:
        row = QHBoxLayout()
        row.addStretch()

        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setStyleSheet(
            f"font-size: 13px; color: {ACCENT};"
        )
        row.addWidget(self._feedback_lbl)

        self._btn_apply = QPushButton("Aplicar")
        self._btn_apply.setFixedHeight(36)
        self._btn_apply.setMinimumWidth(100)
        self._btn_apply.setCursor(Qt.PointingHandCursor)
        self._btn_apply.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: #0077ED;
            }}
            QPushButton:pressed {{
                background: #006CD1;
            }}
        """)
        self._btn_apply.clicked.connect(self._on_apply)
        row.addWidget(self._btn_apply)

        self._content.addLayout(row)

    # ------------------------------------------------------------------
    # Populate
    # ------------------------------------------------------------------

    def _populate(self, config: FullConfig) -> None:
        # Modelo
        model_map = {
            "tiny": 0, "base": 1, "small": 2, "medium": 3, "large-v3-turbo": 4,
        }
        self._cb_model.setCurrentIndex(model_map.get(config.model.name, 2))

        compute_map = {"int8": 0, "int8_float16": 1, "float16": 2}
        self._cb_compute.setCurrentIndex(
            compute_map.get(config.model.compute_type, 1)
        )

        device_map = {"auto": 0, "cuda": 1, "cpu": 2}
        self._cb_device.setCurrentIndex(
            device_map.get(config.model.device, 0)
        )

        lang_map = {"auto": 0, "pt": 1, "en": 2, "es": 3, "fr": 4, "de": 5}
        self._cb_language.setCurrentIndex(
            lang_map.get(config.model.language, 0)
        )

        # Lifecycle
        self._chk_preload.setChecked(config.lifecycle.preload_on_startup)
        self._spin_unload.setValue(config.lifecycle.unload_after_idle_seconds)
        self._chk_load_during.setChecked(config.lifecycle.load_during_recording)

        # Áudio
        self._spin_min_dur.setValue(config.audio.min_duration_ms)
        self._spin_max_dur.setValue(config.audio.max_duration_seconds)

        # Injeção
        strategy_idx = (
            _STRATEGY_VALUES.index(config.injection.strategy)
            if config.injection.strategy in _STRATEGY_VALUES
            else 0
        )
        self._cb_strategy.setCurrentIndex(strategy_idx)
        self._chk_capitalize.setChecked(config.injection.capitalize_first)
        self._chk_trailing.setChecked(config.injection.add_trailing_space)

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def _on_apply(self) -> None:
        model_names = ["tiny", "base", "small", "medium", "large-v3-turbo"]
        compute_values = ["int8", "int8_float16", "float16"]
        device_values = ["auto", "cuda", "cpu"]
        lang_values = ["auto", "pt", "en", "es", "fr", "de"]

        new_cfg = self._config.model_copy(deep=True)

        new_cfg.model.name = model_names[self._cb_model.currentIndex()]
        new_cfg.model.compute_type = compute_values[self._cb_compute.currentIndex()]  # type: ignore[assignment]
        new_cfg.model.device = device_values[self._cb_device.currentIndex()]  # type: ignore[assignment]
        new_cfg.model.language = lang_values[self._cb_language.currentIndex()]

        new_cfg.lifecycle.preload_on_startup = self._chk_preload.isChecked()
        new_cfg.lifecycle.unload_after_idle_seconds = self._spin_unload.value()
        new_cfg.lifecycle.load_during_recording = self._chk_load_during.isChecked()

        new_cfg.audio.min_duration_ms = self._spin_min_dur.value()
        new_cfg.audio.max_duration_seconds = self._spin_max_dur.value()

        new_cfg.injection.strategy = _STRATEGY_VALUES[self._cb_strategy.currentIndex()]  # type: ignore[assignment]
        new_cfg.injection.capitalize_first = self._chk_capitalize.isChecked()
        new_cfg.injection.add_trailing_space = self._chk_trailing.isChecked()

        self._config = new_cfg
        self._engine.update_config(new_cfg)

        self._show_feedback("Configuração aplicada")

    def _show_feedback(self, message: str) -> None:
        self._feedback_lbl.setText(message)
        QTimer.singleShot(2000, lambda: self._feedback_lbl.setText(""))
