#!/usr/bin/env python3
"""
Cross-platform build script for Intel HEX Viewer.

This script creates standalone executables using PyInstaller for Windows, Linux, and macOS.
It automatically detects the platform and applies appropriate build settings.

Usage:
    python build_binary.py                     # Build for current platform
    python build_binary.py --name "CustomName" # Build with custom name
    python build_binary.py --debug             # Build with debug info
    python build_binary.py --console           # Build with console window
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path


def get_platform_info():
    """Get platform-specific information."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        return {
            "name": "Windows",
            "executable_extension": ".exe",
            "python_cmd": "python",
            "pyinstaller_cmd": "pyinstaller",
            "path_separator": ";",
            "hidden_imports": [
                "intelhex",
                "tkinter",
                "tkinter.ttk",
                "tkinter.filedialog",
                "tkinter.messagebox",
                "tkinter.simpledialog",
                "intelhex_viewer",
                "intelhex_viewer.main_app",
                "intelhex_viewer.hex_parser",
                "intelhex_viewer.structure_parser",
                "intelhex_viewer.symbol_manager",
                "intelhex_viewer.gui_components"
            ]
        }
    elif system == "linux":
        return {
            "name": "Linux",
            "executable_extension": "",
            "python_cmd": "python3",
            "pyinstaller_cmd": "pyinstaller",
            "path_separator": ":",
            "hidden_imports": [
                "intelhex",
                "tkinter",
                "tkinter.ttk",
                "tkinter.filedialog",
                "tkinter.messagebox",
                "tkinter.simpledialog",
                "intelhex_viewer",
                "intelhex_viewer.main_app",
                "intelhex_viewer.hex_parser",
                "intelhex_viewer.structure_parser",
                "intelhex_viewer.symbol_manager",
                "intelhex_viewer.gui_components"
            ]
        }
    elif system == "darwin":
        return {
            "name": "macOS",
            "executable_extension": "",
            "python_cmd": "python3",
            "pyinstaller_cmd": "pyinstaller",
            "path_separator": ":",
            "hidden_imports": [
                "intelhex",
                "tkinter",
                "tkinter.ttk",
                "tkinter.filedialog",
                "tkinter.messagebox",
                "tkinter.simpledialog",
                "intelhex_viewer",
                "intelhex_viewer.main_app",
                "intelhex_viewer.hex_parser",
                "intelhex_viewer.structure_parser",
                "intelhex_viewer.symbol_manager",
                "intelhex_viewer.gui_components"
            ]
        }
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("Checking prerequisites...")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        python_version = result.stdout.strip()
        print(f"✓ Python: {python_version}")
    except subprocess.CalledProcessError:
        print("✗ Python is not available")
        return False
    
    # Check if we're in the correct directory
    if not Path("hex_viewer.py").exists():
        print("✗ hex_viewer.py not found - run this script from the project root")
        return False
    
    if not Path("intelhex_viewer").exists():
        print("✗ intelhex_viewer package not found")
        return False
    
    print("✓ Project structure is valid")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    try:
        # Install PyInstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"], 
                      check=True)
        print("✓ PyInstaller installed/updated")
        
        # Install project dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✓ Project dependencies installed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    
    return True


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    paths_to_clean = ["build", "dist", "*.spec"]
    
    for path in paths_to_clean:
        if path.endswith("*.spec"):
            # Remove spec files
            for spec_file in Path(".").glob("*.spec"):
                spec_file.unlink()
                print(f"✓ Removed {spec_file}")
        else:
            # Remove directories
            if Path(path).exists():
                shutil.rmtree(path)
                print(f"✓ Removed {path}/")


def build_executable(platform_info, app_name, debug=False, console=False):
    """Build the executable using PyInstaller."""
    print(f"Building executable for {platform_info['name']}...")
    
    # Prepare PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", app_name,
        "--add-data", f"examples{os.pathsep}examples",
        "--collect-all", "intelhex_viewer",
    ]
    
    # Add hidden imports
    for import_name in platform_info["hidden_imports"]:
        cmd.extend(["--hidden-import", import_name])
    
    # Platform-specific options
    if platform_info["name"] == "Windows":
        if not console:
            cmd.append("--windowed")
    elif platform_info["name"] == "macOS":
        if not console:
            cmd.append("--windowed")
    
    # Debug options
    if debug:
        cmd.append("--debug")
        cmd.append("--console")
    
    # Add the main script
    cmd.append("hex_viewer.py")
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print("PyInstaller output:")
            print(result.stdout)
        print("✓ Build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        if e.stderr:
            print("Error output:")
            print(e.stderr)
        return False


def test_executable(platform_info, app_name):
    """Test the built executable."""
    print("Testing executable...")
    
    executable_name = app_name + platform_info["executable_extension"]
    executable_path = Path("dist") / executable_name
    
    if not executable_path.exists():
        print(f"✗ Executable not found: {executable_path}")
        return False
    
    # Make executable on Unix systems
    if platform_info["name"] != "Windows":
        os.chmod(executable_path, 0o755)
    
    # Test version command
    try:
        result = subprocess.run([str(executable_path), "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Executable test passed")
            return True
        else:
            print(f"✗ Executable test failed (exit code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Executable test timed out")
        return False
    except Exception as e:
        print(f"✗ Executable test failed: {e}")
        return False


def get_file_size(filepath):
    """Get human-readable file size."""
    size = filepath.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build Intel HEX Viewer executable")
    parser.add_argument("--name", default="intel-hex-viewer", 
                       help="Name of the executable")
    parser.add_argument("--debug", action="store_true",
                       help="Build with debug information")
    parser.add_argument("--console", action="store_true",
                       help="Build with console window (Windows/macOS)")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Intel HEX Viewer - Cross-Platform Build Script")
    print("=" * 50)
    
    # Get platform information
    try:
        platform_info = get_platform_info()
        print(f"Platform: {platform_info['name']}")
        print(f"Architecture: {platform.machine()}")
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Build executable
    if not build_executable(platform_info, args.name, args.debug, args.console):
        return 1
    
    # Test executable
    if not test_executable(platform_info, args.name):
        print("Warning: Executable test failed, but build completed")
    
    # Show build summary
    executable_name = args.name + platform_info["executable_extension"]
    executable_path = Path("dist") / executable_name
    
    print("\n" + "=" * 50)
    print("Build Summary:")
    print("=" * 50)
    print(f"Platform: {platform_info['name']} ({platform.machine()})")
    print(f"Executable: {executable_path}")
    
    if executable_path.exists():
        print(f"Size: {get_file_size(executable_path)}")
    
    print(f"Python Version: {platform.python_version()}")
    print("=" * 50)
    print()
    print("Usage:")
    print(f"  {executable_path} [file.hex]")
    print(f"  {executable_path} examples/sample.hex")
    print()
    print("Distribution:")
    print(f"  Copy {executable_path} to target systems")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 