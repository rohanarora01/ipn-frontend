@echo off
cd /d "%~dp0"
python scripts/save_to_github.py %1
pause
