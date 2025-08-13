@echo off
REM ================================================================================
REM                    INSTALADOR ÚNICO DE ZEROX v2.0
REM                         SIMPLE Y EFECTIVO
REM ================================================================================

REM Mantener ventana abierta
if "%1"=="" (
    cmd /k "%~f0" NO_CERRAR
    exit
)

cd /d "%~dp0"
color 0A
title ZEROX - Instalador

cls
echo.
echo    ███████╗███████╗██████╗  ██████╗ ██╗  ██╗
echo    ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗╚██╗██╔╝
echo      ███╔╝ █████╗  ██████╔╝██║   ██║ ╚███╔╝ 
echo     ███╔╝  ██╔══╝  ██╔══██╗██║   ██║ ██╔██╗ 
echo    ███████╗███████╗██║  ██║╚██████╔╝██╔╝ ██╗
echo    ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo              INSTALADOR v2.0
echo         LA IA QUE TE HACE MILLONARIO
echo.
echo ==================================================
echo.
pause

REM Buscar Python
echo.
echo Buscando Python...

python --version >nul 2>&1 && set PYTHON=python && goto :found
python3 --version >nul 2>&1 && set PYTHON=python3 && goto :found
py --version >nul 2>&1 && set PYTHON=py && goto :found

REM Python no encontrado
echo.
echo ❌ Python no encontrado
echo.
echo Descarga Python de: https://www.python.org
echo IMPORTANTE: Marca "Add Python to PATH"
echo.
pause
exit

:found
echo ✅ Python encontrado
echo.

REM Instalar dependencias
echo ==================================================
echo INSTALANDO ZEROX (5-10 minutos)
echo ==================================================
echo.

REM Actualizar pip
echo [1/4] Actualizando pip...
%PYTHON% -m pip install --upgrade pip --quiet

REM Limpiar conflictos
echo [2/4] Limpiando conflictos...
%PYTHON% -m pip uninstall PyQt5 matplotlib -y >nul 2>&1

REM Instalar todo
echo [3/4] Instalando componentes...
%PYTHON% -m pip install -r requirements.txt

REM Crear carpetas
echo [4/4] Creando estructura...
if not exist "data\library" mkdir "data\library"
if not exist "logs" mkdir "logs"
if not exist "config" mkdir "config"

REM Crear lanzador
echo @echo off > ZEROX.bat
echo cd /d "%~dp0" >> ZEROX.bat
echo %PYTHON% main.py >> ZEROX.bat
echo pause >> ZEROX.bat

REM Finalizado
cls
echo.
echo ==================================================
echo         ¡INSTALACIÓN COMPLETADA!
echo ==================================================
echo.
echo ✅ ZEROX instalado correctamente
echo.
echo CÓMO USAR:
echo 1. Ejecuta ZEROX.bat
echo 2. Configura tus API Keys de Bitget
echo 3. ¡Empieza a ganar dinero!
echo.
echo ==================================================
echo.
echo ¿Ejecutar ZEROX ahora? (S/N)
choice /c SN /n

if %errorlevel%==1 (
    start ZEROX.bat
)

echo.
pause