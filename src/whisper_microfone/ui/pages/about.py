from __future__ import annotations

import platform
import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QSizePolicy,
)

from whisper_microfone.engine import Engine
from whisper_microfone.config.schemas import FullConfig

try:
    import psutil as _psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False

try:
    import pynvml as _nvml
    _nvml.nvmlInit()
    _handle = _nvml.nvmlDeviceGetHandleByIndex(0)
    _GPU_NAME: str = _nvml.nvmlDeviceGetName(_handle)
    _CUDA_OK = True
except Exception:
    _GPU_NAME = "Não detectada"
    _CUDA_OK = False

try:
    import torch as _torch
    _TORCH_CUDA = _torch.cuda.is_available()
except ImportError:
    _TORCH_CUDA = False

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG_PRIMARY     = "#FFFFFF"
BG_SECONDARY   = "#F5F5F7"
TEXT_PRIMARY   = "#1D1D1F"
TEXT_SECONDARY = "#6E6E73"
ACCENT         = "#0071E3"
BORDER         = "rgba(0,0,0,0.08)"

APP_VERSION    = "v0.1.0 Alpha"
APP_NAME       = "Whisper Microfone"
APP_SUBTITLE   = "Ditado por voz local com IA"
REPO_URL       = "https://github.com/Gustavo1341/whisper-microphone"
REPO_LABEL     = "github.com/Gustavo1341/whisper-microphone"
LICENSE_LINE   = "MIT License · Gustavo Brandão · 2026"


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


def _grid_row(grid: QGridLayout, row: int, label: str, value: str) -> None:
    lbl = QLabel(label)
    lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")

    val = QLabel(value)
    val.setStyleSheet(f"font-size: 13px; color: {TEXT_PRIMARY}; font-weight: 500;")
    val.setTextInteractionFlags(Qt.TextSelectableByMouse)

    grid.addWidget(lbl, row, 0, Qt.AlignLeft)
    grid.addWidget(val, row, 1, Qt.AlignLeft)


# ---------------------------------------------------------------------------
# AboutPage
# ---------------------------------------------------------------------------

class AboutPage(QWidget):
    def __init__(self, engine: Engine, config: FullConfig) -> None:
        super().__init__()
        self._engine = engine
        self._config = config

        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 48, 48, 48)
        outer.setSpacing(24)
        outer.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setStyleSheet(f"background: {BG_SECONDARY};")

        self._build_hero()
        self._build_system_card()
        self._build_model_card()
        self._build_footer()

    def _build_hero(self) -> None:
        hero = QVBoxLayout()
        hero.setSpacing(6)
        hero.setAlignment(Qt.AlignHCenter)

        icon_lbl = QLabel("🎙")
        icon_font = QFont()
        icon_font.setPointSize(36)
        icon_lbl.setFont(icon_font)
        icon_lbl.setAlignment(Qt.AlignHCenter)

        title_lbl = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        title_lbl.setAlignment(Qt.AlignHCenter)

        version_lbl = QLabel(APP_VERSION)
        version_lbl.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY};")
        version_lbl.setAlignment(Qt.AlignHCenter)

        subtitle_lbl = QLabel(APP_SUBTITLE)
        subtitle_lbl.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY};")
        subtitle_lbl.setAlignment(Qt.AlignHCenter)

        hero.addWidget(icon_lbl)
        hero.addWidget(title_lbl)
        hero.addWidget(version_lbl)
        hero.addWidget(subtitle_lbl)

        self.layout().addLayout(hero)

    def _build_system_card(self) -> None:
        card, layout = _make_card("Sistema")

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 140)
        grid.setColumnStretch(1, 1)

        cuda_text = "Disponível" if (_CUDA_OK or _TORCH_CUDA) else "Não disponível"

        ram_text = "—"
        if _PSUTIL_OK:
            try:
                ram_total = _psutil.virtual_memory().total / (1024 ** 3)
                ram_text = f"{ram_total:.1f} GB"
            except Exception:
                pass

        py_version = (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

        platform_text = platform.platform(aliased=True, terse=True)

        _grid_row(grid, 0, "GPU",       _GPU_NAME)
        _grid_row(grid, 1, "CUDA",      cuda_text)
        _grid_row(grid, 2, "Python",    py_version)
        _grid_row(grid, 3, "Plataforma", platform_text)
        _grid_row(grid, 4, "RAM total", ram_text)

        layout.addLayout(grid)

        # Centraliza o card com largura máxima
        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(card)
        wrapper.addStretch()
        card.setMinimumWidth(420)
        card.setMaximumWidth(600)

        self.layout().addLayout(wrapper)

    def _build_model_card(self) -> None:
        card, layout = _make_card("Modelo atual")

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 140)
        grid.setColumnStretch(1, 1)

        model_name = self._config.model.name or "(não definido)"
        compute    = self._config.model.compute_type or "(padrão)"
        device     = self._config.model.device

        self._model_name_val = QLabel(model_name)
        self._model_name_val.setStyleSheet(
            f"font-size: 13px; color: {TEXT_PRIMARY}; font-weight: 500;"
        )

        self._model_status_val = QLabel("descarregado")
        self._model_status_val.setStyleSheet(
            f"font-size: 13px; color: {TEXT_SECONDARY}; font-weight: 500;"
        )

        lbl_name = QLabel("Nome")
        lbl_name.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        grid.addWidget(lbl_name,               0, 0, Qt.AlignLeft)
        grid.addWidget(self._model_name_val,   0, 1, Qt.AlignLeft)

        _grid_row(grid, 1, "Compute type", compute)
        _grid_row(grid, 2, "Dispositivo",  device)

        lbl_status = QLabel("Status")
        lbl_status.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        grid.addWidget(lbl_status,               3, 0, Qt.AlignLeft)
        grid.addWidget(self._model_status_val,   3, 1, Qt.AlignLeft)

        layout.addLayout(grid)

        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(card)
        wrapper.addStretch()
        card.setMinimumWidth(420)
        card.setMaximumWidth(600)

        self.layout().addLayout(wrapper)

    def _build_footer(self) -> None:
        footer = QVBoxLayout()
        footer.setSpacing(4)
        footer.setAlignment(Qt.AlignHCenter)

        license_lbl = QLabel(LICENSE_LINE)
        license_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
        license_lbl.setAlignment(Qt.AlignHCenter)

        repo_lbl = QLabel(f'<a href="{REPO_URL}" style="color: {ACCENT}; text-decoration: none;">{REPO_LABEL}</a>')
        repo_lbl.setTextFormat(Qt.RichText)
        repo_lbl.setOpenExternalLinks(False)
        repo_lbl.setCursor(Qt.PointingHandCursor)
        repo_lbl.setAlignment(Qt.AlignHCenter)
        repo_lbl.linkActivated.connect(
            lambda _: QDesktopServices.openUrl(QUrl(REPO_URL))
        )

        footer.addWidget(license_lbl)
        footer.addWidget(repo_lbl)

        self.layout().addLayout(footer)

    # ------------------------------------------------------------------
    # Signals
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._engine.model_state_changed.connect(self._on_model_state)

    def _on_model_state(self, state: str) -> None:
        labels = {
            "loaded":   ("carregado",    "#34C759"),
            "loading":  ("carregando…",  "#FF9F0A"),
            "unloaded": ("descarregado", TEXT_SECONDARY),
        }
        text, color = labels.get(state, ("descarregado", TEXT_SECONDARY))
        self._model_status_val.setText(text)
        self._model_status_val.setStyleSheet(
            f"font-size: 13px; color: {color}; font-weight: 500;"
        )
