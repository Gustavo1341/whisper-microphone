# Referência de Configuração — Whisper Microfone

> **Gerado automaticamente** a partir dos schemas Pydantic em `config/schemas.py`.
> Não edite este arquivo manualmente — execute `python scripts/gen_docs.py` para atualizar.

## Como configurar

Os arquivos de configuração ficam em `%APPDATA%\whisper-microfone\config\` (Windows)
ou `~/.local/share/whisper-microfone/config/` (Linux/Mac).

Na primeira execução, os defaults são copiados automaticamente para essa pasta.
Edite os arquivos TOML com qualquer editor de texto — o app detecta as mudanças
automaticamente (hot-reload).

### Precedência

```
Defaults empacotados < Config do usuário < Variáveis de ambiente
```

**Variáveis de ambiente:** `WHISPER_MIC_<SECAO>__<CAMPO>=valor`
Exemplo: `WHISPER_MIC_APP__LANGUAGE_UI=en`

---

### Aplicação

**Arquivo:** `config.toml → [app]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `start_with_windows` | `bool` | `false` |  | Iniciar automaticamente com o Windows |
| `start_minimized` | `bool` | `true` |  | Iniciar minimizado na bandeja do sistema |
| `language_ui` | `Literal['pt-br', 'en']` | `"pt-br"` |  | Idioma da interface (pt-br ou en) |
| `profile` | `str` | `"balanced"` |  | Perfil ativo (economic | balanced | always_ready ou nome de perfil customizado em models.toml) |

### Modelo

**Arquivo:** `config.toml → [model]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `name` | `str` | `""` |  | Nome do modelo faster-whisper. Vazio = herda do perfil ativo em models.toml |
| `compute_type` | `Literal['', 'int8', 'int8_float16', 'float16', 'float32']` | `""` |  | Tipo de computação. Vazio = herda do perfil. Recomendado: int8_float16 (CUDA) |
| `device` | `Literal['auto', 'cuda', 'cpu']` | `"auto"` |  | Dispositivo de inferência. 'auto' usa CUDA se disponível, senão CPU |
| `language` | `str` | `"auto"` |  | Idioma de transcrição. 'auto' = detecção automática. Exemplos: pt, en, es |
| `download_dir` | `str` | `""` |  | Pasta para baixar modelos. Vazio = usa models_dir() padrão em %APPDATA% |

### Ciclo de vida

**Arquivo:** `config.toml → [lifecycle]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `preload_on_startup` | `bool` | `false` |  | Carregar modelo ao iniciar o app (aumenta RAM/VRAM idle, elimina latência na 1ª transcrição) |
| `unload_after_idle_seconds` | `int` | `180` | ≥ 0 | Descarregar modelo após N segundos sem uso. 0 = nunca descarregar |
| `load_during_recording` | `bool` | `true` |  | Iniciar carga do modelo em paralelo assim que o PTT é pressionado |
| `warmup_on_load` | `bool` | `true` |  | Executar inferência de aquecimento com silêncio após carregar o modelo |
| `warmup_audio_seconds` | `float` | `1.0` | > 0 | Duração do áudio de silêncio usado no aquecimento (segundos) |

### Áudio

**Arquivo:** `config.toml → [audio]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `sample_rate` | `Literal[16000]` | `16000` |  | Taxa de amostragem em Hz. Whisper requer 16000 Hz |
| `channels` | `int` | `1` | ≥ 1, ≤ 2 | Canais de áudio. 1 = mono (recomendado para Whisper) |
| `device_name` | `str` | `""` |  | Nome do dispositivo de entrada. Vazio = dispositivo padrão do sistema |
| `device_index` | `int` | `-1` |  | Índice do dispositivo de entrada (sounddevice). -1 = dispositivo padrão |
| `min_duration_ms` | `int` | `300` | ≥ 100 | Duração mínima de áudio para processar (ms). Abaixo disso, descarta |
| `max_duration_seconds` | `int` | `60` | ≥ 5, ≤ 300 | Duração máxima de gravação por pressão de tecla (segundos) |

### VAD (detecção de voz)

**Arquivo:** `config.toml → [vad]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `enabled` | `bool` | `true` |  | Ativar VAD (Voice Activity Detection) com Silero para remover silêncio |
| `threshold` | `float` | `0.5` | ≥ 0.0, ≤ 1.0 | Threshold de probabilidade de fala (0.0-1.0). Mais alto = mais seletivo |
| `min_silence_ms` | `int` | `200` | ≥ 0 | Duração mínima de silêncio para considerar pausa entre falas (ms) |
| `speech_pad_ms` | `int` | `100` | ≥ 0 | Padding em ms adicionado ao redor dos segmentos de fala detectados |

### Transcrição

**Arquivo:** `config.toml → [transcription]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `beam_size` | `int` | `1` | ≥ 1, ≤ 10 | Tamanho do beam search. 1 = greedy (mais rápido). >1 = melhor qualidade, mais lento |
| `no_speech_threshold` | `float` | `0.6` | ≥ 0.0, ≤ 1.0 | Probabilidade mínima de 'sem fala' para descartar segmento. Evita alucinações em silêncio |
| `condition_on_previous_text` | `bool` | `false` |  | Usar texto anterior como contexto. False = mais seguro contra alucinações em loop |
| `initial_prompt` | `str` | `""` |  | Prompt inicial para Whisper. Útil para termos técnicos. Vazio = sem prompt. Ver prompts.toml para predefinidos |
| `suppress_blank` | `bool` | `true` |  | Suprimir transcrições que resultam em espaço em branco |
| `temperature` | `float` | `0.0` | ≥ 0.0, ≤ 1.0 | Temperatura de amostragem. 0.0 = determinístico (recomendado para ditado) |

### Injeção de texto

**Arquivo:** `config.toml → [injection]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `strategy` | `Literal['type_then_paste', 'paste_only', 'type_only']` | `"type_then_paste"` |  | Estratégia de injeção de texto: tenta digitar e cai para paste se falhar, só paste, ou só digitação |
| `type_delay_ms` | `int` | `5` | ≥ 0 | Delay entre cada caractere digitado (ms). Aumentar se a injeção perder caracteres |
| `paste_fallback_after_ms` | `int` | `1500` | ≥ 100 | Timeout em ms para fallback para paste quando strategy=type_then_paste |
| `restore_clipboard` | `bool` | `true` |  | Restaurar conteúdo anterior do clipboard após injeção via paste |
| `restore_clipboard_delay_ms` | `int` | `100` | ≥ 0 | Delay em ms antes de restaurar o clipboard (para garantir que o Ctrl+V foi processado) |
| `trim_whitespace` | `bool` | `true` |  | Remover espaços em branco no início e fim do texto transcrito antes de injetar |
| `add_trailing_space` | `bool` | `false` |  | Adicionar espaço ao final do texto injetado (útil para ditado contínuo) |
| `capitalize_first` | `bool` | `false` |  | Capitalizar a primeira letra do texto transcrito |
| `sentence_end_punctuation` | `str` | `""` |  | Pontuação a adicionar ao final se o texto não terminar com pontuação. Vazio = não adicionar |

### Interface

**Arquivo:** `config.toml → [ui]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `show_tray_icon` | `bool` | `true` |  | Mostrar ícone na bandeja do sistema |
| `play_sounds` | `bool` | `true` |  | Reproduzir sons de feedback (início/fim de gravação) |
| `sound_volume` | `float` | `0.3` | ≥ 0.0, ≤ 1.0 | Volume dos sons de feedback (0.0-1.0) |
| `metrics_update_interval_ms` | `int` | `500` | ≥ 100, ≤ 5000 | Intervalo de atualização das métricas na UI (ms) |
| `chart_history_seconds` | `int` | `60` | ≥ 10, ≤ 300 | Janela de tempo exibida nos gráficos de métricas (segundos) |
| `window_width` | `int` | `900` | ≥ 400 | Largura inicial da janela principal (px) |
| `window_height` | `int` | `600` | ≥ 300 | Altura inicial da janela principal (px) |
| `remember_window_position` | `bool` | `true` |  | Lembrar posição e tamanho da janela entre sessões |

### Histórico

**Arquivo:** `config.toml → [history]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `enabled` | `bool` | `true` |  | Ativar armazenamento do histórico de transcrições |
| `store_text` | `bool` | `true` |  | Armazenar o texto das transcrições (desativar por privacidade) |
| `max_entries` | `int` | `500` | ≥ 10, ≤ 10000 | Número máximo de entradas no histórico |
| `auto_clean_after_days` | `int` | `30` | ≥ 1 | Limpar automaticamente entradas com mais de N dias. 0 = nunca limpar |

### Logs

**Arquivo:** `config.toml → [logging]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `level` | `Literal['DEBUG', 'INFO', 'WARNING', 'ERROR']` | `"INFO"` |  | Nível de log. DEBUG para diagnóstico detalhado |
| `file_rotation_mb` | `int` | `10` | ≥ 1, ≤ 100 | Tamanho máximo do arquivo de log antes de rotacionar (MB) |
| `file_retention` | `int` | `5` | ≥ 1, ≤ 20 | Número máximo de arquivos de log a manter |
| `log_metrics` | `bool` | `false` |  | Logar métricas de RAM/VRAM/GPU/CPU no arquivo de log (verboso) |

### Cores

**Arquivo:** `theme.toml → [colors]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `accent` | `str` | `"#007ACC"` |  | Cor de destaque principal (hex). Padrão: azul VS Code |
| `accent_hover` | `str` | `"#1A8CD8"` |  | Cor de destaque ao passar o mouse (hex) |
| `recording` | `str` | `"#F44747"` |  | Cor do indicador de gravação (hex) |
| `transcribing` | `str` | `"#FFCC02"` |  | Cor do indicador de transcrição em andamento (hex) |
| `ready_warm` | `str` | `"#89D185"` |  | Cor do indicador de pronto com modelo quente (hex) |
| `ready_cold` | `str` | `"#4EC9B0"` |  | Cor do indicador de pronto com modelo frio (hex) |
| `loading` | `str` | `"#569CD6"` |  | Cor do indicador de carregamento (hex) |
| `paused` | `str` | `"#858585"` |  | Cor do indicador de pausado (hex) |
| `error` | `str` | `"#F44747"` |  | Cor do indicador de erro (hex) |

### Fontes

**Arquivo:** `theme.toml → [fonts]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `family` | `str` | `"Segoe UI"` |  | Família de fonte da interface |
| `size_base` | `int` | `13` | ≥ 8, ≤ 24 | Tamanho base da fonte em pontos |
| `size_small` | `int` | `11` | ≥ 6, ≤ 20 | Tamanho de fonte pequena em pontos |
| `size_large` | `int` | `16` | ≥ 10, ≤ 32 | Tamanho de fonte grande em pontos |
| `monospace` | `str` | `"Consolas"` |  | Família de fonte monoespaçada (para logs e código) |

### Layout

**Arquivo:** `theme.toml → [layout]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `sidebar_width` | `int` | `200` | ≥ 120, ≤ 400 | Largura da sidebar em pixels |
| `sidebar_icon_size` | `int` | `20` | ≥ 12, ≤ 48 | Tamanho dos ícones da sidebar em pixels |
| `card_padding` | `int` | `12` | ≥ 4, ≤ 32 | Padding interno dos cards em pixels |
| `card_radius` | `int` | `6` | ≥ 0, ≤ 20 | Raio de borda dos cards em pixels |
| `spacing` | `int` | `8` | ≥ 2, ≤ 24 | Espaçamento padrão entre elementos em pixels |

### Atalhos — Push-to-talk

**Arquivo:** `shortcuts.toml → [push_to_talk]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `combination` | `str` | `PydanticUndefined` |  | Combinação de teclas no formato 'ctrl+alt+space' |
| `enabled` | `bool` | `true` |  | Atalho ativo |

### Catálogo — Perfil

**Arquivo:** `models.toml → [profiles.*]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `name` | `str` | `PydanticUndefined` |  | Nome do modelo faster-whisper (ex: small, medium, large-v3-turbo) |
| `compute_type` | `Literal['int8', 'int8_float16', 'float16', 'float32']` | `"int8_float16"` |  | Tipo de computação para este perfil |
| `device` | `Literal['auto', 'cuda', 'cpu']` | `"auto"` |  | Dispositivo para este perfil |
| `unload_after_idle_seconds` | `int` | `180` | ≥ 0 | Segundos de inatividade antes de descarregar. Sobrescreve lifecycle.toml para este perfil |
| `preload_on_startup` | `bool` | `false` |  | Pré-carregar ao iniciar para este perfil |
| `description_pt` | `str` | `""` |  | Descrição do perfil em PT-BR (exibida na UI) |
| `description_en` | `str` | `""` |  | Descrição do perfil em inglês (exibida na UI) |

### Catálogo — Modelo

**Arquivo:** `models.toml → [[available_models]]`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `id` | `str` | `PydanticUndefined` |  | Identificador único do modelo (ex: small, medium, large-v3-turbo) |
| `display_name` | `str` | `PydanticUndefined` |  | Nome amigável exibido na UI |
| `repo_id` | `str` | `PydanticUndefined` |  | ID no HuggingFace Hub (ex: Systran/faster-whisper-small) |
| `disk_mb` | `int` | `PydanticUndefined` |  | Tamanho aproximado em disco (MB) |
| `vram_mb` | `int` | `PydanticUndefined` |  | VRAM aproximada em uso (MB) com compute_type padrão |
| `languages` | `list` | `PydanticUndefined` |  | Idiomas suportados. Vazio = multilíngue |
| `recommended` | `bool` | `false` |  | Marcar como recomendado na UI |
| `description_pt` | `str` | `""` |  | Descrição em PT-BR |
| `description_en` | `str` | `""` |  | Descrição em inglês |

### Avançado

**Arquivo:** `advanced.toml`

| Campo | Tipo | Default | Restrições | Descrição |
|---|---|---|---|---|
| `worker_thread_priority` | `Literal['normal', 'above_normal', 'high']` | `"normal"` |  | Prioridade das threads de worker (audio, transcription). 'high' pode afetar outras apps |
| `audio_buffer_size` | `int` | `4096` | ≥ 512, ≤ 65536 | Tamanho do buffer de áudio em amostras (sounddevice blocksize) |
| `gpu_memory_fraction` | `float` | `0.0` | ≥ 0.0, ≤ 1.0 | Fração máxima de VRAM a usar (0.0 = sem limite). Útil para compartilhar GPU com jogos |
| `inter_op_threads` | `int` | `0` | ≥ 0 | Threads inter-op do CTranslate2. 0 = automático |
| `intra_op_threads` | `int` | `0` | ≥ 0 | Threads intra-op do CTranslate2. 0 = automático |
| `hotkey_poll_interval_ms` | `int` | `10` | ≥ 1, ≤ 100 | Intervalo de polling do listener de hotkey (ms) |
| `clipboard_timeout_ms` | `int` | `2000` | ≥ 500 | Timeout máximo para operações de clipboard (ms) |
| `sqlite_journal_mode` | `Literal['WAL', 'DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'OFF']` | `"WAL"` |  | Modo de journaling do SQLite para o histórico |
| `portable_mode` | `bool` | `false` |  | Modo portátil: armazena dados na pasta do executável em vez de %APPDATA% |
| `crash_reporter` | `bool` | `true` |  | Enviar relatório de crash anônimo para ajudar no diagnóstico (apenas logs locais, sem upload) |

---

*Gerado por `scripts/gen_docs.py`*
