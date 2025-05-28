import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-server")

API_BASE_URL = os.environ["API_BASE_URL"].rstrip("/")
API_KEY = os.environ.get("API_KEY")  # Bearer token

def get_auth_headers() -> Dict[str, str]:
    """Return HTTP headers including Authorization and Accept."""
    if not API_KEY:
        raise RuntimeError("API_KEY environment variable not set")
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

async def rest_get(
    path: str,
    params: Optional[Dict[str, Any]] = None
) -> Any:
    """Helper to GET from Flight Control API, with error handling."""
    url = f"{API_BASE_URL}{path}"
    headers = get_auth_headers()
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"HTTP error {exc.response.status_code} for {url}: {exc.response.text}"
            )
        except Exception as exc:
            raise RuntimeError(f"Error requesting {url}: {exc}")

@mcp.tool()
async def query_devices(
    label_selector: str = "",
    field_selector: str = "",
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Query Flight Control for devices, with optional label and field selectors.

    Args:
        label_selector: Label selector string, e.g., "location=lab"
        field_selector: Field selector string, e.g., "status.lifecycle.status=Active"
        limit: Max number of devices per request (pagination is automatic)

    Returns:
        List of device context dictionaries (resourceKind, resourceName, data, links, meta)

    Raises:
        RuntimeError: On HTTP/network errors.
    """
    path = "/api/v1/devices"
    params = {"limit": limit}
    if label_selector:
        params["labelSelector"] = label_selector
    if field_selector:
        params["fieldSelector"] = field_selector

    all_devices = []
    continue_token = None

    while True:
        if continue_token:
            params["continue"] = continue_token
        resp = await rest_get(path, params)
        items = resp.get("items", [])
        for device in items:
            metadata = device.get("metadata", {})
            context = {
                "resourceKind": "Device",
                "resourceName": metadata.get("name"),
                "data": device,
                "links": [
                    {"rel": "self", "href": f"/v1/devices/{metadata.get('name')}"}
                ],
                "meta": {
                    "created": metadata.get("creationTimestamp"),
                    "lastUpdated": metadata.get("updateTimestamp"),
                },
            }
            all_devices.append(context)
        continue_token = resp.get("metadata", {}).get("continue")
        if not continue_token:
            break
    return all_devices

@mcp.tool()
async def query_fleets(
    label_selector: str = "",
    field_selector: str = "",
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Query Flight Control for fleets, with optional label and field selectors.

    Args:
        label_selector: Label selector string, e.g., "env=prod"
        field_selector: Field selector string.
        limit: Max number of fleets per request (pagination is automatic)

    Returns:
        List of fleet context dictionaries (resourceKind, resourceName, data, links, meta)

    Raises:
        RuntimeError: On HTTP/network errors.
    """
    path = "/api/v1/fleets"
    params = {"limit": limit}
    if label_selector:
        params["labelSelector"] = label_selector
    if field_selector:
        params["fieldSelector"] = field_selector

    all_fleets = []
    continue_token = None

    while True:
        if continue_token:
            params["continue"] = continue_token
        resp = await rest_get(path, params)
        items = resp.get("items", [])
        for fleet in items:
            metadata = fleet.get("metadata", {})
            context = {
                "resourceKind": "Fleet",
                "resourceName": metadata.get("name"),
                "data": fleet,
                "links": [
                    {"rel": "self", "href": f"/v1/fleets/{metadata.get('name')}"}
                ],
                "meta": {
                    "created": metadata.get("creationTimestamp"),
                    "lastUpdated": metadata.get("updateTimestamp"),
                },
            }
            all_fleets.append(context)
        continue_token = resp.get("metadata", {}).get("continue")
        if not continue_token:
            break
    return all_fleets

if __name__ == "__main__":
    mcp.run(transport=os.environ.get("MCP_TRANSPORT", "stdio"))
