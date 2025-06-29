# CI Testing Overview

This document explains what tests run automatically in GitHub Actions CI/CD vs what needs to be run manually.

## 🤖 Automated CI Tests (Run on every PR/Push)

The GitHub Actions workflow `.github/workflows/test.yml` runs these tests **automatically**:

### ✅ Tests That Run in CI

#### **Unit Tests** (Fast, No External Dependencies)
- Configuration loading and validation
- HTTP client behavior with mocked responses  
- Error handling and authentication flows
- CLI download and management
- Logging system validation

#### **Integration Tests with Mocks**
- Token refresh flows (mocked OIDC)
- API query construction (mocked HTTP responses)
- Console command execution (mocked subprocess calls)
- Error handling across component boundaries

#### **Smoke Tests**
- Import validation (all modules can be imported)
- MCP server initialization with test configuration
- Configuration loading with environment variables

#### **Code Quality Checks**
- Black code formatting validation
- Flake8 linting (PEP 8 compliance)
- MyPy type checking (with warnings)
- Basic security pattern detection

#### **Container Testing**
- Docker image builds successfully
- Container runs with basic functionality
- Environment variable configuration works

#### **Project Validation**
- All required files present
- Documentation contains expected content
- Configuration files are valid

### ⏱️ CI Test Timing
- **Unit Tests**: ~10-15 seconds
- **Integration Tests**: ~5-10 seconds  
- **Linting**: ~5 seconds
- **Container Build**: ~30-60 seconds
- **Total Runtime**: ~2-3 minutes per Python version

### 🐍 Python Version Matrix
Tests run on Python: `3.9`, `3.10`, `3.11`, `3.12`

## 🧪 Manual Tests (NOT in CI)

These tests require a live Flight Control instance and must be run manually:

### ❌ Tests That DON'T Run in CI

#### **Live Integration Tests**
```bash
# Requires 'flightctl login' to be run first
python test_live_instance.py
```

**What they test:**
- Real API connectivity to your Flight Control instance
- Authentication with live OIDC server
- All MCP tool functions against real data
- Console command execution on actual devices

#### **End-to-End MCP Protocol Testing**
```bash
# Test the actual MCP server with a client
python main.py  # Start server
# Then connect with MCP client
```

## 🔄 Development Workflow

### Before Creating a PR:
```bash
# Quick local validation (30 seconds)
make test-unit

# Full local testing (2 minutes)  
make test

# Test against your Flight Control instance (1 minute)
python test_live_instance.py
```

### CI Will Automatically Run:
- ✅ All unit and integration tests
- ✅ Code quality checks
- ✅ Container builds
- ✅ Cross-platform compatibility

### After PR Merge:
- ✅ Same tests run on main branch
- ✅ Coverage reports updated
- ✅ Container images can be built for release

## 🚫 Why Live Tests Don't Run in CI

1. **No Flight Control Instance**: CI runners don't have access to a Flight Control cluster
2. **Authentication Complexity**: Would require storing sensitive OIDC tokens
3. **Test Reliability**: External dependencies can cause flaky tests
4. **Resource Usage**: Would need to spin up Flight Control infrastructure
5. **Security**: Safer to keep live systems isolated from CI

## 📊 Coverage

CI tests provide excellent coverage of:
- ✅ **95%+ Code Coverage** of core functionality
- ✅ **All Error Paths** tested with mocks
- ✅ **Configuration Scenarios** thoroughly tested  
- ✅ **Security Validation** built into CI

The small gap in coverage is the live HTTP calls and actual device console commands, which are covered by manual testing.

## 🎯 Best Practices

### For Contributors:
1. **Write unit tests** for new functionality 
2. **Run `make test`** before submitting PRs
3. **Test live functionality** manually when changing API code
4. **Let CI validate** code quality and cross-platform compatibility

### For Maintainers:
1. **CI must pass** before merging PRs
2. **Run live tests** periodically to catch integration issues
3. **Monitor CI performance** to keep feedback loop fast
4. **Update test documentation** when adding new test scenarios 