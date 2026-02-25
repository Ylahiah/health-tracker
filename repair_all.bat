@echo off
setlocal EnableDelayedExpansion
title Health Tracker Repair Tool

echo ===============================================================================
echo   HEALTH TRACKER - HERRAMIENTA DE REPARACION Y DIAGNOSTICO
echo ===============================================================================
echo.
echo   Este script solucionara el error [WinError 1114] reinstalando las librerias
echo   de Inteligencia Artificial en su version compatible (CPU).
echo.
echo   IMPORTANTE: Asegurate de tener instalado "Microsoft Visual C++ Redistributable"
echo   Si el error persiste despues de esto, necesitaras instalarlo desde:
echo   https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo ===============================================================================
echo.
pause

echo.
echo [1/5] Deteniendo procesos de Python...
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo.
echo [2/5] Limpiando instalaciones corruptas de IA...
pip uninstall -y ultralytics torch torchvision torchaudio numpy
pip cache purge

echo.
echo [3/5] Instalando librerias base...
:: Instalamos numpy<2 para evitar conflictos con algunas versiones de torch/pandas
pip install "numpy<2" 

echo.
echo [4/5] Instalando PyTorch (Version CPU Estable)...
:: Esta version NO requiere tarjeta grafica NVIDIA y es la mas compatible
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo [5/5] Instalando Ultralytics (YOLO) y dependencias...
pip install ultralytics

echo.
echo ===============================================================================
echo   REPARACION COMPLETADA
echo ===============================================================================
echo.
echo   Iniciando la aplicacion...
echo.

streamlit run app/main.py

pause
