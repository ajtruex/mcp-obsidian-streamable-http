import argparse
import asyncio
import logging

from .server import main as _stdio_main
from .http_server import run_streamable_http

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")


def main():
    parser = argparse.ArgumentParser(prog="mcp-obsidian", description="MCP server for Obsidian")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="streamable-http",
        help="Transport to use (default: streamable-http)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7310, help="HTTP port (default: 7310)")
    args = parser.parse_args()

    if args.transport == "streamable-http":
        # FastMCP manages its own event loop internally
        run_streamable_http(args.host, args.port)
    else:
        # Preserve original stdio behavior
        asyncio.run(_stdio_main())