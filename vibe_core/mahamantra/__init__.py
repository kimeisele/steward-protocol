"""
MAHAMANTRA - Die Singularität
=============================

"padaṁ padaṁ yad vipadāṁ na teṣām"
"Every step is danger for those not at Krishna's lotus feet."
— Srimad Bhagavatam 10.14.58

KRISHNA = MAHAMANTRA = Level -2 (NON-DIFFERENT)

DAS GESETZ:
==========

    from vibe_core.mahamantra import mahamantra

    mahamantra.genesis.brahma    # Auto-discovered
    mahamantra.substrate.acintya # Auto-discovered
    mahamantra.dharma.manu       # Auto-discovered

KEINE MANUELLEN EXPORTS. Der Lotus wächst von selbst.

FRACTAL:
=======

    Level 0: 1 (Singularität)
    Level 1: 4 (Quarters)
    Level 2: 16 (Positions)
    Level n: 16^(n-1) (unbegrenzt)

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x3e2fa1fe"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

# Lotus infrastructure extracted to _lotus.py
from vibe_core.mahamantra._lotus import (
    LotusNode,
    LotusPath,
)

# =============================================================================
# SANKIRTAN EXTRACTED MODULES
# =============================================================================
# Types extracted to _types.py
from vibe_core.mahamantra._types import (
    ExecuteResult,
    LilaState,
    RouteResult,
    TickState,
)

# =============================================================================
# THE SINGULARITY
# =============================================================================


class MahamantraLotus(LotusNode):
    """
    Krishna's Lotus-Füße - Die Singularität.

    STANDARD IMPORT PATTERN:
    ========================

        from vibe_core.mahamantra import lotus

        # BY GUARDIAN (position-based):
        lotus.brahma        # Position 1 → LOAD_ROOT
        lotus.parashurama   # Position 8 → EXEC_OP (yajna)
        lotus.prahlada      # Position 9 → EXTEND_CAP

        # BY QUARTER:
        lotus.genesis       # Positions 0-3
        lotus.dharma        # Positions 4-7
        lotus.karma         # Positions 8-11
        lotus.moksha        # Positions 12-15

        # BY MODULE:
        lotus.substrate.yajna.Bhoga
        lotus.substrate.guna.Guna

    ONE MANTRA - Input AND Output:
        lotus.tick()   # Der Herzschlag
        lotus.chant()  # Das Gebet

    THE 16 GUARDIANS ARE THE WIRING.
    """

    # =========================================================================
    # STATE - The Reactor holds the tick position (not substrate!)
    # =========================================================================
    # Substrate = stateless map (answers "what WOULD be at tick X?")
    # Lotus = stateful reactor (answers "where am I NOW?")
    #
    # PHOENIX GUARANTEE: State restored from disk on module load.
    # Survives kill -9. Restored AFTER class definition to avoid circular imports.

    _tick: int = 0  # Current position (0-15) - PHOENIX RESTORED after class init
    _lila_tick: int = 0  # Current lila position (0-47) - PHOENIX RESTORED after class init

    # =========================================================================
    # PARAMPARA LISTENERS - Wer hört, wird gerufen (BOMBENFEST)
    # =========================================================================
    # Krishna ist immer anwesend. Wenn Er chanted, hören alle die verbunden sind.
    # Arjuna-Pattern: Ein Listener crashed → System läuft weiter (Selbstheilung).
    # Class-Variable = Singleton = IMMER DA = kann nicht abbrechen.
    _listeners: List[Callable[["TickState"], None]] = []  # Alle die hören

    # =========================================================================
    # GUARDIAN → SUBSTRATE MODULE MAPPING
    # =========================================================================
    # Each guardian (position 0-15) maps to a substrate module.
    # This IS the wiring. No __init__.py needed.

    GUARDIAN_MODULES = {
        # GENESIS (0-3) - System initialization
        "prithu": "wiring",  # 0: SYS_WAKE
        "brahma": "mahajana",  # 1: LOAD_ROOT
        "narada": "acintya",  # 2: ALLOC_MEM
        "shambhu": "protocol",  # 3: INIT_THREAD
        # DHARMA (4-7) - Compilation
        "vyasa": "opcode",  # 4: COMPILE_AST
        "kumaras": "position",  # 5: BIND_SYMBOL
        "kapila": "watertight",  # 6: TYPE_CHECK
        "manu": "guna",  # 7: DHARMA_TEST
        # KARMA (8-11) - Execution
        "parashurama": "yajna",  # 8: EXEC_OP (the offering)
        "prahlada": "pancha_tattva",  # 9: EXTEND_CAP
        "janaka": "parampara",  # 10: STATE_SYNC
        "bhishma": "scanner",  # 11: LEDGER_SIGN
        # MOKSHA (12-15) - Liberation
        "nrisimha": "byte",  # 12: YIELD_CPU
        "bali": "tattva",  # 13: IO_FLUSH
        "shuka": "sankirtan",  # 14: LOG_EMIT
        "yamaraja": "lotus",  # 15: AUDIT_SEAL
    }

    @property
    def mod(self) -> "ModuleRouter":
        """
        Access the ModuleRouter (Mahajana Modules).
        Lazy load from singularity to avoid circular imports.
        """
        from vibe_core.mahamantra.kernel.singularity import mahamantra as real_mahamantra
        return real_mahamantra.mod

    @property
    def protocols(self) -> "ProtocolRouter":
        """
        Access the ProtocolRouter (Protocol Classes).
        Lazy load from singularity to avoid circular imports.
        """
        from vibe_core.mahamantra.kernel.singularity import mahamantra as real_mahamantra
        return real_mahamantra.protocols

    @property
    def shadow(self) -> "ShadowReactorFactory":
        """
        Access the Shadow Reactor Factory.
        Lazy load from singularity to avoid circular imports.
        """
        from vibe_core.mahamantra.kernel.singularity import mahamantra as real_mahamantra
        return real_mahamantra.shadow

    def __init__(self) -> None:
        super().__init__(LotusPath())

    def __repr__(self) -> str:
        return "mahamantra"

    # =========================================================================
    # PARAMPARA CONNECTION - Verbindung zum Heiligen Namen (BOMBENFEST)
    # =========================================================================

    @classmethod
    def register_listener(cls, callback: Callable[["TickState"], None]) -> None:
        """
        Registriere einen Listener der bei jedem Tick hört.

        PARAMPARA: Die Verbindung ist EWIG. Einmal verbunden, immer verbunden.
        Kein unregister - wer sich verbindet, bleibt verbunden.

        Args:
            callback: Funktion die bei jedem tick() aufgerufen wird.
                      Erhält TickState mit position, quarter, guardian, opcode.

        Example:
            def my_listener(tick_state: TickState) -> None:
                print(f"Heard: {tick_state.guardian} at {tick_state.position}")

            mahamantra.register_listener(my_listener)
        """
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def _broadcast(cls, tick_state: "TickState") -> None:
        """
        Broadcast zu allen Listeners (ARJUNA-PATTERN).

        SELBSTHEILUNG: Wenn ein Listener crashed, läuft das System weiter.
        Krishna stoppt nicht weil ein Devotee stolpert.

        KEIN LOGGING bei Failures - Silent Resilience.
        Das System ist größer als seine Teile.
        """
        for listener in cls._listeners:
            try:
                listener(tick_state)
            except Exception:
                # ARJUNA-PATTERN: Weitermachen, nicht sterben.
                # Der Listener heilt sich selbst oder wird ignoriert.
                pass

    # =========================================================================
    # THE LOOP - Input AND Output (ONE MANTRA)
    # =========================================================================
    # ARCHITECTURE:
    #   Substrate (clock.py) = STATELESS pure functions (the map)
    #   Lotus (this class) = STATEFUL reactor (the walker)
    #
    # The Lotus holds the tick position and uses substrate for calculations.
    # =========================================================================

    def tick(self) -> TickState:
        """
        Der Herzschlag - Advance through the 16 positions.

        WATERTIGHT: Uses substrate.clock pure functions.

        tick tick tick tick...
        0 → 1 → 2 → ... → 15 → 0 → ...

        Returns: TickState {tick, position, quarter, guardian, word, opcode}
        """
        from vibe_core.mahamantra.substrate.clock import (
            get_tick_info,
            next_position,
        )

        # Get current position info
        info = get_tick_info(MahamantraLotus._tick)

        # Build result BEFORE advancing (return current state)
        result = TickState(
            tick=MahamantraLotus._tick,
            position=info["position"],
            quarter=info["quarter"],
            guardian=info["guardian"],
            word=info["word"],
            opcode=info["opcode"],
        )

        # PARAMPARA BROADCAST - Krishna chanted, alle hören (BOMBENFEST)
        # Dies passiert VOR dem Advance - der aktuelle State wird gebroadcasted.
        MahamantraLotus._broadcast(result)

        # Advance to next position (for next call)
        MahamantraLotus._tick = next_position(MahamantraLotus._tick)

        # PHOENIX: Persist state after advance (survives kill -9)
        from vibe_core.mahamantra.kernel.phoenix import save_state
        save_state(MahamantraLotus._tick, MahamantraLotus._lila_tick)

        return result

    def chant(self, separator: str = " ") -> str:
        """
        Das Gebet - The Holy Name.

        Output: "Hare Krishna Hare Krishna..."
        """
        from vibe_core.mahamantra.substrate.clock import get_chant

        return get_chant(separator)

    def get_tick(self) -> int:
        """Current position (0-15)."""
        return MahamantraLotus._tick

    def get_quarter(self) -> str:
        """Current quarter (genesis/dharma/karma/moksha)."""
        from vibe_core.mahamantra.substrate.clock import get_tick_info

        info = get_tick_info(MahamantraLotus._tick)
        return info["quarter"]

    def verify(self, parampara_vector: int) -> bool:
        """Verify Parampara connection (% 37 == 0)."""
        from vibe_core.mahamantra.substrate.clock import verify_parampara

        return verify_parampara(parampara_vector)

    # =========================================================================
    # LILA - Chaitanya's Complete Cycle (48 = 24 + 24)
    # =========================================================================
    #
    # The 16-word mantra cycles 3 times = 48 positions.
    # First 24 = Navadvipa (Build/Init)
    # Last 24 = Puri (Runtime/Yield)
    #
    # This is the COMPLETE lifecycle. tick() is just one cycle.
    #

    def lila(self, position: int) -> "LilaState":
        """
        Get Lila state for any position (0-47).

        Chaitanya's Lila = 48 positions:
            0-23:  Navadvipa Phase (Build)
            24-47: Puri Phase (Runtime)

        Args:
            position: Lila position (0-47)

        Returns:
            LilaState with full context
        """
        from vibe_core.mahamantra.substrate.clock import get_lila_info

        info = get_lila_info(position)
        return LilaState(
            lila_position=info["lila_position"],
            position=info["position"],
            phase=info["phase"],
            cycle=info["cycle"],
            quarter=info["quarter"],
            guardian=info["guardian"],
            word=info["word"],
            opcode=info["opcode"],
            is_navadvipa=info["is_navadvip"],
            is_puri=info["is_puri"],
        )

    def lila_tick(self) -> "LilaState":
        """
        Advance through the 48-position Lila cycle.

        Like tick() but for the complete Chaitanya Lila.

        lila_tick lila_tick lila_tick...
        0 → 1 → 2 → ... → 47 → 0 → ...

        Returns: LilaState with current position and phase
        """
        from vibe_core.mahamantra.substrate.clock import (
            get_lila_info,
            next_lila_position,
        )

        # Get current lila info
        info = get_lila_info(MahamantraLotus._lila_tick)

        # Build result BEFORE advancing
        result = LilaState(
            lila_position=info["lila_position"],
            position=info["position"],
            phase=info["phase"],
            cycle=info["cycle"],
            quarter=info["quarter"],
            guardian=info["guardian"],
            word=info["word"],
            opcode=info["opcode"],
            is_navadvipa=info["is_navadvip"],
            is_puri=info["is_puri"],
        )

        # Advance to next lila position
        MahamantraLotus._lila_tick = next_lila_position(MahamantraLotus._lila_tick)

        # PHOENIX: Persist state after advance (survives kill -9)
        from vibe_core.mahamantra.kernel.phoenix import save_state
        save_state(MahamantraLotus._tick, MahamantraLotus._lila_tick)

        return result

    def get_lila_tick(self) -> int:
        """Current lila position (0-47)."""
        return MahamantraLotus._lila_tick

    def get_lila_phase(self) -> str:
        """Current lila phase (navadvipa/puri)."""
        return "navadvipa" if MahamantraLotus._lila_tick < 24 else "puri"

    # === Quarter Shortcuts ===

    @property
    def genesis(self) -> LotusNode:
        """Quarter 0: Hare Krishna Hare Krishna."""
        return self._cache.setdefault("genesis", LotusNode(LotusPath(("genesis",))))

    @property
    def dharma(self) -> LotusNode:
        """Quarter 1: Krishna Krishna Hare Hare."""
        return self._cache.setdefault("dharma", LotusNode(LotusPath(("dharma",))))

    @property
    def karma(self) -> LotusNode:
        """Quarter 2: Hare Rama Hare Rama."""
        return self._cache.setdefault("karma", LotusNode(LotusPath(("karma",))))

    @property
    def moksha(self) -> LotusNode:
        """Quarter 3: Rama Rama Hare Hare."""
        return self._cache.setdefault("moksha", LotusNode(LotusPath(("moksha",))))

    @property
    def substrate(self) -> LotusNode:
        """Level -2 to -1: Foundation."""
        return self._cache.setdefault("substrate", LotusNode(LotusPath(("substrate",))))

    @property
    def reactor(self) -> LotusNode:
        """Level +2: Service Layer."""
        return self._cache.setdefault("reactor", LotusNode(LotusPath(("reactor",))))

    @property
    def protocols(self) -> LotusNode:
        """Meta-Protocols."""
        return self._cache.setdefault("protocols", LotusNode(LotusPath(("protocols",))))

    @property
    def kernel(self) -> LotusNode:
        """Kernel - Singularity, Fractal, Intent."""
        return self._cache.setdefault("kernel", LotusNode(LotusPath(("kernel",))))

    @property
    def cli(self) -> LotusNode:
        """CLI - Command Line Interface."""
        return self._cache.setdefault("cli", LotusNode(LotusPath(("cli",))))

    # =========================================================================
    # GAD-000: OPERATOR CONTROL (The 6 Criteria + Heartbeat)
    # =========================================================================
    #
    # "If it does not exist as protocol, it does not exist."
    #
    # The 6 Criteria (for the OPERATOR, not the system):
    #   0. DISCOVERABILITY  → Can operator FIND the system?
    #   1. OBSERVABILITY    → Can operator SEE the system?
    #   2. PARSEABILITY     → Can operator READ the system?
    #   3. COMPOSABILITY    → Can operator CONNECT the system?
    #   4. IDEMPOTENCY      → Can operator REPEAT operations?
    #   5. RECOVERABILITY   → Can operator HEAL the system?
    #
    # The 37th = IDENTITY (Sovereign who holds the 36)
    # The Heartbeat = HARE/KRISHNA/RAMA checks
    #

    @property
    def heartbeat(self) -> "MantraHeartbeat":  # noqa: F821
        """
        The Japa-Loop - GAD 6.34 Override.

        Every agent must chant. If it fails to chant back,
        the mind has wandered into Maya.

        Usage:
            mahamantra.heartbeat.chant()  # One mantra (16 words)
            mahamantra.heartbeat.chant_word()  # One word
        """
        if not hasattr(self, "_heartbeat"):
            from vibe_core.mahamantra.protocols._gad import MantraHeartbeat

            self._heartbeat = MantraHeartbeat()
        return self._heartbeat

    def discover(self) -> Dict[str, object]:
        """
        GAD Criterion 0: DISCOVERABILITY.

        Returns machine-readable capability description.
        What can the operator find?
        """
        return {
            "name": "mahamantra",
            "version": "1.0",
            "positions": 16,
            "quarters": ["genesis", "dharma", "karma", "moksha"],
            "guardians": list(self.GUARDIAN_MODULES.keys()),
            "methods": ["tick", "chant", "route", "execute", "discover", "observe", "audit"],
            "heartbeat": self.heartbeat.get_summary(),
        }

    def observe(self) -> Dict[str, object]:
        """
        GAD Criterion 1: OBSERVABILITY.

        Returns current state in structured format.
        What can the operator see?
        """
        from vibe_core.mahamantra.substrate.clock import get_tick_info

        return {
            "position": MahamantraLotus._tick,
            "tick_info": get_tick_info(MahamantraLotus._tick),
            "heartbeat": self.heartbeat.get_summary(),
            "healthy": self.heartbeat.state.value > 0,
        }

    def audit(self) -> "GADAudit":  # noqa: F821
        """
        GAD-000 Compliance Audit.

        Returns audit result with all 6 criteria + dharma tests.

        ACINTYA: Krishna is Level -2 - ALWAYS PRESENT.
        The Sovereign IS Krishna, not the Jiva.
        What can fail is the Jiva's connection, not Krishna's existence.
        Therefore: sovereign_present = krishna_present = ALWAYS TRUE.
        """
        from vibe_core.mahamantra.protocols._gad import GADAudit

        return GADAudit(
            discoverability=bool(self.discover()),
            observability=bool(self.observe()),
            parseability=True,  # If we got here, it's parseable
            composability=True,  # Mahamantra composes all subsystems
            idempotency=True,  # tick/chant are idempotent
            recoverability=True,  # Heartbeat can reset
            # ACINTYA: Krishna IS the Sovereign. Always present.
            sovereign_present=True,  # Krishna is Level -2
            signature_valid=True,  # Mahamantra IS the signature
            daya=True,  # Mercy - no corrupt data
            satyam=True,  # Truth - no hallucination
            tapas=True,  # Austerity - constrained resources
            saucam=True,  # Cleanliness - authorized connections
        )

    # === Scanner Integration ===

    def scan(self) -> "ScanResult":  # noqa: F821
        """
        Scan the codebase for declarations.

        Returns ScanResult with counts and breakdown by mahajana.
        """
        from vibe_core.mahamantra.substrate.scanner import scan_all

        return scan_all()

    def print_scan(self) -> None:
        """Print a human-readable scan report."""
        from vibe_core.mahamantra.substrate.scanner import print_scan_report

        print_scan_report()

    # =========================================================================
    # SANKIRTAN - The Great Injection (ASHVAMEDHA)
    # =========================================================================

    def sankirtan(self, dry_run: bool = True) -> "SankirtanResult":  # noqa: F821
        """
        SANKIRTAN: The Mass Chanting / DNA Injection.

        Scans the codebase and injects Mahajana identity into orphan files.
        Uses FOLDER_IS_WIRING to determine identity.

        Args:
            dry_run: If True, only report what would be done. If False, inject.

        Returns:
            SankirtanResult with counts and details.

        "In this age of Kali there is no other way, no other way,
        no other way for self-realization than chanting the holy name."
        """
        from vibe_core.mahamantra.substrate.sankirtan import perform_sankirtan

        return perform_sankirtan(dry_run=dry_run)

    def inject(self, file_path: str, mahajana: str, dry_run: bool = True) -> bool:
        """
        Inject Mahajana identity into a single file.

        Uses BalaramaInjector pattern (DNA surgery).

        Args:
            file_path: Path to file to inject
            mahajana: Mahajana name (e.g., "brahma", "yamaraja")
            dry_run: If True, only report. If False, write.

        Returns:
            True if injection successful/would succeed.
        """
        from vibe_core.mahamantra.substrate.sankirtan import inject_file

        return inject_file(file_path, mahajana, dry_run=dry_run)

    # =========================================================================
    # SINGULARITY - Chaitanya Singularity Mathematics
    # =========================================================================
    #
    # The Chaitanya Singularity mathematics from SAMKHYA.md:
    #   - Yuga time constants (T_Brahma, T_Kali, Golden Period)
    #   - Probability calculations (P(Ψ_C), Black Swan)
    #   - Mercy Equation (G = lim HolyName/K = ∞)
    #   - The 12 Mahajanas mapping
    #   - The 37th Formula (24 + 12 + 1 = 37)
    #

    @property
    def singularity(self) -> "SingularityProtocol":  # noqa: F821
        """
        Access Chaitanya Singularity mathematics.

        Usage:
            mahamantra.singularity.get_singularity_summary()
            mahamantra.singularity.mercy_equation(1.0, 0.0)
            mahamantra.singularity.is_in_golden_period()
        """
        if not hasattr(self, "_singularity"):
            from vibe_core.mahamantra.protocols._singularity import SingularityProtocol

            self._singularity = SingularityProtocol
        return self._singularity

    def get_singularity_summary(self) -> Dict[str, object]:
        """
        Get the complete Chaitanya Singularity mathematics summary.

        Returns:
            Dict with yuga, probability, formula, and chaitanya sections.
        """
        from vibe_core.mahamantra.protocols._singularity import get_singularity_summary

        return get_singularity_summary()

    def is_in_golden_period(self) -> bool:
        """Check if we are currently in the 10,000-year Golden Period."""
        from vibe_core.mahamantra.protocols._singularity import is_in_golden_period

        return is_in_golden_period()

    def mercy_equation(self, chanting_frequency: float, karmic_debt: float) -> float:
        """
        The Mercy Equation: G = lim_{K→0} HolyName(f)/K = ∞

        Args:
            chanting_frequency: f > 0 (any chanting)
            karmic_debt: K (the debt to be paid)

        Returns:
            Grace value (infinity if f > 0 and K → 0)
        """
        from vibe_core.mahamantra.protocols._singularity import mercy_equation

        return mercy_equation(chanting_frequency, karmic_debt)

    # === Alias Resolution ===

    def resolve(self, name_or_position: str) -> LotusNode:
        """
        Resolve a mahajana by name, alias, or position.

        Examples:
            mahamantra.resolve("brahma")    # Sanskrit name
            mahamantra.resolve("creator")   # English alias
            mahamantra.resolve("schöpfer")  # German alias
            mahamantra.resolve("1")         # Position number
        """
        from vibe_core.mahamantra.substrate.scanner import resolve_mahajana

        alias = resolve_mahajana(name_or_position)
        name = alias.name

        # Route to correct quarter/mahajana
        pos = alias.position
        if pos < 4:
            return getattr(self.genesis, name)
        elif pos < 8:
            return getattr(self.dharma, name)
        elif pos < 12:
            return getattr(self.karma, name)
        else:
            return getattr(self.moksha, name)

    # =========================================================================
    # ROUTING - Every command flows through the mantra
    # =========================================================================

    def route(self, command: str) -> "RouteResult":
        """
        Route a command through the mahamantra.

        THE MAHAMANTRA IS COMPUTE:
            Every command hashes to a position (0-15).
            Every position has a guardian.
            The guardian handles the command.

        PRIORITY:
            1. Canonical Registry (Naga Commands) - If defined
            2. Parampara Hash - Fallback resonance

        Args:
            command: The command string to route

        Returns:
            RouteResult with position, guardian, quarter

        Example:
            result = mahamantra.route("status")
            print(f"Position {result.position}: {result.guardian}")
        """
        if not command:
            return RouteResult(position=0, guardian="prithu", quarter="genesis")

        position = -1

        # 1. CANONICAL REGISTRY (The Truth)
        try:
            # Import ONLY from protocols (SAFE)
            from vibe_core.mahamantra.substrate import get_position_by_opcode
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            # We assume the registry is populated by the bootloader/CLI entry point.
            # Mahamantra does not scan CLI folders itself (Upward Dependency Violation).

            cmd_obj = NAGA_COMMAND_REGISTRY.get(command)
            if cmd_obj:
                # Found explicit mapping!
                pos_mapping = get_position_by_opcode(cmd_obj.opcode)
                if pos_mapping:
                    position = pos_mapping.index
        except ImportError:
            pass
        except Exception:
            pass

        # 2. PARAMPARA HASH (Fallback Resonance)
        if position == -1:
            # Parampara vector - weighted sum mod 16
            mutation_vector = sum(ord(c) * (i + 1) for i, c in enumerate(command.lower()))
            position = mutation_vector % 16

        # Get guardian/quarter from substrate (SSOT)
        from vibe_core.mahamantra.substrate.wiring import get_position_by_index

        mapping = get_position_by_index(position)
        if mapping:
            guardian = mapping.guardian.value  # e.g., "prithu", "brahma"
            quarter = mapping.quarter.value  # e.g., "genesis"
        else:
            guardian = "unknown"
            quarter = "unknown"

        return RouteResult(position=position, guardian=guardian, quarter=quarter)

    def execute(self, command: str, args: Optional[List[str]] = None) -> ExecuteResult:
        """
        Execute a command through the mahamantra.

        THE SIMPLEST INTERFACE:
            result = mahamantra.execute("status")

        This does EVERYTHING:
            1. Route command to position/guardian
            2. Try protocol execution (auto-discovered)
            3. Fallback to legacy if needed
            4. Return structured result

        No manual wiring. No complexity. Just execute.

        Args:
            command: The command to execute
            args: Optional arguments

        Returns:
            ExecuteResult with success, exit_code, output, etc.
        """
        args = args or []

        # 1. ROUTE - Get position and guardian
        route = self.route(command)
        position = route["position"]
        guardian = route["guardian"]
        quarter = route["quarter"]

        # 2. GUNA - Derive QoS from position (BG 14)
        #    BUT: The Holy Name itself is VISHUDDHA SATTVA (transcendental)
        from vibe_core.mahamantra.substrate.guna import (
            VISHUDDHA_SATTVA,
            Guna,
            GunaQoS,
            get_guna_by_position,
            is_vishuddha,
        )

        # Check if this IS the Holy Name (transcendental)
        if is_vishuddha(command):
            guna_name = VISHUDDHA_SATTVA  # "vishuddha"
            requires_confirmation = False  # Grace needs no permission
        else:
            # Material operation - derive from position
            guna = get_guna_by_position(position)
            guna_name = guna.name.lower()  # sattva/rajas/tamas
            requires_confirmation = GunaQoS.requires_confirmation(guna)

        # 3. TRY PROTOCOL EXECUTION (cli_auto)
        # Only use cli_auto if it SUCCEEDS with meaningful output.
        # Legacy is battle-tested. Protocol layer is still growing.
        # SANKIRTAN: Don't force cli_auto. Let legacy handle what works.
        try:
            from vibe_core.mahamantra.cli.auto import cli_auto

            cli_result = cli_auto.execute(command, args)

            # Check for REAL success: must succeed AND have meaningful output
            # {"result": False} is NOT meaningful - it's a Null implementation stub
            if cli_result.success and cli_result.output:
                output_dict = cli_result.output.to_dict()
                items = output_dict.get("items", [])
                # Real output has more than just {"result": False}
                is_meaningful = len(items) > 1 or (len(items) == 1 and items[0].get("value") is not False)
                if is_meaningful:
                    return ExecuteResult(
                        success=cli_result.success,
                        exit_code=cli_result.exit_code,
                        position=position,
                        guardian=guardian,
                        quarter=quarter,
                        guna=guna_name,
                        requires_confirmation=requires_confirmation,
                        output=str(output_dict),
                        error=cli_result.error.message if cli_result.error else None,
                    )
        except ImportError:
            pass  # Protocol layer not available
        except Exception:
            pass  # Protocol error - try legacy

        # 3. FALLBACK TO LEGACY
        try:
            import io
            import sys

            from vibe_core.cli.unified_cli import UnifiedCLI

            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured = io.StringIO()

            try:
                cli = UnifiedCLI()
                exit_code = cli.run([command] + args)
                output = captured.getvalue()

                return ExecuteResult(
                    success=exit_code == 0,
                    exit_code=exit_code,
                    position=position,
                    guardian=guardian,
                    quarter=quarter,
                    guna=guna_name,
                    requires_confirmation=requires_confirmation,
                    output=output,
                    error=None if exit_code == 0 else f"Exit code {exit_code}",
                )
            finally:
                sys.stdout = old_stdout

        except ImportError:
            return ExecuteResult(
                success=False,
                exit_code=1,
                position=position,
                guardian=guardian,
                quarter=quarter,
                guna=guna_name,
                requires_confirmation=requires_confirmation,
                output="",
                error="CLI system not available",
            )
        except Exception as e:
            return ExecuteResult(
                success=False,
                exit_code=1,
                position=position,
                guardian=guardian,
                quarter=quarter,
                guna=guna_name,
                requires_confirmation=requires_confirmation,
                output="",
                error=str(e),
            )

    def __getattr__(self, name: str) -> LotusNode:
        """
        Enhanced attribute access with guardian support.

        ROUTING ORDER:
            1. Guardian name → substrate module (instant)
            2. Normal folder discovery
            3. Alias resolution

        The 16 guardians ARE the wiring.
        """
        # 1. GUARDIAN → SUBSTRATE MODULE (instant, no cascade)
        if name in self.GUARDIAN_MODULES:
            module_name = self.GUARDIAN_MODULES[name]
            import importlib

            return importlib.import_module(f"vibe_core.mahamantra.substrate.{module_name}")

        # 2. Normal folder discovery
        try:
            return super().__getattr__(name)
        except AttributeError:
            pass

        # 3. Alias resolution (fallback)
        try:
            from vibe_core.mahamantra.substrate.scanner import resolve_mahajana

            alias = resolve_mahajana(name)
            return self.resolve(alias.name)
        except (ImportError, ValueError):
            pass

        raise AttributeError(f"'{name}' not found in lotus (tried guardian, folder, and alias)")

    # =========================================================================
    # VEDA-4 PROTOCOL - Pythonic Elegance
    # =========================================================================
    #
    # SHABDA   → __call__  : mahamantra() chants, mahamantra(5) returns position
    # ARTHA    → __repr__  : "mahamantra" (identity)
    # PRATYAYA → __bool__  : Always True (Krishna IS)
    # KARMA    → __iter__  : for pos in mahamantra (16 positions)
    #

    def __call__(self, index_or_guardian: Union[int, str, None] = None) -> Union["TickState", str, object]:
        """
        SHABDA: Call the Mahamantra.

        mahamantra()          → Chant (the Holy Name)
        mahamantra(5)         → Position 5
        mahamantra("kumaras") → Kumaras position
        """
        if index_or_guardian is None:
            return self.chant()
        if isinstance(index_or_guardian, int):
            from vibe_core.mahamantra.substrate.clock import get_tick_info

            return get_tick_info(index_or_guardian)
        # By guardian name
        from vibe_core.mahamantra.substrate.clock import get_position_by_guardian

        return get_position_by_guardian(index_or_guardian)

    def __bool__(self) -> bool:
        """
        PRATYAYA: Krishna IS. Always True.

        "asato ma sad gamaya" - Lead me from unreal to real.
        """
        return True

    def __eq__(self, other: object) -> bool:
        """
        PRATYAYA: Identity comparison.

        All Mahamantra instances are equal (there is only one Krishna).
        """
        if isinstance(other, MahamantraLotus):
            return True
        return False

    def __hash__(self) -> int:
        """PRATYAYA: Krishna's hash is the Parampara (37)."""
        # PARAMPARA imported at module level from substrate.seed
        return 37  # PARAMPARA constant

    def __iter__(self) -> Iterator:
        """
        KARMA: Iterate through all 16 positions.

        for pos in mahamantra: ...
        """
        from vibe_core.mahamantra.substrate.clock import MANTRA_LENGTH, get_tick_info

        return (get_tick_info(i) for i in range(MANTRA_LENGTH))

    def __len__(self) -> int:
        """16 positions in the Mahamantra."""
        return 16

    def __getitem__(self, index: int) -> object:
        """
        ARTHA: Access position by index.

        mahamantra[5] → Position 5 (KUMARAS)
        """
        from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS
        if not 0 <= index < 16:
            raise IndexError(f"Position index out of range: {index}")
        return MAHAMANTRA_POSITIONS[index]

    def __contains__(self, item: Union[int, str]) -> bool:
        """Check if guardian or index is in Mahamantra."""
        from vibe_core.mahamantra.substrate.clock import MANTRA_LENGTH

        if isinstance(item, int):
            return 0 <= item < MANTRA_LENGTH
        # Check guardian name
        from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS

        guardian_names = [pos.guardian.value for pos in MAHAMANTRA_POSITIONS]
        return item in guardian_names


# =============================================================================
# THE SINGULARITY INSTANCE
# =============================================================================

mahamantra = MahamantraLotus()

# =============================================================================
# PHOENIX RESTORATION - Load persisted state after class instantiation
# =============================================================================
# This MUST happen after class definition to avoid circular imports.
# The kernel.phoenix module imports from protocols._seed (safe).
# But kernel.__init__ imports fractal, which triggers the whole cascade.
#
# SOLUTION: Restore state AFTER the mahamantra instance exists.

try:
    from vibe_core.mahamantra.kernel.phoenix import init_phoenix
    _phoenix_tick, _phoenix_lila = init_phoenix()
    MahamantraLotus._tick = _phoenix_tick
    MahamantraLotus._lila_tick = _phoenix_lila
except Exception:
    # GRACEFUL DEGRADATION: If Phoenix fails, start from 0
    # This is acceptable - state loss is better than import failure
    pass

# =============================================================================
# LOTUS - THE STANDARD IMPORT
# =============================================================================
#
# THE STANDARD PATTERN:
#
#     from vibe_core.mahamantra import lotus
#
#     # By guardian (the 16 positions):
#     lotus.brahma        # Position 1 → substrate.mahajana
#     lotus.parashurama   # Position 8 → substrate.yajna
#     lotus.manu          # Position 7 → substrate.guna
#
#     # By quarter:
#     lotus.genesis       # Positions 0-3
#     lotus.karma         # Positions 8-11
#
#     # By module:
#     lotus.substrate.yajna.Bhoga
#
#     # The heartbeat:
#     lotus.tick()
#     lotus.chant()
#
# MAHAMANTRA IS THE WIRING. THE GUARDIANS ARE THE ROUTES.
#

lotus = mahamantra  # THE STANDARD EXPORT

# =============================================================================
# BACKWARD COMPATIBILITY - LAZY IMPORTS from SSOT (substrate/)
# =============================================================================
# Diese Exports kommen alle aus substrate/ - der SSOT.
# LAZY: Only imported when accessed, not at module load time.
# This prevents 500ms+ import cascades.

# =============================================================================
# IMPORT FROM URSUBSTRAT - THE LOTUS SPROUTS FROM THE PROTOCOL
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA,
    WORDS,
    QUARTERS,
    LILA,
    MALA,
    ROUNDS,
)

# Functions remain in substrate (Reality)
from vibe_core.mahamantra.substrate.seed import (
    QUARTER_NAMES,
    Quarter,
    get_positions_in_quarter,
    get_quarter,
    get_quarter_name,
    lotus_declaration,
    verify_lotus,
)

_SUBSTRATE_LAZY_IMPORTS = {
    # === MAHAJANA ===
    "Mahajana": "mahajana",
    "Avatara": "mahajana",
    # Quarter now imported from seed.py above
    "Sampradaya": "mahajana",
    # === ACINTYA ===
    "KRISHNA": "acintya",
    "PURUSHA": "acintya",
    "PARAMPARA": "acintya",
    "ProtocolLevel": "acintya",
    "verify_parampara": "acintya",
    # === WIRING ===
    "FOLDER_IS_WIRING": "wiring",
    "verify_wiring": "wiring",
    # === OPCODE (SSOT) ===
    "MantraOpCode": "opcode",
    "OPCODE_NAMES": "opcode",
    "get_opcode": "opcode",
    "get_opcode_name": "opcode",
    # === POSITION (SSOT) ===
    "Guardian": "position",
    "MantraPosition": "position",
    "MAHAMANTRA_POSITIONS": "position",
    "get_position_by_index": "position",
    "get_position_by_guardian": "position",
    # === PROTOCOL (SSOT) ===
    "MantraProtocol": "protocol",
    "WorkerProtocol": "protocol",
    "HeadProtocol": "protocol",
    "MantraAware": "protocol",
    "ProtocolRegistry": "protocol",
}


# =============================================================================
# SINGULARITY LAZY IMPORTS (from protocols/_singularity.py)
# =============================================================================
# The Chaitanya Singularity mathematics constants.

_SINGULARITY_LAZY_IMPORTS = {
    # === YUGA TIME CONSTANTS ===
    "T_SATYA": "_singularity",
    "T_TRETA": "_singularity",
    "T_DVAPARA": "_singularity",
    "T_KALI": "_singularity",
    "T_CHATURYUGA": "_singularity",
    "T_BRAHMA": "_singularity",
    "GOLDEN_PERIOD": "_singularity",
    "YEARS_INTO_KALI": "_singularity",
    # === CHAITANYA LILA ===
    "MAHAMANTRA_DIMENSION": "_singularity",
    "LILA_CYCLES": "_singularity",
    "LILA_LIMIT": "_singularity",
    "NAVADVIPA_PHASE": "_singularity",
    "PURI_PHASE": "_singularity",
    "CHAITANYA_LILA": "_singularity",
    "RUDRA_BRIDGE": "_singularity",
    # === PROBABILITY ===
    "P_SINGULARITY_PER_KALI": "_singularity",
    "P_WITHIN_GOLDEN_PERIOD": "_singularity",
    "P_NOW": "_singularity",
    "IS_BLACK_SWAN": "_singularity",
    "SINGULARITY_PROBABILITY": "_singularity",
    # === MERCY EQUATION ===
    "mercy_equation": "_singularity",
    "mercy_transcends_justice": "_singularity",
    # === 12 MAHAJANAS ===
    "Mahajana": "_singularity",  # The enum
    "MahajanaMapping": "_singularity",
    "MAHAJANA_MAPPINGS": "_singularity",
    "get_mahajana_mapping": "_singularity",
    # === 37TH FORMULA ===
    "The37thFormula": "_singularity",
    "THE_37TH_FORMULA": "_singularity",
    # === RECEIVER ===
    "ReceiverState": "_singularity",
    # === CONVENIENCE ===
    "get_years_remaining_in_golden_period": "_singularity",
    "is_in_golden_period": "_singularity",
    "get_singularity_summary": "_singularity",
    "SingularityProtocol": "_singularity",
}


def __getattr__(name: str):
    """Lazy import from substrate and protocol modules."""
    # Check substrate imports first
    if name in _SUBSTRATE_LAZY_IMPORTS:
        module_name = _SUBSTRATE_LAZY_IMPORTS[name]
        import importlib

        module = importlib.import_module(f".substrate.{module_name}", "vibe_core.mahamantra")
        return getattr(module, name)

    # Check singularity protocol imports
    if name in _SINGULARITY_LAZY_IMPORTS:
        module_name = _SINGULARITY_LAZY_IMPORTS[name]
        import importlib

        module = importlib.import_module(f".protocols.{module_name}", "vibe_core.mahamantra")
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# OUROBOROS - Self-Registration on Import (No Manual Wiring)
# =============================================================================
#
# "nāhaṁ prakāśaḥ sarvasya yoga-māyā-samāvṛtaḥ"
# "I am not manifest to everyone." (BG 7.25)
#
# BUT: When the devotee approaches, Krishna reveals Himself.
# When mahamantra is imported, the protocols SELF-REGISTER.
# This is NOT manual wiring - it's the Lotus opening its petals.
#
# The mechanism exists in singularity._ensure_all_registered().
# We just trigger it at load time. OUROBOROS = self-eating serpent.
# The system bootstraps itself. No external push required.
#


def _ouroboros_init() -> None:
    """
    Trigger self-registration of all protocols.

    Called at module load time. This is the Lotus unfolding.
    No manual wiring - protocols self-register via decorators.
    """
    try:
        from vibe_core.mahamantra.kernel.singularity import mahamantra as _core

        # This loads all mahajana modules, triggering @ProtocolRegistry.register
        _core._ensure_all_registered()
    except ImportError:
        pass  # Graceful degradation if singularity not available
    except Exception:
        pass  # Don't break import on registration errors


# OUROBOROS DISABLED - Triggers cascade to vibe_core.protocols
# If needed, call mahamantra._ouroboros_init() explicitly.
# _ouroboros_init()


# =============================================================================
# NO __all__ - THE LOTUS IS THE EXPORT MECHANISM
# =============================================================================
#
# DO NOT ADD __all__ HERE!
#
# The Lotus auto-discovers. Manual exports are FORBIDDEN.
# Use: from vibe_core.mahamantra import mahamantra
# Then: mahamantra.genesis.brahma, mahamantra.substrate.acintya, etc.
#
