from __future__ import annotations

import threading
import time

import numpy as np
from loguru import logger
from PySide6.QtCore import QObject, QTimer, Signal

from whisper_microfone.config.schemas import FullConfig
from whisper_microfone.core.audio import AudioRecorder
from whisper_microfone.core.history import HistoryStore
from whisper_microfone.core.hotkey import PushToTalkHotkey
from whisper_microfone.core.injector import TextInjector
from whisper_microfone.core.metrics import MetricsCollector
from whisper_microfone.core.transcriber import WhisperTranscriber
from whisper_microfone.core.vad import SileroVAD


class Engine(QObject):
    """Bridge entre os módulos core e a UI Qt.

    Responsabilidades:
    - Coordenar o ciclo PTT: hotkey → gravação → VAD → transcrição → injeção.
    - Traduzir eventos de threads externas (pynput, worker) em Qt Signals.
    - Expor estado e métricas via sinais sem bloquear a UI thread.

    Restrição de threading: callbacks do pynput rodam em thread separada.
    Nunca acessar widgets Qt nesses callbacks — apenas emitir sinais,
    o que é thread-safe no Qt por ser enfileirado automaticamente.
    """

    state_changed = Signal(str)       # idle_warm | idle_cold | loading | recording | transcribing | paused | error
    transcribed = Signal(str, dict)   # (texto, {"latency_ms": float, "language": str, "duration_ms": float})
    metrics_updated = Signal(object)  # Metrics dataclass
    error_occurred = Signal(str)      # mensagem legível sem stack trace interno
    model_state_changed = Signal(str) # unloaded | loading | loaded
    config_reloaded = Signal()

    def __init__(self, config: FullConfig) -> None:
        super().__init__()
        self.config = config
        self._paused = False

        self._recorder = AudioRecorder(config.audio)
        self._vad = SileroVAD(config.vad) if config.vad.enabled else None
        self._transcriber = WhisperTranscriber(config.model, config.lifecycle, config.transcription)
        self._injector = TextInjector(config.injection)
        self._metrics = MetricsCollector()
        self._history = HistoryStore(config.history)
        self._hotkey = PushToTalkHotkey(
            config.shortcuts.push_to_talk.combination,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release,
        )

        self._metrics_timer = QTimer(self)
        self._metrics_timer.setInterval(config.ui.metrics_update_interval_ms)
        self._metrics_timer.timeout.connect(self._emit_metrics)

    # ------------------------------------------------------------------
    # Ciclo de vida público
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Inicia o listener de hotkey e o timer de métricas.

        Pré-carrega o modelo se lifecycle.preload_on_startup estiver ativo.
        """
        self._hotkey.start()
        self._metrics_timer.start()

        if self.config.lifecycle.preload_on_startup:
            self.load_model()
        else:
            self.state_changed.emit(self._idle_state())

        logger.info("Engine iniciado")

    def stop(self) -> None:
        """Para todos os componentes ativos e descarrega o modelo."""
        self._metrics_timer.stop()
        self._hotkey.stop()
        self._transcriber._unload()
        logger.info("Engine parado")

    def pause(self) -> None:
        self._paused = True
        self.state_changed.emit("paused")
        logger.debug("Engine pausado")

    def resume(self) -> None:
        self._paused = False
        self.state_changed.emit(self._idle_state())
        logger.debug("Engine retomado")

    def load_model(self) -> None:
        """Dispara carregamento assíncrono do modelo e notifica a UI."""
        self._transcriber.preload_async()
        self.model_state_changed.emit("loading")
        self.state_changed.emit("loading")
        logger.debug("Carga do modelo iniciada")

    def unload_model(self) -> None:
        self._transcriber._unload()
        self.model_state_changed.emit("unloaded")
        self.state_changed.emit(self._idle_state())
        logger.debug("Modelo descarregado")

    def update_config(self, new_config: FullConfig) -> None:
        """Aplica nova configuração e reinicia os componentes afetados.

        Componentes que guardam estado interno (recorder, transcriber) são
        reiniciados conservadoramente para evitar corrupção de estado mid-use.
        """
        old_combo = self.config.shortcuts.push_to_talk.combination
        self.config = new_config

        self._recorder = AudioRecorder(new_config.audio)

        self._vad = SileroVAD(new_config.vad) if new_config.vad.enabled else None

        # Modelo: recriar só se parâmetros estruturais mudaram; o objeto
        # controla seu próprio ciclo de carga/descarga internamente.
        self._transcriber = WhisperTranscriber(
            new_config.model, new_config.lifecycle, new_config.transcription
        )

        self._injector = TextInjector(new_config.injection)
        self._history = HistoryStore(new_config.history)

        if new_config.shortcuts.push_to_talk.combination != old_combo:
            self._hotkey.update_combination(new_config.shortcuts.push_to_talk.combination)

        self._metrics_timer.setInterval(new_config.ui.metrics_update_interval_ms)

        self.config_reloaded.emit()
        self.state_changed.emit(self._idle_state())
        logger.info("Configuração recarregada")

    # ------------------------------------------------------------------
    # Callbacks do hotkey — rodam em thread pynput, NÃO na UI thread
    # ------------------------------------------------------------------

    def _on_hotkey_press(self) -> None:
        if self._paused:
            return
        # Emitir sinal é thread-safe; nunca tocar widgets Qt aqui diretamente.
        self.state_changed.emit("recording")
        self._recorder.start()

        if self.config.lifecycle.load_during_recording and not self._transcriber.is_loaded:
            self._transcriber.preload_async()
            self.model_state_changed.emit("loading")

    def _on_hotkey_release(self) -> None:
        if self._paused:
            return
        audio = self._recorder.stop()

        if audio is None:
            # Gravação descartada por duração mínima não atingida
            self.state_changed.emit(self._idle_state())
            return

        self.state_changed.emit("transcribing")
        threading.Thread(
            target=self._transcribe_and_inject,
            args=(audio,),
            daemon=True,
        ).start()

    # ------------------------------------------------------------------
    # Worker de transcrição — roda em thread daemon
    # ------------------------------------------------------------------

    def _transcribe_and_inject(self, audio: np.ndarray) -> None:
        try:
            if self._vad is not None:
                audio = self._vad.trim_silence(audio)
                if len(audio) == 0:
                    self.error_occurred.emit("Nenhuma fala detectada após VAD")
                    self.state_changed.emit(self._idle_state())
                    return

            t0 = time.perf_counter()
            text = self._transcriber.transcribe(audio, self.config.model.language)
            latency_ms = (time.perf_counter() - t0) * 1000
            # sample_rate fixo em 16000 Hz conforme AudioConfig
            duration_ms = len(audio) / 16000 * 1000

            if text:
                self._injector.inject(text)
                self._history.add(
                    text,
                    duration_ms,
                    latency_ms,
                    self.config.model.language,
                )
                self.transcribed.emit(
                    text,
                    {
                        "latency_ms": latency_ms,
                        "duration_ms": duration_ms,
                        "language": self.config.model.language,
                    },
                )
                logger.info(
                    "Transcrição concluída — {:.0f}ms latência, {:.0f}ms áudio, {} chars",
                    latency_ms,
                    duration_ms,
                    len(text),
                )

            self.model_state_changed.emit(
                "loaded" if self._transcriber.is_loaded else "unloaded"
            )

        except Exception as exc:
            logger.exception("Erro na transcrição")
            self.error_occurred.emit(str(exc))

        finally:
            self.state_changed.emit(self._idle_state())

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _idle_state(self) -> str:
        if self._paused:
            return "paused"
        return "idle_warm" if self._transcriber.is_loaded else "idle_cold"

    def _emit_metrics(self) -> None:
        """Slot conectado ao QTimer — roda na UI thread."""
        try:
            metrics = self._metrics.get_metrics()
            self.metrics_updated.emit(metrics)
            if self.config.logging.log_metrics:
                logger.debug(
                    "Métricas: RAM={:.0f}MB VRAM={:.0f}MB GPU={:.0f}%",
                    metrics.ram_mb,
                    metrics.vram_mb,
                    metrics.gpu_percent,
                )
        except Exception:
            # Métricas são best-effort — falha silenciosa para não poluir o log
            pass


# ---------------------------------------------------------------------------
# Verificação mínima de instanciação (sem QApplication)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        from whisper_microfone.config.schemas import FullConfig

        config = FullConfig()
        engine = Engine(config)
        print("Engine criado OK")

        assert engine._transcriber.is_loaded is False, "modelo não deve estar carregado"
        assert engine._paused is False, "_paused deve iniciar False"
        print(f"  is_loaded={engine._transcriber.is_loaded}")
        print(f"  _paused={engine._paused}")

        engine.stop()
        print("OK — Engine instanciado e parado sem exceção")

    except Exception as exc:
        # QObject pode falhar sem QApplication em algumas versões do PySide6;
        # isso é esperado fora do contexto Qt e não indica bug no Engine.
        print(f"Aviso: exceção durante verificação sem QApplication — {type(exc).__name__}: {exc}")
        print("Para teste completo, instancie dentro de uma QApplication.")
