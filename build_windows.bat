@echo off
REM Build script for Intel HEX Viewer on Windows
REM This script creates a standalone Windows executable using PyInstaller

echo ======================================
echo Intel HEX Viewer - Windows Build Script
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "hex_viewer.py" (
    echo ERROR: hex_viewer.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Installing/upgrading PyInstaller...
python -m pip install --upgrade pyinstaller

echo Installing project dependencies...
python -m pip install -r requirements.txt

echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo Building Windows executable...
pyinstaller --onefile ^
    --windowed ^
    --name "IntelHexViewer" ^
    --add-data "examples;examples" ^
    --hidden-import "intelhex" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    --collect-all "intelhex_viewer" ^
    hex_viewer.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Build completed successfully!
echo.
echo Executable location: dist\IntelHexViewer.exe
echo File size: 
for %%I in (dist\IntelHexViewer.exe) do echo %%~zI bytes

echo.
echo Testing executable...
dist\IntelHexViewer.exe --version
if %errorlevel% neq 0 (
    echo WARNING: Executable test failed
) else (
    echo Executable test passed!
)

echo.
echo ======================================
echo Build Summary:
echo ======================================
echo - Executable: dist\IntelHexViewer.exe
echo - Size: 
for %%I in (dist\IntelHexViewer.exe) do echo   %%~zI bytes
echo - Platform: Windows (x64)
echo - Python Version: 
python --version
echo ======================================
echo.
echo To distribute: Copy dist\IntelHexViewer.exe to target systems
echo To test: Run dist\IntelHexViewer.exe examples\sample.hex
echo.

pause 