# Monorepo Build Consolidation Plan

## Executive Summary

**Objective**: Consolidate duplicate build configurations (`requirements.txt` and `pyproject.toml`) from `backend/` and `banktransactions/` into a unified top-level monorepo structure.

**Estimated Time**: 2 weeks  
**Priority**: High  
**Risk Level**: Low  
**Dependencies**: None (can be implemented immediately)

## Current State Analysis

### Identified Issues

1. **Dependency Duplication**: Both modules maintain separate dependency lists with overlapping packages
2. **Version Inconsistencies**: Different versions of the same packages across modules
   - Flask: 3.0.2 (backend) vs 2.3.3 (banktransactions)
   - SQLAlchemy: 2.0.27 (banktransactions) vs 3.1.1 (backend via Flask-SQLAlchemy)
   - pytest: 8.0.2 (backend) vs 7.4.4 (banktransactions)
3. **Maintenance Overhead**: Need to update dependencies in multiple places
4. **Build Complexity**: Separate build processes for related components
5. **Tool Configuration Duplication**: Separate ruff, black, and pytest configurations

### Current File Structure
```
kanakku/
├── backend/
│   ├── requirements.txt (38 dependencies)
│   └── pyproject.toml (220 lines, comprehensive config)
├── banktransactions/
│   ├── requirements.txt (20 dependencies)
│   └── pyproject.toml (37 lines, minimal config)
└── frontend/ (separate Node.js ecosystem)
```

## Proposed Solution

### Target Architecture: Python Monorepo

Transform the project into a Python monorepo with:
- Single top-level `pyproject.toml` for all Python dependencies and tooling
- Simplified `requirements.txt` for development installation
- Unified tool configurations (ruff, black, pytest, mypy)
- Preserved module independence for deployment flexibility

### Target File Structure
```
kanakku/
├── pyproject.toml          # Unified build configuration
├── requirements.txt        # Simple development install
├── backend/               # Flask backend (no build files)
│   ├── app/
│   └── tests/
├── banktransactions/      # Bank processing (no build files)
│   ├── core/
│   ├── automation/
│   └── tests/
└── frontend/              # React frontend (unchanged)
    ├── package.json
    └── ...
```

## Implementation Plan

### Phase 1: Analysis and Preparation (Week 1, Days 1-2)

#### Day 1: Dependency Analysis
- [ ] **Audit Current Dependencies**
  - Create comprehensive dependency matrix
  - Identify version conflicts and compatibility issues
  - Document shared vs. module-specific dependencies
  - Analyze transitive dependencies

- [ ] **Backup Current Configuration**
  ```bash
  # Create backup directory
  mkdir -p .plan/backups/build-consolidation
  
  # Backup existing files
  cp backend/requirements.txt .plan/backups/build-consolidation/backend-requirements.txt
  cp backend/pyproject.toml .plan/backups/build-consolidation/backend-pyproject.toml
  cp banktransactions/requirements.txt .plan/backups/build-consolidation/banktransactions-requirements.txt
  cp banktransactions/pyproject.toml .plan/backups/build-consolidation/banktransactions-pyproject.toml
  ```

#### Day 2: Compatibility Testing
- [ ] **Test Current Setup**
  - Run all tests in both modules
  - Document current test execution commands
  - Verify linting and formatting tools work correctly
  - Record performance baselines

- [ ] **Environment Analysis**
  - Document Python version requirements
  - Check Docker configuration compatibility
  - Analyze CI/CD pipeline requirements

### Phase 2: Configuration Design (Week 1, Days 3-5)

#### Day 3: Dependency Consolidation
- [ ] **Create Unified Dependency List**
  - Merge dependencies from both modules
  - Resolve version conflicts (prefer latest stable)
  - Categorize dependencies (core, dev, optional)
  - Document rationale for version choices

- [ ] **Design Package Structure**
  - Define package namespace strategy
  - Plan import path changes (if any)
  - Design optional dependency groups
  - Plan for future module additions

#### Day 4: Tool Configuration Unification
- [ ] **Merge Tool Configurations**
  - Combine ruff configurations (rules, exclusions)
  - Merge black settings
  - Unify pytest configurations
  - Consolidate mypy settings

- [ ] **Path and Target Updates**
  - Update test paths to include both modules
  - Configure coverage for multiple packages
  - Set appropriate exclusion patterns
  - Define per-file rule overrides

#### Day 5: Build System Design
- [ ] **Create Top-Level pyproject.toml**
  - Define project metadata
  - Set up build system configuration
  - Configure optional dependencies
  - Add comprehensive tool configurations

- [ ] **Design Installation Strategy**
  - Plan development installation process
  - Design production deployment approach
  - Consider Docker build implications
  - Plan CI/CD integration

### Phase 3: Implementation (Week 2, Days 1-3)

#### Day 1: File Creation and Migration
- [ ] **Create Top-Level Configuration**
  - Create unified `pyproject.toml`
  - Create simplified `requirements.txt`
  - Validate configuration syntax
  - Test basic installation

- [ ] **Remove Module-Level Configurations**
  - Remove `backend/requirements.txt`
  - Remove `backend/pyproject.toml`
  - Remove `banktransactions/requirements.txt`
  - Remove `banktransactions/pyproject.toml`

#### Day 2: Testing and Validation
- [ ] **Test Installation Process**
  ```bash
  # Create fresh virtual environment
  python -m venv test-env
  source test-env/bin/activate
  
  # Install in development mode
  pip install -e .[dev]
  
  # Verify all dependencies are available
  python -c "import backend.app; import banktransactions.core"
  ```

- [ ] **Validate Tool Functionality**
  ```bash
  # Test linting
  ruff check .
  
  # Test formatting
  black --check .
  
  # Test type checking
  mypy backend/ banktransactions/
  
  # Run all tests
  pytest
  ```

#### Day 3: Integration Testing
- [ ] **Test Module Functionality**
  - Run backend application
  - Test banktransactions automation
  - Verify API endpoints work correctly
  - Test email processing functionality

- [ ] **Performance Validation**
  - Compare startup times
  - Measure test execution time
  - Verify memory usage patterns
  - Document any performance changes

### Phase 4: Infrastructure Updates (Week 2, Days 4-5)

#### Day 4: CI/CD Updates
- [ ] **Update CI/CD Pipelines**
  - Modify GitHub Actions workflows
  - Update linting pipeline (`lint-black.yml`)
  - Update testing pipeline (`test-backend.yml`)
  - Test automated builds

#### Day 5: Documentation and Cleanup
- [ ] **Update Documentation**
  - Update root `README.md` with new setup instructions
  - Update development documentation
  - Create migration guide for developers
  - Document new dependency management process

- [ ] **Final Validation**
  - Complete end-to-end testing
  - Verify all functionality works
  - Clean up temporary files
  - Archive backup files

## Detailed Configuration Specifications

### Unified pyproject.toml Structure

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kanakku"
version = "1.0.0"
description = "Kanakku - Personal Finance Management System"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    # Core Flask dependencies (latest versions)
    "Flask==3.0.2",
    "Flask-CORS==4.0.0",
    "Flask-SQLAlchemy==3.1.1",
    "Flask-Login==0.6.3",
    "Flask-JWT-Extended==4.6.0",
    "Flask-Mail==0.9.1",
    "Flask-Migrate==4.0.5",
    "Flask-Limiter==3.5.0",
    "Flask-WTF==1.2.1",
    "Flask-Session==0.5.0",
    
    # Database and caching
    "psycopg2-binary==2.9.9",
    "redis==5.0.1",
    
    # Core utilities
    "python-dotenv==1.0.1",
    "Werkzeug==3.0.1",
    "click==8.1.7",
    "itsdangerous==2.1.2",
    "Jinja2==3.1.3",
    "MarkupSafe==2.1.5",
    "requests==2.31.0",
    "certifi==2024.2.2",
    
    # Authentication and security
    "authlib==1.2.1",
    "flask-dance==7.0.0",
    "cryptography==42.0.2",
    "python-jose==3.3.0",
    
    # API documentation
    "flask-swagger-ui==4.11.1",
    "PyYAML==6.0.1",
    
    # AI and automation
    "google-genai>=1.14.0",
    
    # Background processing
    "rq==2.3.3",
    "rq-scheduler==0.14",
    
    # Production server
    "gunicorn==21.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest==8.0.2",
    "pytest-cov==4.1.0",
    "pytest-mock==3.12.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

### Dependency Resolution Strategy

| Package | Backend Version | Banktransactions Version | Unified Version | Rationale |
|---------|----------------|-------------------------|-----------------|-----------|
| Flask | 3.0.2 | 2.3.3 | 3.0.2 | Latest stable, better security |
| SQLAlchemy | 3.1.1 (via Flask-SQLAlchemy) | 2.0.27 | 3.1.1 | Consistent with Flask-SQLAlchemy |
| pytest | 8.0.2 | 7.4.4 | 8.0.2 | Latest stable, better features |
| cryptography | 41.0.7 | 42.0.2 | 42.0.2 | Latest for security fixes |
| gunicorn | 21.2.0 | 21.2.0 | 21.2.0 | Already consistent |

## Risk Assessment and Mitigation

### Low Risk Factors
- **Proven Approach**: Monorepo is a well-established pattern
- **Backward Compatibility**: No breaking changes to module APIs
- **Incremental Migration**: Can be done step-by-step
- **Easy Rollback**: Backup files allow quick reversion

### Medium Risk Factors
- **Import Path Changes**: May need to update some import statements
- **Docker Build Changes**: Dockerfile modifications required
- **CI/CD Updates**: Pipeline configurations need updates
- **Version Conflicts**: Some dependencies may have compatibility issues

### Mitigation Strategies

1. **Comprehensive Testing**
   - Test all functionality before and after migration
   - Validate in multiple environments (dev, staging, production)
   - Performance benchmarking to ensure no regressions

2. **Gradual Rollout**
   - Implement in development environment first
   - Test thoroughly before production deployment
   - Keep backup configurations for quick rollback

3. **Documentation and Communication**
   - Clear migration guide for team members
   - Update all relevant documentation
   - Communicate changes to all stakeholders

4. **Automated Validation**
   - Update CI/CD pipelines to catch issues early
   - Automated testing of all critical functionality
   - Performance monitoring to detect regressions

## Success Metrics

### Quantitative Goals
- [ ] **Dependency Reduction**: Eliminate duplicate dependencies (target: 15+ duplicates removed)
- [ ] **Configuration Consolidation**: Reduce from 4 config files to 2 (50% reduction)
- [ ] **Build Time**: Maintain or improve build times (target: <5% increase)
- [ ] **Test Coverage**: Maintain 100% test coverage throughout migration

### Qualitative Goals
- [ ] **Maintainability**: Single source of truth for dependencies
- [ ] **Consistency**: Unified tool configurations across all modules
- [ ] **Developer Experience**: Simplified setup and development process
- [ ] **Future-Proofing**: Easier to add new Python modules

## Post-Implementation Tasks

### Immediate (Week 3)
- [ ] **Team Training**: Update development setup documentation
- [ ] **CI/CD Monitoring**: Watch for any build or deployment issues
- [ ] **Performance Monitoring**: Track application performance metrics
- [ ] **Documentation Updates**: Ensure all docs reflect new structure

### Medium-term (Month 2)
- [ ] **Dependency Updates**: Establish regular dependency update process
- [ ] **Tool Configuration Optimization**: Fine-tune linting and formatting rules
- [ ] **Build Process Optimization**: Optimize for faster development cycles
- [ ] **New Module Integration**: Plan for adding future Python modules

### Long-term (Quarter 2)
- [ ] **Monorepo Tooling**: Consider advanced monorepo tools if needed
- [ ] **Workspace Management**: Evaluate workspace-based development tools
- [ ] **Cross-Module Optimization**: Identify opportunities for code sharing
- [ ] **Architecture Evolution**: Plan for future architectural improvements

## Troubleshooting Guide

### Common Issues and Solutions

1. **Import Errors After Migration**
   ```python
   # If imports fail, check Python path
   import sys
   sys.path.append('.')
   
   # Verify package installation
   pip list | grep kanakku
   ```

2. **Tool Configuration Conflicts**
   ```bash
   # Clear tool caches
   rm -rf .ruff_cache .pytest_cache .mypy_cache
   
   # Reinstall in development mode
   pip install -e .[dev]
   ```

3. **Docker Build Issues**
   ```dockerfile
   # Update Dockerfile COPY commands
   COPY pyproject.toml requirements.txt ./
   COPY backend/ ./backend/
   COPY banktransactions/ ./banktransactions/
   ```

4. **CI/CD Pipeline Failures**
   - Update workflow files to use root-level configurations
   - Ensure all required dependencies are installed
   - Check for path-related issues in test commands

## Dependencies and Prerequisites

### Technical Prerequisites
- Python 3.12+ installed
- Git access to the repository
- Docker and Docker Compose (for testing)
- Access to CI/CD pipeline configuration

### Team Prerequisites
- Coordination with ongoing development work
- Communication with DevOps team for CI/CD updates
- Notification to all developers about the change

### Environment Prerequisites
- Development environment for testing
- Staging environment for validation
- Backup of current production configuration

## Conclusion

This monorepo build consolidation plan provides a comprehensive approach to unifying the Python build configuration across the Kanakku project. The implementation is designed to be low-risk, incremental, and provide immediate benefits in terms of maintainability and consistency.

The plan addresses the current issues of dependency duplication and version inconsistencies while establishing a solid foundation for future development. With proper execution, this consolidation will result in:

- **Simplified Dependency Management**: Single source of truth for all Python dependencies
- **Improved Consistency**: Unified tool configurations and coding standards
- **Better Developer Experience**: Simplified setup and development process
- **Future-Proof Architecture**: Easy addition of new Python modules
- **Reduced Maintenance Overhead**: Single place to update dependencies and configurations

The estimated 2-week timeline is conservative and allows for thorough testing and validation at each step. The plan can be accelerated if needed, but the phased approach ensures minimal risk and maximum reliability. 