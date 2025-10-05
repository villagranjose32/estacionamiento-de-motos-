@echo off
echo ========================================
echo Sistema de Gestion de Estacionamiento
echo ========================================
echo.
echo Iniciando el sistema...

cd /d "%~dp0"

IF EXIST .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) ELSE (
    echo.
    echo No se encontro el entorno virtual.
    echo.
    echo Por favor, ejecute primero el script de configuracion:
    echo   python configurar.py
    echo.
    pause
)
