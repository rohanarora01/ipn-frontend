@echo off
echo ==========================================
echo   SAVE ALL CHANGED FILES
echo ==========================================
cd /d "%~dp0"
python scripts/save_all_changes.py
pause
