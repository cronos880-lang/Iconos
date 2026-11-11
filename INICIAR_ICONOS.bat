@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [Iconos] Preparando entorno aislado de Python...
    py -3 -m venv .venv
    if errorlevel 1 (echo No se pudo crear el entorno. Instala Python 3.10+ con el lanzador py.& pause & exit /b 1)
)
".venv\Scripts\python.exe" -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [Iconos] Instalando Pillow. Puede requerir Internet la primera vez...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (echo Error instalando dependencias.& pause & exit /b 1)
)
set "PYTHONPATH=%~dp0src"
".venv\Scripts\python.exe" -m iconos
if errorlevel 1 pause
endlocal
