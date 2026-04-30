from __future__ import annotations

import gc
import threading
from typing import TYPE_CHECKING

import numpy as np
from faster_whisper import WhisperModel

from whisper_microfone.config.paths import models_dir
from whisper_microfone.config.schemas import LifecycleConfig, ModelConfig, TranscriptionConfig


class WhisperTranscriber:
    def __init__(
        self,
        model_cfg: ModelConfig,
        lifecycle_cfg: LifecycleConfig,
        transcription_cfg: TranscriptionConfig,
    ) -> None:
        self._model_cfg = model_cfg
        self._lifecycle = lifecycle_cfg
        self._transcription = transcription_cfg
        self._model: WhisperModel | None = None
        self._lock = threading.Lock()
        self._loading: threading.Event | None = None
        self._unload_timer: threading.Timer | None = None
        self._load_error: Exception | None = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def is_loading(self) -> bool:
        return self._loading is not None and not self._loading.is_set()

    def preload_async(self) -> None:
        with self._lock:
            if self._model is not None or (
                self._loading is not None and not self._loading.is_set()
            ):
                return
            self._loading = threading.Event()

        t = threading.Thread(target=self._load, daemon=True)
        t.start()

    def _load(self) -> None:
        try:
            model = WhisperModel(
                self._model_cfg.name or "small",
                device=self._model_cfg.device,
                compute_type=self._model_cfg.compute_type or "int8_float16",
                download_root=str(models_dir()),
            )
            if self._lifecycle.warmup_on_load:
                silence = np.zeros(
                    int(16000 * self._lifecycle.warmup_audio_seconds),
                    dtype=np.float32,
                )
                list(model.transcribe(silence, language="en")[0])
            with self._lock:
                self._model = model
                self._load_error = None
                if self._loading:
                    self._loading.set()
        except Exception as exc:
            with self._lock:
                self._load_error = exc
                if self._loading:
                    self._loading.set()

    def transcribe(self, audio: np.ndarray, language: str | None = None) -> str:
        if self._loading is not None and not self._loading.is_set():
            self._loading.wait(timeout=30)

        if self._load_error is not None:
            raise self._load_error

        if self._model is None:
            with self._lock:
                if self._loading is None:
                    self._loading = threading.Event()
            self._load()
            if self._load_error is not None:
                raise self._load_error

        lang = language if language is not None else (
            self._model_cfg.language if self._model_cfg.language != "auto" else None
        )

        cfg = self._transcription
        segments, _ = self._model.transcribe(
            audio,
            language=lang,
            beam_size=cfg.beam_size,
            no_speech_threshold=cfg.no_speech_threshold,
            condition_on_previous_text=cfg.condition_on_previous_text,
            initial_prompt=cfg.initial_prompt or None,
            suppress_blank=cfg.suppress_blank,
            temperature=cfg.temperature,
        )

        text = "".join(seg.text for seg in segments)
        self._reset_unload_timer()
        return text

    def _reset_unload_timer(self) -> None:
        if self._lifecycle.unload_after_idle_seconds <= 0:
            return
        if self._unload_timer is not None:
            self._unload_timer.cancel()
        self._unload_timer = threading.Timer(
            self._lifecycle.unload_after_idle_seconds,
            self._unload,
        )
        self._unload_timer.daemon = True
        self._unload_timer.start()

    def _unload(self) -> None:
        with self._lock:
            if self._model is None:
                return
            del self._model
            self._model = None
            self._loading = None
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except ImportError:
            pass


if __name__ == "__main__":
    import time

    t = WhisperTranscriber(ModelConfig(), LifecycleConfig(), TranscriptionConfig())
    print("is_loaded:", t.is_loaded)
    print("is_loading:", t.is_loading)
    t.preload_async()
    print("preload_async() chamado, is_loading:", t.is_loading)
    time.sleep(0.5)
    t._unload()
    print("OK — instancia, preload_async e _unload sem excecao")
