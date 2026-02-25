@echo off
echo ===================================================
echo   HEALTH TRACKER - INSTALADOR SEGURO (CPU MODE)
echo ===================================================
echo.
echo 1. Limpiando instalaciones previas de PyTorch...
pip uninstall -y torch torchvision torchaudio ultralytics
echo.
echo 2. Instalando PyTorch (Version CPU - Compatible con todas las PC)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
echo.
echo 3. Instalando el resto de dependencias...
pip install -r requirements.txt
echo.
echo ===================================================
echo   INSTALACION COMPLETADA
echo   Iniciando aplicacion...
echo ===================================================
streamlit run app/main.py
pause
