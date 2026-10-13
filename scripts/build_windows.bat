@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo GharBeka - Windows Executable Packaging ^& Build Automation
echo =====================================================================

REM 1. Verify Windows OS Environment
if not "%OS%"=="Windows_NT" (
    echo [ERROR] This build script must be executed on Microsoft Windows.
    exit /b 1
)

cd /d "%~dp0\.."

REM 2. Identify Python and PyInstaller in virtualenv or system PATH
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    set "PIP_EXE=.venv\Scripts\pip.exe"
    set "PYINSTALLER_EXE=.venv\Scripts\pyinstaller.exe"
    set "PYTEST_EXE=.venv\Scripts\pytest.exe"
) else (
    set "PYTHON_EXE=python"
    set "PIP_EXE=pip"
    set "PYINSTALLER_EXE=pyinstaller"
    set "PYTEST_EXE=pytest"
)

echo [Step 1/7] Verifying Python Environment...
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo [ERROR] Python runtime could not be executed.
    exit /b 1
)

echo [Step 2/7] Checking Declared Project Dependencies...
"%PIP_EXE%" install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install or verify dependencies from requirements.txt.
    exit /b 1
)

echo [Step 3/7] Running Pre-Build Automated Test Suite...
call "%~dp0run_tests.bat"
if errorlevel 1 (
    echo [ERROR] Automated tests failed! Stopping release build to prevent packaging defective binary.
    exit /b 1
)

echo [Step 4/7] Ensuring Assets and Application Icons Exist...
if not exist "assets\icon.ico" (
    echo Generating application icons...
    "%PYTHON_EXE%" scripts\generate_icon.py
    if errorlevel 1 (
        echo [ERROR] Failed to generate application icons.
        exit /b 1
    )
)

echo [Step 5/7] Safely Cleaning Stale Build Artifacts...
if exist "build" (
    echo Removing stale build directory...
    rmdir /s /q "build"
)

echo [Step 6/7] Building Windows Executable via PyInstaller...
"%PYINSTALLER_EXE%" --clean --noconfirm GharBeka.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller packaging encountered an error.
    exit /b 1
)

echo [Step 7/7] Verifying Build Output Artifacts...
if not exist "dist\GharBeka.exe" (
    echo [ERROR] Expected release executable 'dist\GharBeka.exe' was not created!
    exit /b 1
)

if not exist "dist\GharBeka_onedir\GharBeka_diag.exe" (
    echo [WARNING] Diagnostic onedir executable was not found.
)

echo.
echo =====================================================================
echo [BUILD SUCCESSFUL]
echo Output Executables:
echo   - Standalone Release: %CD%\dist\GharBeka.exe
if exist "dist\GharBeka_onedir\GharBeka_diag.exe" (
echo   - Diagnostic Onedir:  %CD%\dist\GharBeka_onedir\GharBeka_diag.exe
)
echo =====================================================================
exit /b 0
