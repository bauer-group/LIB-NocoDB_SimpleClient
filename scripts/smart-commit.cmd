@echo off
REM Smart commit script that handles pre-commit auto-fixes

if "%1"=="" (
    echo Usage: scripts\smart-commit.cmd "commit message"
    exit /b 1
)

echo Attempting commit...
git commit -m "%~1"

REM Check if commit failed (exit code 1 means pre-commit made changes)
if %ERRORLEVEL% equ 1 (
    echo Pre-commit made automatic fixes. Re-staging and committing...
    git add .
    git commit -m "%~1"

    if %ERRORLEVEL% equ 0 (
        echo ✅ Commit successful after auto-fixes!
    ) else (
        echo ❌ Commit failed even after auto-fixes. Please check the errors above.
        exit /b 1
    )
) else if %ERRORLEVEL% equ 0 (
    echo ✅ Commit successful!
) else (
    echo ❌ Commit failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
