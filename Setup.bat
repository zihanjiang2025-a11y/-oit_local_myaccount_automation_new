@echo off

py -3.12 -m venv .venv

call .venv\Scripts\activate.bat

pip install -r requirements.txt

python main.py setup

echo.
echo Setup complete.
pause