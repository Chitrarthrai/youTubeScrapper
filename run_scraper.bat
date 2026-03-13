@echo off
title YouTube Playlist Data Scraper
color 0A

echo ==============================================================
echo        __  __         _____     __           ____         
echo        \ \/ /__  __  ^|_   _^|   / /_  ___    / __ \        
echo         \  / _ \/ / / // /    / __ \/ _ \  / / / /        
echo         / /  __/ /_/ // /    / /_/ /  __/ / /_/ /         
echo        /_/\___/\__,_//_/    /_.___/\___/  \____/          
echo.                                                        
echo                  YOUTUBE PLAYLIST SCRAPER
echo ==============================================================
echo.
echo [*] Checking environment and requirements...

:: Check if Python is installed globally
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Python is not installed globally or not in PATH...
    echo [*] Downloading Python installer...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    if exist python_installer.exe (
        echo [*] Installing Python silently and adding it to PATH. Please wait...
        start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        echo [*] Installation finished. Cleaning up...
        del python_installer.exe
        
        echo [!] IMPORTANT: Python was just installed. You MUST restart this window/script to update the PATH variables!
        pause
        exit /b
    ) else (
        echo [!] Failed to download Python. Please install it manually from python.org.
        pause
        exit /b
    )
)

:: Create virtual environment if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

:: Activate the environment safely
call venv\Scripts\activate.bat

:: Update pip
python -m pip install --upgrade pip

:: Ensure requirements are met safely and keep them updated
python -m pip install --upgrade -r requirements.txt

echo [+] Ready.
echo.

:start_scraper
echo ==============================================================
echo                 STARTING EXTRACTOR SYSTEM
echo ==============================================================
:: Run scraper
python scraper.py

echo.
echo ==============================================================
echo [!] Process Finished.
echo.
set /p choice="Do you want to run another scrape? (Y to continue, N to exit): "
if /I "%choice%"=="Y" goto start_scraper
if /I "%choice%"=="YES" goto start_scraper

exit /b

