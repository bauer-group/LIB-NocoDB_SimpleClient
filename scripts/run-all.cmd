@echo off
REM Windows wrapper for run-all.py
echo Running complete development validation...
echo.

python "%~dp0run-all.py" %*
set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo ✅ All checks completed successfully!
) else (
    echo ❌ Some checks failed. Please review the output above.
)

echo.
echo Press any key to exit...
pause >nul
exit /b %EXIT_CODE%