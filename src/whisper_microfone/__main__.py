from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from whisper_microfone.config.loader import load_config
from whisper_microfone.engine import Engine
from whisper_microfone.logging_setup import setup_logging
from whisper_microfone.ui.app import WhisperApp
from whisper_microfone.ui.main_window import MainWindow
from whisper_microfone.ui.pages.about import AboutPage
from whisper_microfone.ui.pages.config_page import ConfigPage
from whisper_microfone.ui.pages.history import HistoryPage
from whisper_microfone.ui.pages.home import HomePage
from whisper_microfone.ui.pages.monitor import MonitorPage
from whisper_microfone.ui.tray import SystemTray


def main() -> None:
    config = load_config()
    setup_logging(config)

    app = WhisperApp(config, sys.argv)

    engine = Engine(config)

    window = MainWindow(engine, config)

    # Injecta páginas reais nos placeholders
    window.replace_page(0, HomePage(engine, config))
    window.replace_page(1, MonitorPage(engine, config))
    window.replace_page(2, ConfigPage(engine, config))
    window.replace_page(3, HistoryPage(engine, config))
    window.replace_page(4, AboutPage(engine, config))

    # Garante que a página inicial (Início) está selecionada após injeção
    window.navigate_to(0)

    tray = SystemTray(engine, window, config)
    tray.show()

    # Inicia janela conforme configuração
    if config.app.start_minimized:
        window.hide()
    else:
        window.show()

    engine.start()

    exit_code = app.exec()

    engine.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
