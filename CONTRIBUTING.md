# Contributing to Flight Control MCP Server

Thank you for your interest in contributing to the Flight Control MCP Server! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Development Workflow](#development-workflow)
- [Getting Help](#getting-help)

## Code of Conduct

This project follows the standard open source code of conduct. Please be respectful, inclusive, and constructive in all interactions.

## Developer Certificate of Origin (DCO)

This project requires all contributors to sign off on their commits using the **Developer Certificate of Origin**. This is a lightweight way to certify that you wrote or otherwise have the right to pass on the code you are contributing.

### What is DCO?

By signing off on your commits, you are certifying that:
- You wrote the code yourself, OR
- You have the right to pass on the code as open source, OR  
- Someone who had that right passed it on to you

### How to Sign Off

**All commits must be signed off.** Add the `-s` flag to your commit:

```bash
git commit -s -m "Add new feature for device filtering"
```

This automatically adds a "Signed-off-by" line to your commit message:
```
Add new feature for device filtering

Signed-off-by: Your Name <your.email@example.com>
```

### Fixing Missing Sign-offs

If you forget to sign off commits, you can fix them:

```bash
# For the last commit
git commit --amend --signoff

# For multiple commits (interactive rebase)
git rebase -i HEAD~3  # Replace 3 with number of commits
# In the editor, change 'pick' to 'edit' for commits needing sign-off
# For each commit:
git commit --amend --signoff
git rebase --continue
```

### Why DCO?

DCO provides legal clarity for the project and its users by ensuring:
- Clear provenance of contributions
- Protection against copyright issues
- Compliance with open source licensing
- Peace of mind for enterprise users

## Getting Started

### Prerequisites

- **Python 3.9+** (recommended: 3.11 or 3.12)
- **Git** for version control
- **Docker/Podman** for container testing (optional)
- **Flight Control instance** for live testing (optional)

### Understanding the Project

The Flight Control MCP Server provides:
- Read-only access to Flight Control resources (devices, fleets, events, etc.)
- Remote command execution on devices via console commands
- Integration with Model Context Protocol (MCP) for AI assistants

Key components:
- `main.py` - MCP server entry point and tool definitions
- `resource_queries.py` - Flight Control API client with authentication
- `cli.py` - CLI management and console command execution
- Test files for comprehensive testing strategy

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/flightctl-mcp.git
cd flightctl-mcp

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/flightctl-mcp.git
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Install development tools
make install-dev
# Or manually:
pip install pytest pytest-mock pytest-cov black flake8 mypy
```

### 3. Verify Installation

```bash
# Run smoke tests
make smoke-test

# Run unit tests
make test-unit

# Check code formatting
make lint
```

### 4. Optional: Set Up Flight Control

For live testing (not required for most contributions):

```bash
# If you have a Flight Control instance
flightctl login

# Test against live instance
python test_live_instance.py
```

## Making Changes

### Branch Strategy

```bash
# Create a feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes
git checkout -b fix/issue-description
```

### Types of Contributions

We welcome:
- 🐛 **Bug fixes** - Fix issues in existing functionality
- ✨ **New features** - Add new MCP tools or capabilities
- 📚 **Documentation** - Improve docs, examples, comments
- 🧪 **Tests** - Add or improve test coverage
- 🔧 **Infrastructure** - CI/CD, build tools, development experience
- 🎨 **Code quality** - Refactoring, performance improvements

## Testing

**All contributions must include appropriate tests!** See [TESTING.md](TESTING.md) and [CI-TESTING.md](CI-TESTING.md) for detailed testing information.

### Test Requirements

#### For Bug Fixes:
```bash
# Add a test that reproduces the bug (should fail initially)
# Fix the bug
# Verify the test now passes
make test-unit
```

#### For New Features:
```bash
# Add unit tests for new functionality
# Add integration tests if needed
# Update documentation
make test
```

#### Before Submitting:
```bash
# Run all local tests
make test

# Test code formatting
make lint

# Test against live Flight Control (if available)
python test_live_instance.py
```

### Test Categories

1. **Unit Tests** (required) - Fast tests with mocked dependencies
2. **Integration Tests** (recommended) - Component interaction tests
3. **Live Tests** (optional) - Manual testing against real Flight Control

## Code Style

### Python Style Guide

We follow **PEP 8** with these specific requirements:

```bash
# Format code with Black
black --line-length=120 *.py

# Check linting with flake8
flake8 *.py --max-line-length=120 --ignore=E501,W503

# Type checking with mypy
mypy *.py --ignore-missing-imports
```

### Code Quality Standards

- **Line length**: 120 characters maximum
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Document all public functions and classes
- **Error handling**: Use proper exception handling with typed exceptions
- **Logging**: Use the project's logging framework
- **Security**: Follow secure coding practices

### Example Function

```python
def query_devices(
    self, 
    label_selector: Optional[str] = None, 
    field_selector: Optional[str] = None, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Query Flight Control devices with optional filtering.
    
    Args:
        label_selector: Kubernetes label selector for filtering
        field_selector: Kubernetes field selector for filtering  
        limit: Maximum number of results to return
        
    Returns:
        List of device objects from the Flight Control API
        
    Raises:
        APIError: If the API request fails
        AuthenticationError: If authentication fails
    """
    # Implementation here...
```

## Submitting Changes

### Pull Request Process

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run full test suite**:
   ```bash
   make test
   make lint
   ```

3. **Commit with clear, signed-off messages**:
   ```bash
   git commit -s -m "Add support for device labels filtering
   
   - Implement label selector validation
   - Add unit tests for new functionality
   - Update documentation with examples"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

### PR Requirements

✅ **Required for PR approval:**
- [ ] All CI tests pass (unit tests, linting, container builds)
- [ ] Code follows style guidelines (Black formatting, flake8 compliance)
- [ ] New code has appropriate test coverage
- [ ] Documentation updated if needed
- [ ] Clear commit messages and PR description

✅ **PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Tested against live Flight Control instance
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process

1. **Automated checks** - CI must pass
2. **Code review** - Maintainer review for quality and correctness  
3. **Testing** - Verify functionality works as expected
4. **Documentation** - Ensure changes are properly documented

## Reporting Issues

### Bug Reports

Use the GitHub issue template and include:

```markdown
**Describe the bug**
Clear description of what went wrong

**To Reproduce**
Steps to reproduce the behavior:
1. Set up environment with...
2. Run command...
3. See error...

**Expected behavior** 
What you expected to happen

**Environment:**
- OS: [e.g. Linux, macOS]
- Python version: [e.g. 3.11]
- Flight Control version: [if applicable]
- MCP server version/commit: [git commit hash]

**Additional context**
- Configuration details (redact sensitive info)
- Log files (use LOG_LEVEL=DEBUG)
- Screenshots if applicable
```

### Feature Requests

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**  
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Any other context, mockups, or examples
```

## Development Workflow

### Typical Development Cycle

```bash
# 1. Set up development environment
make install-dev

# 2. Create feature branch
git checkout -b feature/new-tool

# 3. Develop with TDD approach
# Write failing test
pytest test_flightctl_mcp.py::TestNewFeature::test_new_functionality -v

# Implement feature
# Run test again (should pass)

# 4. Run full test suite frequently
make test-unit  # Quick feedback (30 seconds)

# 5. Before committing
make test       # Full test suite (2 minutes)
make lint       # Code quality checks

# 6. Manual testing (if needed)
python test_live_instance.py

# 7. Commit with sign-off and submit PR
git commit -s -m "Add new MCP tool for device management

- Implement device filtering functionality
- Add comprehensive unit tests
- Update documentation"

git push origin feature/new-tool
```

### Debugging

```bash
# View logs
make logs

# Run tests with debugging
pytest --pdb test_flightctl_mcp.py::TestClass::test_method

# Run with detailed output
pytest -vvv -s test_flightctl_mcp.py

# Debug configuration issues
LOG_LEVEL=DEBUG python main.py
```

## Getting Help

### Resources

- 📖 **Documentation**: [README.md](README.md), [TESTING.md](TESTING.md)
- 🧪 **Testing Guide**: [CI-TESTING.md](CI-TESTING.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/OWNER/flightctl-mcp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/OWNER/flightctl-mcp/discussions)

### Common Questions

**Q: How do I test without a Flight Control instance?**
A: Most development can be done with unit tests that use mocks. See [TESTING.md](TESTING.md) for details.

**Q: My tests are failing in CI but passing locally?**
A: Check the [CI-TESTING.md](CI-TESTING.md) guide. Likely a dependency or environment difference.

**Q: How do I add a new MCP tool?**
A: Add the tool function in `main.py`, implement the backend logic in `resource_queries.py`, and add comprehensive tests.

**Q: What's the difference between unit and integration tests?**
A: Unit tests mock external dependencies, integration tests may use mocked HTTP responses but test component interactions.

**Q: I forgot to sign off my commits, how do I fix it?**
A: Use `git commit --amend --signoff` for the last commit, or `git rebase -i` for multiple commits. See the DCO section above for details.

**Q: Why do I need to sign off commits?**
A: The Developer Certificate of Origin (DCO) ensures legal clarity about contribution rights and protects both contributors and users of the project.

### Getting Support

1. **Check existing issues** - Your question might already be answered
2. **Read the documentation** - Comprehensive guides are available
3. **Start a discussion** - For questions about architecture or design
4. **Create an issue** - For bugs or feature requests
5. **Submit a draft PR** - For complex changes, get early feedback

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes for significant contributions  
- GitHub contributor graphs
- Special thanks in major releases

Thank you for contributing to Flight Control MCP Server! 🚀 