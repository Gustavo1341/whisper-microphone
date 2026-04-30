from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# AppConfig
# ---------------------------------------------------------------------------
class AppConfig(BaseModel):
    start_with_windows: bool = Field(False, description="Iniciar automaticamente com o Windows")
    start_minimized: bool = Field(True, description="Iniciar minimizado na bandeja do sistema")
    language_ui: Literal["pt-br", "en"] = Field("pt-br", description="Idioma da interface (pt-br ou en)")


# ---------------------------------------------------------------------------
# ModelConfig
# ---------------------------------------------------------------------------
class ModelConfig(BaseModel):
    groq_model: str = Field(
        "whisper-large-v3-turbo",
        description="Modelo Groq Whisper. Opções: whisper-large-v3-turbo, whisper-large-v3, distil-whisper-large-v3-en",
    )
    language: str = Field(
        "auto", description="Idioma de transcrição. 'auto' = detecção automática. Exemplos: pt, en, es"
    )


# ---------------------------------------------------------------------------
# AudioConfig
# ---------------------------------------------------------------------------
class AudioConfig(BaseModel):
    sample_rate: Literal[16000] = Field(16000, description="Taxa de amostragem em Hz. Whisper requer 16000 Hz")
    channels: int = Field(1, ge=1, le=2, description="Canais de áudio. 1 = mono (recomendado para Whisper)")
    device_name: str = Field("", description="Nome do dispositivo de entrada. Vazio = dispositivo padrão do sistema")
    device_index: int = Field(
        -1, description="Índice do dispositivo de entrada (sounddevice). -1 = dispositivo padrão"
    )
    min_duration_ms: int = Field(
        300, ge=100, description="Duração mínima de áudio para processar (ms). Abaixo disso, descarta"
    )
    max_duration_seconds: int = Field(
        60, ge=5, le=300, description="Duração máxima de gravação por pressão de tecla (segundos)"
    )


# ---------------------------------------------------------------------------
# VADConfig
# ---------------------------------------------------------------------------
class VADConfig(BaseModel):
    enabled: bool = Field(True, description="Ativar VAD (Voice Activity Detection) com Silero para remover silêncio")
    threshold: float = Field(
        0.5, ge=0.0, le=1.0, description="Threshold de probabilidade de fala (0.0-1.0). Mais alto = mais seletivo"
    )
    min_silence_ms: int = Field(
        200, ge=0, description="Duração mínima de silêncio para considerar pausa entre falas (ms)"
    )
    speech_pad_ms: int = Field(
        100, ge=0, description="Padding em ms adicionado ao redor dos segmentos de fala detectados"
    )


# ---------------------------------------------------------------------------
# TranscriptionConfig
# ---------------------------------------------------------------------------
class TranscriptionConfig(BaseModel):
    initial_prompt: str = Field(
        "",
        description="Prompt inicial para o Whisper. Útil para termos técnicos. Vazio = sem prompt",
    )
    temperature: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Temperatura de amostragem. 0.0 = determinístico (recomendado para ditado)",
    )


# ---------------------------------------------------------------------------
# InjectionConfig
# ---------------------------------------------------------------------------
class InjectionConfig(BaseModel):
    strategy: Literal["type_then_paste", "paste_only", "type_only"] = Field(
        "type_then_paste",
        description="Estratégia de injeção de texto: tenta digitar e cai para paste se falhar, só paste, ou só digitação",
    )
    type_delay_ms: int = Field(
        5, ge=0, description="Delay entre cada caractere digitado (ms). Aumentar se a injeção perder caracteres"
    )
    paste_fallback_after_ms: int = Field(
        1500,
        ge=100,
        description="Timeout em ms para fallback para paste quando strategy=type_then_paste",
    )
    restore_clipboard: bool = Field(
        True, description="Restaurar conteúdo anterior do clipboard após injeção via paste"
    )
    restore_clipboard_delay_ms: int = Field(
        100, ge=0, description="Delay em ms antes de restaurar o clipboard"
    )
    trim_whitespace: bool = Field(
        True, description="Remover espaços em branco no início e fim do texto transcrito antes de injetar"
    )
    add_trailing_space: bool = Field(
        False, description="Adicionar espaço ao final do texto injetado (útil para ditado contínuo)"
    )
    capitalize_first: bool = Field(
        False, description="Capitalizar a primeira letra do texto transcrito"
    )
    sentence_end_punctuation: str = Field(
        "",
        description="Pontuação a adicionar ao final se o texto não terminar com pontuação. Vazio = não adicionar",
    )


# ---------------------------------------------------------------------------
# UIConfig
# ---------------------------------------------------------------------------
class UIConfig(BaseModel):
    show_tray_icon: bool = Field(True, description="Mostrar ícone na bandeja do sistema")
    play_sounds: bool = Field(True, description="Reproduzir sons de feedback (início/fim de gravação)")
    sound_volume: float = Field(
        0.3, ge=0.0, le=1.0, description="Volume dos sons de feedback (0.0-1.0)"
    )
    metrics_update_interval_ms: int = Field(
        500, ge=100, le=5000, description="Intervalo de atualização das métricas na UI (ms)"
    )
    chart_history_seconds: int = Field(
        60, ge=10, le=300, description="Janela de tempo exibida nos gráficos de métricas (segundos)"
    )
    window_width: int = Field(900, ge=400, description="Largura inicial da janela principal (px)")
    window_height: int = Field(600, ge=300, description="Altura inicial da janela principal (px)")
    remember_window_position: bool = Field(
        True, description="Lembrar posição e tamanho da janela entre sessões"
    )


# ---------------------------------------------------------------------------
# HistoryConfig
# ---------------------------------------------------------------------------
class HistoryConfig(BaseModel):
    enabled: bool = Field(True, description="Ativar armazenamento do histórico de transcrições")
    store_text: bool = Field(True, description="Armazenar o texto das transcrições (desativar por privacidade)")
    max_entries: int = Field(
        500, ge=10, le=10000, description="Número máximo de entradas no histórico"
    )
    auto_clean_after_days: int = Field(
        30, ge=1, description="Limpar automaticamente entradas com mais de N dias. 0 = nunca limpar"
    )


# ---------------------------------------------------------------------------
# LoggingConfig
# ---------------------------------------------------------------------------
class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        "INFO", description="Nível de log. DEBUG para diagnóstico detalhado"
    )
    file_rotation_mb: int = Field(
        10, ge=1, le=100, description="Tamanho máximo do arquivo de log antes de rotacionar (MB)"
    )
    file_retention: int = Field(
        5, ge=1, le=20, description="Número máximo de arquivos de log a manter"
    )
    log_metrics: bool = Field(
        False, description="Logar métricas de RAM/CPU no arquivo de log (verboso)"
    )


# ---------------------------------------------------------------------------
# ThemeConfig
# ---------------------------------------------------------------------------
class ThemeColor(BaseModel):
    accent: str = Field("#007ACC", description="Cor de destaque principal (hex)")
    accent_hover: str = Field("#1A8CD8", description="Cor de destaque ao passar o mouse (hex)")
    recording: str = Field("#F44747", description="Cor do indicador de gravação (hex)")
    transcribing: str = Field("#FFCC02", description="Cor do indicador de transcrição em andamento (hex)")
    ready: str = Field("#89D185", description="Cor do indicador de pronto (hex)")
    paused: str = Field("#858585", description="Cor do indicador de pausado (hex)")
    error: str = Field("#F44747", description="Cor do indicador de erro (hex)")


class ThemeFont(BaseModel):
    family: str = Field("Segoe UI", description="Família de fonte da interface")
    size_base: int = Field(13, ge=8, le=24, description="Tamanho base da fonte em pontos")
    size_small: int = Field(11, ge=6, le=20, description="Tamanho de fonte pequena em pontos")
    size_large: int = Field(16, ge=10, le=32, description="Tamanho de fonte grande em pontos")
    monospace: str = Field("Consolas", description="Família de fonte monoespaçada")


class ThemeLayout(BaseModel):
    sidebar_width: int = Field(200, ge=120, le=400, description="Largura da sidebar em pixels")
    sidebar_icon_size: int = Field(20, ge=12, le=48, description="Tamanho dos ícones da sidebar em pixels")
    card_padding: int = Field(12, ge=4, le=32, description="Padding interno dos cards em pixels")
    card_radius: int = Field(6, ge=0, le=20, description="Raio de borda dos cards em pixels")
    spacing: int = Field(8, ge=2, le=24, description="Espaçamento padrão entre elementos em pixels")


class ThemeConfig(BaseModel):
    colors: ThemeColor = Field(default_factory=ThemeColor)
    fonts: ThemeFont = Field(default_factory=ThemeFont)
    layout: ThemeLayout = Field(default_factory=ThemeLayout)


# ---------------------------------------------------------------------------
# ShortcutsConfig
# ---------------------------------------------------------------------------
class KeyCombination(BaseModel):
    combination: str = Field(description="Combinação de teclas no formato 'ctrl+alt+space'")
    enabled: bool = Field(True, description="Atalho ativo")


class ShortcutsConfig(BaseModel):
    push_to_talk: KeyCombination = Field(
        default_factory=lambda: KeyCombination(combination="ctrl+alt+space"),
        description="Atalho push-to-talk (segurar para gravar)",
    )
    open_mic_popup: KeyCombination = Field(
        default_factory=lambda: KeyCombination(combination="ctrl+f9"),
        description="Abrir/fechar mini janela de microfone (clique para gravar)",
    )
    toggle_pause: KeyCombination = Field(
        default_factory=lambda: KeyCombination(combination="ctrl+alt+p"),
        description="Alternar pause/resume do PTT",
    )
    focus_window: KeyCombination = Field(
        default_factory=lambda: KeyCombination(combination="ctrl+alt+w"),
        description="Focar/mostrar a janela principal",
    )
    quit_app: KeyCombination = Field(
        default_factory=lambda: KeyCombination(combination="ctrl+q"),
        description="Sair do aplicativo (apenas com janela em foco)",
    )


# ---------------------------------------------------------------------------
# PromptsConfig
# ---------------------------------------------------------------------------
class UIStrings(BaseModel):
    model_config = {"extra": "allow"}

    app_title: str = "Whisper Microfone"
    app_subtitle: str = "Ditado por voz via Groq"
    quit_confirm_title: str = "Sair"
    quit_confirm_message: str = "Tem certeza que deseja sair?"
    sidebar_home: str = "Início"
    sidebar_monitor: str = "Monitor"
    sidebar_config: str = "Configurações"
    sidebar_history: str = "Histórico"
    sidebar_about: str = "Sobre"
    status_idle: str = "Pronto"
    status_recording: str = "Ouvindo..."
    status_transcribing: str = "Processando..."
    status_paused: str = "Pausado"
    status_error: str = "Erro"


class PromptsConfig(BaseModel):
    ui: dict[str, UIStrings] = Field(
        default_factory=dict,
        description="Strings da UI por idioma. Chaves: 'pt-br', 'en'",
    )
    whisper_prompts: dict[str, str] = Field(
        default_factory=dict,
        description="Prompts opcionais para o Whisper por contexto (ex: technical_pt, medical_en)",
    )


# ---------------------------------------------------------------------------
# ModelsCatalog
# ---------------------------------------------------------------------------
class GroqModelEntry(BaseModel):
    id: str = Field(description="ID do modelo na API Groq (ex: whisper-large-v3-turbo)")
    display_name: str = Field(description="Nome amigável exibido na UI")
    recommended: bool = Field(False, description="Marcar como recomendado na UI")
    description_pt: str = Field("", description="Descrição em PT-BR")
    description_en: str = Field("", description="Descrição em inglês")


class ModelsCatalog(BaseModel):
    available_models: list[GroqModelEntry] = Field(
        default_factory=list, description="Modelos Groq Whisper disponíveis"
    )


# ---------------------------------------------------------------------------
# AdvancedConfig
# ---------------------------------------------------------------------------
class AdvancedConfig(BaseModel):
    worker_thread_priority: Literal["normal", "above_normal", "high"] = Field(
        "normal", description="Prioridade das threads de worker (audio, transcription)"
    )
    audio_buffer_size: int = Field(
        4096, ge=512, le=65536, description="Tamanho do buffer de áudio em amostras (sounddevice blocksize)"
    )
    hotkey_poll_interval_ms: int = Field(
        10, ge=1, le=100, description="Intervalo de polling do listener de hotkey (ms)"
    )
    clipboard_timeout_ms: int = Field(
        2000, ge=500, description="Timeout máximo para operações de clipboard (ms)"
    )
    sqlite_journal_mode: Literal["WAL", "DELETE", "TRUNCATE", "PERSIST", "MEMORY", "OFF"] = Field(
        "WAL", description="Modo de journaling do SQLite para o histórico"
    )
    portable_mode: bool = Field(
        False,
        description="Modo portátil: armazena dados na pasta do executável em vez de %APPDATA%",
    )


# ---------------------------------------------------------------------------
# FullConfig — raiz que une todos os schemas
# ---------------------------------------------------------------------------
class FullConfig(BaseModel):
    """Configuração completa do whisper-microfone após merge de todas as camadas."""

    app: AppConfig = Field(default_factory=AppConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    vad: VADConfig = Field(default_factory=VADConfig)
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    injection: InjectionConfig = Field(default_factory=InjectionConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    history: HistoryConfig = Field(default_factory=HistoryConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    shortcuts: ShortcutsConfig = Field(default_factory=ShortcutsConfig)
    prompts: PromptsConfig = Field(default_factory=PromptsConfig)
    models_catalog: ModelsCatalog = Field(default_factory=ModelsCatalog)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)
