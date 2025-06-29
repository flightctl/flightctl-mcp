# mcp-server

Model Context Protocol (MCP) server for Flight Control

---

## Overview

The **MCP server** provides a read-only API layer for querying and retrieving contextual information about devices and fleets managed by [Flight Control](https://github.com/flightctl/flightctl).  
It is designed for safe external integration, reporting, and automation, exposing a REST API that supports filtering and selector-based queries. The MCP server leverages the [flightctl-python-client](https://github.com/flightctl/flightctl-python-client) for backend communication and enforces authentication compatible with Flight Control’s authorization model.

---

## Building locally

To build the container image locally using Podman, run:

```sh
podman build -t mcp-server:latest .
```

This will create a local image named `mcp-server:latest` that you can use to run the server.

---

## Running with Podman or Docker

### Example: Using Automatic Configuration (Recommended)

If you've run `flightctl login`, you can mount the config directory:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "~/.config/flightctl:/root/.config/flightctl:ro",
        "-e", "MCP_TRANSPORT",
        "localhost/mcp-server:latest"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Example: Using Environment Variables

For environments where mounting the config file isn't possible:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "API_BASE_URL",
        "-e", "OIDC_TOKEN_URL",
        "-e", "OIDC_CLIENT_ID",
        "-e", "REFRESH_TOKEN",
        "-e", "INSECURE_SKIP_VERIFY",
        "-e", "LOG_LEVEL",
        "-e", "MCP_TRANSPORT",
        "localhost/mcp-server:latest"
      ],
      "env": {
        "API_BASE_URL": "https://api.flightctl.example.com",
        "OIDC_TOKEN_URL": "https://auth.flightctl.example.com/realms/flightctl/protocol/openid-connect/token",
        "OIDC_CLIENT_ID": "flightctl",
        "REFRESH_TOKEN": "REDACTED",
        "INSECURE_SKIP_VERIFY": "false",
        "LOG_LEVEL": "INFO",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## Authentication Setup

The MCP server uses OIDC/OAuth2 refresh tokens for authentication. To obtain the required credentials:

1. **OIDC_TOKEN_URL**: This is typically in the format `https://your-auth-server/realms/your-realm/protocol/openid-connect/token`
   - If you only have the base realm URL (e.g., `https://auth.example.com/realms/flightctl`), the server will automatically append `/protocol/openid-connect/token`

2. **REFRESH_TOKEN**: Obtain this from your Flight Control authentication system
   - This token should have appropriate permissions to read Flight Control resources

3. **OIDC_CLIENT_ID**: Usually `flightctl` (this is the default if not specified)

---

## Configuration

The MCP server supports two configuration methods:

### 1. Automatic Configuration (Recommended)
If you've run `flightctl login`, the server will automatically read configuration from `~/.config/flightctl/client.yaml`. This includes:
- API server URL
- OIDC authentication settings
- SSL certificate configuration
- Refresh tokens

### 2. Environment Variable Configuration
The following environment variables can override or supplement the automatic configuration:

- **API_BASE_URL:** Base URL for the Flight Control API (e.g., `https://api.flightctl.example.com`) - **Optional** (read from config file)
- **OIDC_TOKEN_URL:** Full URL to the OIDC token endpoint (e.g., `https://auth.flightctl.example.com/realms/flightctl/protocol/openid-connect/token`) - **Optional** (read from config file)
- **OIDC_CLIENT_ID:** OIDC client identifier (defaults to `flightctl`) - **Optional**
- **REFRESH_TOKEN:** OAuth2 refresh token for authentication - **Optional** (read from config file)
- **INSECURE_SKIP_VERIFY:** Skip SSL certificate verification (`true`/`false`) - **Optional** (read from config file)
- **CA_CERT_PATH:** Path to custom CA certificate file for SSL verification - **Optional**
- **LOG_LEVEL:** Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) - **Optional** (defaults to `INFO`)
- **MCP_TRANSPORT:** Transport mechanism for input/output communication (`stdio` for standard input/output) - **Optional**

### SSL Certificate Handling
The server properly handles SSL certificates in the following priority:
1. **Custom CA Certificate**: If `CA_CERT_PATH` is set, uses the specified certificate file
2. **Skip SSL Verification**: If `INSECURE_SKIP_VERIFY=true`, disables certificate verification (useful for development)
3. **System CA Bundle**: Uses the system's default certificate authority bundle (production default)

### Logging
The server uses file-based logging to avoid conflicts with the MCP protocol on stdio:
- **Log Location**: `~/.local/share/flightctl-mcp/flightctl-mcp.log`
- **Log Rotation**: Automatic rotation at 10MB with 5 backup files
- **Log Levels**: Configurable via `LOG_LEVEL` environment variable
- **Structured Logging**: Includes timestamps, component names, and detailed error context

### Error Handling
The server provides robust error handling:
- **Specific Exceptions**: Uses typed exceptions (`AuthenticationError`, `APIError`, `FlightControlError`)
- **Detailed Logging**: All errors are logged with full context
- **No Silent Failures**: API errors are properly reported to the MCP client
- **Graceful Degradation**: Clear error messages help with troubleshooting

---

## Features

- Read-only querying of **devices**, **fleets**, **events**, **enrollment requests**, **repositories**, and **resource syncs** from Flight Control
- Support for filtering by labels and fields using Kubernetes-style selectors
- Context-rich JSON responses including metadata and links to related resources
- Secure OIDC/OAuth2 refresh token–based authentication
- Remote device console access for executing commands on managed devices
- Automatic pagination handling for large result sets

---

## Documentation

API endpoints, filtering options, and example requests will be described in the [docs/](docs/) directory or in the OpenAPI specification.

---

## License

This project is open source. See [LICENSE](LICENSE) for details.

---

## Contributing

Issues and pull requests are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---
