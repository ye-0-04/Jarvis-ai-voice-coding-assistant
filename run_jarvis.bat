@echo off
title Jarvis - Code Assistant
echo ========================================
echo  🤖 STARTING JARVIS
echo ========================================
echo.

cd /d D:\Jarvis

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python.
    pause
    exit /b 1
)

REM Check if Ollama is running
ollama list >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama not running! Starting Ollama...
    start "" "C:\Program Files\Ollama\ollama.exe"
    echo Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
)

echo.
echo 🚀 Launching Jarvis...
echo.

python jarvis.py

pause