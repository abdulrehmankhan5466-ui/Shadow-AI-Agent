@echo off
title Start Ollama
echo Starting Ollama server...
start "" "ollama" serve
echo Ollama is now running in background.
echo You can close this window.
pause