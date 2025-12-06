"""
WATCHMAN Tools

Tools are accessed via kernel routing:
    self.system.execute_tool("watchman_102224_4840.tool_name", params)

NEVER import tools directly in cartridge_main.py.
The kernel handles tool discovery and routing.

To add a new tool:
1. Create your_tool.py in this directory
2. Define a class with an execute() method
3. Register in the kernel's tool discovery
"""

__all__ = []
