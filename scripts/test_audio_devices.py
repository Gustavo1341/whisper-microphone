"""Lista dispositivos de audio disponiveis para entrada.

Uso:
    python scripts/test_audio_devices.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite importar do pacote mesmo rodando fora do venv instalado
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / "src"))


def main() -> None:
    try:
        import sounddevice as sd
    except ImportError:
        print(
            "[ERRO] sounddevice nao encontrado. "
            "Instale com: pip install sounddevice",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        devices = sd.query_devices()
        default_input_idx = sd.default.device[0]  # type: ignore[index]
    except Exception as exc:
        print(f"[ERRO] Nao foi possivel consultar dispositivos: {exc}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("Dispositivos de entrada de audio disponiveis")
    print("=" * 60)

    input_devices: list[tuple[int, object]] = []
    for idx, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:  # type: ignore[index]
            input_devices.append((idx, dev))

    if not input_devices:
        print("Nenhum dispositivo de entrada encontrado.")
        return

    for idx, dev in input_devices:
        marker = " [PADRAO]" if idx == default_input_idx else ""
        name: str = dev["name"]  # type: ignore[index]
        channels: int = dev["max_input_channels"]  # type: ignore[index]
        sample_rate: float = dev["default_samplerate"]  # type: ignore[index]
        star = "★" if idx == default_input_idx else " "
        print(f"  {star} [{idx:>2}] {name}{marker}")
        print(f"        Canais: {channels}  |  Sample rate padrao: {int(sample_rate)} Hz")

    print("=" * 60)

    # Exibe o dispositivo padrao de forma destacada
    if default_input_idx is not None and default_input_idx >= 0:
        default_dev = devices[default_input_idx]
        print(f"\nDispositivo padrao atual: [{default_input_idx}] {default_dev['name']}")

    print("\nPara usar um dispositivo especifico, adicione ao config.toml:")
    print()
    print("  [audio]")
    print("  device_index = <indice>   # substitua pelo numero acima")
    print()
    print("  Exemplo:")
    if input_devices:
        first_idx, first_dev = input_devices[0]
        print(f"  device_index = {first_idx}  # {first_dev['name']}")  # type: ignore[index]


if __name__ == "__main__":
    main()
