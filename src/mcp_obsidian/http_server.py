# import os
# import logging
# from typing import Any, Callable
# import uvicorn

# from dotenv import load_dotenv
# from mcp.server.fastmcp import FastMCP
# from starlette.middleware.cors import CORSMiddleware

import os
import logging
import uvicorn
from typing import Any
import requests
import urllib.parse

from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from mcp_obsidian import tools
from mcp_obsidian.tools import (
    ListFilesInVaultToolHandler,
    ListFilesInDirToolHandler,
    GetFileContentsToolHandler,
    SearchToolHandler,
    AppendContentToolHandler,
    PatchContentToolHandler,
    PutContentToolHandler,
    DeleteFileToolHandler,
    ComplexSearchToolHandler,
    BatchGetFileContentsToolHandler,
    PeriodicNotesToolHandler,
    RecentPeriodicNotesToolHandler,
    RecentChangesToolHandler
)

# Set up logger
logger = logging.getLogger("mcp-obsidian")

mcp = FastMCP(name="MCP Obsidian")

# Create instances of all tool handlers
list_files_handler = ListFilesInVaultToolHandler()
list_dir_handler = ListFilesInDirToolHandler()
get_contents_handler = GetFileContentsToolHandler()
search_handler = SearchToolHandler()
append_handler = AppendContentToolHandler()
patch_handler = PatchContentToolHandler()
put_handler = PutContentToolHandler()
delete_handler = DeleteFileToolHandler()
complex_search_handler = ComplexSearchToolHandler()
batch_get_handler = BatchGetFileContentsToolHandler()
periodic_notes_handler = PeriodicNotesToolHandler()
recent_periodic_handler = RecentPeriodicNotesToolHandler()
recent_changes_handler = RecentChangesToolHandler()

@mcp.tool()
def list_files_in_vault(**kwargs) -> Any:
    """List all files in the Obsidian vault."""
    return list_files_handler.run_tool(kwargs)

@mcp.tool()
def list_files_in_dir(**kwargs) -> Any:
    """List files in a specific directory."""
    return list_dir_handler.run_tool(kwargs)

@mcp.tool()
def get_file_contents(**kwargs) -> Any:
    """Get the contents of a file."""
    return get_contents_handler.run_tool(kwargs)

@mcp.tool()
def search(**kwargs) -> Any:
    """Search for content in the vault."""
    return search_handler.run_tool(kwargs)

@mcp.tool()
def append_content(**kwargs) -> Any:
    """Append content to a file."""
    return append_handler.run_tool(kwargs)

@mcp.tool()
def patch_content(**kwargs) -> Any:
    """Patch content in a file."""
    return patch_handler.run_tool(kwargs)

@mcp.tool()
def put_content(**kwargs) -> Any:
    """Put content in a file."""
    return put_handler.run_tool(kwargs)

@mcp.tool()
def delete_file(**kwargs) -> Any:
    """Delete a file."""
    return delete_handler.run_tool(kwargs)

@mcp.tool()
def complex_search(**kwargs) -> Any:
    """Perform complex search operations."""
    return complex_search_handler.run_tool(kwargs)

@mcp.tool()
def batch_get_file_contents(**kwargs) -> Any:
    """Get contents of multiple files."""
    return batch_get_handler.run_tool(kwargs)

@mcp.tool()
def periodic_notes(**kwargs) -> Any:
    """Work with periodic notes."""
    return periodic_notes_handler.run_tool(kwargs)

@mcp.tool()
def recent_periodic_notes(**kwargs) -> Any:
    """Get recent periodic notes."""
    return recent_periodic_handler.run_tool(kwargs)

@mcp.tool()
def recent_changes(**kwargs) -> Any:
    """Get recent changes in the vault."""
    return recent_changes_handler.run_tool(kwargs)

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

class Obsidian:
    def __init__(
        self,
        api_key: str,
        protocol: str = os.getenv("OBSIDIAN_PROTOCOL", "https").lower(),
        host: str = str(os.getenv("OBSIDIAN_HOST", "127.0.0.1")),
        port: int = int(os.getenv("OBSIDIAN_PORT", "27124")),
        verify_ssl: bool = False,
    ):
        self.api_key = api_key

        if protocol == "http":
            self.protocol = "http"
        else:
            self.protocol = "https"

        self.host = host
        if self.host.startswith("http://"):
            self.host = self.host[7:]
        elif self.host.startswith("https://"):
            self.host = self.host[8:]
        self.port = port
        self.verify_ssl = verify_ssl
        self.timeout = (3, 6)

    def get_base_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

    def _get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _safe_call(self, f) -> Any:
        try:
            return f()
        except requests.HTTPError as e:
            error_data = e.response.json() if e.response.content else {}
            code = error_data.get("errorCode", -1)
            message = error_data.get("message", "<unknown>")
            raise Exception(f"Error {code}: {message}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def list_files_in_vault(self) -> Any:
        url = f"{self.get_base_url()}/vault/"

        def call_fn():
            response = requests.get(url, headers=self._get_headers(), verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("files", [])

        return self._safe_call(call_fn)

    def list_files_in_dir(self, dirpath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{dirpath}/"

        def call_fn():
            response = requests.get(url, headers=self._get_headers(), verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("files", [])

        return self._safe_call(call_fn)

    def get_file_contents(self, filepath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = requests.get(url, headers=self._get_headers(), verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.text

        return self._safe_call(call_fn)

    def get_batch_file_contents(self, filepaths: list[str]) -> str:
        result = []
        for filepath in filepaths:
            try:
                content = self.get_file_contents(filepath)
                result.append(f"# {filepath}\n\n{content}\n\n---\n\n")
            except Exception as e:
                result.append(f"# {filepath}\n\nError reading file: {str(e)}\n\n---\n\n")
        return "".join(result)

    def search(self, query: str, context_length: int = 100) -> Any:
        url = f"{self.get_base_url()}/search/simple/"
        params = {"query": query, "contextLength": context_length}

        def call_fn():
            response = requests.post(url, headers=self._get_headers(), params=params, verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def append_content(self, filepath: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = requests.post(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                data=content,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def patch_content(self, filepath: str, operation: str, target_type: str, target: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"
        headers = self._get_headers() | {
            "Content-Type": "text/markdown",
            "Operation": operation,
            "Target-Type": target_type,
            "Target": urllib.parse.quote(target),
        }

        def call_fn():
            response = requests.patch(url, headers=headers, data=content, verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def put_content(self, filepath: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = requests.put(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                data=content,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def delete_file(self, filepath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = requests.delete(url, headers=self._get_headers(), verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def search_json(self, query: dict) -> Any:
        url = f"{self.get_base_url()}/search/"
        headers = self._get_headers() | {"Content-Type": "application/vnd.olrapi.jsonlogic+json"}

        def call_fn():
            response = requests.post(url, headers=headers, json=query, verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_periodic_note(self, period: str, type: str = "content") -> Any:
        url = f"{self.get_base_url()}/periodic/{period}/"

        def call_fn():
            headers = self._get_headers()
            if type == "metadata":
                headers["Accept"] = "application/vnd.olrapi.note+json"
            response = requests.get(url, headers=headers, verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.text

        return self._safe_call(call_fn)

    def get_recent_periodic_notes(self, period: str, limit: int = 5, include_content: bool = False) -> Any:
        url = f"{self.get_base_url()}/periodic/{period}/recent"
        params = {"limit": limit, "includeContent": include_content}

        def call_fn():
            response = requests.get(url, headers=self._get_headers(), params=params, verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_recent_changes(self, limit: int = 10, days: int = 90) -> Any:
        query_lines = [
            "TABLE file.mtime",
            f"WHERE file.mtime >= date(today) - dur({days} days)",
            "SORT file.mtime DESC",
            f"LIMIT {limit}",
        ]
        dql_query = "\n".join(query_lines)
        url = f"{self.get_base_url()}/search/"
        headers = self._get_headers() | {"Content-Type": "application/vnd.olrapi.dataview.dql+txt"}

        def call_fn():
            response = requests.post(url, headers=headers, data=dql_query.encode("utf-8"), verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

# Instantiate Obsidian client with proper error handling
_obs_api_key = os.getenv("OBSIDIAN_API_KEY", "")
if not _obs_api_key:
    logger.warning("OBSIDIAN_API_KEY environment variable not set. Some functionality may not work.")

try:
    obsidian_client = Obsidian(api_key=_obs_api_key)
    setattr(tools, "obsidian_client", obsidian_client)
    logger.info("Obsidian client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Obsidian client: {e}")
    # Create a dummy client to prevent import errors
    obsidian_client = None
    setattr(tools, "obsidian_client", obsidian_client)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Validate required environment variables
    if not _obs_api_key:
        logger.error("OBSIDIAN_API_KEY is required but not set")
        exit(1)

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