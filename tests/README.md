# Reflask Unit Tests

This directory contains unit tests for the Reflask application, with a focus on security vulnerabilities and best practices.

## Test Coverage

### test_werkzeug_security.py
Tests for Werkzeug security vulnerabilities and fixes:

1. **Werkzeug Version Upgrade (CVE-2025-0995)**
   - Verifies that Werkzeug 3.1.5 or higher is installed
   - Ensures the CVE vulnerability is resolved
   - Checks that security functions are importable

2. **safe_join Windows Device Name Exploits**
   - Tests blocking of Windows reserved device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
   - Verifies prevention of device names with file extensions
   - Ensures legitimate filenames are still allowed
   - Tests path traversal prevention with device names

3. **send_from_directory Windows Device Handling**
   - Ensures Flask's send_from_directory rejects device names
   - Tests blocking of device names with extensions
   - Verifies legitimate file access still works
   - Tests integration with safe_join function

4. **Application Integration**
   - Verifies the application endpoints reject device names
   - Ensures correct Werkzeug version is used in the application context

## Running the Tests

### Prerequisites
Ensure pytest is installed:
```powershell
uv add --dev pytest
```

### Run All Tests
```powershell
# Using uv (recommended)
uv run pytest tests/

# Or with pytest directly
pytest tests/
```

### Run Specific Test File
```powershell
uv run pytest tests/test_werkzeug_security.py
```

### Run Specific Test Class
```powershell
uv run pytest tests/test_werkzeug_security.py::TestWerkzeugVersionUpgrade
```

### Run Specific Test Method
```powershell
uv run pytest tests/test_werkzeug_security.py::TestWerkzeugVersionUpgrade::test_werkzeug_version_installed
```

### Run with Verbose Output
```powershell
uv run pytest tests/ -v
```

### Run with Coverage Report
```powershell
uv add --dev pytest-cov
uv run pytest tests/ --cov=. --cov-report=html
```

### Run Only Windows-Specific Tests
The Windows-specific tests are marked with `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")` and will automatically run only on Windows systems.

## Test Structure

### Test Classes
- `TestWerkzeugVersionUpgrade`: Version verification tests
- `TestSafeJoinWindowsDeviceExploits`: safe_join function tests
- `TestSendFromDirectoryWindowsDevices`: send_from_directory tests
- `TestApplicationIntegration`: Integration tests with the Flask app

### Fixtures
- `flask_app`: Creates a test Flask application instance
- `test_directory`: Creates a temporary directory for file testing
- `app_client`: Creates a test client for the actual Reflask application

## Platform-Specific Notes

### Windows
Most security tests are Windows-specific due to the nature of Windows device name exploits. These tests will run automatically on Windows systems and be skipped on other platforms.

### Linux/macOS
While device name tests are skipped, the version verification tests will still run to ensure the correct Werkzeug version is installed.

## Expected Results

All tests should pass if:
- Werkzeug 3.1.5 or higher is installed
- The application properly uses Flask's security functions
- No endpoints expose Windows device names

## Troubleshooting

### Import Errors
If you encounter import errors, ensure the virtual environment is activated and all dependencies are installed:
```powershell
uv sync
```

### Test Failures
If tests fail:
1. Check that Werkzeug 3.1.5+ is installed: `uv pip list | Select-String werkzeug`
2. Verify the application is importable: `uv run python -c "from app import app"`
3. Review the specific test failure message for details

## Adding New Tests

When adding new security tests:
1. Follow the existing test structure with descriptive class and method names
2. Use docstrings to explain what each test verifies
3. Mark Windows-specific tests with the appropriate pytest marker
4. Update this README with the new test coverage

## Related Documentation
- [Werkzeug Security Advisory](https://github.com/pallets/werkzeug/security/advisories)
- [CVE-2025-0995 Details](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-0995)
- [Windows Reserved Device Names](https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
