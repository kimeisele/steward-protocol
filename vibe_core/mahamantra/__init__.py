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

import importlib
from pathlib import Path
from types import ModuleType
from typing import (
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    TYPE_CHECKING,
    TypedDict,
    Union,
)


# =============================================================================
# WATERTIGHT TYPES - No Any allowed
# =============================================================================

class TickState(TypedDict):
    """Return type for tick() - WATERTIGHT."""
    tick: int
    position: int
    quarter: str
    guardian: str
    word: str
    opcode: Optional[int]


class RouteResult(TypedDict):
    """Return type for route() - WATERTIGHT."""
    position: int
    guardian: str
    quarter: str


class ExecuteResult(TypedDict):
    """Return type for execute() - WATERTIGHT."""
    success: bool
    exit_code: int
    position: int
    guardian: str
    quarter: str
    guna: str                       # sattva/rajas/tamas
    requires_confirmation: bool     # True for TAMAS ops
    output: str
    error: Optional[str]

# =============================================================================
# THE LOTUS PATH
# =============================================================================

class LotusPath:
    """Path through the lotus."""
    __slots__ = ("_segments",)

    def __init__(self, segments: Tuple[str, ...] = ()) -> None:
        self._segments = segments

    @property
    def segments(self) -> Tuple[str, ...]:
        return self._segments

    @property
    def depth(self) -> int:
        return len(self._segments)

    @property
    def is_root(self) -> bool:
        return self.depth == 0

    @property
    def folder_path(self) -> str:
        return "/".join(self._segments)

    @property
    def module_path(self) -> str:
        if self.is_root:
            return "vibe_core.mahamantra"
        return "vibe_core.mahamantra." + ".".join(self._segments)

    def child(self, name: str) -> "LotusPath":
        return LotusPath(self._segments + (name,))

    def __repr__(self) -> str:
        return f"LotusPath({self._segments})"


# =============================================================================
# THE LOTUS NODE - Auto-Discovery
# =============================================================================

class LotusNode:
    """
    A node in Krishna's Lotus.

    Auto-discovers children from folder structure.
    FOLDER = EXISTENCE = WIRING.
    """
    __slots__ = ("_path", "_base", "_cache", "_module")

    # Base path for the mahamantra package
    _BASE_PATH: Path = Path(__file__).parent

    def __init__(self, path: LotusPath = LotusPath()) -> None:
        self._path = path
        self._cache: Dict[str, LotusNode] = {}
        self._module: Optional[object] = None

    def __getattr__(self, name: str) -> "LotusNode":
        """
        Auto-discover child from folder structure.

        mahamantra.genesis → discovers genesis/
        mahamantra.genesis.brahma → discovers genesis/brahma/
        """
        # Skip private
        if name.startswith("_"):
            raise AttributeError(name)

        # Check cache
        if name in self._cache:
            return self._cache[name]

        # Discover from folder structure
        child = self._discover(name)
        if child is not None:
            self._cache[name] = child
            return child

        # Try to get from loaded module
        module = self._get_module()
        if module is not None and hasattr(module, name):
            return getattr(module, name)

        raise AttributeError(
            f"'{name}' not found in lotus at '{self._path.folder_path or 'root'}'"
        )

    def _discover(self, name: str) -> Optional["LotusNode"]:
        """
        Discover child from folder structure.

        FOLDER = EXISTENCE:
            Folder exists → Node exists
            No folder → Doesn't exist
        """
        child_path = self._path.child(name)

        # Check folder
        folder = self._BASE_PATH / child_path.folder_path
        if folder.exists() and folder.is_dir():
            return LotusNode(child_path)

        # Check .py file (for substrate modules)
        if self._path.is_root:
            py_file = self._BASE_PATH / f"{name}.py"
            if py_file.exists():
                return LotusNode(child_path)

        # Check in current folder
        if not self._path.is_root:
            current_folder = self._BASE_PATH / self._path.folder_path
            py_file = current_folder / f"{name}.py"
            if py_file.exists():
                return LotusNode(child_path)

        return None

    def _get_module(self) -> Optional[object]:
        """Lazy-load the actual Python module."""
        if self._module is not None:
            return self._module

        try:
            self._module = importlib.import_module(self._path.module_path)
            return self._module
        except ImportError:
            return None

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Allow calling if the node has a __call__ method."""
        module = self._get_module()
        if module is not None and hasattr(module, "__call__"):
            return module(*args, **kwargs)  # type: ignore[operator]
        raise TypeError(f"'{self._path.folder_path}' is not callable")

    def __repr__(self) -> str:
        if self._path.is_root:
            return "mahamantra"
        return f"mahamantra.{'.'.join(self._path.segments)}"

    def __dir__(self) -> list:
        """
        List available children for tab-completion.

        LILA BOUNDARY (Chaitanya's 24+24):
            Returns max 24 items per call (Navadvipa phase).
            Use _dir_full() for complete listing.
            This prevents exponential output explosion.
        """
        from vibe_core.mahamantra.substrate.byte import LILA_LIMIT

        NAVADVIPA_LIMIT = LILA_LIMIT // 2  # 24

        items = []

        # Folders
        if self._path.is_root:
            base = self._BASE_PATH
        else:
            base = self._BASE_PATH / self._path.folder_path

        if base.exists():
            for child in base.iterdir():
                if child.name.startswith("_"):
                    continue
                if child.is_dir():
                    items.append(child.name)
                elif child.suffix == ".py":
                    items.append(child.stem)

                # Lila boundary check
                if len(items) >= NAVADVIPA_LIMIT:
                    break

        # Module exports (only if we have capacity)
        if len(items) < NAVADVIPA_LIMIT:
            module = self._get_module()
            if module is not None:
                remaining = NAVADVIPA_LIMIT - len(items)
                module_items = [
                    name for name in dir(module)
                    if not name.startswith("_")
                ]
                items.extend(module_items[:remaining])

        result = sorted(set(items))

        # Add hint if truncated
        if len(result) >= NAVADVIPA_LIMIT:
            result.append("__has_more__")

        return result

    def _dir_full(self) -> list:
        """Full directory listing (bypasses Lila boundary for internal use)."""
        items = []

        if self._path.is_root:
            base = self._BASE_PATH
        else:
            base = self._BASE_PATH / self._path.folder_path

        if base.exists():
            for child in base.iterdir():
                if child.name.startswith("_"):
                    continue
                if child.is_dir():
                    items.append(child.name)
                elif child.suffix == ".py":
                    items.append(child.stem)

        module = self._get_module()
        if module is not None:
            items.extend(
                name for name in dir(module)
                if not name.startswith("_")
            )

        return sorted(set(items))

    # === Iteration ===

    def _walk(self, depth: int = 1) -> Iterator[Tuple[LotusPath, "LotusNode"]]:
        """Walk the lotus fractally."""
        yield (self._path, self)

        if depth <= 0:
            return

        if self._path.is_root:
            base = self._BASE_PATH
        else:
            base = self._BASE_PATH / self._path.folder_path

        if not base.exists():
            return

        for child in sorted(base.iterdir()):
            if child.name.startswith("_"):
                continue
            if child.is_dir():
                child_node = LotusNode(self._path.child(child.name))
                yield from child_node._walk(depth - 1)

    # === Properties ===

    @property
    def path(self) -> LotusPath:
        return self._path

    @property
    def depth(self) -> int:
        return self._path.depth


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

    _tick: int = 0  # Current position (0-15) - shared across instances

    # =========================================================================
    # GUARDIAN → SUBSTRATE MODULE MAPPING
    # =========================================================================
    # Each guardian (position 0-15) maps to a substrate module.
    # This IS the wiring. No __init__.py needed.

    GUARDIAN_MODULES = {
        # GENESIS (0-3) - System initialization
        "prithu": "wiring",           # 0: SYS_WAKE
        "brahma": "mahajana",         # 1: LOAD_ROOT
        "narada": "acintya",          # 2: ALLOC_MEM
        "shambhu": "protocol",        # 3: INIT_THREAD
        # DHARMA (4-7) - Compilation
        "vyasa": "opcode",            # 4: COMPILE_AST
        "kumaras": "position",        # 5: BIND_SYMBOL
        "kapila": "watertight",       # 6: TYPE_CHECK
        "manu": "guna",               # 7: DHARMA_TEST
        # KARMA (8-11) - Execution
        "parashurama": "yajna",       # 8: EXEC_OP (the offering)
        "prahlada": "pancha_tattva",  # 9: EXTEND_CAP
        "janaka": "parampara",        # 10: STATE_SYNC
        "bhishma": "scanner",         # 11: LEDGER_SIGN
        # MOKSHA (12-15) - Liberation
        "nrisimha": "byte",           # 12: YIELD_CPU
        "bali": "tattva",             # 13: IO_FLUSH
        "shuka": "sankirtan",         # 14: LOG_EMIT
        "yamaraja": "lotus",          # 15: AUDIT_SEAL
    }

    def __init__(self) -> None:
        super().__init__(LotusPath())

    def __repr__(self) -> str:
        return "mahamantra"

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

        # Advance to next position (for next call)
        MahamantraLotus._tick = next_position(MahamantraLotus._tick)

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

    # === Scanner Integration ===

    def scan(self) -> "ScanResult":
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

    def sankirtan(self, dry_run: bool = True) -> "SankirtanResult":
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
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY
            from vibe_core.mahamantra.substrate import get_position_by_opcode
            
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
            guardian = mapping.owner  # e.g., "prithu", "brahma"
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
            get_guna_by_position,
            Guna,
            GunaQoS,
            VISHUDDHA_SATTVA,
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
                is_meaningful = (
                    len(items) > 1 or
                    (len(items) == 1 and items[0].get("value") is not False)
                )
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
            from vibe_core.cli.unified_cli import UnifiedCLI
            import io
            import sys

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
            return importlib.import_module(
                f"vibe_core.mahamantra.substrate.{module_name}"
            )

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

        raise AttributeError(
            f"'{name}' not found in lotus (tried guardian, folder, and alias)"
        )

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
        from vibe_core.mahamantra.substrate.acintya import PARAMPARA
        return PARAMPARA

    def __iter__(self) -> Iterator:
        """
        KARMA: Iterate through all 16 positions.

        for pos in mahamantra: ...
        """
        from vibe_core.mahamantra.substrate.clock import get_tick_info, MANTRA_LENGTH
        return (get_tick_info(i) for i in range(MANTRA_LENGTH))

    def __len__(self) -> int:
        """16 positions in the Mahamantra."""
        return 16

    def __getitem__(self, index: int) -> object:
        """
        ARTHA: Access position by index.

        mahamantra[5] → Position 5 (KUMARAS)
        """
        from vibe_core.mahamantra.substrate.clock import get_tick_info
        return get_tick_info(index)

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

_SUBSTRATE_LAZY_IMPORTS = {
    # === MAHAJANA ===
    "Mahajana": "mahajana",
    "Avatara": "mahajana",
    "Quarter": "mahajana",
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


def __getattr__(name: str):
    """Lazy import from substrate modules."""
    if name in _SUBSTRATE_LAZY_IMPORTS:
        module_name = _SUBSTRATE_LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(
            f".substrate.{module_name}", "vibe_core.mahamantra"
        )
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
