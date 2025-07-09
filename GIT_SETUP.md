# Git Setup and Configuration Guide

This document explains the Git configuration files and how to use them effectively with the Intel HEX Viewer project.

## 📁 Git Files Overview

### Core Git Files

#### `.gitignore`
- **Purpose**: Specifies files and directories that Git should ignore
- **Contents**: 
  - Python build artifacts (`__pycache__`, `*.pyc`, `dist/`, `build/`)
  - IDE files (`.vscode/`, `.idea/`, etc.)
  - OS-specific files (`.DS_Store`, `Thumbs.db`)
  - Virtual environments (`venv/`, `.env`)
  - Project-specific exclusions (user HEX files, but keeps examples)

#### `.gitattributes`
- **Purpose**: Defines attributes for paths in the repository
- **Key Features**:
  - Automatic line ending normalization (`text=auto`)
  - Explicit LF line endings for source code
  - CRLF line endings for Windows batch files
  - Binary file detection
  - Language detection for GitHub
  - Export-ignore for distribution files

### Code Quality Files

#### `.pre-commit-config.yaml`
- **Purpose**: Automated code quality checks before commits
- **Features**:
  - Code formatting (black, isort)
  - Linting (flake8, pydocstyle)
  - Security checks (bandit)
  - Type checking (mypy)
  - Documentation checks
  - Markdown and YAML formatting

#### `.flake8`
- **Purpose**: Python linting configuration
- **Configuration**:
  - Max line length: 88 characters
  - Compatible with black formatter
  - Google-style docstrings
  - Complexity limits

### GitHub Integration

#### `.github/workflows/ci.yml`
- **Purpose**: Continuous Integration/Continuous Deployment
- **Features**:
  - Multi-platform testing (Windows, Linux, macOS)
  - Multiple Python versions (3.8-3.11)
  - Code quality checks
  - Automated building and testing
  - Release automation

#### `.github/ISSUE_TEMPLATE/`
- **Purpose**: Standardized issue reporting
- **Templates**:
  - `bug_report.yml`: Bug reports with detailed information
  - `feature_request.yml`: Feature requests with use cases

#### `.github/PULL_REQUEST_TEMPLATE.md`
- **Purpose**: Standardized pull request format
- **Features**:
  - Change type classification
  - Testing checklist
  - Code quality requirements
  - Documentation requirements

## 🚀 Getting Started

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/intel-hex-viewer.git
cd intel-hex-viewer

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Pre-commit Setup (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (optional)
pre-commit run --all-files
```

### 3. Development Workflow

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# ...

# The pre-commit hooks will automatically run
git add .
git commit -m "feat: add new feature"

# Push to your fork
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

## 🔧 Code Quality Tools

### Manual Code Quality Checks

```bash
# Format code
black intelhex_viewer/ tests/

# Sort imports
isort intelhex_viewer/ tests/

# Check linting
flake8 intelhex_viewer/ tests/

# Type checking
mypy intelhex_viewer/

# Run tests
pytest

# Security check
bandit -r intelhex_viewer/
```

### Pre-commit Hooks

The pre-commit hooks will automatically run these checks before each commit:

1. **File Checks**: Trailing whitespace, file endings, merge conflicts
2. **Python Formatting**: Black code formatting, isort import sorting
3. **Linting**: Flake8 style checking, pydocstyle documentation
4. **Security**: Bandit security scanning
5. **Type Checking**: MyPy type validation
6. **Documentation**: Markdown linting

## 📋 Best Practices

### Git Workflow

1. **Branch Naming**:
   - `feature/description` - New features
   - `bugfix/description` - Bug fixes
   - `hotfix/description` - Critical fixes
   - `docs/description` - Documentation updates

2. **Commit Messages**:
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
   - Keep first line under 50 characters
   - Provide detailed description in body if needed

3. **Pull Requests**:
   - Fill out the PR template completely
   - Ensure all checks pass
   - Add screenshots for UI changes
   - Link related issues

### Code Quality

1. **Before Committing**:
   - Run tests: `pytest`
   - Check formatting: `black --check intelhex_viewer/`
   - Verify imports: `isort --check intelhex_viewer/`
   - Check linting: `flake8 intelhex_viewer/`

2. **Documentation**:
   - Add docstrings to all public functions
   - Update README for new features
   - Add examples for complex functionality

3. **Testing**:
   - Write unit tests for new features
   - Ensure good test coverage
   - Test on multiple platforms when possible

## 🔍 Troubleshooting

### Common Issues

1. **Pre-commit Failures**:
   ```bash
   # Skip pre-commit for emergency commits
   git commit -m "emergency fix" --no-verify
   
   # Fix issues and recommit
   pre-commit run --all-files
   git add .
   git commit -m "fix: resolve code quality issues"
   ```

2. **Line Ending Issues**:
   ```bash
   # Normalize line endings
   git add --renormalize .
   git commit -m "normalize line endings"
   ```

3. **Large Files**:
   ```bash
   # Check file sizes
   git ls-files | xargs ls -la | sort -k5 -n -r | head -20
   
   # Remove large files from history (if needed)
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch large-file.bin' --prune-empty --tag-name-filter cat -- --all
   ```

### Configuration Updates

1. **Update Pre-commit Hooks**:
   ```bash
   pre-commit autoupdate
   pre-commit run --all-files
   ```

2. **Update Dependencies**:
   ```bash
   pip-compile requirements.in
   pip-compile requirements-dev.in
   ```

## 🛡️ Security

### Sensitive Information

- Never commit API keys, passwords, or credentials
- Use `.env` files for local configuration (already in `.gitignore`)
- Be careful with sample files - ensure no sensitive data

### Security Checks

- Bandit runs automatically in pre-commit hooks
- GitHub Security Advisories are enabled
- Dependabot is configured for dependency updates

## 📚 Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [Pre-commit Documentation](https://pre-commit.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Code Quality Tools](https://realpython.com/python-code-quality/)

---

This setup ensures consistent code quality, automated testing, and professional development practices for the Intel HEX Viewer project. 