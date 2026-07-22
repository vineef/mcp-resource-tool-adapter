from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

ResourceHandler = Callable[[], Any]
F = TypeVar("F", bound=Callable[..., Any])


class ResourceToolAdapter:
    """
    Exposes FastMCP resources through generic tools for clients that do not
    implement the MCP resources/read capability.
    """

    def __init__(
        self,
        mcp: Any,
        *,
        read_tool_name: str = "read_resource",
        list_tool_name: str = "list_resources",
    ) -> None:
        self._mcp = mcp
        self._handlers: dict[str, ResourceHandler] = {}
        self._read_tool_name = read_tool_name
        self._list_tool_name = list_tool_name
        self._read_tool_registered = False
        self._list_tool_registered = False

    @staticmethod
    def _typed_decorator(decorator: Any) -> Callable[[F], F]:
        """Convert a dynamically typed FastMCP decorator to a typed decorator."""
        return cast(Callable[[F], F], decorator)

    def resource(self, uri: str) -> Callable[[ResourceHandler], ResourceHandler]:
        """Register an MCP resource and its local resolver."""
        if not uri or "://" not in uri:
            raise ValueError(
                f"Resource URI must be non-empty and contain '://'. Received: {uri!r}"
            )

        def decorator(func: ResourceHandler) -> ResourceHandler:
            if uri in self._handlers:
                raise ValueError(f"Resource URI already registered: {uri!r}")

            @wraps(func)
            def resource_wrapper() -> Any:
                return func()

            register_resource = self._typed_decorator(self._mcp.resource(uri))
            registered_handler = register_resource(resource_wrapper)

            self._handlers[uri] = registered_handler
            return registered_handler

        return decorator

    def read(self, uri: str) -> Any:
        """Read a previously registered resource by URI."""
        try:
            handler = self._handlers[uri]
        except KeyError as exc:
            available = ", ".join(sorted(self._handlers)) or "<none>"
            raise ValueError(
                f"Unknown resource URI: {uri!r}. Available resources: {available}"
            ) from exc

        return handler()

    def list_resources(self) -> list[dict[str, str]]:
        """List resource metadata for tool-only clients."""
        return [
            {
                "uri": uri,
                "name": handler.__name__,
                "description": (handler.__doc__ or "").strip(),
            }
            for uri, handler in sorted(self._handlers.items())
        ]

    def register_read_tool(self) -> None:
        """Register the generic resource-read compatibility tool."""
        if self._read_tool_registered:
            return

        def read_resource(uri: str) -> Any:
            """
            Read a registered MCP resource by URI.

            Use this tool when the MCP client cannot call resources/read.
            """
            return self.read(uri)

        register_tool = self._typed_decorator(self._mcp.tool(self._read_tool_name))
        register_tool(read_resource)
        self._read_tool_registered = True

    def register_list_tool(self) -> None:
        """Register the resource discovery compatibility tool."""
        if self._list_tool_registered:
            return

        def list_registered_resources() -> list[dict[str, str]]:
            """List resource URIs available through read_resource."""
            return self.list_resources()

        register_tool = self._typed_decorator(self._mcp.tool(self._list_tool_name))
        register_tool(list_registered_resources)
        self._list_tool_registered = True

    def register_tools(self, *, include_list_tool: bool = True) -> None:
        """Register all compatibility tools."""
        self.register_read_tool()

        if include_list_tool:
            self.register_list_tool()
