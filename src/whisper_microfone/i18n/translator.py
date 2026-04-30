from __future__ import annotations

from whisper_microfone.config.schemas import PromptsConfig


class Translator:
    """Resolve strings da UI pelo idioma ativo com fallback EN → '<key>'.

    Uso:
        t = Translator(prompts_config, language="pt-br")
        button.setText(t("btn_pause"))
        label.setText(t("notif_model_loaded", seconds=1.4))

    Troca de idioma em runtime:
        t.set_language("en")

    Atualização de prompts (hot-reload):
        t.update(new_prompts_config)
    """

    _FALLBACK_LANG = "en"

    def __init__(self, prompts: PromptsConfig, language: str = "pt-br") -> None:
        self._prompts = prompts
        self._language = language.lower()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def __call__(self, key: str, **kwargs: object) -> str:
        """Alias de t() para uso como t("key") em vez de t.t("key")."""
        return self.t(key, **kwargs)

    def t(self, key: str, **kwargs: object) -> str:
        """Retorna a string localizada para *key* no idioma ativo.

        Ordem de fallback:
        1. Idioma ativo (ex: pt-br)
        2. Inglês (en)
        3. Literal '<key>' — nunca lança KeyError
        """
        value = self._resolve(key)
        if not kwargs:
            return value
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value

    def set_language(self, language: str) -> None:
        """Troca o idioma ativo em runtime (ex: 'pt-br' → 'en')."""
        self._language = language.lower()

    def language(self) -> str:
        """Retorna o idioma ativo."""
        return self._language

    def update(self, prompts: PromptsConfig) -> None:
        """Substitui o PromptsConfig (chamado após hot-reload do watcher)."""
        self._prompts = prompts

    def has_key(self, key: str) -> bool:
        """Retorna True se a chave existe em qualquer idioma disponível."""
        for lang_strings in self._prompts.ui.values():
            if hasattr(lang_strings, key) or key in (lang_strings.model_extra or {}):
                return True
        return False

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _resolve(self, key: str) -> str:
        """Resolve key com fallback: idioma ativo → EN → '<key>'."""
        for lang in (self._language, self._FALLBACK_LANG):
            strings = self._prompts.ui.get(lang)
            if strings is None:
                continue
            # Tenta atributo fixo primeiro, depois model_extra (chaves dinâmicas)
            value = getattr(strings, key, None)
            if value is None:
                value = (strings.model_extra or {}).get(key)
            if value is not None:
                return str(value)
        return f"<{key}>"
