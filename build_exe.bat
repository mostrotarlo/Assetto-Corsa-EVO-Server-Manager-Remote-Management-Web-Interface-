@echo off
cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "EVO Web Server Manager" ^
  --add-data "templates;templates" ^
  --hidden-import werkzeug.middleware.proxy_fix ^
  main.py

pause