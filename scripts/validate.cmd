@echo off
REM Windows wrapper for validate.py
python "%~dp0validate.py" %*
if %errorlevel% neq 0 (
    echo.
    echo Validation failed. Press any key to exit.
    pause >nul
    exit /b %errorlevel%
)
echo.
pause
