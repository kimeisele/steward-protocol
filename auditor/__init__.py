"""
AUDITOR - GAD-000 Enforcement Agent for Steward Protocol

The third agent in the STEWARD Protocol ecosystem.
While HERALD creates and ARCHIVIST verifies, AUDITOR enforces system integrity.

"Who watches the watchers?" - The AUDITOR does.
"""

from .cartridge_main import AuditorCartridge

__version__ = "1.0.0"
__all__ = ["AuditorCartridge"]
