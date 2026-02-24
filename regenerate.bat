@echo off
echo ==========================================
echo   REGENERATE DOCUMENTATION FILES
echo ==========================================
echo.

REM Detect changed files and regenerate
cd /d "%~dp0"
python scripts/regenerate_single_file.py

echo.
echo ==========================================
echo   NOW COMMIT THE REGENERATED FILES:
echo ==========================================
echo.
echo   git add public/docs/
echo   git commit -m "Regenerated original docs"
echo   git push origin main
echo.
pause
