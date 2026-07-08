@echo off

cd /d "%~dp0"

call .venv\Scripts\activate.bat

:run
cls
python main.py

echo.
echo ====================================
echo Program finished.
echo.
echo [R] Restart
echo [Q] Quit
echo ====================================

set /p choice=^> 

if /I "%choice%"=="R" goto run
if /I "%choice%"=="Q" goto end

echo Invalid option.
timeout /t 1 >nul
goto run

:end