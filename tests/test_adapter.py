import pytest

from mcp_resource_tool_adapter import ResourceToolAdapter


class FakeMCP:
    def resource(self, uri: str):
        def decorator(func):
            return func

        return decorator

    def tool(self, name: str):
        def decorator(func):
            return func

        return decorator


def test_reads_registered_resource() -> None:
    adapter = ResourceToolAdapter(FakeMCP())

    @adapter.resource("robot://current_state")
    def current_state() -> dict[str, str]:
        return {"status": "ready"}

    assert adapter.read("robot://current_state") == {"status": "ready"}


def test_lists_registered_resources() -> None:
    adapter = ResourceToolAdapter(FakeMCP())

    @adapter.resource("world://current_state")
    def world_state() -> dict[str, str]:
        """Current world state."""
        return {"map": "ready"}

    assert adapter.list_resources() == [
        {
            "uri": "world://current_state",
            "name": "world_state",
            "description": "Current world state.",
        }
    ]


def test_unknown_uri_raises_value_error() -> None:
    adapter = ResourceToolAdapter(FakeMCP())

    with pytest.raises(ValueError, match="Unknown resource URI"):
        adapter.read("missing://resource")


def test_duplicate_uri_is_rejected() -> None:
    adapter = ResourceToolAdapter(FakeMCP())

    @adapter.resource("robot://current_state")
    def first() -> dict[str, bool]:
        return {"first": True}

    with pytest.raises(ValueError, match="already registered"):

        @adapter.resource("robot://current_state")
        def second() -> dict[str, bool]:
            return {"second": True}
