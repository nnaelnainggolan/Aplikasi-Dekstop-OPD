@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" periksa_excel.py
) else (
  python periksa_excel.py
)
pause
