@echo off
REM Windows wrapper for setup.py
echo Running NocoDB Simple Client setup...
python "%~dp0setup.py" %*
if %errorlevel% neq 0 (
    echo.
    echo Setup failed. Press any key to exit.
    pause >nul
    exit /b %errorlevel%
)
echo.
echo Setup completed successfully!
pause
