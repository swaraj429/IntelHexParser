# Changelog

All notable changes to the Intel HEX Viewer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete modular architecture with 5 focused modules
- Professional Google-style docstrings throughout
- Comprehensive type hints for all functions
- MIT license for open source distribution
- Contributing guidelines and documentation
- Examples directory with usage examples
- Test suite foundation with pytest
- Modern Python packaging with pyproject.toml
- Command-line interface with argparse
- Development requirements and tooling

### Changed
- Restructured from monolithic 672-line file to modular 5-module architecture
- Renamed src/ to intelhex_viewer/ for proper package naming
- Updated build scripts and moved to build/ directory
- Enhanced README with contribution guidelines
- Improved project structure following Python standards

### Fixed
- Proper error handling and cleanup
- Package imports and dependencies
- Build system compatibility

## [1.0.0] - 2024-01-15

### Added
- Intel HEX file loading and visualization
- Hex data display with customizable bytes per row (1-64)
- ASCII representation alongside hex values
- Symbol navigation via map file support
- C structure parsing and interpretation
- Memory location jumping with precise highlighting
- Search functionality for hex values and ASCII text
- Export capabilities (CSV and binary formats)
- Cross-platform support (Windows, Linux, macOS)
- PyInstaller binary building
- Comprehensive error handling

### Features
- **File Support**: 
  - Intel HEX files (.hex, .ihx)
  - Map files for symbol navigation
  - C header files for symbol extraction
  
- **Display Options**:
  - Configurable bytes per row (1-64)
  - Precise byte highlighting with brackets
  - Symbol overlay on hex display
  - Structure field visualization
  
- **Analysis Tools**:
  - C structure parser with endianness support
  - Symbol manager for navigation
  - Memory statistics
  - Search with hex/ASCII support
  
- **Export Options**:
  - CSV export with formatting
  - Binary export for external tools
  - Structure values export

### Technical Details
- Built with Python 3.6+ and tkinter
- Modular architecture for maintainability
- Comprehensive error handling
- Cross-platform compatibility
- Professional documentation standards

### Known Issues
- None at this time

## [0.1.0] - 2024-01-10

### Added
- Initial monolithic implementation
- Basic hex file viewing
- Map file symbol support
- Structure parsing prototype
- Export functionality

---

## Version History Summary

- **v1.0.0**: Complete professional implementation with all features
- **v0.1.0**: Initial working prototype

## Migration Guide

### From v0.1.0 to v1.0.0

The application has been completely restructured but maintains full backward compatibility:

1. **Entry Point**: Use `hex_viewer.py` instead of `main_gui.py`
2. **Module Structure**: Code is now organized in `intelhex_viewer/` package
3. **Installation**: Can now be installed as a proper Python package
4. **Features**: All existing features preserved and enhanced

### For Developers

If you were using the old monolithic structure:
- Use `from intelhex_viewer import *` for imports
- All functionality is preserved with improved organization
- See `examples/basic_usage.py` for programmatic usage 