"""
DAYA (Mercy) - Implementation of IDataSanitizer.
Layer: -1 (Naga Loka / Substrate Enforcement)
"""

from typing import Optional, TypeVar, Union

from vibe_core.protocols.defense import IDataSanitizer

T = TypeVar("T")
ContextT = TypeVar("ContextT")


class DataSanitizer(IDataSanitizer):
    """
    Enforces Data Purity.
    """

    def enforce_purity(self, data: T, context: Optional[ContextT] = None) -> T:
        # Strict Null Check
        if data is None:
            # Mercy allow None? Only if explicitly typed Optional.
            # For now, pass through.
            return data

        # String Sanitization
        if isinstance(data, str):
            if "DROP TABLE" in data.upper() or "RM -RF" in data.upper():
                raise ValueError("CRITICAL: Toxic Input Detected (Daya Violation)")

        return data
