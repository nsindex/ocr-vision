@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
python ocr.py
echo.
timeout /t 3
