@echo off
setlocal
cd /d "%~dp0"
title Compilacion instalador Iconos V0.1.5

echo [1/4] Localizando Python...
where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: No se encuentra el lanzador py de Python.
  echo Instala Python para Windows y vuelve a intentarlo.
  goto :fallo
)

if not exist ".buildvenv\Scripts\python.exe" (
  echo [2/4] Creando entorno exclusivo de compilacion...
  py -3 -m venv ".buildvenv"
  if errorlevel 1 goto :fallo
)

echo [2/4] Instalando dependencias de compilacion...
".buildvenv\Scripts\python.exe" -m pip install -r "requirements.txt" "pyinstaller>=6,<7"
if errorlevel 1 goto :fallo

echo [3/4] Creando aplicacion independiente...
".buildvenv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --noconsole --onedir --name Iconos --icon "assets\Iconos_App.ico" --paths src "lanzar_gui.py"
if errorlevel 1 goto :fallo
if not exist "dist\Iconos\Iconos.exe" goto :fallo

echo [4/4] Buscando Inno Setup 6...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
  where iscc.exe >nul 2>&1
  if not errorlevel 1 set "ISCC=iscc.exe"
)
if not defined ISCC (
  echo No se encuentra Inno Setup 6. Instala Inno Setup 6 y repite este BAT.
  echo El EXE ya esta generado en dist\Iconos\Iconos.exe
  goto :fallo
)
"%ISCC%" "Iconos_Instalador.iss"
if errorlevel 1 goto :fallo
if not exist "instalador\Iconos_Setup_V0.1.5.exe" goto :fallo

echo.
echo Instalador generado en instalador\Iconos_Setup_V0.1.5.exe
pause
exit /b 0

:fallo
echo.
echo ERROR: no se pudo completar el instalador. Revisa los mensajes anteriores.
pause
exit /b 1
