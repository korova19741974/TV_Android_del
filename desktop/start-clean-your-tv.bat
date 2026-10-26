@echo off
setlocal
set "ROOT=%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\desktop\prepare-windows.ps1"
if errorlevel 1 goto :error
where py >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required. Install it and start this file again.
    pause
    exit /b 1
)
if not exist "%ROOT%\tools\venv\Scripts\python.exe" (
    echo Preparing the TV connection tools. This happens only once.
    py -m venv "%ROOT%\tools\venv"
    if errorlevel 1 goto :error
    "%ROOT%\tools\venv\Scripts\python.exe" -m pip install -r "%ROOT%\tools\requirements.txt"
    if errorlevel 1 goto :error
)
where pyw >nul 2>&1
if errorlevel 1 (
    echo Python 3 window launcher is missing. Reinstall Python with the standard launcher.
    pause
    exit /b 1
)
start "CleanYourTV" "%ROOT%\tools\venv\Scripts\pythonw.exe" "%~dp0CleanYourTV.py"
exit /b 0

:error
echo The first-time setup failed. Check the internet connection and try again.
pause
exit /b 1
