# mcp-resource-tool-adapter

Expose MCP resources through generic tools for MCP clients and models that
cannot call `resources/read` directly.

## Why?

Some OpenAI-compatible LLM runtimes support tool calls but do not implement
the MCP resource protocol. This package keeps standard MCP resources available
while exposing a generic `read_resource(uri)` compatibility tool.

## Installation

```bash
pip install mcp-resource-tool-adapter
```

## Example

```python
from mcp.server.fastmcp import FastMCP
from mcp_resource_tool_adapter import ResourceToolAdapter

mcp = FastMCP("example-server")
resources = ResourceToolAdapter(mcp)

@resources.resource("robot://current_state")
def get_robot_state():
    return {"battery_percent": 87, "mode": "standing"}

resources.register_tools()

mcp.run(transport="stdio")
```

A tool-only client can then call:

```json
{
  "uri": "robot://current_state"
}
```

through the `read_resource` tool.

## Available compatibility tools

- `read_resource(uri)`: reads one registered resource.
- `list_resources()`: lists URIs that can be read through `read_resource`.

## Scope

This package does not handle robot control, ROS2, authentication, caching,
authorization, or resource freshness. Those remain responsibilities of the
application server.