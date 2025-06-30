# mcp-server

Model Context Protocol (MCP) server for Flight Control

---

## Overview

The **MCP server** provides a read-only API layer for querying and retrieving contextual information about devices and fleets managed by [Flight Control](https://github.com/flightctl/flightctl).
It is designed for safe external integration, reporting, and automation, exposing a REST API that supports filtering and selector-based queries. The MCP server leverages the [flightctl-python-client](https://github.com/flightctl/flightctl-python-client) for backend communication and enforces authentication compatible with Flight Control's authorization model.

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

If you've run `flightctl login`, you can mount the config directory. **Note**: The server now defaults to `streamable-http` transport for better web-based integration.

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-p", "8000:8000",
        "-v", "~/.config/flightctl:/root/.config/flightctl:ro",
        "-e", "MCP_TRANSPORT",
        "-e", "MCP_HOST",
        "-e", "MCP_PORT",
        "localhost/mcp-server:latest"
      ],
      "env": {
        "MCP_TRANSPORT": "streamable-http",
        "MCP_HOST": "0.0.0.0",
        "MCP_PORT": "8000"
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
        "-p", "8000:8000",
        "-e", "API_BASE_URL",
        "-e", "OIDC_TOKEN_URL",
        "-e", "OIDC_CLIENT_ID",
        "-e", "REFRESH_TOKEN",
        "-e", "INSECURE_SKIP_VERIFY",
        "-e", "LOG_LEVEL",
        "-e", "MCP_TRANSPORT",
        "-e", "MCP_HOST",
        "-e", "MCP_PORT",
        "localhost/mcp-server:latest"
      ],
      "env": {
        "API_BASE_URL": "https://api.flightctl.example.com",
        "OIDC_TOKEN_URL": "https://auth.flightctl.example.com/realms/flightctl/protocol/openid-connect/token",
        "OIDC_CLIENT_ID": "flightctl",
        "REFRESH_TOKEN": "REDACTED",
        "INSECURE_SKIP_VERIFY": "false",
        "LOG_LEVEL": "INFO",
        "MCP_TRANSPORT": "streamable-http",
        "MCP_HOST": "0.0.0.0",
        "MCP_PORT": "8000"
      }
    }
  }
}
```

---

## Transport Configuration

The MCP server now supports three transport methods with `streamable-http` as the default:

### Streamable HTTP (Default - Recommended)
- **Best for**: Web-based deployments, microservices, exposing MCP over a network
- **Default endpoint**: `http://127.0.0.1:8000/mcp`
- **Configuration**: Set `MCP_TRANSPORT=streamable-http` (default)

### STDIO
- **Best for**: Local tools, command-line scripts, integrations with clients like Claude Desktop
- **Configuration**: Set `MCP_TRANSPORT=stdio`

### SSE (Server-Sent Events)
- **Best for**: Legacy deployments that specifically require SSE
- **Configuration**: Set `MCP_TRANSPORT=sse`
- **Default endpoint**: `http://127.0.0.1:8000/sse`

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

### 3. MCP Transport Configuration
The following environment variables control the MCP server transport and network settings:

- **MCP_TRANSPORT:** Transport mechanism (`stdio`, `sse`, `streamable-http`) - **Optional** (defaults to `streamable-http`)
- **MCP_HOST:** Host to bind to for HTTP transports - **Optional** (defaults to `127.0.0.1`)
- **MCP_PORT:** Port to listen on for HTTP transports - **Optional** (defaults to `8000`)
- **MCP_PATH:** Path for the MCP endpoint - **Optional** (defaults to `/mcp` for streamable-http)
- **MCP_LOG_LEVEL:** Server log level (`debug`, `info`, `warning`, `error`) - **Optional** (defaults to `info`)

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

---

## Running the Server

### Local Development
```bash
# Run with default streamable-http transport
python main.py

# Run with custom configuration
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8080 python main.py

# Run with stdio transport (for Claude Desktop integration)
MCP_TRANSPORT=stdio python main.py
```

### Accessing the HTTP Endpoint
When running with HTTP transport, the MCP endpoint will be available at:
- **Streamable HTTP**: `http://127.0.0.1:8000/mcp` (default)
- **SSE**: `http://127.0.0.1:8000/sse`

### Client Connection Examples

#### For HTTP clients (streamable-http):
```python
from fastmcp import Client

# Connect to streamable-http server
client = Client("http://127.0.0.1:8000/mcp")
```

#### For Claude Desktop (stdio):
```json
{
  "mcpServers": {
    "flightctl": {
      "command": "python",
      "args": ["main.py"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## API Endpoints

The MCP server exposes the following tool endpoints:

### Device Management
- `query_devices`: Query and filter devices using label and field selectors
- `run_command_on_device`: Execute Linux commands on specific devices

### Fleet Management
- `query_fleets`: Query and filter fleet configurations

### Events and Monitoring
- `query_events`: Query system events and audit logs

### Enrollment
- `query_enrollment_requests`: Query device enrollment requests

### Configuration Management
- `query_repositories`: Query configuration repositories
- `query_resource_syncs`: Query resource synchronization status

---

## Testing

### Live Instance Testing
To test against your actual Flight Control instance:

```bash
# Ensure you have logged in first
flightctl login

# Run the live integration test
python test_live_instance.py
```

### Unit Testing
```bash
# Run unit tests
python -m pytest test_flightctl_mcp.py -v

# Run with coverage
python -m pytest test_flightctl_mcp.py --cov=resource_queries --cov=main --cov=cli --cov-report=html
```

### MCP Client Testing
```bash
# Test the MCP server with a simple client
python -c "
from fastmcp import Client
import asyncio

async def test():
    client = Client('http://127.0.0.1:8000/mcp')
    async with client:
        tools = await client.list_tools()
        print(f'Available tools: {[t.name for t in tools]}')

asyncio.run(test())
"
```

---

## Troubleshooting

### Common Issues

1. **Server not starting**: Check if the port is already in use
   ```bash
   lsof -i :8000
   ```

2. **Authentication failures**: Verify your Flight Control credentials
   ```bash
   flightctl login
   ```

3. **Connection refused**: Ensure the server is running and accessible
   ```bash
   curl -v http://127.0.0.1:8000/mcp
   ```

4. **Transport issues**: Verify the transport configuration matches your client
   ```bash
   # Check server logs
   tail -f ~/.local/share/flightctl-mcp/flightctl-mcp.log
   ```

### Debug Mode
Enable debug logging for more detailed information:
```bash
MCP_LOG_LEVEL=debug LOG_LEVEL=DEBUG python main.py
```

---

## Migration from STDIO

If you're migrating from the previous stdio-only version:

1. **Update your client configuration** to use HTTP endpoints instead of stdio
2. **Set environment variables** for host/port configuration if needed
3. **Update firewall rules** if running on a remote server
4. **Test the connection** using the provided client examples

The server will still support stdio transport if you set `MCP_TRANSPORT=stdio`, maintaining backward compatibility.

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
