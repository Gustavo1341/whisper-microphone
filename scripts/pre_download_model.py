"""Baixa um modelo faster-whisper antes do primeiro uso.

Uso:
    python scripts/pre_download_model.py [--model small] [--dir <path>]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Permite importar do pacote mesmo rodando fora do venv instalado
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / "src"))


def _models_dir_default() -> Path:
    from whisper_microfone.config.paths import models_dir

    return models_dir()


def _model_already_cached(model_name: str, cache_dir: Path) -> bool:
    """Verifica se o modelo já foi baixado verificando a existência do diretório."""
    # faster-whisper salva em <cache_dir>/models--Systran--faster-whisper-<name>/
    # ou simplesmente <cache_dir>/<name>/ dependendo da versão.
    # Checamos ambas as convenções para ser robusto.
    candidates = [
        cache_dir / model_name,
        cache_dir / f"models--Systran--faster-whisper-{model_name}",
    ]
    return any(c.exists() and any(c.iterdir()) for c in candidates if c.exists())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa um modelo faster-whisper para uso offline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python scripts/pre_download_model.py\n"
            "  python scripts/pre_download_model.py --model medium\n"
            "  python scripts/pre_download_model.py --model large-v3 --dir D:\\models\n"
        ),
    )
    parser.add_argument(
        "--model",
        default="small",
        metavar="NAME",
        help=(
            "Nome do modelo a baixar. "
            "Opcoes: tiny, base, small, medium, large-v2, large-v3 "
            "(default: small)"
        ),
    )
    parser.add_argument(
        "--dir",
        default=None,
        metavar="PATH",
        help="Diretorio de destino para o modelo (default: diretorio padrao do app)",
    )
    args = parser.parse_args()

    model_name: str = args.model
    cache_dir: Path = Path(args.dir).resolve() if args.dir else _models_dir_default()
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"Modelo   : {model_name}")
    print(f"Destino  : {cache_dir}")

    if _model_already_cached(model_name, cache_dir):
        print(f"\nModelo '{model_name}' ja existe em '{cache_dir}'. Nenhum download necessario.")
        return

    print(f"\nBaixando modelo '{model_name}'...")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print(
            "[ERRO] faster-whisper nao encontrado. "
            "Instale com: pip install faster-whisper",
            file=sys.stderr,
        )
        sys.exit(1)

    t0 = time.perf_counter()
    try:
        # Instanciar o modelo força o download completo via huggingface_hub
        WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            download_root=str(cache_dir),
        )
    except Exception as exc:
        print(f"\n[ERRO] Falha ao baixar o modelo: {exc}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.perf_counter() - t0
    print(f"\nModelo baixado em {elapsed:.1f}s")
    print(f"Local: {cache_dir}")


if __name__ == "__main__":
    main()
