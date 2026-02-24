@echo off
cd /d "%~dp0"
python scripts/fix_save.py %1
pause
