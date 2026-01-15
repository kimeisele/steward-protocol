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

    NAVADVIPA IDENTITY AWARENESS:
    -----------------------------
    The proxy reads __mahajana__ and __position__ from the module.
    Services are no longer anonymous - they know WHO they are.

    "Wir fluten das Land mit dem Ozean (Seed). Wer schwimmt, ist integriert."
    — MAHAPROMPT.md

    Usage:
        >>> proxy = BalaramaProxy("vibe_core.services.manifestation_service")
        >>> proxy.mahajana  # "janaka"
        >>> proxy.position  # 10
        >>> # Service now has mahamantra in namespace
        >>> # Service's Path is now _GovernedPath
        >>> # All writes route through bridge.offer()

    Attributes:
        module: The wrapped service module
        module_name: Name of the wrapped module
        mahajana: The Mahajana identity (e.g., "janaka", "prithu")
        position: The Mahamantra position (0-15)
        is_wrapped: Whether wrapping succeeded
    """

    def __init__(self, module_name: str, *, silent: bool = False):
        """
        Initialize Balarama Proxy for a service module.

        NAVADVIPA EMBRACE:
        ------------------
        1. Import the module
        2. Extract identity (__mahajana__, __position__)
        3. Inject mahamantra context
        4. Replace Path with _GovernedPath
        5. Log the embrace (unless silent)

        Args:
            module_name: Full module path (e.g., "vibe_core.services.foo")
            silent: If True, suppress logging (for bootstrap)

        Raises:
            ImportError: If module cannot be imported
        """
        self.module_name = module_name
        self.module = None
        self.is_wrapped = False

        # Identity (Navadvipa Awareness)
        self._mahajana: str = "unknown"
        self._position: int = -1
        self._genesis: str = ""

        # Import the module
        try:
            self.module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Cannot import module {module_name}: {e}")

        # Extract identity from module (THE AWAKENING)
        self._extract_identity()

        # Apply wrapping
        self._inject_mahamantra_context()
        self._replace_path()

        self.is_wrapped = True

        # Log the embrace (Navadvipa welcome)
        if not silent:
            self._log_embrace()

    def _extract_identity(self) -> None:
        """
        Extract Mahajana identity from module.

        NAVADVIPA AWAKENING:
        --------------------
        Read __mahajana__, __position__, __genesis__ from module.
        If not present, the service remains "unknown" (amnesia).

        "Who am I? Where do I belong in the Mahamantra?"
        """
        if self.module is None:
            return

        # Read identity declarations
        self._mahajana = getattr(self.module, "__mahajana__", "unknown")
        self._position = getattr(self.module, "__position__", -1)
        self._genesis = getattr(self.module, "__genesis__", "")

    def _log_embrace(self) -> None:
        """
        Log the Navadvipa embrace.

        SANKIRTAN ANNOUNCEMENT:
        -----------------------
        When a service is embraced, we announce its identity.
        This is the service "joining the dance".
        """
        import logging
        logger = logging.getLogger("BALARAMA")

        if self._mahajana != "unknown" and self._position >= 0:
            # Service has identity - welcome by name
            logger.info(
                f"🙏 {self._mahajana.upper()} (Position {self._position}) embraced: "
                f"{self.module_name.split('.')[-1]}"
            )
        else:
            # Anonymous service - still welcomed
            logger.debug(f"🤝 Anonymous service embraced: {self.module_name}")

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

    @property
    def mahajana(self) -> str:
        """The Mahajana identity of this service."""
        return self._mahajana

    @property
    def position(self) -> int:
        """The Mahamantra position (0-15) of this service."""
        return self._position

    @property
    def genesis(self) -> str:
        """The GenesisByte hash of this service."""
        return self._genesis

    @property
    def has_identity(self) -> bool:
        """Check if service has Mahajana identity."""
        return self._mahajana != "unknown" and self._position >= 0

    def __repr__(self) -> str:
        """String representation with identity."""
        if self.has_identity:
            return f"BalaramaProxy({self._mahajana}@{self._position}, {self.module_name})"
        status = "wrapped" if self.is_wrapped else "unwrapped"
        return f"BalaramaProxy({self.module_name}, {status})"


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def wrap_service(module_name: str, *, silent: bool = False) -> BalaramaProxy:
    """
    Wrap a service module with Balarama Proxy.

    CONVENIENCE WRAPPER:
    --------------------
    Instead of: proxy = BalaramaProxy("vibe_core.services.foo")
    Use: service = wrap_service("vibe_core.services.foo")

    NAVADVIPA IDENTITY:
    -------------------
    The proxy automatically extracts __mahajana__ and __position__.
    Access via: service.mahajana, service.position

    Args:
        module_name: Full module path to wrap
        silent: If True, suppress embrace logging

    Returns:
        BalaramaProxy instance with identity awareness

    Example:
        >>> manifestation = wrap_service("vibe_core.services.manifestation_service")
        >>> manifestation.mahajana  # "janaka"
        >>> manifestation.position  # 10
        >>> # manifestation now has mahamantra in namespace
        >>> # All Path operations governed
    """
    return BalaramaProxy(module_name, silent=silent)


# =============================================================================
# AUTO-WRAP REGISTRY
# =============================================================================

# Services that should be auto-wrapped on import
# Add service names here to auto-govern them
#
# NITYANANDA STRATEGY: Jagai & Madhai are embraced, not killed.
# These services are powerful but "wild" - they write directly to disk.
# The proxy wraps them, replacing Path with _GovernedPath.
# All writes now flow through bridge.offer() → Dharmic governance.
#
AUTO_WRAP_SERVICES = [
    "vibe_core.services.manifestation_service",  # Jagai: Markdown manifestation
    "vibe_core.protocols.prakriti_binding",  # Madhai: File blessing/signature
]


def auto_wrap_services(*, silent: bool = True) -> dict[str, BalaramaProxy]:
    """
    Auto-wrap services listed in AUTO_WRAP_SERVICES.

    NAVADVIPA SANKIRTAN:
    --------------------
    Each service is embraced and welcomed by identity.
    The log shows WHO joined the dance:

        🙏 JANAKA (Position 10) embraced: manifestation_service
        🙏 PRITHU (Position 0) embraced: prakriti_binding

    Args:
        silent: If True, suppress individual embrace logs (default for bootstrap)

    Returns:
        Dict mapping module name → BalaramaProxy (with identity)

    Example:
        >>> proxies = auto_wrap_services(silent=False)
        >>> for name, proxy in proxies.items():
        ...     print(f"{proxy.mahajana}: {proxy.position}")
    """
    import logging
    logger = logging.getLogger("BALARAMA")

    proxies = {}
    embraced_count = 0
    identity_count = 0

    for service_name in AUTO_WRAP_SERVICES:
        try:
            proxy = wrap_service(service_name, silent=silent)
            proxies[service_name] = proxy
            embraced_count += 1

            if proxy.has_identity:
                identity_count += 1

        except Exception as e:
            # Graceful degradation - continue with other services
            logger.warning(f"⚠️ Failed to embrace {service_name}: {e}")

    # Summary log (always shown)
    if embraced_count > 0:
        logger.info(
            f"🎵 Sankirtan: {embraced_count} services embraced, "
            f"{identity_count} with Mahajana identity"
        )

    return proxies


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BalaramaProxy",
    "wrap_service",
    "auto_wrap_services",
]
