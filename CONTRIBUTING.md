# Contributing to Intel HEX Viewer

We welcome contributions to the Intel HEX Viewer project! This document provides guidelines for contributing to make the process smooth and effective for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

We are committed to fostering a welcoming and inclusive community. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature/fix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.6 or higher
- tkinter (usually included with Python)
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/intelhex-viewer.git
cd intelhex-viewer

# Install dependencies
pip install -r requirements.txt

# Run the application
python hex_viewer.py
```

### Optional Development Tools

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Type checking
mypy src/

# Code formatting
black src/

# Linting
flake8 src/
```

## Project Structure

The project is organized into modular components:

```
intelhex-viewer/
├── src/                    # Main source code
│   ├── __init__.py        # Package initialization
│   ├── main_app.py        # Main application class
│   ├── hex_parser.py      # Intel HEX file handling
│   ├── structure_parser.py # C structure parsing
│   ├── symbol_manager.py  # Symbol/tag management
│   └── gui_components.py  # GUI dialogs and widgets
├── hex_viewer.py          # Main entry point
├── hex_viewer_full.py     # Legacy monolithic version
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── CONTRIBUTING.md       # This file
├── LICENSE               # MIT license
└── build/                # Build scripts and configs
    ├── build_windows.bat
    ├── build_linux.sh
    └── build_binary.py
```

### Module Responsibilities

- **`hex_parser.py`**: Intel HEX file loading, parsing, and data management
- **`structure_parser.py`**: C structure definition parsing and memory interpretation
- **`symbol_manager.py`**: Symbol/tag loading from map files and headers
- **`gui_components.py`**: Reusable GUI dialogs and widgets
- **`main_app.py`**: Main application coordination and GUI layout

## Coding Standards

### Python Style

We follow PEP 8 with these specific guidelines:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Docstrings**: Google style docstrings for all public functions and classes
- **Type hints**: Use type hints for function parameters and return values
- **Imports**: Organize imports in this order:
  1. Standard library
  2. Third-party packages
  3. Local modules

### Example Code Style

```python
from typing import List, Optional, Dict
import tkinter as tk
from intelhex import IntelHex

class ExampleClass:
    """
    Brief description of the class.
    
    Longer description with more details about the purpose
    and usage of the class.
    
    Attributes:
        attribute_name (type): Description of the attribute
    """
    
    def __init__(self, parameter: str) -> None:
        """
        Initialize the class.
        
        Args:
            parameter (str): Description of the parameter
        """
        self.attribute_name = parameter
    
    def public_method(self, data: List[int]) -> Optional[Dict[str, int]]:
        """
        Brief description of what the method does.
        
        Args:
            data (List[int]): Description of the parameter
            
        Returns:
            Optional[Dict[str, int]]: Description of return value
            
        Raises:
            ValueError: When data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        return {"result": sum(data)}
    
    def _private_method(self) -> None:
        """Private methods also need docstrings."""
        pass
```

### Documentation Requirements

- **All public classes and functions** must have docstrings
- **Complex algorithms** should have inline comments
- **Module docstrings** should explain the module's purpose
- **Type hints** are required for all function signatures

### GUI Guidelines

- Use **descriptive variable names** for widgets
- **Separate layout logic** from business logic
- **Handle exceptions gracefully** with user-friendly error messages
- **Follow accessibility guidelines** (proper tab order, keyboard shortcuts)

## Submitting Changes

### Branch Naming

Use descriptive branch names:

- `feature/structure-parsing-improvements`
- `bugfix/memory-leak-in-parser`
- `docs/update-contributing-guide`

### Commit Messages

Write clear, descriptive commit messages:

```
Add support for 64-bit address parsing

- Extend hex parser to handle 64-bit addresses
- Update structure parser for larger address spaces
- Add tests for 64-bit address edge cases

Fixes #42
```

### Pull Request Process

1. **Update documentation** if your changes affect user-facing functionality
2. **Add tests** for new functionality
3. **Update version numbers** if applicable
4. **Ensure all tests pass**
5. **Write a clear PR description** explaining:
   - What changes were made
   - Why they were made
   - How to test them

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] New tests added for new functionality

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Additional Notes
Any additional information that reviewers should know
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_hex_parser.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

- **Unit tests** for individual functions and classes
- **Integration tests** for component interactions
- **GUI tests** for user interface components (when possible)
- **Edge case testing** for error conditions

### Test Structure

```python
import unittest
from src.hex_parser import HexDataParser

class TestHexDataParser(unittest.TestCase):
    """Test cases for HexDataParser class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = HexDataParser()
    
    def test_load_valid_hex_file(self):
        """Test loading a valid hex file."""
        # Test implementation here
        pass
    
    def test_load_invalid_hex_file(self):
        """Test error handling for invalid hex files."""
        # Test implementation here
        pass
```

## Documentation

### Code Documentation

- **Docstrings** for all public APIs
- **Inline comments** for complex logic
- **Type hints** for better IDE support

### User Documentation

- **README.md** for project overview and quick start
- **Feature documentation** in docs/ directory
- **API documentation** generated from docstrings

### Documentation Style

- Use **clear, concise language**
- **Include examples** for complex features
- **Keep documentation up-to-date** with code changes

## Getting Help

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Code Reviews**: Participate in code review discussions

## Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **Git commit history** as the permanent record

Thank you for contributing to Intel HEX Viewer! 