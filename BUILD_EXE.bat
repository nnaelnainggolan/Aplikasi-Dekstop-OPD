@echo off
cd /d "%~dp0"
echo Memeriksa PyInstaller ...
python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
  echo Memasang PyInstaller, tunggu sebentar ...
  python -m pip install --quiet pyinstaller
  if errorlevel 1 (
    echo Gagal memasang PyInstaller. Pastikan Python dan pip terpasang dan terhubung internet.
    pause
    exit /b 1
  )
)

if exist "OPD Automation Suite.exe" del /f /q "OPD Automation Suite.exe" >nul 2>nul

echo.
echo PENTING: jika laptop memakai Windows Defender/antivirus lain, tambahkan folder ini
echo ke pengecualian (Exclusions) SEBELUM lanjut. PyInstaller sering diam-diam dikarantina
echo di tengah proses, menghasilkan .exe yang rusak/tidak lengkap tanpa pesan error apa pun.
echo.

if exist "icon.ico" (
  echo Memakai icon.ico sebagai logo aplikasi.
  echo Membangun "OPD Automation Suite.exe" ...
  python -m PyInstaller --onefile --windowed --clean --name "OPD Automation Suite" --icon "%~dp0icon.ico" ^
    --distpath . --workpath build_temp --specpath build_temp --noconfirm launcher_opd.py
) else (
  echo Tidak ada icon.ico, memakai ikon bawaan PyInstaller.
  echo ^(Jalankan BUAT_IKON.bat dulu jika ingin logo sendiri, lalu jalankan file ini lagi.^)
  echo Membangun "OPD Automation Suite.exe" ...
  python -m PyInstaller --onefile --windowed --clean --name "OPD Automation Suite" ^
    --distpath . --workpath build_temp --specpath build_temp --noconfirm launcher_opd.py
)

if not exist "OPD Automation Suite.exe" (
  echo.
  echo Build gagal. Periksa pesan error di atas.
  pause
  exit /b 1
)

rmdir /s /q build_temp >nul 2>nul

for %%A in ("OPD Automation Suite.exe") do set EXE_SIZE=%%~zA
echo.
echo Ukuran file: %EXE_SIZE% bytes
if %EXE_SIZE% LSS 3000000 (
  echo.
  echo PERINGATAN: ukuran file jauh lebih kecil dari wajar ^(biasanya 8-15 MB^).
  echo File kemungkinan tidak lengkap, sering karena antivirus mengarantina DLL saat build.
  echo Tambahkan folder ini ke Exclusions Windows Defender, lalu jalankan file ini lagi.
) else (
  echo.
  echo Selesai. File "OPD Automation Suite.exe" sudah ada di folder ini dan ukurannya wajar.
  echo.
  echo Klik kanan file itu lalu pilih "Show more options" ^> "Send to" ^> "Desktop (create shortcut)"
  echo untuk membuat ikon di Desktop.
)
pause
