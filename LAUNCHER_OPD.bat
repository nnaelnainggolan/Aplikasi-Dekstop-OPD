@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python tidak ditemukan di PATH. Install Python 3.10+ terlebih dahulu ^(pilih "Add to PATH" saat instalasi^), lalu jalankan file ini lagi.
  pause
  exit /b 1
)
python launcher_opd.py
if errorlevel 1 pause
