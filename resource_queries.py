import logging
import logging.handlers
import threading
import time
import shutil
import subprocess
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


def setup_logging():
    """Set up file-based logging for the MCP server."""
    # Create logs directory
    log_dir = Path.home() / ".local" / "share" / "flightctl-mcp"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "flightctl-mcp.log"
    
    # Get log level from environment
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create rotating file handler (10MB max, keep 5 files)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    # Log startup message
    logger.info("FlightCtl MCP Server logging initialized - log file: %s", log_file)
    return logger


class FlightControlError(Exception):
    """Base exception for Flight Control API errors."""
    pass


class AuthenticationError(FlightControlError):
    """Raised when authentication fails."""
    pass


class APIError(FlightControlError):
    """Raised when API requests fail."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class Configuration:
    """Configuration manager that reads from flightctl config and environment variables."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_path = Path.home() / ".config" / "flightctl" / "client.yaml"
        self.certs_path = Path.home() / ".config" / "flightctl" / "certs"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from flightctl client.yaml and environment variables."""
        self.logger.debug("Loading configuration from %s", self.config_path)
        
        # Default values
        self.api_base_url = None
        self.oidc_token_url = None
        self.client_id = "flightctl"
        self.refresh_token = None
        self.insecure_skip_verify = False
        self.ca_cert_path = None
        
        # Try to read from flightctl config file
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Extract service configuration
                service_config = config.get('service', {})
                self.api_base_url = service_config.get('server', '').rstrip('/')
                self.insecure_skip_verify = service_config.get('insecureSkipVerify', False)
                
                # Extract authentication configuration
                auth_config = config.get('authentication', {})
                auth_provider = auth_config.get('auth-provider', {})
                provider_config = auth_provider.get('config', {})
                
                self.oidc_token_url = provider_config.get('server', '').rstrip('/')
                self.client_id = provider_config.get('client-id', 'flightctl')
                self.refresh_token = provider_config.get('refresh-token')
                
                # Check for certificate authority
                ca_cert = provider_config.get('certificate-authority')
                if ca_cert and Path(ca_cert).exists():
                    self.ca_cert_path = ca_cert
                
                self.logger.info("Loaded configuration from flightctl config file")
                    
            except Exception as e:
                self.logger.warning("Failed to read flightctl config: %s", e)
        else:
            self.logger.info("No flightctl config file found at %s", self.config_path)
        
        # Environment variable overrides (higher priority)
        if os.environ.get("API_BASE_URL"):
            self.api_base_url = os.environ["API_BASE_URL"].rstrip("/")
            self.logger.debug("API_BASE_URL overridden by environment variable")
        if os.environ.get("OIDC_TOKEN_URL"):
            self.oidc_token_url = os.environ["OIDC_TOKEN_URL"].rstrip("/")
            self.logger.debug("OIDC_TOKEN_URL overridden by environment variable")
        if os.environ.get("OIDC_CLIENT_ID"):
            self.client_id = os.environ["OIDC_CLIENT_ID"]
            self.logger.debug("OIDC_CLIENT_ID overridden by environment variable")
        if os.environ.get("REFRESH_TOKEN"):
            self.refresh_token = os.environ["REFRESH_TOKEN"]
            self.logger.debug("REFRESH_TOKEN overridden by environment variable")
        if os.environ.get("INSECURE_SKIP_VERIFY"):
            self.insecure_skip_verify = os.environ["INSECURE_SKIP_VERIFY"].lower() in ("true", "1", "yes")
            self.logger.debug("INSECURE_SKIP_VERIFY overridden by environment variable: %s", self.insecure_skip_verify)
        if os.environ.get("CA_CERT_PATH"):
            ca_path = Path(os.environ["CA_CERT_PATH"])
            if ca_path.exists():
                self.ca_cert_path = str(ca_path)
                self.logger.debug("CA_CERT_PATH overridden by environment variable: %s", self.ca_cert_path)
            else:
                self.logger.warning("CA_CERT_PATH points to non-existent file: %s", ca_path)
        
        # Auto-fix OIDC URL format if needed
        if self.oidc_token_url and not self.oidc_token_url.endswith('/protocol/openid-connect/token'):
            import re
            match = re.match(r"(https?://.+/realms/[^/]+)$", self.oidc_token_url)
            if match:
                self.oidc_token_url = match.group(1) + "/protocol/openid-connect/token"
                self.logger.debug("Auto-corrected OIDC token URL to: %s", self.oidc_token_url)
        
        self.logger.info("Configuration loaded - API: %s, Skip SSL: %s", 
                        self.api_base_url, self.insecure_skip_verify)
    
    def get_ssl_verify(self):
        """Get SSL verification setting for requests."""
        if self.insecure_skip_verify:
            return False
        elif self.ca_cert_path:
            return self.ca_cert_path
        else:
            return True  # Use system CA bundle


class FlightControlClient:
    def __init__(self, config: Optional[Configuration] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or Configuration()
        
        # Validate required configuration
        if not self.config.api_base_url:
            raise FlightControlError("API_BASE_URL not configured. Set environment variable or run 'flightctl login'")
        if not self.config.oidc_token_url:
            raise FlightControlError("OIDC_TOKEN_URL not configured. Set environment variable or run 'flightctl login'")
        if not self.config.refresh_token:
            raise FlightControlError("REFRESH_TOKEN not configured. Set environment variable or run 'flightctl login'")

        self._token_lock = threading.Lock()
        self._access_token = None
        self._token_expiry = 0  # Epoch seconds
        
        self.logger.info("FlightControl client initialized for API: %s", self.config.api_base_url)

    def query_devices(
        self,
        *,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._query_resources(
            resource="devices",
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
        )

    def query_fleets(
        self,
        *,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._query_resources(
            resource="fleets",
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
        )

    def query_events(
        self,
        *,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._query_resources(
            resource="events",
            field_selector=field_selector,
            limit=limit,
        )

    def query_enrollment_requests(
        self,
        *,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._query_resources(
            resource="enrollmentrequests",
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
        )

    def query_repositories(
        self,
        *,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._query_resources(
            resource="repositories",
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
        )

    def query_resource_syncs(
        self,
        *,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._query_resources(
            resource="resourcesyncs",
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
        )

    def run_console_command(self, cli_path: str, device_name: str, command: str) -> str:
        """
        Runs a console command on a device using the installed flightctl CLI.
        Args:
            cli_path: The path to the flightctl CLI binary.
            device_name: The name of the target device.
            command: The shell command to execute (as a string).
        Returns:
            The standard output from the console command.
        Raises:
            FlightControlError: On CLI failure or configuration issues.
        """
        self.logger.info("Running console command on device '%s': %s", device_name, command)
        
        if not shutil.which("flightctl"):
            self.logger.error("flightctl CLI not found in PATH")
            raise FlightControlError("flightctl CLI not found. Please ensure it's installed and in PATH.")

        # Validate inputs
        if not device_name or not device_name.strip():
            raise FlightControlError("Device name cannot be empty")
        if not command or not command.strip():
            raise FlightControlError("Command cannot be empty")

        try:
            # Get access token for authentication
            access_token = self._get_access_token()
        except AuthenticationError as e:
            self.logger.error("Failed to get access token for console command: %s", e)
            raise

        # Login with the CLI
        login_cmd = [
            cli_path,
            "console",
            "login",
            "--insecure-skip-tls-verify" if self.config.insecure_skip_verify else "",
            "--token",
            access_token,
        ]
        # Remove empty strings from the command
        login_cmd = [arg for arg in login_cmd if arg]
        
        self.logger.debug("Logging in to flightctl console")
        try:
            result = subprocess.run(login_cmd, check=True, capture_output=True, text=True)
            self.logger.debug("Console login successful")
        except subprocess.CalledProcessError as e:
            self.logger.error("Console login failed: %s", e.stderr)
            raise FlightControlError(f"Failed to login to flightctl console: {e.stderr}")

        # Execute the command
        cmd = [
            cli_path,
            "console",
            f"device/{device_name}",
            "--insecure-skip-tls-verify" if self.config.insecure_skip_verify else "",
            "--"
        ] + command.split()
        # Remove empty strings from the command
        cmd = [arg for arg in cmd if arg]

        self.logger.debug("Executing console command: %s", ' '.join(cmd[:-len(command.split()):]))
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.logger.info("Console command completed successfully on device '%s'", device_name)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error("Console command failed on device '%s': exit code %d, stderr: %s", 
                            device_name, e.returncode, e.stderr)
            raise FlightControlError(f"Console command failed on device '{device_name}': {e.stderr}")
        except Exception as e:
            self.logger.error("Unexpected error running console command on device '%s': %s", device_name, e)
            raise FlightControlError(f"Unexpected error running console command: {e}")


    # --- Internal Methods ---

    def _get_access_token(self) -> str:
        with self._token_lock:
            now = time.time()
            if self._access_token and now < self._token_expiry - 60:
                self.logger.debug("Using cached access token")
                return self._access_token

            self.logger.debug("Refreshing OIDC access token")
            try:
                resp = requests.post(
                    f"{self.config.oidc_token_url}",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.config.refresh_token,
                        "client_id": self.config.client_id,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    verify=self.config.get_ssl_verify(),
                )
                resp.raise_for_status()
                data = resp.json()
                self._access_token = data["access_token"]
                self._token_expiry = now + data.get("expires_in", 3600)
                self.logger.info("Successfully refreshed OIDC access token")
                return self._access_token
            except requests.exceptions.RequestException as e:
                self.logger.error("Failed to refresh OIDC token - network error: %s", e)
                if hasattr(e, 'response') and e.response is not None:
                    self.logger.error("Response status: %s, body: %s", e.response.status_code, e.response.text)
                    raise AuthenticationError(f"Failed to refresh OIDC token: HTTP {e.response.status_code}")
                else:
                    raise AuthenticationError(f"Failed to refresh OIDC token: {e}")
            except KeyError as e:
                self.logger.error("Invalid OIDC token response - missing field: %s", e)
                raise AuthenticationError(f"Invalid OIDC token response: missing {e}")
            except Exception as e:
                self.logger.error("Unexpected error during token refresh: %s", e)
                raise AuthenticationError(f"Failed to refresh OIDC token: {e}")

    def _query_resources(
        self,
        resource: str,
        *,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        url = f"{self.config.api_base_url}/api/v1/{resource}"
        items: List[Dict[str, Any]] = []
        continue_token: Optional[str] = None
        
        self.logger.debug("Querying %s with label_selector=%s, field_selector=%s, limit=%s", 
                         resource, label_selector, field_selector, limit)
        
        try:
            headers = {
                "Authorization": f"Bearer {self._get_access_token()}"
            }
        except AuthenticationError:
            self.logger.error("Authentication failed for %s query", resource)
            raise

        page_count = 0
        while True:
            page_count += 1
            params = {}
            if label_selector:
                params["labelSelector"] = label_selector
            if field_selector:
                params["fieldSelector"] = field_selector
            if continue_token:
                params["continue"] = continue_token

            self.logger.debug("Fetching page %d for %s", page_count, resource)
            
            try:
                resp = requests.get(url, headers=headers, params=params, verify=self.config.get_ssl_verify())
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.HTTPError as e:
                self.logger.error("HTTP error querying %s: %s %s", resource, e.response.status_code, e.response.reason)
                if e.response.status_code == 401:
                    raise AuthenticationError(f"Authentication failed for {resource} query: {e}")
                elif e.response.status_code == 403:
                    raise APIError(f"Access denied for {resource} query: {e}", e.response.status_code)
                elif e.response.status_code == 404:
                    raise APIError(f"Resource not found: {resource}", e.response.status_code)
                else:
                    raise APIError(f"Failed to query {resource}: HTTP {e.response.status_code}", 
                                 e.response.status_code, e.response.text)
            except requests.exceptions.RequestException as e:
                self.logger.error("Network error querying %s: %s", resource, e)
                raise APIError(f"Network error querying {resource}: {e}")
            except ValueError as e:
                self.logger.error("Invalid JSON response from %s: %s", resource, e)
                raise APIError(f"Invalid JSON response from {resource}: {e}")
            except Exception as e:
                self.logger.error("Unexpected error querying %s: %s", resource, e)
                raise APIError(f"Unexpected error querying {resource}: {e}")

            page_items = data.get("items", [])
            items.extend(page_items)
            
            self.logger.debug("Fetched %d items from page %d of %s", len(page_items), page_count, resource)

            if limit and len(items) >= limit:
                result = items[:limit]
                self.logger.info("Successfully queried %s: %d items (limited to %d)", resource, len(result), limit)
                return result

            continue_token = data.get("continue")
            if not continue_token:
                break

        self.logger.info("Successfully queried %s: %d items total", resource, len(items))
        return items
