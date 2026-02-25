@echo off
echo Desinstalando versiones conflictivas de PyTorch...
pip uninstall -y torch torchvision torchaudio ultralytics

echo Instalando PyTorch version CPU (Mas estable para Windows)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo Reinstalando Ultralytics...
pip install ultralytics

echo.
echo Reparacion completada. Intenta ejecutar run_app.bat de nuevo.
pause
