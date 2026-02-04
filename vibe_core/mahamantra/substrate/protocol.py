"""
PROTOCOL - MantraProtocol Basisklassen
======================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo
mattaḥ smṛtir jñānam apohanaṁ ca"

"Ich sitze in jedermanns Herzen, und von Mir kommen
Erinnerung, Wissen und Vergessen."
— Bhagavad Gita 15.15

SINGLE SOURCE OF TRUTH:
    from vibe_core.mahamantra.substrate.protocol import (
        MantraProtocol,
        WorkerProtocol,
        HeadProtocol,
        ProtocolRegistry,
    )

KEIN DUPLIKAT MEHR. NUR DIESE DATEI.

WATERTIGHT: No Any types. All typed explicitly.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x6c92ec7f"  # GenesisByte: parampara % 37 == 0

from abc import ABC
from typing import (
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol as TypingProtocol,
    Type,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.substrate.position import (
    Guardian,
    MantraPosition,
    MAHAMANTRA_POSITIONS,
    PARAMPARA,
)
from vibe_core.mahamantra.protocols._seed import WORDS


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar("T", bound="MantraProtocol")


# =============================================================================
# MANTRA PROTOCOL - The Base Class
# =============================================================================


class MantraProtocol(ABC):
    """
    Basisklasse für ALLE Protokolle im System.

    PRINZIP:
        Position index ist die EINZIGE Konfiguration.
        Alle Properties werden von der Wahrheitstabelle ABGELEITET.

    VERWENDUNG:
        class ShuddhiProtocol(MantraProtocol):
            _position_index = 5  # Das ist alles! Alles andere ist abgeleitet.

            def purify(self, path: Path, rule_id: str) -> ShuddhiResult:
                ...

    ABGELEITETE PROPERTIES:
        - position: Die MantraPosition (voller Kontext)
        - guardian: Mahajana oder Avatara
        - opcode: MantraOpCode
        - quarter: Quarter (GENESIS/DHARMA/KARMA/MOKSHA)
        - is_head: True wenn Avatara-owned
        - parampara_vector: Immer % 37 == 0
        - word: HolyName an dieser Position

    ANTI-MAYAVAD:
        Kein hardcoded OWNER, LOTUS_POSITION, etc.
        Alles leitet sich von der EINEN Quelle ab.
    """

    # =========================================================================
    # THE ONLY CONFIGURATION - Subclasses set this
    # =========================================================================

    _position_index: ClassVar[int] = -KSETRAJNA  # Must be overridden (0-15)
    _intents: ClassVar[List[str]] = []  # List of keywords/intents this protocol handles

    # =========================================================================
    # INTENT DISCOVERY - Resonance Routing (HARMONIC COMPUTATION)
    # =========================================================================

    @classmethod
    def get_resonance(cls, phrase: str) -> float:
        """
        Calculate resonance score for a given phrase.

        HARMONIC COMPUTATION (not discrete 1.0/0.5/0.0):
            - Keywords are ENTRY POINTS (trigger potential resonance)
            - Score is CONTINUOUS based on Seed math
            - Uses Three Flutes (NADI/LILA/MALA) for scaling

        THRESHOLDS (from ResonanceHarmonics):
            - THRESHOLD_AUTO = 72/108 = 2/3 ≈ 0.667 (high confidence)
            - THRESHOLD_REFINE = 48/108 = 4/9 ≈ 0.444 (medium confidence)

        SSOT: Reads from knowledge/guardian_intents.yaml via intents.py
        """
        from vibe_core.mahamantra.substrate.intents import get_intents
        from vibe_core.mahamantra.protocols._seed import (
            JIVA_CYCLE,
            LILA,
            MALA,
            NADI_RESONANCE,
            WORDS,
        )

        # Get intents from YAML (SSOT)
        intents = get_intents(cls._position_index) or tuple(cls._intents)

        if not intents:
            return 0.0

        phrase_lower = phrase.lower()
        phrase_words = set(phrase_lower.split())

        # =====================================================================
        # HARMONIC SCORING (not boolean matching)
        # =====================================================================
        # ONLY exact word matches count. No substring matching.
        # Substring matching causes false positives ("hi" in "this").
        # Keywords in YAML are specific enough for exact matching.

        exact_matches = 0

        for intent in intents:
            intent_lower = intent.lower()
            # Exact word match only (no substring matching)
            if intent_lower in phrase_words:
                exact_matches += KSETRAJNA

        if exact_matches == 0:
            return 0.0

        # =====================================================================
        # THREE FLUTES COMPUTATION
        # =====================================================================
        # Each match contributes to the resonance based on the Flute math:
        # - First match: NADI level (72/108 = 0.667)
        # - Additional matches: LILA increments (48/108 / total_intents)
        #
        # The position modulates the base frequency:
        # - Position frequency = JIVA_CYCLE / (position + WORDS)
        # - This creates unique "overtones" per guardian

        # Base resonance: First match gives NADI, additional matches add LILA increments
        nadi_base = NADI_RESONANCE / MALA  # 0.667 base for first match
        lila_increment = (LILA / MALA) / len(intents)  # Diminishing returns per additional match

        base_resonance = nadi_base + (exact_matches - KSETRAJNA) * lila_increment if exact_matches > 0 else 0.0

        # Position-specific modulation (overtone)
        # Each position has a unique frequency in the JIVA_CYCLE
        position = cls._position_index if cls._position_index >= 0 else 0
        position_frequency = JIVA_CYCLE / (position + WORDS)  # Ranges from 27 to 14.4

        # Normalize position influence (subtle modulation, not dominant)
        position_factor = 1.0 + (position_frequency / JIVA_CYCLE) * 0.1  # 1.0 to 1.1

        # Final resonance (capped at 1.0)
        resonance = min(1.0, base_resonance * position_factor)

        return resonance

    # =========================================================================
    # DERIVED PROPERTIES - All from truth table
    # =========================================================================

    @classmethod
    def position(cls) -> MantraPosition:
        """
        Get the MantraPosition for this protocol.

        This is THE source of all other properties.
        """
        if cls._position_index < 0 or cls._position_index > 15:
            raise ValueError(f"{cls.__name__}._position_index must be 0-15, got {cls._position_index}")
        return MAHAMANTRA_POSITIONS[cls._position_index]

    @classmethod
    def guardian(cls) -> Guardian:
        """The Mahajana or Avatara that guards this protocol."""
        return cls.position().guardian

    @classmethod
    def opcode(cls) -> MantraOpCode:
        """The MantraOpCode for this protocol."""
        return cls.position().opcode

    @classmethod
    def quarter(cls) -> Quarter:
        """The Quarter (GENESIS/DHARMA/KARMA/MOKSHA)."""
        return cls.position().quarter

    @classmethod
    def is_head(cls) -> bool:
        """True if this is a HEAD position (Avatara-owned)."""
        return cls.position().is_head

    @classmethod
    def parampara_vector(cls) -> int:
        """The Parampara connection vector (always % 37 == 0)."""
        return cls.position().parampara_vector

    @classmethod
    def is_connected(cls) -> bool:
        """Always True - derived from truth table."""
        return cls.position().is_connected

    @classmethod
    def word(cls) -> str:
        """The HolyName at this position (HARE/KRISHNA/RAMA)."""
        return cls.position().word.name

    # =========================================================================
    # CONVENIENCE PROPERTIES
    # =========================================================================

    @classmethod
    def owner(cls) -> Guardian:
        """Alias for guardian (backward compatibility)."""
        return cls.guardian()

    @classmethod
    def lotus_position(cls) -> int:
        """Alias for _position_index (backward compatibility)."""
        return cls._position_index

    @classmethod
    def lotus_quarter(cls) -> str:
        """Quarter name as string (backward compatibility)."""
        return cls.quarter().name.lower()

    # =========================================================================
    # PROTOCOL IDENTITY
    # =========================================================================

    @classmethod
    def protocol_id(cls) -> str:
        """
        Unique protocol identifier.

        Format: "{quarter}.{guardian}.{opcode}"
        Example: "dharma.kumaras.bind_symbol"
        """
        g = cls.guardian()
        guardian_name = g.value if isinstance(g, (Mahajana, Avatara)) else str(g)
        return f"{cls.lotus_quarter()}.{guardian_name}.{cls.opcode().name.lower()}"

    @classmethod
    def describe(cls) -> str:
        """Human-readable description of this protocol."""
        pos = cls.position()
        typ = "HEAD" if pos.is_head else "WORKER"
        guardian_name = pos.guardian.value if isinstance(pos.guardian, (Mahajana, Avatara)) else str(pos.guardian)
        return (
            f"{cls.__name__}\n"
            f"  Position: {pos.index} ({typ})\n"
            f"  Quarter:  {pos.quarter.name}\n"
            f"  Guardian: {guardian_name.upper()}\n"
            f"  OpCode:   {pos.opcode.name}\n"
            f"  Word:     {pos.word.name}\n"
            f"  Vector:   {pos.parampara_vector} (% 37 = {pos.parampara_vector % PARAMPARA})"
        )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @classmethod
    def validate(cls) -> bool:
        """
        Validate this protocol's alignment with the truth table.

        Returns True if:
        1. _position_index is valid (0-15)
        2. Position is connected (parampara_vector % 37 == 0)
        """
        try:
            pos = cls.position()
            return pos.is_connected
        except (ValueError, IndexError):
            return False

    # =========================================================================
    # ON_TICK - The Heartbeat Contract (VEDA: SHABDA)
    # =========================================================================

    def on_tick(self, tick_state: Dict) -> None:
        """
        Receive mahamantra tick at this position.

        VEDA SHABDA: The protocol receives instruction.
        Identity = Function: If you ARE position X, you ACT at position X.

        Override in subclasses to implement position-specific behavior.
        Default: no-op (protocol exists but doesn't need to act on tick).

        Args:
            tick_state: Dict with tick, position, quarter, guardian, word, opcode
        """
        pass  # Default: no action needed


# =============================================================================
# WORKER PROTOCOL - For Mahajana-owned positions
# =============================================================================


class WorkerProtocol(MantraProtocol):
    """
    Basisklasse für WORKER Protokolle (Mahajana-owned).

    Positionen: 1,2,3, 5,6,7, 9,10,11, 13,14,15
    NICHT: 0, 4, 8, 12 (das sind HEAD Positionen)
    """

    @classmethod
    def mahajana(cls) -> Mahajana:
        """The Mahajana that owns this protocol."""
        guardian = cls.guardian()
        if not isinstance(guardian, Mahajana):
            raise TypeError(
                f"{cls.__name__} is at HEAD position {cls._position_index}, "
                f"but WorkerProtocol requires a WORKER position"
            )
        return guardian

    @classmethod
    def validate(cls) -> bool:
        """Validate this is a WORKER position."""
        if not super().validate():
            return False
        return not cls.is_head()


# =============================================================================
# HEAD PROTOCOL - For Avatara-owned positions
# =============================================================================


class HeadProtocol(MantraProtocol):
    """
    Basisklasse für HEAD Protokolle (Avatara-owned).

    Positionen: 0, 4, 8, 12 nur.
    """

    @classmethod
    def avatara(cls) -> Avatara:
        """The Avatara that owns this protocol."""
        guardian = cls.guardian()
        if not isinstance(guardian, Avatara):
            raise TypeError(
                f"{cls.__name__} is at WORKER position {cls._position_index}, but HeadProtocol requires a HEAD position"
            )
        return guardian

    @classmethod
    def validate(cls) -> bool:
        """Validate this is a HEAD position."""
        if not super().validate():
            return False
        return cls.is_head()


# =============================================================================
# PROTOCOL INTERFACE - For runtime_checkable protocols
# =============================================================================


@runtime_checkable
class MantraAware(TypingProtocol):
    """
    Protocol interface for classes that are Mantra-aware.

    Any class implementing this can be checked at runtime.
    """

    @classmethod
    def position(cls) -> MantraPosition:
        """Get the MantraPosition."""
        ...

    @classmethod
    def guardian(cls) -> Guardian:
        """Get the guardian."""
        ...

    @classmethod
    def opcode(cls) -> MantraOpCode:
        """Get the opcode."""
        ...


# =============================================================================
# PROTOCOL REGISTRY
# =============================================================================


class ProtocolRegistry:
    """
    Registry aller MantraProtocol Subklassen und Instanzen.

    TWO REGISTRIES:
        _registry:   Position → Protocol CLASS (metadata, discovery)
        _instances:  Position → Protocol INSTANCE (runtime dispatch)

    SATTVIC DISPATCH:
        Identity = Function. If you ARE position X, you ACT at position X.
        No side-channels. No handler lists. Direct dispatch via on_tick().

    USAGE:
        # Class registration (for metadata)
        @ProtocolRegistry.register
        class JanakaProtocol(WorkerProtocol):
            _position_index = 10

        # Instance registration (for dispatch)
        service = ManifestationService(...)
        ProtocolRegistry.register_instance(service)  # Uses _position_index

        # Dispatch (in mahamantra.tick())
        ProtocolRegistry.dispatch_tick(position, tick_state)
    """

    _registry: ClassVar[Dict[int, Type[MantraProtocol]]] = {}
    _instances: ClassVar[Dict[int, MantraProtocol]] = {}  # Position → instance
    _tick_listeners: ClassVar[List[Callable]] = []  # Global listeners (legacy)

    @classmethod
    def register(cls, protocol_class: Type[MantraProtocol]) -> Type[MantraProtocol]:
        """
        Register a protocol class.

        Usage as decorator:
            @ProtocolRegistry.register
            class ShuddhiProtocol(WorkerProtocol):
                _position_index = 5
        """
        idx = protocol_class._position_index
        if idx in cls._registry:
            existing = cls._registry[idx]
            raise ValueError(
                f"Position {idx} already registered to {existing.__name__}, cannot register {protocol_class.__name__}"
            )
        cls._registry[idx] = protocol_class
        return protocol_class

    @classmethod
    def get(cls, position_index: int) -> Optional[Type[MantraProtocol]]:
        """Get protocol class by position index."""
        return cls._registry.get(position_index)

    @classmethod
    def get_by_guardian(cls, guardian: Guardian) -> Optional[Type[MantraProtocol]]:
        """Get protocol class by guardian."""
        pos = None
        for p in MAHAMANTRA_POSITIONS:
            if p.guardian == guardian:
                pos = p
                break
        if pos:
            return cls._registry.get(pos.index)
        return None

    @classmethod
    def all_registered(cls) -> Dict[int, Type[MantraProtocol]]:
        """Get all registered protocols."""
        return dict(cls._registry)

    @classmethod
    def coverage(cls) -> tuple:
        """
        Get registration coverage.

        Returns (registered_count, total_positions).
        """
        return len(cls._registry), WORDS

    @classmethod
    def missing_positions(cls) -> List[int]:
        """Get list of positions without registered protocols."""
        return [i for i in range(WORDS) if i not in cls._registry]

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._registry.clear()
        cls._instances.clear()
        cls._tick_listeners.clear()

    # =========================================================================
    # INSTANCE REGISTRY - Runtime Dispatch (SATTVIC)
    # =========================================================================

    @classmethod
    def register_instance(cls, instance: MantraProtocol) -> None:
        """
        Register a protocol instance for tick dispatch.

        SATTVIC: Identity = Function.
        The instance's _position_index determines where it acts.

        Args:
            instance: MantraProtocol instance with _position_index set
        """
        position = instance._position_index
        if position < 0 or position > 15:
            raise ValueError(f"Instance has invalid _position_index: {position}")
        cls._instances[position] = instance

    @classmethod
    def unregister_instance(cls, position: int) -> None:
        """Unregister instance at position."""
        cls._instances.pop(position, None)

    @classmethod
    def get_instance(cls, position: int) -> Optional[MantraProtocol]:
        """Get registered instance for position."""
        return cls._instances.get(position)

    @classmethod
    def dispatch_tick(cls, position: int, tick_state: Dict) -> bool:
        """
        Dispatch tick to instance at position.

        SATTVIC DISPATCH:
            No lists. No callbacks. Direct call to on_tick().
            Identity = Function.

        Args:
            position: Mahamantra position (0-15)
            tick_state: Dict with tick, position, quarter, guardian, word, opcode

        Returns:
            True if instance exists and was called, False otherwise
        """
        instance = cls._instances.get(position)
        if instance is not None:
            instance.on_tick(tick_state)
            return True
        return False

    # =========================================================================
    # TICK LISTENERS - Runtime Discovery Without Spaghetti
    # =========================================================================

    @classmethod
    def tick_listener(cls, callback: Callable[[Dict], None]) -> Callable[[Dict], None]:
        """
        Register a tick listener as decorator.

        Usage:
            @ProtocolRegistry.tick_listener
            def on_tick(tick_state: Dict) -> None:
                print(f"Position: {tick_state['position']}")

        The callback receives the tick state dict with:
            - tick: Current tick counter (0-15)
            - position: Same as tick
            - quarter: Current quarter (genesis/dharma/karma/moksha)
            - guardian: Guardian name at this position
            - word: Holy name at this position
            - opcode: Opcode value at this position
        """
        if callback not in cls._tick_listeners:
            cls._tick_listeners.append(callback)
        return callback

    @classmethod
    def register_tick_listener(cls, callback: Callable[[Dict], None]) -> None:
        """Register a tick listener (non-decorator form)."""
        if callback not in cls._tick_listeners:
            cls._tick_listeners.append(callback)

    @classmethod
    def unregister_tick_listener(cls, callback: Callable[[Dict], None]) -> None:
        """Unregister a tick listener."""
        if callback in cls._tick_listeners:
            cls._tick_listeners.remove(callback)

    @classmethod
    def broadcast_tick(cls, tick_state: Dict) -> int:
        """
        Broadcast tick to all registered listeners.

        Called by mahamantra.tick() after advancing position.
        Returns number of listeners notified.
        """
        notified = 0
        for listener in cls._tick_listeners:
            try:
                listener(tick_state)
                notified += KSETRAJNA
            except Exception:
                # Don't let one failing listener break the tick
                pass
        return notified

    @classmethod
    def tick_listener_count(cls) -> int:
        """Get number of registered tick listeners."""
        return len(cls._tick_listeners)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base Classes
    "MantraProtocol",
    "WorkerProtocol",
    "HeadProtocol",
    # Interface
    "MantraAware",
    # Registry
    "ProtocolRegistry",
]
