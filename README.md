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

Example configuration for running with Podman:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "FC_API_BASE_URL",
        "-e", "FC_API_TOKEN",
        "-e", "MCP_TRANSPORT",
        "localhost/mcp-server:latest"
      ],
      "env": {
        "FC_API_BASE_URL": "https://api.flightctl.example.com",
        "FC_API_TOKEN": "REDACTED",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## Configuration

The following environment variables are used to configure the MCP server:

- **FC_API_BASE_URL:** Base URL for the Flight Control API (e.g., `https://api.flightctl.example.com`)
- **FC_API_TOKEN:** API token (bearer token) with read-only permissions for accessing Flight Control resources
- **MCP_TRANSPORT:** Transport mechanism for input/output communication (`stdio` for standard input/output)

---

## Features

- Read-only querying of **devices** and **fleets** from Flight Control
- Support for filtering by labels and fields
- Context-rich JSON responses including metadata and links to related resources
- Secure, bearer token–based authentication

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
