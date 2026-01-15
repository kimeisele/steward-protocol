"""
PROXY - Balarama Wrapper (Der Umarmer)
=======================================

"balarāmaḥ prathamaḥ sarva-saṅkarṣaṇaḥ"
"Balarama is the first, the Supreme Attractor."
— Caitanya Caritamrita

THE BALARAMA PATTERN:
---------------------
Services remain unchanged (Wildnis).
Proxy wraps them and routes operations through Mahamantra.

"Let the wildness be wild. We flood the land with the ocean (Seed)."
— MAHAPROMPT.md

WATERTIGHT: NO hardcoded numbers. ALL from seed.py.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "nityananda"
__position__ = 1
__genesis__ = "0x4a925e36"  # GenesisByte: parampara % 37 == 0

import importlib
import sys
from pathlib import Path as StdPath
from typing import Any, Optional, Union

# Import bridge for routing
from vibe_core.mahamantra.substrate.bridge import offer


# =============================================================================
# GOVERNED PATH - Internal class (not exported)
# =============================================================================

class _GovernedPath(type(StdPath())):
    """
    Path class that routes file writes through bridge.offer().

    INTERNAL USE ONLY. Not exported. Injected into service namespaces.

    Inherits from pathlib.Path but intercepts write operations.
    All writes go through bridge.offer() for Parampara validation.

    WATERTIGHT: Uses bridge.offer() which derives all from seed.py.
    """

    def write_text(
        self,
        data: str,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> int:
        """
        Write text to file via bridge.offer().

        GOVERNED: Routes through bridge → Mahajana → Execution.

        Args:
            data: Text content to write
            encoding: Text encoding (default: None = utf-8)
            errors: Error handling strategy
            newline: Newline handling

        Returns:
            Number of bytes written

        Raises:
            PermissionError: If bridge rejects the write
        """
        # Route through bridge
        result = offer(
            content=data,
            purpose="file_flush",
            actor=f"governed_path:{self}",
        )

        if not result["success"]:
            raise PermissionError(
                f"Bridge rejected write to {self}: {result['error']}"
            )

        # Bridge approved - execute original write
        return super().write_text(
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def write_bytes(self, data: bytes) -> int:
        """
        Write bytes to file via bridge.offer().

        GOVERNED: Routes through bridge → Mahajana → Execution.

        Args:
            data: Bytes content to write

        Returns:
            Number of bytes written

        Raises:
            PermissionError: If bridge rejects the write
        """
        # Route through bridge
        result = offer(
            content=data,
            purpose="file_flush",
            actor=f"governed_path:{self}",
        )

        if not result["success"]:
            raise PermissionError(
                f"Bridge rejected write to {self}: {result['error']}"
            )

        # Bridge approved - execute original write
        return super().write_bytes(data)


# =============================================================================
# BALARAMA PROXY - The Service Wrapper
# =============================================================================

class BalaramaProxy:
    """
    Balarama Proxy - Wraps services and routes operations through Mahamantra.

    THE PATTERN (Acintya Bheda Abheda):
    ------------------------------------
    Service code remains unchanged (Wildnis).
    Proxy injects mahamantra context and governed operations.

    "Wir fluten das Land mit dem Ozean (Seed). Wer schwimmt, ist integriert."
    — MAHAPROMPT.md

    Usage:
        >>> proxy = BalaramaProxy("vibe_core.services.manifestation_service")
        >>> # Service now has mahamantra in namespace
        >>> # Service's Path is now _GovernedPath
        >>> # All writes route through bridge.offer()

    Attributes:
        module: The wrapped service module
        module_name: Name of the wrapped module
        is_wrapped: Whether wrapping succeeded
    """

    def __init__(self, module_name: str):
        """
        Initialize Balarama Proxy for a service module.

        Args:
            module_name: Full module path (e.g., "vibe_core.services.foo")

        Raises:
            ImportError: If module cannot be imported
        """
        self.module_name = module_name
        self.module = None
        self.is_wrapped = False

        # Import the module
        try:
            self.module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Cannot import module {module_name}: {e}")

        # Apply wrapping
        self._inject_mahamantra_context()
        self._replace_path()

        self.is_wrapped = True

    def _inject_mahamantra_context(self) -> None:
        """
        Inject mahamantra into service namespace.

        CONTEXT INJECTION:
        ------------------
        Service "wakes up" with mahamantra available:

            from vibe_core.mahamantra import mahamantra
            # NOW available as: mahamantra (in module scope)

        The service can now use mahamantra.offer(), mahamantra.tick(), etc.
        """
        # Lazy import to avoid circular dependency
        from vibe_core.mahamantra import mahamantra

        # Inject into module's global namespace
        self.module.__dict__["mahamantra"] = mahamantra

    def _replace_path(self) -> None:
        """
        Replace pathlib.Path in service namespace with _GovernedPath.

        NAMESPACE REPLACEMENT:
        ----------------------
        If service imports: from pathlib import Path
        We replace: module.__dict__['Path'] = _GovernedPath

        Service continues using: path = Path("foo.txt")
        But now it's governed (routes through bridge).
        """
        # Check if Path is in module namespace
        if "Path" in self.module.__dict__:
            # Replace with governed version
            self.module.__dict__["Path"] = _GovernedPath

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to wrapped module.

        This makes the proxy transparent:
            proxy.some_function() → module.some_function()

        Args:
            name: Attribute name

        Returns:
            Attribute from wrapped module
        """
        if self.module is None:
            raise AttributeError(f"Module {self.module_name} not loaded")

        return getattr(self.module, name)

    def __repr__(self) -> str:
        """String representation."""
        status = "wrapped" if self.is_wrapped else "unwrapped"
        return f"BalaramaProxy({self.module_name}, {status})"


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def wrap_service(module_name: str) -> BalaramaProxy:
    """
    Wrap a service module with Balarama Proxy.

    CONVENIENCE WRAPPER:
    --------------------
    Instead of: proxy = BalaramaProxy("vibe_core.services.foo")
    Use: service = wrap_service("vibe_core.services.foo")

    Args:
        module_name: Full module path to wrap

    Returns:
        BalaramaProxy instance (transparent access to module)

    Example:
        >>> manifestation = wrap_service("vibe_core.services.manifestation_service")
        >>> # manifestation now has mahamantra in namespace
        >>> # All Path operations governed
        >>> # Use as normal: manifestation.some_function()
    """
    return BalaramaProxy(module_name)


# =============================================================================
# AUTO-WRAP REGISTRY
# =============================================================================

# Services that should be auto-wrapped on import
# Add service names here to auto-govern them
AUTO_WRAP_SERVICES = [
    # "vibe_core.services.manifestation_service",
    # Disabled by default - enable per deployment
]


def auto_wrap_services() -> dict[str, BalaramaProxy]:
    """
    Auto-wrap services listed in AUTO_WRAP_SERVICES.

    Returns:
        Dict mapping module name → BalaramaProxy

    Example:
        >>> proxies = auto_wrap_services()
        >>> # All listed services now governed
    """
    proxies = {}
    for service_name in AUTO_WRAP_SERVICES:
        try:
            proxies[service_name] = wrap_service(service_name)
        except Exception:
            # Graceful degradation - continue with other services
            pass

    return proxies


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BalaramaProxy",
    "wrap_service",
    "auto_wrap_services",
]
