@echo off
cd /d "%~dp0"
python -m pip show pillow >nul 2>nul
if errorlevel 1 (
  echo Memasang Pillow ...
  python -m pip install --quiet pillow
)
python buat_ikon.py
pause
