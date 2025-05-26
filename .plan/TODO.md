# Kanakku Project TODO

## Post-Consolidation Tasks

Following the successful monorepo build consolidation, this document outlines the next steps and improvements for the Kanakku project.

## High Priority Issues

### 1. Email Automation Test Failures 🔴
**Status**: Critical - 17 failing tests  
**Impact**: Email automation functionality may be broken  
**Location**: `backend/tests/test_email_automation.py`

**Issue Description**:
- All failures show: `'NoneType' object has no attribute 'isoformat'`
- Affects email configuration creation, connection testing, and processing triggers
- Pre-existing issue (not caused by build consolidation)

**Failed Tests**:
- `TestEmailAutomationConfig::test_create_email_config_success`
- `TestEmailAutomationConfig::test_create_email_config_missing_required_fields`
- `TestEmailAutomationConfig::test_create_email_config_with_defaults`
- `TestEmailConnectionTesting::test_test_connection_missing_required_fields`
- `TestEmailProcessingTrigger::test_trigger_processing_success`
- And 12 more related tests

**Action Items**:
- [ ] Investigate the root cause of the `'NoneType' object has no attribute 'isoformat'` error
- [ ] Check email configuration model timestamp handling
- [ ] Review email automation service layer for null timestamp issues
- [ ] Fix the underlying issue causing timestamp problems
- [ ] Verify all email automation functionality works correctly
- [ ] Update tests if business logic has changed

**Estimated Effort**: 1-2 days

---

## Medium Priority Improvements

### 2. Code Quality - Linting Issues ✅
**Status**: ✅ COMPLETED  
**Impact**: Code style consistency  
**Location**: `banktransactions/` module

**Completed Actions**:
- ✅ Fixed dictionary key checking in `banktransactions/core/imap_client.py:159`
- ✅ Replaced `assert False` with `raise AssertionError()` in test files:
  - `banktransactions/tests/test_automation/test_deduplication.py:43`
  - `banktransactions/tests/test_automation/test_wrapper.py:50`
  - `banktransactions/tests/test_integration/test_direct.py:86`

**Result**: All linting checks now pass! 🎉

**Completed**: 2025-05-26

### 3. Import Path Issues 🟡
**Status**: Needs investigation  
**Impact**: Module import functionality  

**Issue Description**:
- Backend module has import path issues when imported directly
- Error: `ModuleNotFoundError: No module named 'app'` in `backend/app/accounts_bp/routes.py`
- Tests work correctly due to `pythonpath = ["backend"]` in pytest configuration

**Action Items**:
- [ ] Review import paths in backend module
- [ ] Ensure relative imports work correctly for standalone usage
- [ ] Consider updating import statements to use absolute paths
- [ ] Test module imports outside of pytest context
- [ ] Document proper import patterns for the monorepo structure

**Estimated Effort**: 1 day

---

## Low Priority Enhancements

### 4. Documentation Updates 📚
**Status**: Enhancement  
**Impact**: Developer experience  

**Action Items**:
- [ ] Update root `README.md` with new monorepo setup instructions
- [ ] Create/update development setup documentation
- [ ] Document the unified dependency management process
- [ ] Add migration guide for developers working with the old structure
- [ ] Update API documentation if affected by consolidation
- [ ] Document new testing procedures with unified configuration

**Estimated Effort**: 1 day

### 5. CI/CD Pipeline Optimization ⚙️
**Status**: Enhancement  
**Impact**: Build efficiency  

**Current Status**: CI/CD pipelines work with consolidated configuration

**Potential Improvements**:
- [ ] Review GitHub Actions workflows for optimization opportunities
- [ ] Consider caching strategies for the unified dependency installation
- [ ] Optimize test execution order for faster feedback
- [ ] Add dependency vulnerability scanning to CI pipeline
- [ ] Consider adding automated dependency updates (Dependabot)

**Estimated Effort**: 1-2 days

### 6. Performance Monitoring 📊
**Status**: Enhancement  
**Impact**: System reliability  

**Action Items**:
- [ ] Establish baseline performance metrics post-consolidation
- [ ] Monitor application startup times with unified dependencies
- [ ] Track test execution performance
- [ ] Monitor memory usage patterns
- [ ] Set up alerts for performance regressions

**Estimated Effort**: 1 day

---

## Future Considerations

### 7. Advanced Monorepo Tooling 🔧
**Status**: Future enhancement  
**Impact**: Developer productivity  

**Considerations**:
- [ ] Evaluate advanced monorepo tools (e.g., Nx, Rush, Lerna for Python equivalents)
- [ ] Consider workspace-based development tools
- [ ] Evaluate selective testing based on changed modules
- [ ] Consider build caching strategies

**Estimated Effort**: 2-3 days (research and implementation)

### 8. Cross-Module Code Sharing 🔄
**Status**: Future optimization  
**Impact**: Code maintainability  

**Opportunities**:
- [ ] Identify common code patterns between backend and banktransactions
- [ ] Extract shared utilities to the `shared/` module
- [ ] Standardize error handling patterns across modules
- [ ] Consider shared data models and validation logic

**Estimated Effort**: 1-2 weeks

### 9. Dependency Management Automation 🤖
**Status**: Future enhancement  
**Impact**: Maintenance efficiency  

**Action Items**:
- [ ] Set up automated dependency update process
- [ ] Implement dependency vulnerability scanning
- [ ] Create dependency update testing pipeline
- [ ] Establish dependency update review process

**Estimated Effort**: 1 week

---

## Completed ✅

### Monorepo Build Consolidation
- ✅ Created unified top-level `pyproject.toml`
- ✅ Created simplified top-level `requirements.txt`
- ✅ Removed duplicate module-level configuration files
- ✅ Resolved dependency version conflicts
- ✅ Unified tool configurations (ruff, black, pytest, mypy)
- ✅ Verified installation and testing functionality
- ✅ Fixed 68 import sorting issues in banktransactions module
- ✅ Created backup of original configuration files

### Code Quality Improvements
- ✅ Fixed all 72 linting issues in banktransactions module
- ✅ Resolved dictionary key checking issues
- ✅ Replaced `assert False` with proper `raise AssertionError()`
- ✅ Achieved 100% linting compliance across all modules

---

## Priority Matrix

| Task | Priority | Effort | Impact | Dependencies |
|------|----------|--------|--------|--------------|
| Email Automation Fixes | 🔴 High | 1-2 days | High | None |
| ~~Linting Issues~~ | ✅ DONE | ~~30 min~~ | ~~Low~~ | ~~None~~ |
| Import Path Issues | 🟡 Medium | 1 day | Medium | None |
| Documentation Updates | 📚 Low | 1 day | Medium | Email fixes |
| CI/CD Optimization | ⚙️ Low | 1-2 days | Medium | None |
| Performance Monitoring | 📊 Low | 1 day | Medium | None |

---

## Notes

- **Test Status**: 541 passed, 17 failed (email automation), 7 skipped
- **Build Status**: ✅ Fully functional monorepo setup
- **Installation**: ✅ `pip install -e ".[dev]"` works correctly
- **Linting**: ✅ All 72 issues resolved - 100% compliance achieved
- **Dependencies**: ✅ All unified and up-to-date

---

## Getting Started

To work on these tasks:

1. **For Email Automation Issues**:
   ```bash
   # Run specific failing tests to investigate
   pytest backend/tests/test_email_automation.py::TestEmailAutomationConfig::test_create_email_config_success -v
   ```

2. **For Linting Issues**:
   ```bash
   # Fix remaining linting issues
   ruff check --fix --unsafe-fixes banktransactions/
   ```

3. **For Import Issues**:
   ```bash
   # Test module imports
   python -c "import backend.app; print('Backend import successful')"
   python -c "import banktransactions.core; print('Banktransactions import successful')"
   ```

---

*Last Updated: 2025-05-26*  
*Status: Post-Consolidation Phase* 