from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from whisper_microfone.config.schemas import FullConfig
from whisper_microfone.ui.theme import AppTheme
from whisper_microfone.version import __version__


class WhisperApp(QApplication):
    """QApplication configurada para o Whisper Microfone.

    Responsabilidades:
    - Aplicar o design system (AppTheme) antes de qualquer widget ser criado.
    - Configurar metadados da aplicação usados por QSettings e pela tray.
    - Centralizar a instância única de QApplication.
    """

    def __init__(self, config: FullConfig, argv: list[str]) -> None:
        super().__init__(argv)

        # Metadados — usados por QSettings e pelo sistema operacional
        self.setApplicationName("Whisper Microfone")
        self.setApplicationVersion(__version__)
        self.setOrganizationName("Gustavo1341")
        self.setOrganizationDomain("github.com/Gustavo1341")

        # Design system Apple-style (Fusion + QSS + fonte base)
        AppTheme.apply(self)

        # Fechar a aplicação apenas quando a janela principal for fechada,
        # não quando qualquer widget auxiliar (diálogo, tray menu) for fechado.
        self.setQuitOnLastWindowClosed(False)

        self._config = config

    @property
    def config(self) -> FullConfig:
        return self._config


# ---------------------------------------------------------------------------
# Verificação mínima — abre a app sem janela e encerra imediatamente
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    config = FullConfig()
    app = WhisperApp(config, sys.argv)

    print(f"applicationName    : {app.applicationName()}")
    print(f"applicationVersion : {app.applicationVersion()}")
    print(f"organizationName   : {app.organizationName()}")
    print(f"style              : {app.style().objectName()}")
    print("WhisperApp OK — encerrando sem abrir janela")
    sys.exit(0)
