# Whisper Microfone

![Status](https://img.shields.io/badge/status-Alpha%200.1.0-orange) ![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![Licença](https://img.shields.io/badge/licença-MIT-green) ![Plataforma](https://img.shields.io/badge/plataforma-Windows-blue)

Substituto open source do Win+H do Windows. Pressione um atalho, fale, solte — o texto aparece onde o cursor estiver. Transcrição 100% local com Whisper, sem nuvem, sem assinatura.

---

## Funcionalidades

- **Push-to-talk global** — atalho configurável (padrão: `Ctrl+Alt+Space`) funciona em qualquer janela
- **Transcrição local com faster-whisper** — sem enviar áudio para servidores externos
- **Aceleração CUDA** — latência de ~400ms para 5 segundos de áudio em GPU NVIDIA
- **Lazy load do modelo** — consome ~80 MB de RAM e 0 VRAM em idle; modelo carrega em paralelo enquanto você fala
- **VAD integrado** — Silero VAD remove silêncio antes de transcrever, reduzindo alucinações
- **Injeção inteligente de texto** — tenta digitar direto na janela ativa; cai para clipboard se necessário
- **Interface estilo VS Code** — dark theme, 5 abas: Início, Monitor, Config, Histórico, Sobre
- **Multilíngue** — interface em PT-BR e EN, transcrição em qualquer idioma suportado pelo Whisper
- **Zero hardcoded** — tudo configurável em arquivos TOML com hot-reload automático
- **Histórico de transcrições** — armazenamento local em SQLite, pesquisável pela interface
- **Perfis de uso** — alternar entre modos `economic`, `balanced` e `always_ready` sem reiniciar
- **Bandeja do sistema** — roda em background sem ocupar a barra de tarefas

---

## Requisitos

| Componente | Versão mínima |
|---|---|
| Windows | 10 / 11 (64-bit) |
| Python | 3.11 ou superior |
| GPU NVIDIA | Recomendada (qualquer GPU Pascal ou mais nova) |
| Drivers NVIDIA | Atualizados com suporte a CUDA 12 |
| VRAM | 2 GB+ recomendados (modelo `small`) |

> A GPU é recomendada mas não obrigatória. Em CPU, a latência sobe para alguns segundos dependendo do modelo escolhido.

---

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/Gustavo1341/whisper-microphone.git
cd whisper-microphone

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Iniciar o app
run.bat
```

---

## Primeiro uso

Antes de usar pela primeira vez, baixe o modelo de transcrição:

```bash
# Ative o venv antes
.venv\Scripts\activate

# Baixar o modelo padrão (small — ~460 MB)
python scripts/pre_download_model.py
```

Depois de baixado, inicie o app com `run.bat` e pressione `Ctrl+Alt+Space` em qualquer campo de texto para começar a ditar.

> Na primeira transcrição após iniciar, há uma pausa de 1 a 5 segundos para carregar o modelo na GPU. As transcrições seguintes respondem em ~400ms.

---

## Configuração

Os arquivos de configuração ficam em `%APPDATA%\whisper-microfone\config\` e são criados automaticamente na primeira execução.

Os arquivos TOML podem ser editados com qualquer editor de texto. O app detecta as mudanças e aplica sem precisar reiniciar (**hot-reload**).

| Arquivo | Conteúdo |
|---|---|
| `config.toml` | App, modelo, áudio, VAD, transcrição, injeção, UI, histórico, logs |
| `models.toml` | Catálogo de modelos e perfis |
| `shortcuts.toml` | Atalhos de teclado |
| `theme.toml` | Cores, fontes e layout |
| `advanced.toml` | Configurações avançadas de threads, buffer e GPU |

Consulte a referência completa de todas as opções em [docs/CONFIG.md](docs/CONFIG.md).

---

## Atalhos padrão

| Atalho | Ação |
|---|---|
| `Ctrl+Alt+Space` | Push-to-talk (segurar para gravar, soltar para transcrever) |
| `Ctrl+Alt+P` | Pausar / retomar o listener de hotkey |
| `Ctrl+Alt+W` | Mostrar / esconder a janela principal |

Todos os atalhos são configuráveis em `shortcuts.toml`.

---

## Perfis de uso

O perfil ativo é definido em `config.toml → [app] → profile` e pode ser trocado pela interface sem reiniciar o app.

| Perfil | Modelo | Comportamento | Indicado para |
|---|---|---|---|
| `economic` | tiny / base | Modelo descarregado em 60s de idle; load rápido | Uso esporádico, RAM limitada |
| `balanced` | small | Modelo descarregado em 3min de idle; load paralelo durante fala | Uso diário — equilíbrio padrão |
| `always_ready` | small / medium | Modelo sempre na VRAM; sem latência de load | Ditado intenso, máquina dedicada |

Você pode criar perfis customizados diretamente em `models.toml`.

---

## Troubleshooting

**CUDA não encontrado / transcrição rodando em CPU**

Verifique se os drivers NVIDIA estão atualizados e se o pacote correto do PyTorch com CUDA está instalado. O app exibe o dispositivo ativo na aba Monitor. Para forçar CPU explicitamente, defina `device = "cpu"` em `config.toml → [model]`.

**Microfone não detectado**

Liste os dispositivos disponíveis com:
```bash
python scripts/test_audio_devices.py
```
Copie o nome ou índice do microfone desejado e configure em `config.toml → [audio] → device_name` ou `device_index`.

**App elevado (Executado como Administrador) não recebe o texto**

Quando a janela alvo roda com privilégios elevados (ex.: Gerenciador de Tarefas, alguns jogos), o app precisa ser iniciado também como Administrador para conseguir injetar texto. Clique com o botão direito em `run.bat` e selecione "Executar como administrador".

**Primeira transcrição demora muito**

É normal. O modelo é carregado na GPU durante a primeira fala (lazy load). O tempo de espera é de 2 a 8 segundos dependendo do modelo e do disco. Para eliminar essa latência, defina `preload_on_startup = true` em `config.toml → [lifecycle]` — o modelo carrega ao iniciar o app, consumindo VRAM mesmo em idle.

**Texto transcrito está incorreto ou tem alucinações**

Reduza o threshold de VAD (`vad.threshold`) para um valor entre 0.3 e 0.5 se o áudio tiver muito ruído. Aumente `transcription.no_speech_threshold` se o app transcrever silêncio. Considere trocar para o modelo `medium` ou `large-v3-turbo` para maior precisão.

---

## Licença

MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.

Autor: Gustavo Brandão
