from mcp.server.fastmcp import FastMCP

from mcp_resource_tool_adapter import ResourceToolAdapter


def test_registers_resource_and_compatibility_tools() -> None:
    mcp = FastMCP("adapter-test")
    adapter = ResourceToolAdapter(mcp)

    @adapter.resource("robot://current_state")
    def get_robot_state() -> dict[str, str]:
        return {"status": "ready"}

    adapter.register_tools()

    assert adapter.read("robot://current_state") == {"status": "ready"}
    assert adapter.list_resources() == [
        {
            "uri": "robot://current_state",
            "name": "get_robot_state",
            "description": "",
        }
    ]