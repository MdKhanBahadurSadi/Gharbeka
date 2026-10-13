@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo GharBeka Automated Test Suite Runner
echo ===================================================

cd /d "%~dp0\.."

REM Determine python interpreter
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    set "PYTEST_EXE=.venv\Scripts\pytest.exe"
) else (
    set "PYTHON_EXE=python"
    set "PYTEST_EXE=pytest"
)

echo [1/2] Checking Python Environment...
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo [ERROR] Python not found or invalid!
    exit /b 1
)

echo [2/2] Running PyTest Suite...
"%PYTEST_EXE%" -v tests
if errorlevel 1 (
    echo.
    echo [FAILURE] Test suite encountered failures. Aborting.
    exit /b 1
)

echo.
echo ===================================================
echo [SUCCESS] All GharBeka automated tests passed!
echo ===================================================
exit /b 0
