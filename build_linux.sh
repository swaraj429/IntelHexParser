#!/bin/bash
# Build script for Intel HEX Viewer on Linux
# This script creates a standalone Linux executable using PyInstaller

echo "======================================"
echo "Intel HEX Viewer - Linux Build Script"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.6+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-tk"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip tkinter"
    echo "  Fedora: sudo dnf install python3 python3-pip python3-tkinter"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "hex_viewer.py" ]; then
    echo "ERROR: hex_viewer.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 using your package manager"
    exit 1
fi

echo "Installing/upgrading PyInstaller..."
python3 -m pip install --user --upgrade pyinstaller

echo "Installing project dependencies..."
python3 -m pip install --user -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build dist *.spec

echo "Building Linux executable..."
python3 -m PyInstaller \
    --onefile \
    --name "intel-hex-viewer" \
    --add-data "examples:examples" \
    --hidden-import "intelhex" \
    --hidden-import "tkinter" \
    --hidden-import "tkinter.ttk" \
    --hidden-import "tkinter.filedialog" \
    --hidden-import "tkinter.messagebox" \
    --collect-all "intelhex_viewer" \
    hex_viewer.py

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo "Build completed successfully!"
echo

# Get file size
if [ -f "dist/intel-hex-viewer" ]; then
    echo "Executable location: dist/intel-hex-viewer"
    echo "File size: $(stat -c%s dist/intel-hex-viewer) bytes"
    
    # Make executable
    chmod +x dist/intel-hex-viewer
    
    echo
    echo "Testing executable..."
    if ./dist/intel-hex-viewer --version; then
        echo "Executable test passed!"
    else
        echo "WARNING: Executable test failed"
    fi
else
    echo "ERROR: Executable not found at dist/intel-hex-viewer"
    exit 1
fi

echo
echo "======================================"
echo "Build Summary:"
echo "======================================"
echo "- Executable: dist/intel-hex-viewer"
echo "- Size: $(stat -c%s dist/intel-hex-viewer) bytes"
echo "- Platform: Linux ($(uname -m))"
echo "- Python Version: $(python3 --version)"
echo "======================================"
echo
echo "To distribute: Copy dist/intel-hex-viewer to target systems"
echo "To test: Run ./dist/intel-hex-viewer examples/sample.hex"
echo "To install system-wide: sudo cp dist/intel-hex-viewer /usr/local/bin/"
echo

# Optional: Create a .desktop file for GUI integration
read -p "Create desktop entry for GUI integration? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_FILE="intel-hex-viewer.desktop"
    CURRENT_DIR=$(pwd)
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Intel HEX Viewer
Comment=View and analyze Intel HEX files
Exec=$CURRENT_DIR/dist/intel-hex-viewer
Icon=applications-engineering
Terminal=false
Type=Application
Categories=Development;Engineering;
MimeType=application/x-intel-hex;
EOF
    
    echo "Desktop file created: $DESKTOP_FILE"
    echo "To install: cp $DESKTOP_FILE ~/.local/share/applications/"
fi

echo "Build completed successfully!" 