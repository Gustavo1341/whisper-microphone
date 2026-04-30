@echo off
setlocal
cd /d "%~dp0"

REM Verificar se venv existe
if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] venv nao encontrado. Execute primeiro:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m whisper_microfone %*
