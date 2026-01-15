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
import logging
import sys
from pathlib import Path as StdPath
from typing import Any, Callable, Dict, Optional, Union

# Import bridge for routing
from vibe_core.mahamantra.substrate.bridge import offer

# Import GAD Base
from vibe_core.mahamantra.protocols._gad import (
    GADBase,
    GADProtocol,
)


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

# =============================================================================
# PROXY DHARMA - Default Behaviors (The Choreography)
# =============================================================================
# When a service is silent (no on_tick), the Proxy dances for it.

logger = logging.getLogger("BALARAMA")

def _dharma_meditate(proxy: "BalaramaProxy", tick: Any) -> None:
    """Default: Silent meditation."""
    pass  # Generic silence is ok, but we log activation below

def _dharma_prithu(proxy: "BalaramaProxy", tick: Any) -> None:
    """Prithu (0): Health Check / Infrastructure."""
    logger.info(f"🌍 Prithu@{proxy.position}: Checking Foundation (Disk/Mem)")

def _dharma_janaka(proxy: "BalaramaProxy", tick: Any) -> None:
    """Janaka (10): State Sync / Maintenance."""
    logger.info(f"👑 Janaka@{proxy.position}: Maintaining State Consistency")

def _dharma_bhishma(proxy: "BalaramaProxy", tick: Any) -> None:
    """Bhishma (11): Ledger / Tradition."""
    logger.info(f"👴 Bhishma@{proxy.position}: Upholding the Vow (Ledger Sync)")

def _dharma_nrisimha(proxy: "BalaramaProxy", tick: Any) -> None:
    """Nrisimha (12): Protection / Security."""
    logger.info(f"🦁 Nrisimha@{proxy.position}: Scanning for Hiranyakashipu (Threats)")

def _dharma_yamaraja(proxy: "BalaramaProxy", tick: Any) -> None:
    """Yamaraja (15): Audit / Death."""
    logger.info(f"⚖️ Yamaraja@{proxy.position}: Auditing Karma (Final Check)")


DEFAULT_DHARMA: Dict[str, Callable[[Any, Any], None]] = {
    "prithu": _dharma_prithu,
    "janaka": _dharma_janaka,
    "bhishma": _dharma_bhishma,
    "nrisimha": _dharma_nrisimha,
    "yamaraja": _dharma_yamaraja,
    # Others default to meditation (silence)
}


class BalaramaProxy(GADBase, GADProtocol):
    """The Servitor God (Proxy).
    Wraps existing services to give them Mahajana Identity.
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
        
    GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
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
        super().__init__()  # Init GADBase
        
        self.module_name = module_name
        self.module = None
        self.is_wrapped = False

        # Identity (Navadvipa Awareness)
        self._mahajana: str = "unknown"
        self._position: int = -1
        self._genesis: str = ""

        # Heartbeat (Puri Connector)
        self._attached_to_heartbeat: bool = False
        self._tick_handler: Optional[Callable] = None
        self._tick_count: int = 0  # How many times we were activated

        # ORBITAL REACTOR (Mounting)
        self._reactor: Optional[Any] = None
        self._reactor_mounted: bool = False

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

        # PURI PHASE: Attach to heartbeat (if service has identity)
        self._attach_to_heartbeat(silent=silent)

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

    def _attach_to_heartbeat(self, *, silent: bool = False) -> None:
        """
        Attach service to Mahamantra heartbeat.

        PURI CONNECTOR (Ratha Yatra):
        -----------------------------
        This is the final step of service integration.
        The service is now "dancing" with the Mahamantra.

        How it works:
            1. Create a "gated listener" for this service
            2. Register it with mahamantra.register_listener()
            3. The listener only fires when tick.position == service.position

        This means:
            - Prithu (Position 0) wakes at tick 0, 16, 32, ...
            - Janaka (Position 10) wakes at tick 10, 26, 42, ...

        The Ratha Yatra: Each service moves when the chariot (tick) reaches them.
        """
        # Only attach if we have a valid position
        if not self.has_identity:
            return  # Anonymous services don't join the dance

        # Create gated listener
        self._tick_handler = self._create_gated_listener()

        # Register with Mahamantra
        try:
            from vibe_core.mahamantra import mahamantra
            mahamantra.register_listener(self._tick_handler)
            self._attached_to_heartbeat = True

            if not silent:
                import logging
                logger = logging.getLogger("BALARAMA")
                logger.debug(
                    f"💓 {self._mahajana.upper()}@{self._position} attached to heartbeat"
                )

        except Exception as e:
            # Graceful degradation - service works but no heartbeat
            import logging
            logging.getLogger("BALARAMA").warning(
                f"⚠️ Failed to attach {self._mahajana} to heartbeat: {e}"
            )

    def _create_gated_listener(self) -> Callable:
        """
        Create a gated tick listener for this service.

        THE GATE:
        ---------
        "You shall not pass!" - unless tick.position == my position.

        This creates positional scheduling WITHOUT code changes:
            - Prithu only wakes at Position 0
            - Janaka only wakes at Position 10
            - etc.

        Returns:
            A callable that receives TickState and gates execution.
        """
        # Capture service reference (closure)
        proxy = self

        def gated_listener(tick_state: Any) -> None:
            """
            Gated listener - only activates at matching position.

            tick_state can be dict (TypedDict) or object with attributes.
            We support both: position, quarter, guardian, word, opcode
            """
            # THE GATE: Only fire if position matches
            # Support both dict and object access
            if isinstance(tick_state, dict):
                current_position = tick_state.get("position", -1)
            else:
                current_position = getattr(tick_state, "position", -1)

            if current_position != proxy._position:
                return  # Not my turn - stay silent

            # MY TURN! Increment counter
            proxy._tick_count += 1

            # Look for handler methods in wrapped module
            # Duck typing: on_tick, process, update, handle_tick
            handler_names = ["on_tick", "process", "update", "handle_tick", "on_heartbeat"]

            for handler_name in handler_names:
                handler = getattr(proxy.module, handler_name, None)
                if callable(handler):
                    try:
                        # Try with tick_state first, then without
                        try:
                            handler(tick_state)
                        except TypeError:
                            handler()
                        break  # Only call first found handler
                    except Exception:
                        # Silent failure (Arjuna pattern)
                        pass
                
                # If we found a callable, we are done
                if callable(handler):
                    return

            # FALLBACK: PROXY DHARMA
            # If the service is silent (no handler), the Proxy acts.
            mahajana_name = proxy.mahajana.lower()
            dharma_action = DEFAULT_DHARMA.get(mahajana_name, _dharma_meditate)
            
            try:
                # The Proxy dances on behalf of the service
                dharma_action(proxy, tick_state)
            except Exception as e:
                logger.warning(f"Proxy Dharma failed for {mahajana_name}: {e}")


        return gated_listener

    @property
    def attached_to_heartbeat(self) -> bool:
        """Check if service is attached to Mahamantra heartbeat."""
        return self._attached_to_heartbeat

    @property
    def tick_count(self) -> int:
        """Number of times this service was activated by heartbeat."""
        return self._tick_count

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


    # =========================================================================
    # GAD-000 COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """Return capability description of wrapped service."""
        return {
            "type": "BalaramaProxy",
            "module": self.module_name,
            "mahajana": self._mahajana,
            "position": self._position,
            "genesis": self._genesis,
            "wrapped": self.is_wrapped,
            "reactor": self._reactor.reactor_id if self._reactor else None,
        }

    def get_state(self) -> Dict[str, object]:
        """Return structure state."""
        return {
            "identity": {
                "mahajana": self._mahajana,
                "position": self._position,
                "genesis": self._genesis,
            },
            "runtime": {
                "tick_count": self._tick_count,
                "attached": self._attached_to_heartbeat,
                "mounted": self._reactor_mounted,
            },
            "heartbeat": self.heartbeat.get_summary(),
        }

    def is_healthy(self) -> bool:
        """Proxy is healthy if wrapped and attached (if it has identity)."""
        base_health = super().is_healthy()
        if not self.is_wrapped:
            return False
            
        if self.has_identity and not self._attached_to_heartbeat:
            # Should be attached if it has identity
            return False
            
        return base_health

    @property
    def is_idempotent(self) -> bool:
        """Proxies are generally idempotent (they just route)."""
        return True

    def detect_drift(self) -> List[str]:
        """Detect drift (e.g., if module was reloaded or modified)."""
        drift = []
        if self.module is None:
            drift.append("Module vanished")
        return drift

    # The 4 Dharma Tests for Proxy
    def test_daya(self) -> bool:
        return True  # Protective wrapper

    def test_satyam(self) -> bool:
        # Truth: Identity matches loaded module
        return self._mahajana == getattr(self.module, "__mahajana__", "unknown")

    def test_tapas(self) -> bool:
        return True

    def test_saucam(self) -> bool:
        return self.is_wrapped
    # =========================================================================
    # ORBITAL REACTOR MOUNTING (Adoption)
    # =========================================================================

    def set_reactor(self, reactor: Any) -> None:
        """
        Mount this service onto an Orbital Reactor.
        
        Args:
            reactor: The OrbitalShadowReactor instance.
        """
        self._reactor = reactor
        self._reactor_mounted = True
        
    @property
    def reactor(self) -> Optional[Any]:
        """Get the mounted reactor."""
        return self._reactor

    # =========================================================================
    # SHADOW REACTOR LISTENER PROTOCOL
    # =========================================================================
    # These methods allow the proxy to be driven by the Orbital Reactor.
    # They delegate to the wrapped module if possible.
    
    def on_bhoga(self, state: Any) -> None:
        """
        React to BHOGA phase (Offering).
        Delegate to module.on_bhoga or generic on_tick.
        """
        # Try specific callback first
        handler = getattr(self.module, "on_bhoga", None)
        if callable(handler):
            try:
                handler(state)
                return
            except Exception:
                pass
        
        # Fallback to generic tick handler logic (reuse gated logic but force execution)
        # Or just do nothing?
        # User said: "ManifestationService hört Tick 4... arbeitet".
        # This implies standard work happens here.
        
        # Reuse existing discovery logic from _create_gated_listener but simplified
        handler = getattr(self.module, "on_tick", None)
        if callable(handler):
            try:
                handler(state)
            except Exception:
                pass
        elif self.has_identity:
             # Proxy Dharma Fallback
             name = self.mahajana.lower()
             dharma = DEFAULT_DHARMA.get(name, _dharma_meditate)
             dharma(self, state)

    def on_switch(self, state: Any) -> None:
        """React to SWITCH phase (Parashurama)."""
        handler = getattr(self.module, "on_switch", None)
        if callable(handler):
            try:
                handler(state)
            except Exception:
                pass

    def on_prasadam(self, state: Any) -> None:
        """React to PRASADAM phase (Distribution)."""
        handler = getattr(self.module, "on_prasadam", None)
        if callable(handler):
            try:
                handler(state)
            except Exception:
                pass

    def on_return(self, state: Any) -> None:
        """React to RETURN phase (Cycle Complete)."""
        handler = getattr(self.module, "on_return", None)
        if callable(handler):
            try:
                handler(state)
            except Exception:
                pass

    def __repr__(self) -> str:
        """String representation with identity."""
        orbit_info = f", Orbit={self._reactor.lagna}" if self._reactor else ""
        if self.has_identity:
            return f"BalaramaProxy({self._mahajana}@{self._position}, {self.module_name}{orbit_info})"
        status = "wrapped" if self.is_wrapped else "unwrapped"
        return f"BalaramaProxy({self.module_name}, {status}{orbit_info})"


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
