# Intel HEX Viewer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/contributors/intelhex-viewer)

A comprehensive, open-source GUI application for viewing and analyzing Intel HEX files with advanced features including C structure parsing, symbol navigation, and customizable display options.

**🎉 Now Open Source!** This project has been restructured into a modular, contributor-friendly codebase. We welcome contributions from the community!

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

## Quick Start

### Running from Source

```bash
# Clone the repository
git clone https://github.com/contributors/intelhex-viewer.git
cd intelhex-viewer

# Install dependencies
pip install -r requirements.txt

# Run the application
python hex_viewer.py
```

### Running Binary (Pre-built)
- **Windows**: Double-click `dist/windows/IntelHexViewer.exe`
- **Linux**: `./dist/linux/IntelHexViewer`

### Legacy Version
The original monolithic version is still available as `hex_viewer_full.py` for backward compatibility.

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

## Project Structure

The project has been restructured into a modular, maintainable architecture:

```
intelhex-viewer/
├── src/                      # 🔧 Core source code (modular design)
│   ├── __init__.py          # Package initialization
│   ├── main_app.py          # Main application coordinator
│   ├── hex_parser.py        # Intel HEX file operations
│   ├── structure_parser.py  # C structure parsing & interpretation
│   ├── symbol_manager.py    # Symbol/tag management
│   └── gui_components.py    # Reusable GUI components
├── hex_viewer.py            # 🚀 New modular entry point
├── hex_viewer_full.py       # 📜 Legacy monolithic version
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT license
├── CONTRIBUTING.md          # Contribution guidelines
├── README.md               # This file
├── build/                  # Build system
│   ├── build_windows.bat
│   ├── build_linux.sh
│   └── build_binary.py
└── dist/                   # Generated binaries
    ├── windows/
    │   └── IntelHexViewer.exe
    └── linux/
        └── IntelHexViewer
```

### 🏗️ Modular Architecture Benefits

- **🔍 Easy to Understand**: Each module has a clear, single responsibility
- **🛠️ Easy to Extend**: Add new features without touching existing code
- **🐛 Easy to Debug**: Isolated components make troubleshooting simpler
- **🤝 Contributor Friendly**: Clear separation makes it easy for new contributors
- **✅ Testable**: Each module can be unit tested independently

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

## 🤝 Contributing

We welcome contributions from the community! This project is designed to be contributor-friendly.

### 🚀 Quick Contribution Guide

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/intelhex-viewer.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes in the modular `src/` directory
5. **Test** your changes: `python hex_viewer.py`
6. **Commit** your changes: `git commit -m "Add amazing feature"`
7. **Push** to your fork: `git push origin feature/amazing-feature`
8. **Submit** a Pull Request

### 🎯 Areas Where We Need Help

- **🐛 Bug Fixes**: Report and fix issues
- **✨ New Features**: Hex analysis tools, export formats, UI improvements
- **📚 Documentation**: Code comments, user guides, examples
- **🧪 Testing**: Unit tests, integration tests, edge cases
- **🌍 Internationalization**: Multi-language support
- **🎨 UI/UX**: Design improvements, accessibility features

### 📋 Development Guidelines

- **Follow PEP 8** Python style guidelines
- **Add docstrings** to all public functions and classes
- **Include type hints** for better code clarity
- **Write tests** for new functionality
- **Update documentation** when adding features

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### 🏆 Contributors

We appreciate all contributors! Contributors will be recognized in the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Why Open Source?

We believe that open source software benefits everyone:
- **🔍 Transparency**: See exactly how the software works
- **🛡️ Security**: Community review improves security
- **🚀 Innovation**: Collective contributions drive innovation
- **🎓 Learning**: Great way to learn and improve coding skills 