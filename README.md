# Intel HEX Viewer

A comprehensive GUI application for viewing and analyzing Intel HEX files with advanced features including C structure parsing, symbol navigation, and customizable display options.

## Features

- **Intel HEX File Support**: Load and view Intel HEX files with hex and ASCII representation
- **Symbol Navigation**: Load map files and header files to navigate to specific symbols
- **C Structure Parsing**: Parse C structure definitions and interpret memory values
- **Customizable Display**: Configure bytes per row (1-64)
- **Precise Highlighting**: Highlight specific memory bytes when jumping to symbols
- **Export Options**: Export data as CSV or binary files
- **Endianness Support**: Little and Big Endian interpretation
- **Search Functionality**: Search for ASCII or HEX values
- **Memory Statistics**: View memory usage and address ranges

## Building Portable Binaries

### Prerequisites

- Python 3.6 or higher
- tkinter (usually included with Python)
- pip (Python package manager)

### Windows Binary

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Build the binary**:
   ```cmd
   # Double-click build_windows.bat or run from command prompt:
   build_windows.bat
   ```

3. **Output**: `dist/windows/IntelHexViewer.exe`

### Linux/Ubuntu Binary

1. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   ```

2. **Make build script executable and run**:
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

3. **Output**: `dist/linux/IntelHexViewer`

### Manual Build (Any Platform)

If the automated scripts don't work, you can build manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Create binary
pyinstaller --onefile --windowed --name=IntelHexViewer hex_viewer_full.py
```

## Usage

### Running from Source
```bash
python hex_viewer_full.py
```

### Running Binary
- **Windows**: Double-click `IntelHexViewer.exe`
- **Linux**: `./IntelHexViewer`

### Basic Workflow

1. **Load HEX File**: File → Open HEX File
2. **Load Symbols** (optional): File → Load Map File or Load Header File
3. **Navigate**: Click on symbols in the left panel to jump to their locations
4. **Parse Structures**: Tools → Parse C Structure to interpret memory as C structures
5. **Configure Display**: View → Set Bytes Per Row to customize layout

### C Structure Parsing Example

```c
struct firmware_header {
    uint32_t magic;
    uint16_t version;
    uint16_t flags;
    uint32_t data_offset;
    uint32_t data_size;
    uint8_t reserved[8];
    char name[16];
};
```

1. Tools → Parse C Structure
2. Enter structure address (e.g., `0x1000`)
3. Paste structure definition
4. Click "View Values" to see interpreted values
5. Click "Parse & Apply" to show values in main hex view

## File Structure

```
intelhex/
├── hex_viewer_full.py      # Main application
├── requirements.txt        # Python dependencies
├── build_binary.py        # Cross-platform build script
├── build_windows.bat      # Windows build script
├── build_linux.sh         # Linux build script
├── README.md              # This file
└── dist/                  # Generated binaries
    ├── windows/
    │   └── IntelHexViewer.exe
    └── linux/
        └── IntelHexViewer
```

## Dependencies

- **intelhex**: For parsing Intel HEX files
- **tkinter**: For GUI (included with Python)
- **PyInstaller**: For creating portable binaries

## Supported File Formats

- **Intel HEX**: `.hex`, `.ihx` files
- **Map Files**: `.map`, `.txt` files with address/symbol pairs
- **Header Files**: `.h`, `.hpp` files with C structure definitions
- **Export**: `.csv`, `.bin` files

## Platform Support

- **Windows**: 7, 8, 10, 11 (32-bit and 64-bit)
- **Linux**: Ubuntu 16.04+, Debian 9+, CentOS 7+, and other distributions
- **macOS**: 10.12+ (build with same process as Linux)

## Binary Size

- **Windows**: ~15-20 MB
- **Linux**: ~20-25 MB

## Troubleshooting

### Windows
- If you get "Python not found": Install Python from python.org
- If you get permission errors: Run as Administrator
- If tkinter is missing: Reinstall Python with "tcl/tk and IDLE" option

### Linux
- If you get "python3 not found": `sudo apt install python3`
- If you get "tkinter not found": `sudo apt install python3-tk`
- If you get permission errors: `chmod +x build_linux.sh`

### General
- If PyInstaller fails: Try `pip install --upgrade pyinstaller`
- If binary is too large: Remove `--onefile` flag to create a directory instead
- If binary won't run: Check if all dependencies are included

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Feel free to submit issues and pull requests for improvements and bug fixes. 