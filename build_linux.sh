#!/bin/bash
echo "Intel HEX Viewer Binary Builder for Linux"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.6 or higher:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip python3-tk"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    echo "Try: pip3 install --user -r requirements.txt"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build *.spec

# Create binary
echo "Creating Linux binary..."
python3 -m PyInstaller --onefile --windowed --name=IntelHexViewer --distpath=dist/linux hex_viewer_full.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to create binary"
    exit 1
fi

# Success
echo ""
echo "Build completed successfully!"
echo "Binary location: dist/linux/IntelHexViewer"
echo ""

# Show binary size
if [ -f "dist/linux/IntelHexViewer" ]; then
    size_bytes=$(stat -c%s "dist/linux/IntelHexViewer")
    size_mb=$((size_bytes / 1024 / 1024))
    echo "Binary size: ${size_mb} MB"
    echo ""
    echo "To run the binary:"
    echo "  chmod +x dist/linux/IntelHexViewer"
    echo "  ./dist/linux/IntelHexViewer"
fi 