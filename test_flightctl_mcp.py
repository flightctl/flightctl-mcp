#!/usr/bin/env python3
"""
Test suite for Flight Control MCP Server

This test suite includes:
1. Unit tests - Test components in isolation with mocks
2. Integration tests - Test against mocked HTTP responses
3. Live tests - Test against real Flight Control instance (optional)
"""

import os
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from resource_queries import (
    Configuration,
    FlightControlClient,
    FlightControlError,
    AuthenticationError,
    APIError,
    setup_logging,
)
from cli import FlightctlCLI


class TestConfiguration:
    """Test Configuration class functionality."""

    def test_default_configuration(self):
        """Test configuration with no files or environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                config = Configuration()
                assert config.api_base_url is None
                assert config.oidc_token_url is None
                assert config.client_id == "flightctl"
                assert config.refresh_token is None
                assert config.insecure_skip_verify is False

    def test_environment_variable_override(self):
        """Test that environment variables override config file settings."""
        env_vars = {
            "API_BASE_URL": "https://api.test.com",
            "OIDC_TOKEN_URL": "https://auth.test.com/token",
            "OIDC_CLIENT_ID": "test-client",
            "REFRESH_TOKEN": "test-token",
            "INSECURE_SKIP_VERIFY": "true",
        }

        with patch.dict(os.environ, env_vars):
            with patch("pathlib.Path.exists", return_value=False):
                config = Configuration()
                assert config.api_base_url == "https://api.test.com"
                assert config.oidc_token_url == "https://auth.test.com/token"
                assert config.client_id == "test-client"
                assert config.refresh_token == "test-token"
                assert config.insecure_skip_verify is True

    def test_config_file_parsing(self):
        """Test parsing of flightctl client.yaml configuration."""
        config_data = {
            "service": {"server": "https://api.flightctl.example.com", "insecureSkipVerify": True},
            "authentication": {
                "auth-provider": {
                    "config": {
                        "server": "https://auth.flightctl.example.com/realms/flightctl",
                        "client-id": "flightctl",
                        "refresh-token": "eyJ...",
                    }
                }
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            with patch.object(Configuration, "__init__", lambda self: None):
                config = Configuration()
                config.logger = Mock()
                config.config_path = Path(config_path)
                config.certs_path = Path("/tmp/certs")
                config._load_config()

                assert config.api_base_url == "https://api.flightctl.example.com"
                assert config.insecure_skip_verify is True
                assert (
                    config.oidc_token_url
                    == "https://auth.flightctl.example.com/realms/flightctl/protocol/openid-connect/token"
                )
                assert config.client_id == "flightctl"
                assert config.refresh_token == "eyJ..."
        finally:
            os.unlink(config_path)

    def test_ssl_verify_settings(self):
        """Test SSL verification configuration."""
        config = Configuration()

        # Test insecure skip verify
        config.insecure_skip_verify = True
        assert config.get_ssl_verify() is False

        # Test custom CA certificate
        config.insecure_skip_verify = False
        config.ca_cert_path = "/path/to/ca.pem"
        assert config.get_ssl_verify() == "/path/to/ca.pem"

        # Test system CA bundle
        config.ca_cert_path = None
        assert config.get_ssl_verify() is True


class TestFlightControlClient:
    """Test FlightControlClient functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock()
        config.api_base_url = "https://api.test.com"
        config.oidc_token_url = "https://auth.test.com/token"
        config.client_id = "test-client"
        config.refresh_token = "test-refresh-token"
        config.insecure_skip_verify = False
        config.get_ssl_verify.return_value = True
        return config

    @pytest.fixture
    def client(self, mock_config):
        """Create a FlightControlClient with mock configuration."""
        with patch("resource_queries.logging.getLogger"):
            return FlightControlClient(mock_config)

    def test_client_initialization_success(self, mock_config):
        """Test successful client initialization."""
        with patch("resource_queries.logging.getLogger"):
            client = FlightControlClient(mock_config)
            assert client.config == mock_config
            assert client._access_token is None
            assert client._token_expiry == 0

    def test_client_initialization_missing_config(self):
        """Test client initialization with missing configuration."""
        config = Mock()
        config.api_base_url = None
        config.oidc_token_url = "https://auth.test.com/token"
        config.refresh_token = "token"

        with patch("resource_queries.logging.getLogger"):
            with pytest.raises(FlightControlError, match="API_BASE_URL not configured"):
                FlightControlClient(config)

    @patch("resource_queries.requests.post")
    def test_token_refresh_success(self, mock_post, client):
        """Test successful token refresh."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"access_token": "new-access-token", "expires_in": 3600}
        mock_post.return_value = mock_response

        token = client._get_access_token()

        assert token == "new-access-token"
        assert client._access_token == "new-access-token"
        mock_post.assert_called_once()

    @patch("resource_queries.requests.post")
    def test_token_refresh_failure(self, mock_post, client):
        """Test token refresh failure handling."""
        # Mock failed token response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"
        mock_post.side_effect = Exception("HTTP 400: Bad Request")

        with pytest.raises(AuthenticationError):
            client._get_access_token()

    @patch("resource_queries.requests.get")
    def test_query_devices_success(self, mock_get, client):
        """Test successful device query."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "items": [
                {"apiVersion": "v1", "kind": "Device", "metadata": {"name": "device-1"}, "spec": {}, "status": {}}
            ]
        }
        mock_get.return_value = mock_response

        # Mock token refresh
        with patch.object(client, "_get_access_token", return_value="valid-token"):
            devices = client.query_devices()

        assert len(devices) == 1
        assert devices[0]["metadata"]["name"] == "device-1"
        mock_get.assert_called_once()

    @patch("resource_queries.requests.get")
    def test_query_devices_http_error(self, mock_get, client):
        """Test device query with HTTP error."""
        # Mock HTTP error response
        import requests

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        error = requests.exceptions.HTTPError()
        error.response = mock_response
        mock_get.side_effect = error

        # Mock token refresh
        with patch.object(client, "_get_access_token", return_value="valid-token"):
            with pytest.raises(APIError, match="Resource not found"):
                client.query_devices()

    @patch("resource_queries.subprocess.run")
    def test_console_command_success(self, mock_run, client):
        """Test successful console command execution."""
        # Mock successful command execution
        mock_result = Mock()
        mock_result.stdout = "command output"
        mock_run.return_value = mock_result

        # Mock token refresh and CLI check
        with patch.object(client, "_get_access_token", return_value="valid-token"):
            with patch("resource_queries.shutil.which", return_value="/usr/bin/flightctl"):
                result = client.run_console_command("/usr/bin/flightctl", "test-device", "ps aux")

        assert result == "command output"
        assert mock_run.call_count == 2  # login + command

    @patch("resource_queries.subprocess.run")
    def test_console_command_failure(self, mock_run, client):
        """Test console command execution failure."""
        import subprocess

        # Mock command execution failure
        error = subprocess.CalledProcessError(1, ["flightctl"], stderr="Command failed")
        mock_run.side_effect = error

        # Mock token refresh and CLI check
        with patch.object(client, "_get_access_token", return_value="valid-token"):
            with patch("resource_queries.shutil.which", return_value="/usr/bin/flightctl"):
                with pytest.raises(FlightControlError, match="Failed to login"):
                    client.run_console_command("/usr/bin/flightctl", "test-device", "ps aux")


class TestCLI:
    """Test FlightctlCLI functionality."""

    def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = FlightctlCLI("https://api.test.com")
        assert cli.api_url == "https://api.test.com"
        assert cli.arch == "amd64"
        assert cli.os_name == "linux"

    @patch("cli.shutil.which")
    def test_download_skip_existing(self, mock_which):
        """Test skipping download when CLI already exists."""
        mock_which.return_value = "/usr/local/bin/flightctl"

        cli = FlightctlCLI("https://api.test.com")
        cli.download()

        assert cli.cli_path == "/usr/local/bin/flightctl"

    @patch("cli.shutil.which")
    @patch("cli.subprocess.run")
    @patch("cli.shutil.move")
    @patch("cli.os.chmod")
    @patch("cli.os.makedirs")
    @patch("cli.tempfile.TemporaryDirectory")
    def test_download_success(self, mock_tempdir, mock_makedirs, mock_chmod, mock_move, mock_run, mock_which):
        """Test successful CLI download."""
        mock_which.return_value = None  # CLI not found
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test"

        cli = FlightctlCLI("https://api.test.com")
        cli.download()

        # Verify download steps were called
        assert mock_run.call_count == 2  # curl + tar
        mock_move.assert_called_once()
        mock_chmod.assert_called_once()


class TestIntegration:
    """Integration tests that can run against a real Flight Control instance."""

    @pytest.fixture
    def live_config(self):
        """Get configuration for live testing (requires environment setup)."""
        config = Configuration()
        if not config.api_base_url:
            pytest.skip("No live Flight Control instance configured")
        return config

    @pytest.fixture
    def live_client(self, live_config):
        """Create client for live testing."""
        return FlightControlClient(live_config)

    @pytest.mark.integration
    def test_live_device_query(self, live_client):
        """Test querying devices from live instance."""
        try:
            devices = live_client.query_devices(limit=1)
            assert isinstance(devices, list)
            # Don't assert on specific content since it depends on cluster state
        except Exception as e:
            pytest.fail(f"Live device query failed: {e}")

    @pytest.mark.integration
    def test_live_fleet_query(self, live_client):
        """Test querying fleets from live instance."""
        try:
            fleets = live_client.query_fleets(limit=1)
            assert isinstance(fleets, list)
        except Exception as e:
            pytest.fail(f"Live fleet query failed: {e}")


class TestLogging:
    """Test logging configuration."""

    def test_logging_setup(self):
        """Test that logging can be set up without errors."""
        with patch("logging.handlers.RotatingFileHandler"):
            with patch("pathlib.Path.mkdir"):
                logger = setup_logging()
                assert logger is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
