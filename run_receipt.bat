@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
python ocr.py --mode receipt
echo.
timeout /t 3
