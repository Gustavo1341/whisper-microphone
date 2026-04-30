# Whisper Microfone

![Status](https://img.shields.io/badge/status-Alpha%200.1.0-orange) ![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Platform](https://img.shields.io/badge/platform-Windows-blue)

An open source replacement for Windows' built-in Win+H dictation. Hold a hotkey, speak, release — the transcribed text appears wherever your cursor is. Fully local transcription powered by Whisper, no cloud, no subscription.

---

## Features

- **Global push-to-talk** — configurable hotkey (default: `Ctrl+Alt+Space`) works in any window
- **Local transcription with faster-whisper** — audio never leaves your machine
- **CUDA acceleration** — ~400ms latency for 5 seconds of audio on an NVIDIA GPU
- **Lazy model loading** — idle memory footprint is ~80 MB RAM and 0 VRAM; the model loads in parallel while you speak
- **Integrated VAD** — Silero VAD strips silence before transcription, reducing hallucinations
- **Smart text injection** — attempts to type directly into the active window; falls back to clipboard paste if needed
- **VS Code-style interface** — dark theme, 5 tabs: Home, Monitor, Config, History, About
- **Multilingual** — UI in PT-BR and EN; transcription supports any language Whisper handles
- **Zero hardcoded values** — everything is configurable via TOML files with automatic hot-reload
- **Transcription history** — stored locally in SQLite, searchable from the interface
- **Usage profiles** — switch between `economic`, `balanced`, and `always_ready` without restarting
- **System tray** — runs in the background without occupying the taskbar

---

## Requirements

| Component | Minimum version |
|---|---|
| Windows | 10 / 11 (64-bit) |
| Python | 3.11 or higher |
| NVIDIA GPU | Recommended (any Pascal or newer GPU) |
| NVIDIA Drivers | Up to date with CUDA 12 support |
| VRAM | 2 GB+ recommended (for the `small` model) |

> A GPU is recommended but not required. On CPU, latency increases to a few seconds depending on the model.

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Gustavo1341/whisper-microphone.git
cd whisper-microphone

# 2. Create and activate the virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
run.bat
```

---

## First use

Before using the app for the first time, download the transcription model:

```bash
# Activate the venv first
.venv\Scripts\activate

# Download the default model (small — ~460 MB)
python scripts/pre_download_model.py
```

Once downloaded, start the app with `run.bat` and press `Ctrl+Alt+Space` in any text field to start dictating.

> On the very first transcription after startup, there is a 1–5 second pause while the model loads onto the GPU. Subsequent transcriptions respond in ~400ms.

---

## Configuration

Configuration files are stored in `%APPDATA%\whisper-microfone\config\` and are created automatically on first launch.

TOML files can be edited with any text editor. The app detects changes and applies them without restarting (**hot-reload**).

| File | Contents |
|---|---|
| `config.toml` | App, model, audio, VAD, transcription, injection, UI, history, logs |
| `models.toml` | Model catalog and profiles |
| `shortcuts.toml` | Keyboard shortcuts |
| `theme.toml` | Colors, fonts, and layout |
| `advanced.toml` | Advanced thread, buffer, and GPU settings |

See the full reference for every available option in [docs/CONFIG.en.md](docs/CONFIG.en.md).

---

## Default shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Alt+Space` | Push-to-talk (hold to record, release to transcribe) |
| `Ctrl+Alt+P` | Pause / resume the hotkey listener |
| `Ctrl+Alt+W` | Show / hide the main window |

All shortcuts are configurable in `shortcuts.toml`.

---

## Usage profiles

The active profile is set in `config.toml → [app] → profile` and can be changed from the interface without restarting the app.

| Profile | Model | Behavior | Best for |
|---|---|---|---|
| `economic` | tiny / base | Model unloads after 60s idle; fast reload | Occasional use, limited RAM |
| `balanced` | small | Model unloads after 3min idle; loads in parallel during speech | Daily use — the default balance |
| `always_ready` | small / medium | Model stays in VRAM; zero load latency | Heavy dictation, dedicated machine |

You can define custom profiles directly in `models.toml`.

---

## Troubleshooting

**CUDA not found / transcription running on CPU**

Make sure your NVIDIA drivers are up to date and that the correct PyTorch build with CUDA support is installed. The app shows the active device in the Monitor tab. To explicitly force CPU, set `device = "cpu"` in `config.toml → [model]`.

**Microphone not detected**

List available audio devices with:
```bash
python scripts/test_audio_devices.py
```
Copy the name or index of the desired microphone and configure it in `config.toml → [audio] → device_name` or `device_index`.

**App running as Administrator does not receive text**

When the target window runs with elevated privileges (e.g., Task Manager, some games), the app must also be started as Administrator in order to inject text. Right-click `run.bat` and select "Run as administrator".

**First transcription takes too long**

This is expected. The model is loaded onto the GPU during the first speech session (lazy load). The wait is typically 2–8 seconds depending on the model and disk speed. To eliminate this latency, set `preload_on_startup = true` in `config.toml → [lifecycle]` — the model will load at startup, consuming VRAM even when idle.

**Transcribed text is wrong or shows hallucinations**

Lower the VAD threshold (`vad.threshold`) to a value between 0.3 and 0.5 if your audio environment is noisy. Increase `transcription.no_speech_threshold` if the app transcribes silence. Consider switching to the `medium` or `large-v3-turbo` model for higher accuracy.

---

## License

MIT — see the [LICENSE](LICENSE) file for details.

Author: Gustavo Brandão
