#!/usr/bin/env python3
"""
Build script for creating portable binaries of the Intel HEX Viewer
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, error_msg="Command failed"):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {cmd}")
        if result.stdout:
            print(f"  Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {error_msg}: {cmd}")
        print(f"  Error: {e.stderr}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    return run_command("pip install -r requirements.txt", "Failed to install dependencies")

def create_binary():
    """Create the portable binary using PyInstaller"""
    print(f"Creating binary for {platform.system()}...")
    
    # PyInstaller options
    options = [
        "--onefile",  # Create a single executable file
        "--windowed",  # No console window (for GUI app)
        "--name=IntelHexViewer",  # Name of the executable
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",  # Icon if available
        "--add-data=README.md;." if os.path.exists("README.md") else "",  # Include README
        "hex_viewer_full.py"  # Main script
    ]
    
    # Filter out empty options
    options = [opt for opt in options if opt]
    
    cmd = "pyinstaller " + " ".join(options)
    return run_command(cmd, "Failed to create binary")

def main():
    """Main build process"""
    print("Intel HEX Viewer Binary Builder")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create binary
    if not create_binary():
        sys.exit(1)
    
    # Success message
    print()
    print("Build completed successfully!")
    print(f"Binary location: dist/IntelHexViewer{'.exe' if platform.system() == 'Windows' else ''}")
    print()
    
    # Show binary size
    binary_name = "IntelHexViewer.exe" if platform.system() == "Windows" else "IntelHexViewer"
    binary_path = os.path.join("dist", binary_name)
    if os.path.exists(binary_path):
        size_mb = os.path.getsize(binary_path) / (1024 * 1024)
        print(f"Binary size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main() 