from __future__ import annotations

import os
import logging
from typing import Any, Callable
import uvicorn

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

# from mcp_obsidian import tools

load_dotenv()
logger = logging.getLogger("mcp-obsidian")


# def _ensure_env() -> None:
#     api_key = os.getenv("OBSIDIAN_API_KEY")
#     if not api_key:
#         raise ValueError(
#             f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}"
#         )


# def _to_schema_dict(schema: Any) -> dict[str, Any]:
#     """
#     Convert various schema representations to a plain dict.
#     Supports pydantic models (model_dump), plain dicts, or None.
#     """
#     if schema is None:
#         return {}
#     # pydantic v2 BaseModel
#     if hasattr(schema, "model_dump"):
#         try:
#             return schema.model_dump(by_alias=True)  # type: ignore[call-arg]
#         except Exception:
#             return schema.model_dump()  # type: ignore
#     if isinstance(schema, dict):
#         return schema
#     # Fallback: try attribute access common on typed classes
#     props = getattr(schema, "properties", None)
#     req = getattr(schema, "required", None)
#     out: dict[str, Any] = {}
#     if props is not None:
#         out["properties"] = props
#     if req is not None:
#         out["required"] = req
#     return out


# def _register_tools(mcp: FastMCP) -> None:
#     """
#     Register wrappers around existing tool handlers into FastMCP so we can run over HTTP.
#     Creates explicit parameter lists from each tool's JSON schema to satisfy FastMCP validation.
#     """
#     # Recreate the same handlers as in server.py
#     handlers: dict[str, tools.ToolHandler] = {
#         h.name: h
#         for h in [
#             tools.ListFilesInDirToolHandler(),
#             tools.ListFilesInVaultToolHandler(),
#             tools.GetFileContentsToolHandler(),
#             tools.SearchToolHandler(),
#             tools.PatchContentToolHandler(),
#             tools.AppendContentToolHandler(),
#             tools.PutContentToolHandler(),
#             tools.DeleteFileToolHandler(),
#             tools.ComplexSearchToolHandler(),
#             tools.BatchGetFileContentsToolHandler(),
#             tools.PeriodicNotesToolHandler(),
#             tools.RecentPeriodicNotesToolHandler(),
#             tools.RecentChangesToolHandler(),
#         ]
#     }

#     for tool_name, handler in handlers.items():
#         # Read the tool's declared schema to build a proper signature
#         try:
#             desc = handler.get_tool_description()
#         except Exception:
#             desc = None

#         # Try both camelCase and snake_case, and tolerate None
#         schema_obj = None
#         if desc is not None:
#             schema_obj = getattr(desc, "input_schema", None) or getattr(desc, "inputSchema", None)

#         schema = _to_schema_dict(schema_obj)
#         properties: dict[str, Any] = schema.get("properties", {}) or {}
#         required = set(schema.get("required", []) or [])

#         # Build a function with explicit parameters matching the schema
#         namespace: dict[str, Any] = {"handler": handler}
#         arg_names = list(properties.keys())

#         if not arg_names:
#             # Zero-argument tool
#             src = (
#                 "def _tool_func():\n"
#                 "    return handler.run_tool({})\n"
#             )
#         else:
#             # Build signature with required params first, then optional params with default None
#             required_params = [name for name in arg_names if name in required]
#             optional_params = [name for name in arg_names if name not in required]

#             sig_parts = []
#             for n in required_params:
#                 sig_parts.append(f"{n}")
#             for n in optional_params:
#                 sig_parts.append(f"{n}=None")
#             sig = ", ".join(sig_parts)

#             src_lines = [f"def _tool_func({sig}):",
#                          "    _args = {}"]
#             # Only include keys that are not None (so clients can omit optionals)
#             for n in arg_names:
#                 src_lines.append(f"    if {n} is not None: _args['{n}'] = {n}")
#             src_lines.append("    return handler.run_tool(_args)")
#             src = "\n".join(src_lines) + "\n"

#         try:
#             exec(src, namespace)
#             func = namespace["_tool_func"]
#         except Exception as e:
#             logger.error("Failed to build tool wrapper for %s: %s", tool_name, e)
#             # Fallback: a permissive single-dict-arg wrapper (clients must pass a single object)
#             def func(_args: dict[str, Any] | None = None) -> Any:  # type: ignore[no-redef]
#                 return handler.run_tool(_args or {})

#         # Register with FastMCP
#         mcp.tool(name=tool_name)(func)  # type: ignore[misc]



# def run_streamable_http(host: str = "127.0.0.1", port: int = 7310) -> None:
#     """
#     Start the MCP server over Streamable HTTP using the official Python SDK.
#     """
#     logging.basicConfig(level=logging.INFO)

#     _ensure_env()

#     mcp = FastMCP("mcp-obsidian", host=host, port=port)
#     _register_tools(mcp)

#     # Run using the SDK's built-in Streamable HTTP transport.
#     # Available transports include: "stdio", "sse", "streamable-http"
#     mcp.run(transport="streamable-http")


mcp = FastMCP(name="Say Hello")

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"


    # Get the Starlette app and add CORS middleware
    app = mcp.streamable_http_app()

    # Add CORS middleware with proper header exposure for MCP session management
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this more restrictively in production
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],  # Allow client to read session ID
        max_age=86400,
    )

    # Use PORT environment variable
    port = int(os.environ.get("PORT", 8081))

    # Run the MCP server with HTTP transport using uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces for containerized deployment
        port=port,
        log_level="debug"
    )