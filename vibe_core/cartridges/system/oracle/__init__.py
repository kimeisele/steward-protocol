"""
THE ORACLE - System Self-Awareness Module

The Oracle provides read-only introspection of the system state.
It aggregates data from all ledgers and provides natural language explanations.
"""

from .cartridge_main import OracleCartridge

# Export both names for backwards compatibility
Oracle = OracleCartridge

__all__ = ["OracleCartridge", "Oracle"]
