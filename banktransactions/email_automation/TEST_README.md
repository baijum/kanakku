# Email Automation Test Suite

This directory contains comprehensive tests for the email automation system in the kanakku project.

## Test Structure

The test suite is organized into several files, each focusing on different aspects of the email automation system:

### Core Component Tests

- **`test_email_processor.py`** - Tests for the `process_user_emails_standalone` function (removed)
- **`test_scheduler.py`** - Tests for the `EmailScheduler` class and job scheduling logic
- **`test_run_worker.py`** - Tests for the worker script functionality and command-line interface
- **`test_run_scheduler.py`** - Tests for the scheduler script functionality and command-line interface

### Utility and Integration Tests

- **`test_utilities.py`** - Tests for utility scripts like `check_configs.py`, `check_failed.py`, `move_jobs.py`, etc.
- **`test_integration.py`** - End-to-end integration tests for the complete email automation workflow

## Test Categories

### Unit Tests
- Test individual functions and methods in isolation
- Use extensive mocking to avoid external dependencies
- Fast execution and focused on specific functionality

### Integration Tests
- Test complete workflows and component interactions
- Verify data flow through the entire system
- Test error handling and recovery mechanisms

### System Tests
- Test configuration validation
- Test system dependencies (Redis, Database)
- Test environment variable handling

## Running the Tests

### Prerequisites

1. **Python Dependencies**
   ```bash
   pip install pytest pytest-mock pytest-cov
   ```

2. **Environment Setup**
   ```bash
   # Set required environment variables for testing
   export DATABASE_URL="postgresql://test:test@localhost/test"
   export REDIS_URL="redis://localhost:6379/0"
   export ENCRYPTION_KEY="test_encryption_key_123"
   ```

### Running All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=banktransactions.email_automation --cov-report=html

# Run with verbose output
pytest -v
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests that don't require external services
pytest -m "not external"
```

### Running Specific Test Files

```bash
# Test scheduler
pytest test_scheduler.py

# Test integration workflows
pytest test_integration.py
```

### Running Specific Test Classes or Methods

```bash
# Test specific class
pytest test_scheduler.py::TestEmailScheduler

# Test specific method
pytest test_scheduler.py::TestEmailScheduler::test_schedule_jobs_success
```

## Test Configuration

The test suite uses `pytest.ini` for configuration:

- **Test Discovery**: Automatically finds `test_*.py` files
- **Markers**: Custom markers for categorizing tests
- **Logging**: Configured for detailed test output
- **Warnings**: Filters out deprecation warnings for cleaner output

## Mock Strategy

The tests use extensive mocking to ensure:

1. **Isolation**: Tests don't depend on external services
2. **Speed**: Fast execution without network calls or database operations
3. **Reliability**: Consistent results regardless of external system state
4. **Safety**: No side effects on real systems

### Key Mocked Components

- **Database Sessions**: SQLAlchemy sessions and queries
- **Redis Connections**: Redis client operations
- **IMAP Clients**: Email server connections and operations
- **API Clients**: HTTP requests to external APIs
- **Encryption/Decryption**: Password handling operations
- **Job Queues**: RQ job scheduling and execution

## Test Data

Tests use realistic but anonymized test data:

- **Email Configurations**: Mock user email settings
- **Email Messages**: Sample bank transaction emails
- **Transaction Data**: Parsed transaction information
- **API Responses**: Mock API success and error responses

## Coverage Goals

The test suite aims for:

- **90%+ Code Coverage**: Comprehensive testing of all code paths
- **100% Critical Path Coverage**: All main workflows fully tested
- **Error Scenario Coverage**: All error conditions tested

## Debugging Tests

### Running Tests with Debug Output

```bash
# Enable debug logging
pytest --log-cli-level=DEBUG

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb
```

### Common Issues and Solutions

1. **Import Errors**
   - Ensure the project root is in Python path
   - Check that all dependencies are installed

2. **Mock Assertion Failures**
   - Verify mock setup matches actual code behavior
   - Check call arguments and return values

3. **Environment Variable Issues**
   - Ensure all required environment variables are set
   - Use `@patch.dict(os.environ, {...})` for test-specific variables

## Test Maintenance

### Adding New Tests

1. **Follow Naming Conventions**
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

2. **Use Appropriate Markers**
   ```python
   @pytest.mark.unit
   def test_individual_function():
       pass

   @pytest.mark.integration
   def test_complete_workflow():
       pass
   ```

3. **Include Docstrings**
   ```python
   def test_email_processing_success(self):
       """Test successful email processing with valid configuration."""
       pass
   ```

### Updating Tests

When modifying the email automation code:

1. **Update Related Tests**: Ensure tests reflect code changes
2. **Add New Test Cases**: Cover new functionality or edge cases
3. **Update Mocks**: Adjust mock behavior to match new code
4. **Run Full Test Suite**: Verify no regressions

## Performance Considerations

- **Fast Execution**: Most tests complete in milliseconds
- **Parallel Execution**: Tests can be run in parallel with `pytest-xdist`
- **Resource Usage**: Minimal memory and CPU usage due to mocking

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- **No External Dependencies**: All external services are mocked
- **Deterministic Results**: Tests produce consistent results
- **Clear Failure Messages**: Easy to diagnose issues from test output

## Security Testing

The test suite includes security-focused tests:

- **Password Encryption/Decryption**: Verify secure handling of credentials
- **Input Validation**: Test against malicious input
- **Error Information Leakage**: Ensure sensitive data isn't exposed in errors
- **Authentication**: Verify proper authentication handling

## Future Enhancements

Planned improvements to the test suite:

1. **Property-Based Testing**: Use Hypothesis for more comprehensive testing
2. **Load Testing**: Add tests for high-volume email processing
3. **End-to-End Tests**: Tests with real (sandboxed) external services
4. **Performance Benchmarks**: Track performance metrics over time

## Contributing

When contributing to the test suite:

1. **Follow Existing Patterns**: Use similar structure and style
2. **Add Comprehensive Tests**: Cover both success and failure cases
3. **Update Documentation**: Keep this README current
4. **Run Tests Locally**: Ensure all tests pass before submitting

## Support

For questions about the test suite:

1. **Check Existing Tests**: Look for similar test patterns
2. **Review Documentation**: This README and inline comments
3. **Run with Debug Output**: Use verbose flags for more information
4. **Check CI Logs**: Review automated test results 