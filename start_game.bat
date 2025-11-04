@echo off
title Space Triangle Launcher
color 0A
setlocal

echo ===============================
echo       Space Triangle Launcher
echo ===============================
echo.

:: Step 1 - Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python not found!
    echo.
    set /p choice="Do you want to automatically install Python 3.11? (Y/N): "
    if /I "%choice%"=="Y" (
        echo Downloading Python 3.11 installer...
        powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -OutFile %TEMP%\python_installer.exe"
        
        echo Installing Python silently...
        start /wait "" "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        
        echo Checking Python installation...
        python --version >nul 2>&1
        IF ERRORLEVEL 1 (
            echo Installation failed. Please install manually from https://www.python.org/downloads/
            pause
            exit /b
        )
    ) else (
        echo Python is required to play. Exiting.
        pause
        exit /b
    )
)

:: Step 2 - Check pygame
python -m pip show pygame >nul 2>&1
IF ERRORLEVEL 1 (
    echo.
    echo Pygame not found!
    echo Installing pygame automatically...
    python -m pip install pygame
    if ERRORLEVEL 1 (
        echo.
        echo Failed to install pygame. Check your internet connection.
        pause
        exit /b
    )
)

:: Step 3 - Launch the game
echo.
echo Starting Space Triangle...
echo.
python "%~dp0\1.py"

echo.
echo Game closed.
pause
