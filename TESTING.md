# Testing Guide for Flight Control MCP Server

This document explains how to test the Flight Control MCP Server at different levels.

## Testing Strategy

The project uses a multi-layered testing approach:

1. **Unit Tests** - Fast tests with mocked dependencies 
2. **Integration Tests** - Tests with mocked HTTP responses
3. **Live Tests** - Tests against a real Flight Control instance
4. **End-to-End Tests** - Full MCP protocol testing

## Prerequisites

Install testing dependencies:
```bash
pip install pytest pytest-mock pytest-cov
# Or use the Makefile
make install-dev
```

## Test Types

### 1. Unit Tests (Recommended for Development)

Unit tests run fast and don't require external dependencies. They test individual components in isolation.

```bash
# Run all unit tests
make test-unit

# Or run specific test classes
pytest test_flightctl_mcp.py::TestConfiguration -v
pytest test_flightctl_mcp.py::TestFlightControlClient -v
pytest test_flightctl_mcp.py::TestCLI -v
```

**What they test:**
- Configuration loading and validation
- HTTP client behavior with mocked responses
- Error handling and authentication flows
- CLI download and management

### 2. Integration Tests with Mocks

These tests verify the integration between components but use mocked HTTP responses.

```bash
# Run integration tests
make test-integration

# Run with verbose output
pytest -m "integration" -v
```

**What they test:**
- Token refresh flows
- API query construction
- Response parsing
- Error handling across component boundaries

### 3. Live Instance Tests

Test against your actual Flight Control instance. Requires `flightctl login` to be run first.

```bash
# Quick live test
python test_live_instance.py

# Or run through pytest
make test-live
```

**What they test:**
- Real API connectivity
- Authentication with live OIDC
- All MCP tool functions
- Console command execution (if devices available)

**Example output:**
```
🚀 Flight Control MCP Server - Live Integration Test
============================================================
🔧 Testing Flight Control API connectivity...
   API URL: https://api.10.100.102.206.nip.io:3443
   Skip SSL: True
✅ Client initialized successfully

🔍 Testing API queries...
   Testing device query...
   ✅ Found 0 devices
   Testing fleet query...
   ✅ Found 0 fleets
   [...]

📊 Test Summary:
==============================
   devices             : ✅ 0 items
   fleets              : ✅ 0 items
   events              : ✅ 1 events
   [...]
```

### 4. Coverage Testing

Generate test coverage reports:

```bash
# Generate coverage report
make test-coverage

# View HTML coverage report
open htmlcov/index.html
```

## Running Tests

### Quick Commands

```bash
# Run all tests (except live)
make test

# Run specific test categories
make test-unit
make test-integration

# Run tests with coverage
make test-coverage

# Test against live instance
python test_live_instance.py
```

### Pytest Commands

```bash
# Run all tests with verbose output
pytest -v

# Run tests by marker
pytest -m "unit" -v
pytest -m "integration" -v

# Run specific test file
pytest test_flightctl_mcp.py -v

# Run specific test class or method
pytest test_flightctl_mcp.py::TestConfiguration::test_default_configuration -v

# Run tests matching a pattern
pytest -k "test_config" -v
```

## Test Configuration

The project uses `pytest.ini` for configuration:

```ini
[tool:pytest]
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may require live Flight Control instance)
    slow: Slow tests that take more than a few seconds

addopts = 
    -v
    --tb=short
    --strict-markers
```

## Setting Up Live Testing

To test against a real Flight Control instance:

### Option 1: Use Existing Login

If you've already run `flightctl login`:
```bash
python test_live_instance.py
```

### Option 2: Environment Variables

Set these environment variables:
```bash
export API_BASE_URL="https://your-flightctl-api.com"
export OIDC_TOKEN_URL="https://your-auth-server.com/token"
export OIDC_CLIENT_ID="flightctl"
export REFRESH_TOKEN="your-refresh-token"
export INSECURE_SKIP_VERIFY="true"  # if using self-signed certs

python test_live_instance.py
```

### Option 3: Custom Configuration

Create a temporary config file:
```yaml
# ~/.config/flightctl/client.yaml
service:
  server: https://your-flightctl-api.com
  insecureSkipVerify: true
authentication:
  auth-provider:
    config:
      server: https://your-auth-server.com/realms/flightctl
      client-id: flightctl
      refresh-token: your-refresh-token
```

## CI/CD Testing

The project includes GitHub Actions workflows for continuous testing:

```yaml
# .github/workflows/test.yml
- Unit tests across Python 3.9-3.12
- Linting with flake8 and black
- Type checking with mypy
- Container build testing
- Coverage reporting
```

## Test Development

### Writing New Tests

1. **Unit tests** - Add to `test_flightctl_mcp.py` in appropriate test class
2. **Mock external dependencies** - Use `unittest.mock` or `pytest-mock`
3. **Use appropriate markers** - Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`
4. **Test error conditions** - Include negative test cases
5. **Use fixtures** - For common test setup

Example test:
```python
def test_new_feature(self, mock_config):
    """Test description."""
    with patch('module.external_call') as mock_call:
        mock_call.return_value = "expected"
        
        result = function_under_test()
        
        assert result == "expected"
        mock_call.assert_called_once()
```

### Test Data

- Use temporary files for file-based tests
- Mock HTTP responses with realistic Flight Control API data
- Use pytest fixtures for reusable test setup

### Debugging Tests

```bash
# Run with debugger
pytest --pdb test_flightctl_mcp.py::TestClass::test_method

# Show print statements
pytest -s test_flightctl_mcp.py

# Show detailed output
pytest -vvv test_flightctl_mcp.py

# Run single test with full traceback
pytest --tb=long test_flightctl_mcp.py::TestClass::test_method
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure dependencies are installed
pip install -r requirements.txt
```

**SSL Certificate Issues:**
```bash
# For live testing with self-signed certs
export INSECURE_SKIP_VERIFY=true
```

**Authentication Failures:**
```bash
# Re-run flightctl login
flightctl login

# Or check your refresh token
flightctl whoami
```

**No Devices for Console Testing:**
```bash
# This is normal for new installations
# Console command tests will be skipped
```

### Log Files

Test runs create log files:
```bash
# View MCP server logs
make logs

# Or directly
tail -f ~/.local/share/flightctl-mcp/flightctl-mcp.log
```

## Performance Testing

For performance testing of the MCP server:

```bash
# Time the test execution
time python test_live_instance.py

# Profile with pytest-benchmark (if installed)
pip install pytest-benchmark
pytest --benchmark-only
```

## Test Environment Cleanup

Clean up test artifacts:
```bash
make clean

# Or manually
rm -rf __pycache__/ .pytest_cache/ .coverage htmlcov/
``` 