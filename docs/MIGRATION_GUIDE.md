# Migration Guide: Individual Modules to Unified Monorepo

This guide helps developers transition from the old individual module structure to the new unified monorepo setup.

## Overview of Changes

Kanakku has been consolidated from individual modules with separate dependency management to a unified monorepo with centralized configuration.

### What Changed

#### Before (Individual Modules)
```
kanakku/
├── backend/
│   ├── requirements.txt          # Backend-specific dependencies
│   ├── pyproject.toml           # Backend-specific config
│   └── ...
├── banktransactions/
│   ├── requirements.txt          # Bank transaction dependencies
│   ├── pyproject.toml           # Bank transaction config
│   └── ...
└── shared/
    ├── requirements.txt          # Shared dependencies
    └── ...
```

#### After (Unified Monorepo)
```
kanakku/
├── pyproject.toml               # ✅ Unified config for all modules
├── requirements.txt             # ✅ Simple: -e .[dev]
├── backend/                     # ✅ No individual requirements
├── banktransactions/            # ✅ No individual requirements
└── shared/                      # ✅ No individual requirements
```

### Key Benefits

- **No version conflicts**: Single source of truth for dependencies
- **Simplified installation**: One command installs everything
- **Consistent tooling**: Unified linting, formatting, and testing
- **Easier maintenance**: Update dependencies in one place
- **Better CI/CD**: Streamlined build and test processes

## Migration Steps

### For Existing Developers

If you have an existing development environment:

1. **Backup your current setup** (optional):
   ```bash
   cp -r kanakku kanakku-backup
   ```

2. **Pull the latest changes**:
   ```bash
   cd kanakku
   git pull origin main
   ```

3. **Remove old virtual environments**:
   ```bash
   # Remove any existing virtual environments
   rm -rf backend/venv
   rm -rf banktransactions/venv
   rm -rf venv
   ```

4. **Create new unified virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

5. **Install unified dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

6. **Verify installation**:
   ```bash
   # Test backend imports
   python -c "import backend.app; print('Backend imports work!')"
   
   # Test banktransactions imports
   python -c "import banktransactions; print('Bank transactions imports work!')"
   
   # Run tests
   python -m pytest backend/tests/ -v
   ```

### For New Developers

Follow the [Development Setup Guide](DEVELOPMENT_SETUP.md) for the complete setup process.

## Command Changes

### Installation Commands

| Old Approach | New Approach |
|--------------|--------------|
| `cd backend && pip install -r requirements.txt` | `pip install -e ".[dev]"` |
| `cd banktransactions && pip install -r requirements.txt` | *(included in unified install)* |
| `cd shared && pip install -r requirements.txt` | *(included in unified install)* |

### Testing Commands

| Old Approach | New Approach |
|--------------|--------------|
| `cd backend && python -m pytest tests/` | `python -m pytest backend/tests/` |
| `cd banktransactions && python -m pytest tests/` | `python -m pytest banktransactions/tests/` |
| *(separate test runs)* | `./test.sh` *(runs all tests)* |

### Linting Commands

| Old Approach | New Approach |
|--------------|--------------|
| `cd backend && ruff check .` | `ruff check .` *(from project root)* |
| `cd banktransactions && ruff check .` | *(included in unified lint)* |
| *(separate lint runs)* | `./lint.sh` *(lints all modules)* |

## Configuration Changes

### Dependency Management

#### Before: Multiple requirements.txt files
```bash
# backend/requirements.txt
Flask==3.0.2
SQLAlchemy==2.0.25
# ... backend-specific deps

# banktransactions/requirements.txt  
requests==2.31.0
google-genai==1.14.0
# ... banktransactions-specific deps
```

#### After: Single pyproject.toml
```toml
# pyproject.toml (project root)
[project]
dependencies = [
    "Flask==3.0.2",
    "SQLAlchemy==2.0.25",
    "requests==2.31.0",
    "google-genai>=1.14.0",
    # ... all dependencies unified
]
```

### Tool Configuration

#### Before: Multiple configuration files
```bash
backend/pyproject.toml     # Backend-specific ruff/black config
banktransactions/setup.cfg # Bank transaction linting config
```

#### After: Unified configuration
```toml
# pyproject.toml (project root)
[tool.ruff]
# Unified linting rules for all modules

[tool.black]
# Unified formatting rules for all modules

[tool.pytest.ini_options]
# Unified test configuration
```

## Import Path Changes

### Backend Module Imports

The backend module now supports imports from any location:

#### Before
```python
# Only worked from within backend/ directory
from app.models import User
```

#### After
```python
# Works from project root or any location
from backend.app.models import User
```

### Path Setup

The unified setup automatically configures Python paths:

```python
# backend/__init__.py now includes path setup
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
```

## Development Workflow Changes

### Starting Development

#### Before
```bash
# Multiple terminal windows needed
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd banktransactions && source venv/bin/activate && pip install -r requirements.txt
```

#### After
```bash
# Single setup command
source venv/bin/activate && pip install -e ".[dev]"
```

### Running Services

#### Before
```bash
# Backend
cd backend && ./run-backend.sh

# Email workers (separate environment)
cd banktransactions && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd email_automation && python run_worker.py
```

#### After
```bash
# Backend (same as before)
cd backend && ./run-backend.sh

# Email workers (unified environment)
cd banktransactions/email_automation && python run_worker.py
```

## Troubleshooting Migration Issues

### Common Problems

1. **Import errors after migration**:
   ```bash
   # Solution: Reinstall in development mode
   pip install -e ".[dev]"
   ```

2. **Old virtual environments interfering**:
   ```bash
   # Solution: Remove all old venvs and create fresh one
   rm -rf */venv venv
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```

3. **IDE not recognizing imports**:
   ```bash
   # Solution: Point IDE to new virtual environment
   # VS Code: Ctrl+Shift+P -> "Python: Select Interpreter"
   # PyCharm: Settings -> Project -> Python Interpreter
   ```

4. **Tests failing after migration**:
   ```bash
   # Solution: Run from project root with full paths
   python -m pytest backend/tests/ banktransactions/tests/ -v
   ```

### Verification Steps

After migration, verify everything works:

```bash
# 1. Check imports work
python -c "import backend.app; import banktransactions; print('✅ Imports work')"

# 2. Run all tests
python -m pytest backend/tests/ banktransactions/tests/ -v

# 3. Check linting
ruff check .

# 4. Check formatting
black --check .

# 5. Start backend
cd backend && ./run-backend.sh
```

## Rollback Plan

If you need to rollback to the old structure:

1. **Checkout previous commit**:
   ```bash
   git log --oneline | grep "before consolidation"
   git checkout <commit-hash>
   ```

2. **Restore individual environments**:
   ```bash
   cd backend && python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

## Getting Help

If you encounter issues during migration:

1. Check the [Development Setup Guide](DEVELOPMENT_SETUP.md)
2. Review the [Troubleshooting section](DEVELOPMENT_SETUP.md#troubleshooting)
3. Check existing [GitHub issues](https://github.com/yourusername/kanakku/issues)
4. Create a new issue with:
   - Your operating system
   - Python version
   - Error messages
   - Steps you've tried

## Benefits After Migration

Once migrated, you'll enjoy:

- **Faster setup**: New developers can get started in minutes
- **Consistent environment**: No more "works on my machine" issues
- **Simplified CI/CD**: Single test and build process
- **Better dependency management**: No version conflicts
- **Unified tooling**: Same linting and formatting rules everywhere
- **Easier maintenance**: Update dependencies in one place

The migration effort is worth it for the long-term benefits to development velocity and code quality! 