@echo off
REM ================================================================================
REM                         EJECUTAR ZEROX
REM                    Doble click para iniciar
REM ================================================================================

cd /d "%~dp0"
color 0A
title ZEROX - La IA que te hace millonario

cls
echo.
echo    ███████╗███████╗██████╗  ██████╗ ██╗  ██╗
echo    ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗╚██╗██╔╝
echo      ███╔╝ █████╗  ██████╔╝██║   ██║ ╚███╔╝ 
echo     ███╔╝  ██╔══╝  ██╔══██╗██║   ██║ ██╔██╗ 
echo    ███████╗███████╗██║  ██║╚██████╔╝██╔╝ ██╗
echo    ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo         Iniciando ZEROX v2.0...
echo.

REM Buscar Python
python --version >nul 2>&1 && set PYTHON=python && goto :run
python3 --version >nul 2>&1 && set PYTHON=python3 && goto :run
py --version >nul 2>&1 && set PYTHON=py && goto :run

REM Si no encuentra Python
echo ❌ ERROR: Python no encontrado
echo.
echo Ejecuta primero INSTALAR.bat
echo.
pause
exit

:run
REM Ejecutar ZEROX
%PYTHON% main.py

REM Si hay error
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR al ejecutar ZEROX
    echo.
    echo Posibles soluciones:
    echo 1. Ejecuta INSTALAR.bat
    echo 2. Verifica que Python esté instalado
    echo.
)

pause