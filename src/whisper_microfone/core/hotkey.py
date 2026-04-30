from __future__ import annotations

import threading
import time
from collections.abc import Callable

from loguru import logger
from pynput.keyboard import Key, KeyCode, Listener


_MODIFIER_MAP: dict[str, Key] = {
    "ctrl": Key.ctrl_l,
    "alt": Key.alt_l,
    "shift": Key.shift,
    "space": Key.space,
    **{f"f{n}": getattr(Key, f"f{n}") for n in range(1, 13)},
}


def _parse_combination(combination: str) -> frozenset[Key | KeyCode]:
    keys: set[Key | KeyCode] = set()
    for part in combination.lower().split("+"):
        part = part.strip()
        if part in _MODIFIER_MAP:
            keys.add(_MODIFIER_MAP[part])
        elif len(part) == 1:
            keys.add(KeyCode.from_char(part))
        else:
            raise ValueError(f"Token de tecla desconhecido: {part!r}")
    return frozenset(keys)


class PushToTalkHotkey:
    def __init__(
        self,
        combination: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        self._on_press = on_press
        self._on_release = on_release
        self._target = _parse_combination(combination)
        self._held: set[Key | KeyCode] = set()
        self._active = False
        self._lock = threading.Lock()
        self._listener: Listener | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._listener = Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
            daemon=True,
        )
        self._listener.start()
        logger.debug("PushToTalkHotkey listener iniciado (combo={})", self._target)

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        with self._lock:
            self._held.clear()
            self._active = False
        logger.debug("PushToTalkHotkey listener parado")

    def update_combination(self, combination: str) -> None:
        with self._lock:
            self._target = _parse_combination(combination)
            self._held.clear()
            self._active = False
        logger.debug("PushToTalkHotkey combo atualizado para {}", self._target)

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------

    def _normalize(self, key: Key | KeyCode) -> Key | KeyCode:
        _left_right: dict[Key, Key] = {
            Key.ctrl_r: Key.ctrl_l,
            Key.alt_r: Key.alt_l,
            Key.shift_r: Key.shift,
            Key.shift_l: Key.shift,
        }
        if isinstance(key, Key):
            return _left_right.get(key, key)
        return key

    def _handle_press(self, key: Key | KeyCode | None) -> None:
        if key is None:
            return
        normalized = self._normalize(key)
        with self._lock:
            self._held.add(normalized)
            if self._target.issubset(self._held) and not self._active:
                self._active = True
                fire = True
            else:
                fire = False
        if fire:
            try:
                self._on_press()
            except Exception:
                logger.exception("Erro no callback on_press do hotkey")

    def _handle_release(self, key: Key | KeyCode | None) -> None:
        if key is None:
            return
        normalized = self._normalize(key)
        with self._lock:
            was_active = self._active
            self._held.discard(normalized)
            if normalized in self._target and self._active:
                self._active = False
                fire = True
            else:
                fire = False
        if fire:
            try:
                self._on_release()
            except Exception:
                logger.exception("Erro no callback on_release do hotkey")


if __name__ == "__main__":
    hotkey = PushToTalkHotkey(
        "ctrl+alt+space",
        on_press=lambda: print("PRESS"),
        on_release=lambda: print("RELEASE"),
    )
    hotkey.start()
    print("Pressione Ctrl+Alt+Space (5s para testar, depois encerra)")
    time.sleep(0.1)
    hotkey.stop()
    print("OK — hotkey listener iniciou e parou sem erro")
