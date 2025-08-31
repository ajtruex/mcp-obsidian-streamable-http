# GEMINI.md

## Project Overview

This project is a Python-based MCP (Model-centric Protocol) server that acts as a bridge to the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin. It allows a Gemini-powered agent to interact with an Obsidian vault, enabling a wide range of automation and content management tasks.

The server exposes a set of tools for interacting with an Obsidian vault, including:

*   Listing files and directories
*   Reading and writing file content
*   Searching for notes
*   Creating, deleting, and modifying notes
*   Working with periodic notes (daily, weekly, etc.)

The project is built using the `mcp` library for creating the server, `uv` for package management, and `requests` for communicating with the Obsidian API.

## Building and Running

### Prerequisites

*   Python 3.11+
*   `uv` package manager
*   Obsidian with the Local REST API plugin installed and enabled.

### Installation

1.  **Install Dependencies:**
    ```bash
    uv sync
    ```

### Running the Server

The server can be run using the following command:

```bash
uvx mcp-obsidian
```

### Configuration

The server requires the following environment variables to be set:

*   `OBSIDIAN_API_KEY`: Your Obsidian Local REST API key.
*   `OBSIDIAN_HOST`: The host for the Obsidian API (default: `127.0.0.1`).
*   `OBSIDIAN_PORT`: The port for the Obsidian API (default: `27124`).

These can be set in a `.env` file in the project root or through the server configuration in your client application.

## Development Conventions

*   **Package Management:** Dependencies are managed using `uv` and are defined in the `pyproject.toml` file.
*   **Entry Point:** The main entry point for the server is the `main` function in `src/mcp_obsidian/__init__.py`, which is exposed as the `mcp-obsidian` script.
*   **Tool Implementation:** Each tool is implemented as a `ToolHandler` class in `src/mcp_obsidian/tools.py`. Each handler is responsible for defining the tool's schema and executing the corresponding logic.
*   **Obsidian API Interaction:** All interactions with the Obsidian Local REST API are encapsulated within the `Obsidian` class in `src/mcp_obsidian/obsidian.py`.
*   **Testing:** The project does not currently have a dedicated test suite.
