#!/usr/bin/env python3
import sys
import os

# Add the parent directory to the path so we can import mcp_obsidian
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_obsidian import main

if __name__ == "__main__":
    main()
