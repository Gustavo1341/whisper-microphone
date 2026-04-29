from __future__ import annotations

import os
from pathlib import Path

_APP_NAME = "whisper-microfone"

# Permite override via variável de ambiente para testes e CI
_ENV_APPDATA_OVERRIDE = "WHISPER_MIC_APPDATA_DIR"
_ENV_PORTABLE = "WHISPER_MIC_PORTABLE"

# Resolvido uma vez por processo; None = ainda não inicializado
_base_dir: Path | None = None


def _resolve_base() -> Path:
    """Determina e cria o diretório base de dados do usuário.

    Ordem de precedência:
    1. WHISPER_MIC_APPDATA_DIR (env var — CI / testes)
    2. WHISPER_MIC_PORTABLE=1 → pasta do executável / raiz do projeto
    3. advanced.toml portable_mode=true → mesmo que (2), mas lido depois do boot
    4. %APPDATA%\\whisper-microfone  (padrão Windows)
    5. ~/.local/share/whisper-microfone  (Linux / Mac — uso futuro)
    """
    env_override = os.environ.get(_ENV_APPDATA_OVERRIDE)
    if env_override:
        return Path(env_override).resolve()

    if os.environ.get(_ENV_PORTABLE, "").lower() in ("1", "true", "yes"):
        return _portable_root()

    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / _APP_NAME

    # Fallback XDG / Unix
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / _APP_NAME

    return Path.home() / ".local" / "share" / _APP_NAME


def _portable_root() -> Path:
    """Raiz portátil: pasta do executável (PyInstaller) ou raiz do repositório."""
    try:
        import sys
        # sys.frozen = True quando empacotado pelo PyInstaller
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent / "data"
    except Exception:
        pass
    # Em desenvolvimento: dois níveis acima de src/whisper_microfone/
    return Path(__file__).parent.parent.parent.parent / "data"


def set_portable_mode(enabled: bool) -> None:
    """Ativa modo portátil em runtime (chamado pelo loader após ler advanced.toml)."""
    global _base_dir
    if enabled:
        os.environ[_ENV_PORTABLE] = "1"
    else:
        os.environ.pop(_ENV_PORTABLE, None)
    _base_dir = None  # força re-resolução na próxima chamada


def appdata_dir() -> Path:
    """Diretório raiz de dados do usuário. Criado automaticamente se não existir."""
    global _base_dir
    if _base_dir is None:
        _base_dir = _resolve_base()
    _base_dir.mkdir(parents=True, exist_ok=True)
    return _base_dir


def config_dir() -> Path:
    """Subpasta de configuração do usuário (onde os *.toml do usuário ficam)."""
    p = appdata_dir() / "config"
    p.mkdir(parents=True, exist_ok=True)
    return p


def models_dir() -> Path:
    """Subpasta onde os modelos Whisper são baixados e cacheados."""
    p = appdata_dir() / "models"
    p.mkdir(parents=True, exist_ok=True)
    return p


def logs_dir() -> Path:
    """Subpasta de arquivos de log rotativos."""
    p = appdata_dir() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def history_db_path() -> Path:
    """Caminho do arquivo SQLite de histórico de transcrições."""
    return appdata_dir() / "history.db"


def assets_dir() -> Path:
    """Pasta de assets empacotados (ícones, sons). Sempre aponta para o pacote."""
    candidate = Path(__file__).parent.parent.parent.parent / "assets"
    if candidate.exists():
        return candidate
    # Fallback PyInstaller: assets ao lado do executável
    try:
        import sys
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent / "assets"
    except Exception:
        pass
    return candidate


def defaults_dir() -> Path:
    """Pasta dos TOMLs default empacotados (read-only)."""
    return Path(__file__).parent / "defaults"
