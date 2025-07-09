import os
from typing import List, Dict, Any, Literal
from mcp.server.fastmcp import FastMCP
from resource_queries import FlightControlClient, Configuration, setup_logging
from cli import FlightctlCLI

# Initialize logging first (before any other components)
setup_logging()

mcp = FastMCP("mcp-server")

# Global variables for lazy initialization
_client = None
_cli = None


def get_client():
    """Get or create the FlightControlClient instance."""
    global _client
    if _client is None:
        config = Configuration()
        _client = FlightControlClient(config)
    return _client


def get_cli():
    """Get or create the FlightctlCLI instance."""
    global _cli
    if _cli is None:
        config = Configuration()
        _cli = FlightctlCLI(config.api_base_url)  # type: ignore
        _cli.download()
    return _cli


@mcp.tool()
async def query_devices(
    label_selector: str = "",
    field_selector: str = "",
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Query Flight Control for devices using label and field selectors.

    Label Selectors:
        Label selectors filter resources based on metadata labels. They support:
        - '=': Exact match (e.g., "env=prod")
        - '!=': Not equal (e.g., "tier!=frontend")
        - 'in (...)': Value is in a list (e.g., "region in (us, eu)")

    Field Selectors:
        Field selectors filter based on resource attributes and support the following fields for Devices:
        - metadata.alias
        - metadata.creationTimestamp
        - metadata.name
        - metadata.nameOrAlias
        - metadata.owner
        - status.applicationsSummary.status
        - status.lastSeen
        - status.lifecycle.status
        - status.summary.status
        - status.updated.status

        Supported operators:
        - Existence:        <field>, !<field>
        - Equality:         =, ==, !=
        - Comparison:       >, >=, <, <=
        - Set-based:        in (...), notin (...)
        - Containment:      contains, notcontains

        Operator Support by Field Type:
        - **String**:     =, ==, !=, in, notin, contains, notcontains, exists, !exists
        - **Timestamp**:  =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Number**:     =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Boolean**:    =, ==, !=, in, notin, exists, !exists
        - **Array**:      contains, notcontains, in, notin, exists, !exists

    Args:
        label_selector (str): Label selector string, e.g., "location=lab"
        field_selector (str): Field selector string, e.g., "status.lifecycle.status=Active"
        limit (int): Maximum number of results to return. Pagination is automatic.

    Returns:
        List[Dict]: A list of full Device resource dictionaries in Flight Control API format.
        Each dictionary contains:
            - apiVersion (str): API version of the resource (e.g., "v1").
            - kind (str): Resource kind (e.g., "Device").
            - metadata (dict): Standard Kubernetes-style metadata, including:
                - name (str): Name of the device.
                - labels (dict): Key-value labels assigned to the device.
                - owner (str): Owning resource (e.g., "Fleet/core").
                - creationTimestamp (str): Creation time (RFC 3339).
                - annotations, generation, deletionTimestamp, etc.
            - spec (dict): Desired state configuration of the device, including:
                - applications, config, os, systemd, resources, updatePolicy, etc.
            - status (dict): Current state of the device as reported by the agent, including:
                - lastSeen (str): Timestamp of last heartbeat.
                - applicationsSummary.status (str)
                - lifecycle.status (str)
                - summary.status (str)
                - updated.status (str)
                - conditions, config, os, resources, systemInfo, etc.

    Raises:
        RuntimeError: If a network or HTTP error occurs while querying the MCP server.
    """
    return get_client().query_devices(label_selector=label_selector, field_selector=field_selector, limit=limit)


@mcp.tool()
async def query_fleets(label_selector: str = "", field_selector: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Query Flight Control for fleets using label and field selectors.

    Label Selectors:
        Label selectors filter resources based on metadata labels. They support:
        - '=': Exact match (e.g., "env=prod")
        - '!=': Not equal (e.g., "tier!=frontend")
        - 'in (...)': Value is in a list (e.g., "region in (us, eu)")

    Field Selectors:
        Field selectors filter based on resource attributes and support the following fields for Devices:
        - metadata.creationTimestamp
        - metadata.name
        - metadata.owner
        - spec.template.spec.os.image

        Supported operators:
        - Existence:        <field>, !<field>
        - Equality:         =, ==, !=
        - Comparison:       >, >=, <, <=
        - Set-based:        in (...), notin (...)
        - Containment:      contains, notcontains

        Operator Support by Field Type:
        - **String**:     =, ==, !=, in, notin, contains, notcontains, exists, !exists
        - **Timestamp**:  =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Number**:     =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Boolean**:    =, ==, !=, in, notin, exists, !exists
        - **Array**:      contains, notcontains, in, notin, exists, !exists

    Args:
        label_selector (str): Label selector string, e.g., "location=lab"
        field_selector (str): Field selector string, e.g., "status.lifecycle.status=Active"
        limit (int): Maximum number of results to return. Pagination is automatic.

    Returns:
        List[Dict]: A list of full Fleet resource dictionaries in Flight Control API format.
        Each dictionary contains:
            - apiVersion (str): API version of the resource (e.g., "v1").
            - kind (str): Resource kind (e.g., "Fleet").
            - metadata (dict): Standard Kubernetes-style metadata, including:
                - name (str): Name of the fleet.
                - labels (dict): Key-value labels for targeting devices.
                - owner (str): Owning resource in "kind/name" format.
                - creationTimestamp (str): When the fleet was created (RFC 3339).
                - annotations, generation, resourceVersion, etc.
            - spec (dict): Desired state of the fleet, including:
                - rolloutPolicy (dict): Configuration for device rollout behavior.
                - selector (dict): Label selector for identifying devices.
                - template (dict): Desired metadata and spec to apply to devices.
            - status (dict, optional): Reported status of the fleet, including:
                - conditions (list): Condition objects indicating current status.
                - devicesSummary (dict): Aggregated health/status of member devices.
                - rollout (dict): Current status of any ongoing rollout operation.

    Raises:
        RuntimeError: If a network or HTTP error occurs while querying the MCP server.
    """
    return get_client().query_fleets(label_selector=label_selector, field_selector=field_selector, limit=limit)


@mcp.tool()
async def query_events(field_selector: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Query Flight Control for events using field selectors.

    Field Selectors:
        Field selectors filter based on resource attributes and support the following fields for Devices:
        - actor
        - involvedObject.kind
        - involvedObject.name
        - metadata.creationTimestamp
        - metadata.name
        - metadata.owner
        - reason
        - type

        Supported operators:
        - Existence:        <field>, !<field>
        - Equality:         =, ==, !=
        - Comparison:       >, >=, <, <=
        - Set-based:        in (...), notin (...)
        - Containment:      contains, notcontains

        Operator Support by Field Type:
        - **String**:     =, ==, !=, in, notin, contains, notcontains, exists, !exists
        - **Timestamp**:  =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Number**:     =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Boolean**:    =, ==, !=, in, notin, exists, !exists
        - **Array**:      contains, notcontains, in, notin, exists, !exists

    Args:
        field_selector (str): Field selector string, e.g., "status.lifecycle.status=Active"
        limit (int): Maximum number of results to return. Pagination is automatic.

    Returns:
        List[Dict]: A list of Event resource dictionaries in Flight Control API format.
        Each dictionary contains:
            - apiVersion (str): API version of the event resource (e.g., "v1").
            - kind (str): Resource kind (always "Event").
            - metadata (dict): Standard metadata fields, including:
                - name (str): Unique name of the event.
                - creationTimestamp (str): Timestamp when the event occurred.
                - labels, annotations, etc.
            - involvedObject (dict): Reference to the resource this event is about:
                - kind (str): Resource kind (e.g., "Device", "Fleet", etc.).
                - name (str): Resource name.
            - actor (str): The entity that triggered the event (e.g., "user:alice", "service:syncer").
            - type (str): The event type ("Normal" or "Warning").
            - reason (str): Machine-readable reason for the event (e.g., "DeviceUpdated").
            - message (str): Human-readable message describing what happened.
            - source (dict): The component that generated the event (e.g., "fleet-controller").
            - details (dict, optional): Structured event-specific details based on the event reason/type.

    Raises:
        RuntimeError: If a network or HTTP error occurs while querying the MCP server.
    """
    return get_client().query_events(field_selector=field_selector, limit=limit)


@mcp.tool()
async def query_enrollment_requests(
    label_selector: str = "", field_selector: str = "", limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Query Flight Control for enrollment requests using label and field selectors.

    Label Selectors:
        Label selectors filter resources based on metadata labels. They support:
        - '=': Exact match (e.g., "env=prod")
        - '!=': Not equal (e.g., "tier!=frontend")
        - 'in (...)': Value is in a list (e.g., "region in (us, eu)")

    Field Selectors:
        Field selectors filter based on resource attributes and support the following fields for Devices:
        - metadata.creationTimestamp
        - metadata.name
        - metadata.owner
        - status.approval.approved
        - status.certificate

        Supported operators:
        - Existence:        <field>, !<field>
        - Equality:         =, ==, !=
        - Comparison:       >, >=, <, <=
        - Set-based:        in (...), notin (...)
        - Containment:      contains, notcontains

        Operator Support by Field Type:
        - **String**:     =, ==, !=, in, notin, contains, notcontains, exists, !exists
        - **Timestamp**:  =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Number**:     =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Boolean**:    =, ==, !=, in, notin, exists, !exists
        - **Array**:      contains, notcontains, in, notin, exists, !exists

    Args:
        label_selector (str): Label selector string, e.g., "location=lab"
        field_selector (str): Field selector string, e.g., "status.lifecycle.status=Active"
        limit (int): Maximum number of results to return. Pagination is automatic.

    Returns:
        List[Dict]: A list of EnrollmentRequest resource dictionaries in Flight Control API format.
        Each dictionary contains:
            - apiVersion (str): API version of the resource (e.g., "v1").
            - kind (str): Resource kind (e.g., "EnrollmentRequest").
            - metadata (dict): Standard resource metadata, including:
                - name (str): Unique name of the enrollment request.
                - creationTimestamp (str): When the request was submitted.
                - labels, annotations, etc.
            - spec (dict): Desired state of the enrollment request, including:
                - csr (str): PEM-encoded certificate signing request.
                - deviceStatus (dict, optional): Status info reported by the device.
                - labels (dict, optional): Labels to apply upon approval.
            - status (dict, optional): Current status of the request, including:
                - approval (dict): Approval status details (approved flag, approver, timestamp).
                - certificate (str, optional): Signed certificate if approved.
                - conditions (list): Lifecycle or validation conditions.

    Raises:
        RuntimeError: If a network or HTTP error occurs while querying the MCP server.
    """
    return get_client().query_enrollment_requests(
        label_selector=label_selector, field_selector=field_selector, limit=limit
    )


@mcp.tool()
async def query_repositories(
    label_selector: str = "", field_selector: str = "", limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Query Flight Control for repositories using label and field selectors.

    Label Selectors:
        Label selectors filter resources based on metadata labels. They support:
        - '=': Exact match (e.g., "env=prod")
        - '!=': Not equal (e.g., "tier!=frontend")
        - 'in (...)': Value is in a list (e.g., "region in (us, eu)")

    Field Selectors:
        Field selectors filter based on resource attributes and support the following fields for Devices:
        - metadata.creationTimestamp
        - metadata.name
        - metadata.owner
        - spec.type
        - spec.url

        Supported operators:
        - Existence:        <field>, !<field>
        - Equality:         =, ==, !=
        - Comparison:       >, >=, <, <=
        - Set-based:        in (...), notin (...)
        - Containment:      contains, notcontains

        Operator Support by Field Type:
        - **String**:     =, ==, !=, in, notin, contains, notcontains, exists, !exists
        - **Timestamp**:  =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Number**:     =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Boolean**:    =, ==, !=, in, notin, exists, !exists
        - **Array**:      contains, notcontains, in, notin, exists, !exists

    Args:
        label_selector (str): Label selector string, e.g., "location=lab"
        field_selector (str): Field selector string, e.g., "status.lifecycle.status=Active"
        limit (int): Maximum number of results to return. Pagination is automatic.

    Returns:
        List[Dict]: A list of Repository resource dictionaries in Flight Control API format.
        Each dictionary contains:
            - apiVersion (str): API version of the resource (e.g., "v1").
            - kind (str): Resource kind (e.g., "Repository").
            - metadata (dict): Standard Kubernetes-style metadata, including:
                - name (str): Repository name.
                - creationTimestamp (str): Time the repository was created.
                - labels, annotations, etc.
            - spec (dict): Type-specific specification for the repository. The structure depends on the repository type:
                - For `http` repositories: contains `type`, `url`, `httpConfig`, and optional `validationSuffix`.
                - For `ssh` repositories: contains `type`, `url`, and `sshConfig`.
                - For `generic` repositories: contains `type` and `url`.
            - status (dict, optional): Current state of the repository, including:
                - conditions (list): Condition entries indicating health, validation results, etc.

    Raises:
        RuntimeError: If a network or HTTP error occurs while querying the MCP server.
    """
    return get_client().query_repositories(label_selector=label_selector, field_selector=field_selector, limit=limit)


@mcp.tool()
async def query_resource_syncs(
    label_selector: str = "", field_selector: str = "", limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Query Flight Control for resource syncs using label and field selectors.

    Label Selectors:
        Label selectors filter resources based on metadata labels. They support:
        - '=': Exact match (e.g., "env=prod")
        - '!=': Not equal (e.g., "tier!=frontend")
        - 'in (...)': Value is in a list (e.g., "region in (us, eu)")

    Field Selectors:
        Field selectors filter based on resource attributes and support the following fields for Devices:
        - metadata.creationTimestamp
        - metadata.name
        - metadata.owner
        - spec.repository

        Supported operators:
        - Existence:        <field>, !<field>
        - Equality:         =, ==, !=
        - Comparison:       >, >=, <, <=
        - Set-based:        in (...), notin (...)
        - Containment:      contains, notcontains

        Operator Support by Field Type:
        - **String**:     =, ==, !=, in, notin, contains, notcontains, exists, !exists
        - **Timestamp**:  =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Number**:     =, ==, !=, >, >=, <, <=, in, notin, exists, !exists
        - **Boolean**:    =, ==, !=, in, notin, exists, !exists
        - **Array**:      contains, notcontains, in, notin, exists, !exists

    Args:
        label_selector (str): Label selector string, e.g., "location=lab"
        field_selector (str): Field selector string, e.g., "status.lifecycle.status=Active"
        limit (int): Maximum number of results to return. Pagination is automatic.

    Returns:
        List[Dict]: A list of ResourceSync resource dictionaries in Flight Control API format.
        Each dictionary contains:
            - apiVersion (str): API version of the resource (e.g., "v1").
            - kind (str): Resource kind (e.g., "ResourceSync").
            - metadata (dict): Standard metadata including:
                - name (str): Name of the ResourceSync object.
                - creationTimestamp (str): When the sync request was created.
                - labels, annotations, etc.
            - spec (dict): Desired source of resource definitions to sync, including:
                - repository (str): Name of the repository to sync from.
                - path (str): Path to the file or directory in the repo.
                - targetRevision (str): Git revision (branch, tag, or commit).
            - status (dict, optional): Current sync state, including:
                - conditions (list): Current status conditions (e.g., success, failure).
                - observedCommit (str, optional): Git commit that was last synced.
                - observedGeneration (int, optional): Generation that was last processed.

    Raises:
        RuntimeError: If a network or HTTP error occurs while querying the MCP server.
    """
    return get_client().query_resource_syncs(label_selector=label_selector, field_selector=field_selector, limit=limit)


@mcp.tool()
async def run_command_on_device(device_name: str, command: str) -> str:
    """
    Runs a Linux console command on a specific device using the Flightctl CLI.

    This tool allows the MCP server to remotely execute shell commands on an edge device
    managed by Flight Control. The Flightctl CLI is downloaded at runtime to ensure it
    matches the API server version. The command is executed in a remote console session
    using `flightctl console device/<device_name> -- <command>`.

    This is useful for:
    - Retrieving live system information (e.g., `journalctl`, `ps`, `df`, `cat /proc/meminfo`)
      Specifically, you can find information about the agent managing the device using `journalctl -u flightctl-agent`
    - Performing diagnostics or ad hoc checks
    - Making on-device changes (e.g., restarting services or applying quick fixes)

    Args:
        device_name (str): The name of the target device resource.
        command (str): The Linux shell command to run on the device.

    Returns:
        str: The standard output (stdout) of the command execution.

    Raises:
        RuntimeError: If the CLI is not found or the command fails to execute.
    """
    return get_client().run_console_command(get_cli().cli_path, device_name, command)


if __name__ == "__main__":
    # Get transport configuration from environment variables
    transport_env = os.environ.get("MCP_TRANSPORT", "stdio")

    # Validate transport type
    if transport_env not in ["stdio", "sse", "streamable-http"]:
        transport_env = "stdio"

    transport: Literal["stdio", "sse", "streamable-http"] = transport_env  # type: ignore

    # Run the server with appropriate transport
    if transport == "stdio":
        mcp.run(transport=transport)
    else:
        # For HTTP-based transports, FastMCP will use environment variables or defaults
        # Ensure the environment variables are set for FastMCP to pick up
        if "MCP_HOST" not in os.environ:
            os.environ["MCP_HOST"] = "127.0.0.1"
        if "MCP_PORT" not in os.environ:
            os.environ["MCP_PORT"] = "8000"
        if "MCP_PATH" not in os.environ:
            os.environ["MCP_PATH"] = "/mcp"

        # Run with HTTP transport
        mcp.run(transport=transport)
