@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=python"
if exist ".build-venv\Scripts\python.exe" set "PYTHON=.build-venv\Scripts\python.exe"

"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -r requirements.txt
"%PYTHON%" -m pip install pyinstaller
"%PYTHON%" -m pip install reportlab

set "OUT=dist\EVO-Web-Server-Manager-v1.5.0"
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "EVO Web Server Manager Control Panel" ^
  --distpath "%OUT%" ^
  main.py
if errorlevel 1 goto :failed

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --noconsole ^
  --name "EVO Web Server Manager Engine" ^
  --distpath "%OUT%" ^
  --add-data "templates;templates" ^
  --hidden-import werkzeug.middleware.proxy_fix ^
  --hidden-import win32timezone ^
  --hidden-import servicemanager ^
  --hidden-import win32service ^
  --hidden-import win32serviceutil ^
  --hidden-import win32event ^
  backend_engine.py
if errorlevel 1 goto :failed

"%PYTHON%" build_manual.py
if errorlevel 1 goto :failed

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "EVO Web Server Manager v1.5.0 Installer" ^
  --distpath "%OUT%" ^
  --add-data "%OUT%\EVO Web Server Manager Control Panel.exe;payload" ^
  --add-data "%OUT%\EVO Web Server Manager Engine.exe;payload" ^
  --add-data "%OUT%\EVO Web Server Manager Manual.pdf;payload" ^
  installer.py
if errorlevel 1 goto :failed

copy /y "app_config.example.json" "%OUT%\app_config.example.json" >nul
copy /y "README.md" "%OUT%\README.md" >nul
copy /y "LICENSE" "%OUT%\LICENSE" >nul

echo.
echo Build complete: %OUT%
exit /b 0

:failed
echo.
echo Build failed.
exit /b 1
