@echo off
REM Windows wrapper for quick-test.py
python "%~dp0quick-test.py" %*
if %errorlevel% neq 0 (
    echo.
    echo Tests failed. Press any key to exit.
    pause >nul
    exit /b %errorlevel%
)
echo.
pause
