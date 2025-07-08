@echo off
echo Intel HEX Viewer Binary Builder for Windows
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

REM Create binary
echo Creating Windows binary...
python -m PyInstaller --onefile --windowed --name=IntelHexViewer --distpath=dist/windows hex_viewer_full.py
if %errorlevel% neq 0 (
    echo Error: Failed to create binary
    pause
    exit /b 1
)

REM Success
echo.
echo Build completed successfully!
echo Binary location: dist/windows/IntelHexViewer.exe
echo.

REM Show binary size
for %%A in (dist/windows/IntelHexViewer.exe) do (
    set /a size_mb=%%~zA/1024/1024
    echo Binary size: !size_mb! MB
)

pause 