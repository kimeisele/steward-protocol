"""
LILA MIGRATION - The Immigration Office
=======================================

"sarva-dharman parityajya mam ekam saranam vraja"
"Abandon all varieties of religion and just surrender unto Me."
-- Bhagavad Gita 18.66

FUNCTION:
    This module handles the migration of Legacy Code ("Outlaws")
    into the Mahamantra ("The Garden").

MECHANISM:
    It uses the Balarama Proxy (mahamantra.protocols._proxy)
    to wrap legacy objects, giving them a Pancha Tattva identity.

LOCATION: vibe_core.mahamantra.lila.migration (THE GATE)
"""

from typing import Any, Optional
import importlib
from vibe_core.mahamantra.protocols._proxy import MahamantraProxy
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol

def migrate(target: Any, guardian: str = "unknown", position: int = 0) -> Any:
    """
    Migrate a target object into the Mahamantra.
    
    If the target is already compliant (implements PanchaTattvaProtocol),
    it is returned as-is.
    
    If not, it is wrapped in a MahamantraProxy (Balarama).
    
    Args:
        target: The object/module to migrate.
        guardian: The name of the guardian (e.g. "brahma").
        position: The position index (0-15).
        
    Returns:
        A PanchaTattvaProtocol compliant object.
    """
    if isinstance(target, PanchaTattvaProtocol) or hasattr(target, "__tattva__"):
        return target
        
    return MahamantraProxy(target, position, guardian)

def import_and_migrate(module_path: str, guardian: str, position: int) -> Any:
    """
    Import a legacy module and immediately migrate it.
    
    Usage:
        service = import_and_migrate("vibe_core.services.old_service", "shambhu", 3)
    """
    try:
        module = importlib.import_module(module_path)
        return migrate(module, guardian, position)
    except ImportError as e:
        # Graceful failure (Kali Yuga)
        return None

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "migrate",
    "import_and_migrate",
]
