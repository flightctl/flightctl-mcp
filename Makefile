# Makefile for Flight Control MCP Server development

.PHONY: help test test-unit test-integration test-live clean lint format install-dev build

# Default target
help:
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  install-dev    - Install development dependencies"
	@echo "  test           - Run all tests except live integration tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests with mocks"
	@echo "  test-live      - Run tests against live Flight Control instance"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  lint           - Run linting checks"
	@echo "  format         - Format code with black"
	@echo "  clean          - Clean up temporary files"
	@echo "  build          - Build container image"
	@echo "  logs           - Show MCP server logs"

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install black flake8 mypy

# Run all tests except live integration
test:
	pytest -m "not integration"

# Run unit tests only
test-unit:
	pytest -m "unit" || pytest test_flightctl_mcp.py::TestConfiguration test_flightctl_mcp.py::TestFlightControlClient test_flightctl_mcp.py::TestCLI test_flightctl_mcp.py::TestLogging

# Run integration tests with mocks
test-integration:
	pytest -m "integration" || pytest test_flightctl_mcp.py::TestIntegration

# Run tests against live Flight Control instance (requires setup)
test-live:
	@echo "Running tests against live Flight Control instance..."
	@echo "Make sure you have run 'flightctl login' first!"
	pytest -m "integration" --tb=short

# Run tests with coverage
test-coverage:
	pytest --cov=resource_queries --cov=main --cov=cli --cov-report=html --cov-report=term

# Lint code
lint:
	flake8 *.py --max-line-length=120 --ignore=E501,W503
	mypy *.py --ignore-missing-imports || true

# Format code
format:
	black *.py --line-length=120

# Clean temporary files
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf *.pyc
	rm -rf .mypy_cache/

# Build container image
build:
	podman build -t flightctl-mcp:latest .

# Show MCP server logs
logs:
	@echo "=== Recent MCP Server Logs ==="
	@if [ -f ~/.local/share/flightctl-mcp/flightctl-mcp.log ]; then \
		tail -n 50 ~/.local/share/flightctl-mcp/flightctl-mcp.log; \
	else \
		echo "No log file found. Run the server first."; \
	fi

# Run a quick smoke test
smoke-test:
	@echo "Running smoke test..."
	python -c "from resource_queries import Configuration, FlightControlClient; print('✅ Imports successful')"
	python -c "from main import mcp; print('✅ MCP server imports successful')"

# Development server (for testing MCP protocol)
dev-server:
	@echo "Starting MCP server in development mode..."
	@echo "Use Ctrl+C to stop"
	LOG_LEVEL=DEBUG python main.py 