@echo off
title Shadow AI - Abdulrehman's Companion
cd /d "D:\Shadow-AI-Companion" || (
    echo ERROR: Cannot find project folder D:\Shadow-AI-Companion
    pause
    exit /b
)

echo Activating virtual environment...
call venv\Scripts\activate.bat || (
    echo ERROR: Failed to activate venv. Make sure venv exists.
    pause
    exit /b
)

echo Launching Shadow AI...
python scripts\app.py

echo.
echo Shadow AI closed.
pause