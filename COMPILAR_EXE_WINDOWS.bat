@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ejecuta primero INICIAR_ICONOS.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install "pyinstaller>=6,<7"
if errorlevel 1 (echo Error al preparar PyInstaller& pause& exit /b 1)
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --noconsole --onedir --name Iconos --paths src lanzar_gui.py
if errorlevel 1 (echo Error al compilar& pause& exit /b 1)
echo EXE disponible en dist\Iconos\Iconos.exe
pause
endlocal
