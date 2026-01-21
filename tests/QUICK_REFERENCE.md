# Quick Test Reference

## Run All Tests
```powershell
uv run pytest tests/
```

## Run Specific Test File
```powershell
uv run pytest tests/test_werkzeug_security.py
```

## Run with Verbose Output
```powershell
uv run pytest tests/ -v
```

## Run Specific Test Class
```powershell
# Version upgrade tests
uv run pytest tests/test_werkzeug_security.py::TestWerkzeugVersionUpgrade

# safe_join tests
uv run pytest tests/test_werkzeug_security.py::TestSafeJoinWindowsDeviceExploits

# send_from_directory tests
uv run pytest tests/test_werkzeug_security.py::TestSendFromDirectoryWindowsDevices

# Integration tests
uv run pytest tests/test_werkzeug_security.py::TestApplicationIntegration
```

## Run Specific Test
```powershell
uv run pytest tests/test_werkzeug_security.py::TestWerkzeugVersionUpgrade::test_werkzeug_version_installed
```

## Additional Options
```powershell
# Show detailed failure info
uv run pytest tests/ -v --tb=short

# Stop at first failure
uv run pytest tests/ -x

# Run only Windows-specific tests (auto-detected)
uv run pytest tests/ -v -m "not skipif"

# Generate coverage report
uv run pytest tests/ --cov=. --cov-report=html

# Run tests in parallel (requires pytest-xdist)
# uv add --dev pytest-xdist
uv run pytest tests/ -n auto
```

## Expected Results
- **Total:** 16 tests
- **Passed:** 14 tests
- **Skipped:** 2 tests (app integration - requires modell.pkl)
- **Failed:** 0 tests

## Test Categories

### ✅ Werkzeug Version Tests (3 tests)
Verify Werkzeug 3.1.5+ installation and CVE patch

### ✅ safe_join Tests (5 tests)
Validate Windows device name blocking

### ✅ send_from_directory Tests (6 tests)
Ensure Flask file serving security

### ⏭️ Application Integration Tests (2 tests)
Full app context tests (skipped if modell.pkl missing)

## Troubleshooting

### All tests skipped on Linux/macOS
This is expected - Windows-specific tests auto-skip on non-Windows platforms.

### "Cannot import app module" errors
The application integration tests require a fully initialized Flask app with modell.pkl. These tests will be skipped automatically.

### Import errors
Ensure dependencies are installed:
```powershell
uv sync
```

## CI/CD Integration

Add to your CI pipeline:
```yaml
- name: Run Security Tests
  run: uv run pytest tests/test_werkzeug_security.py -v
```

## More Information
- See `README.md` for detailed test documentation
- See `TEST_SUMMARY.md` for complete test results and analysis
