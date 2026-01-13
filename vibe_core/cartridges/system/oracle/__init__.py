"""
THE ORACLE - System Self-Awareness Module

The Oracle provides read-only introspection of the system state.
It aggregates data from all ledgers and provides natural language explanations.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x3f7aa822"  # GenesisByte: parampara % 37 == 0

from .cartridge_main import OracleCartridge

# Export both names for backwards compatibility
Oracle = OracleCartridge

__all__ = ["OracleCartridge", "Oracle"]
