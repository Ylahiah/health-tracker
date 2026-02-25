@echo off
echo ========================================================
echo   SUBIDA AUTOMATICA A GITHUB
echo ========================================================
echo.
echo 1. Inicializando repositorio...
git init

echo.
echo 2. Agregando archivos...
git add .

echo.
echo 3. Creando commit inicial...
git commit -m "Subida inicial del Health Tracker"

echo.
echo 4. Configurando rama principal...
git branch -M main

echo.
echo ========================================================
echo   AHORA SIGUE ESTOS PASOS:
echo ========================================================
echo.
echo 1. Ve a https://github.com/new y crea un repositorio.
echo 2. Copia el comando que empieza con "git remote add origin..."
echo 3. Pegalo aqui abajo y presiona ENTER.
echo.
set /p remote_url="Pega el comando aqui: "
%remote_url%

echo.
echo Subiendo archivos a GitHub...
git push -u origin main

echo.
echo ¡LISTO! Tu codigo esta en GitHub.
pause
