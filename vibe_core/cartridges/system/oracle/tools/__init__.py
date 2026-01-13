"""
Oracle Tools - Introspection and Analysis
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x63db04c4"  # GenesisByte: parampara % 37 == 0

from .introspection_tool import IntrospectionError, IntrospectionTool

__all__ = ["IntrospectionTool", "IntrospectionError"]
