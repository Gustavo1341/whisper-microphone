from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# AppConfig
# ---------------------------------------------------------------------------
class AppConfig(BaseModel):
    start_with_windows: bool = Field(False, description="Iniciar automaticamente com o Windows")
    start_minimized: bool = Field(True, description="Iniciar minimizado na bandeja do sistema")
    language_ui: Literal["pt-br", "en"] = Field("pt-br", description="Idioma da interface (pt-br ou en)")
    profile: str = Field("balanced", description="Perfil ativo (economic | balanced | always_ready ou nome de perfil customizado em models.toml)")


# ---------------------------------------------------------------------------
# ModelConfig
# ---------------------------------------------------------------------------
class ModelConfig(BaseModel):
    name: str = Field("", description="Nome do modelo faster-whisper. Vazio = herda do perfil ativo em models.toml")
    compute_type: Literal["", "int8", "int8_float16", "float16", "float32"] = Field(
        "", description="Tipo de computação. Vazio = herda do perfil. Recomendado: int8_float16 (CUDA)"
    )
    device: Literal["auto", "cuda", "cpu"] = Field(
        "auto", description="Dispositivo de inferência. 'auto' usa CUDA se disponível, senão CPU"
    )
    language: str = Field(
        "auto", description="Idioma de transcrição. 'auto' = detecção automática. Exemplos: pt, en, es"
    )
    download_dir: str = Field(
        "", description="Pasta para baixar modelos. Vazio = usa models_dir() padrão em %APPDATA%"
    )


# ---------------------------------------------------------------------------
# LifecycleConfig
# ---------------------------------------------------------------------------
class LifecycleConfig(BaseModel):
    preload_on_startup: bool = Field(
        False, description="Carregar modelo ao iniciar o app (aumenta RAM/VRAM idle, elimina latência na 1ª transcrição)"
    )
    unload_after_idle_seconds: int = Field(
        180,
        ge=0,
        description="Descarregar modelo após N segundos sem uso. 0 = nunca descarregar",
    )
    load_during_recording: bool = Field(
        True, description="Iniciar carga do modelo em paralelo assim que o PTT é pressionado"
    )
    warmup_on_load: bool = Field(
        True, description="Executar inferência de aquecimento com silêncio após carregar o modelo"
    )
    warmup_audio_seconds: float = Field(
        1.0, gt=0, description="Duração do áudio de silêncio usado no aquecimento (segundos)"
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
    beam_size: int = Field(
        1, ge=1, le=10, description="Tamanho do beam search. 1 = greedy (mais rápido). >1 = melhor qualidade, mais lento"
    )
    no_speech_threshold: float = Field(
        0.6,
        ge=0.0,
        le=1.0,
        description="Probabilidade mínima de 'sem fala' para descartar segmento. Evita alucinações em silêncio",
    )
    condition_on_previous_text: bool = Field(
        False,
        description="Usar texto anterior como contexto. False = mais seguro contra alucinações em loop",
    )
    initial_prompt: str = Field(
        "",
        description="Prompt inicial para Whisper. Útil para termos técnicos. Vazio = sem prompt. Ver prompts.toml para predefinidos",
    )
    suppress_blank: bool = Field(
        True, description="Suprimir transcrições que resultam em espaço em branco"
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
        100, ge=0, description="Delay em ms antes de restaurar o clipboard (para garantir que o Ctrl+V foi processado)"
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
        False, description="Logar métricas de RAM/VRAM/GPU/CPU no arquivo de log (verboso)"
    )


# ---------------------------------------------------------------------------
# ThemeConfig
# ---------------------------------------------------------------------------
class ThemeColor(BaseModel):
    accent: str = Field("#007ACC", description="Cor de destaque principal (hex). Padrão: azul VS Code")
    accent_hover: str = Field("#1A8CD8", description="Cor de destaque ao passar o mouse (hex)")
    recording: str = Field("#F44747", description="Cor do indicador de gravação (hex)")
    transcribing: str = Field("#FFCC02", description="Cor do indicador de transcrição em andamento (hex)")
    ready_warm: str = Field("#89D185", description="Cor do indicador de pronto com modelo quente (hex)")
    ready_cold: str = Field("#4EC9B0", description="Cor do indicador de pronto com modelo frio (hex)")
    loading: str = Field("#569CD6", description="Cor do indicador de carregamento (hex)")
    paused: str = Field("#858585", description="Cor do indicador de pausado (hex)")
    error: str = Field("#F44747", description="Cor do indicador de erro (hex)")


class ThemeFont(BaseModel):
    family: str = Field("Segoe UI", description="Família de fonte da interface")
    size_base: int = Field(13, ge=8, le=24, description="Tamanho base da fonte em pontos")
    size_small: int = Field(11, ge=6, le=20, description="Tamanho de fonte pequena em pontos")
    size_large: int = Field(16, ge=10, le=32, description="Tamanho de fonte grande em pontos")
    monospace: str = Field("Consolas", description="Família de fonte monoespaçada (para logs e código)")


class ThemeLayout(BaseModel):
    sidebar_width: int = Field(200, ge=120, le=400, description="Largura da sidebar em pixels")
    sidebar_icon_size: int = Field(20, ge=12, le=48, description="Tamanho dos ícones da sidebar em pixels")
    card_padding: int = Field(12, ge=4, le=32, description="Padding interno dos cards em pixels")
    card_radius: int = Field(6, ge=0, le=20, description="Raio de borda dos cards em pixels")
    spacing: int = Field(8, ge=2, le=24, description="Espaçamento padrão entre elementos em pixels")


class ThemeConfig(BaseModel):
    colors: ThemeColor = Field(default_factory=ThemeColor, description="Cores da interface")
    fonts: ThemeFont = Field(default_factory=ThemeFont, description="Configurações de fontes")
    layout: ThemeLayout = Field(default_factory=ThemeLayout, description="Dimensões e espaçamentos do layout")


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
    app_subtitle: str = "Ditado por voz local"
    quit_confirm_title: str = "Sair"
    quit_confirm_message: str = "Tem certeza que deseja sair?"
    sidebar_home: str = "Início"
    sidebar_monitor: str = "Monitor"
    sidebar_config: str = "Configurações"
    sidebar_history: str = "Histórico"
    sidebar_about: str = "Sobre"
    status_idle_warm: str = "Pronto"
    status_idle_cold: str = "Pronto (modelo descarregado)"
    status_loading: str = "Carregando IA..."
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
class ModelProfile(BaseModel):
    name: str = Field(description="Nome do modelo faster-whisper (ex: small, medium, large-v3-turbo)")
    compute_type: Literal["int8", "int8_float16", "float16", "float32"] = Field(
        "int8_float16", description="Tipo de computação para este perfil"
    )
    device: Literal["auto", "cuda", "cpu"] = Field("auto", description="Dispositivo para este perfil")
    unload_after_idle_seconds: int = Field(
        180, ge=0, description="Segundos de inatividade antes de descarregar. Sobrescreve lifecycle.toml para este perfil"
    )
    preload_on_startup: bool = Field(False, description="Pré-carregar ao iniciar para este perfil")
    description_pt: str = Field("", description="Descrição do perfil em PT-BR (exibida na UI)")
    description_en: str = Field("", description="Descrição do perfil em inglês (exibida na UI)")


class ModelEntry(BaseModel):
    id: str = Field(description="Identificador único do modelo (ex: small, medium, large-v3-turbo)")
    display_name: str = Field(description="Nome amigável exibido na UI")
    repo_id: str = Field(description="ID no HuggingFace Hub (ex: Systran/faster-whisper-small)")
    disk_mb: int = Field(description="Tamanho aproximado em disco (MB)")
    vram_mb: int = Field(description="VRAM aproximada em uso (MB) com compute_type padrão")
    languages: list[str] = Field(default_factory=list, description="Idiomas suportados. Vazio = multilíngue")
    recommended: bool = Field(False, description="Marcar como recomendado na UI")
    description_pt: str = Field("", description="Descrição em PT-BR")
    description_en: str = Field("", description="Descrição em inglês")


class ModelsCatalog(BaseModel):
    default_profile: str = Field(
        "balanced", description="Nome do perfil padrão (deve existir em profiles)"
    )
    profiles: dict[str, ModelProfile] = Field(
        default_factory=dict, description="Perfis disponíveis (economic, balanced, always_ready, custom...)"
    )
    available_models: list[ModelEntry] = Field(
        default_factory=list, description="Catálogo de modelos disponíveis para download e uso"
    )


# ---------------------------------------------------------------------------
# AdvancedConfig
# ---------------------------------------------------------------------------
class AdvancedConfig(BaseModel):
    worker_thread_priority: Literal["normal", "above_normal", "high"] = Field(
        "normal", description="Prioridade das threads de worker (audio, transcription). 'high' pode afetar outras apps"
    )
    audio_buffer_size: int = Field(
        4096, ge=512, le=65536, description="Tamanho do buffer de áudio em amostras (sounddevice blocksize)"
    )
    gpu_memory_fraction: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Fração máxima de VRAM a usar (0.0 = sem limite). Útil para compartilhar GPU com jogos",
    )
    inter_op_threads: int = Field(
        0, ge=0, description="Threads inter-op do CTranslate2. 0 = automático"
    )
    intra_op_threads: int = Field(
        0, ge=0, description="Threads intra-op do CTranslate2. 0 = automático"
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
    crash_reporter: bool = Field(
        True, description="Enviar relatório de crash anônimo para ajudar no diagnóstico (apenas logs locais, sem upload)"
    )


# ---------------------------------------------------------------------------
# FullConfig — raiz que une todos os schemas
# ---------------------------------------------------------------------------
class FullConfig(BaseModel):
    """Configuração completa do whisper-microfone após merge de todas as camadas."""

    app: AppConfig = Field(default_factory=AppConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    lifecycle: LifecycleConfig = Field(default_factory=LifecycleConfig)
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
