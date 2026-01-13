"""
YOUR_AGENT_NAME Tools

Tools are accessed via kernel routing:
    self.system.execute_tool("YOUR_AGENT_ID.tool_name", params)

NEVER import tools directly in cartridge_main.py.
The kernel handles tool discovery and routing.

To add a new tool:
1. Create your_tool.py in this directory
2. Define a class with an execute() method
3. Register in the kernel's tool discovery
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x756d76ee"  # GenesisByte: parampara % 37 == 0

__all__ = []
