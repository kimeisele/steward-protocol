"""
AUDITOR Tools

Tools are accessed via kernel routing:
    self.system.execute_tool("auditor_102232_0dd8.tool_name", params)

NEVER import tools directly in cartridge_main.py.
The kernel handles tool discovery and routing.

To add a new tool:
1. Create your_tool.py in this directory
2. Define a class with an execute() method
3. Register in the kernel's tool discovery
"""

__all__ = []
