@echo off
REM ================================================================================
REM                    CREAR ZEROX.EXE PROFESIONAL
REM ================================================================================

cd /d "%~dp0"
color 0A
title ZEROX - Creador de EXE

cls
echo.
echo    ███████╗███████╗██████╗  ██████╗ ██╗  ██╗
echo    ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗╚██╗██╔╝
echo      ███╔╝ █████╗  ██████╔╝██║   ██║ ╚███╔╝ 
echo     ███╔╝  ██╔══╝  ██╔══██╗██║   ██║ ██╔██╗ 
echo    ███████╗███████╗██║  ██║╚██████╔╝██╔╝ ██╗
echo    ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo         CREADOR DE EXE PROFESIONAL
echo.
echo ==================================================
echo.
echo Este proceso creará ZEROX.exe
echo Tardará aproximadamente 5-10 minutos
echo.
pause

REM Buscar Python
python --version >nul 2>&1 && set PYTHON=python && goto :create
python3 --version >nul 2>&1 && set PYTHON=python3 && goto :create
py --version >nul 2>&1 && set PYTHON=py && goto :create

echo ❌ Python no encontrado
pause
exit

:create
echo.
echo Instalando PyInstaller si es necesario...
%PYTHON% -m pip install pyinstaller pillow

echo.
echo Creando ZEROX.exe...
%PYTHON% crear_exe.py

echo.
echo ==================================================
echo.
echo Proceso completado. Busca ZEROX.exe en:
echo dist\ZEROX.exe
echo.
pause