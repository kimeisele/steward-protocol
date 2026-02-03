"""
MAHA CLI ADAPTER - Bridge between Resonance and Action
======================================================

"yogaḥ karmasu kauśalam" - Yoga is skill in action.

The Lotus (MahamantraLotus) remains PURE - only resonance and computation.
The Adapter is the SERVANT that translates resonance into action.

ARCHITECTURE:
    User Input → MahamantraLotus.__call__() → Resonance
                                                  │
                                                  ▼
                                           MahaCLIAdapter
                                                  │
                                                  ▼
                                           Domain CLIs (audit, genesis, etc.)
                                                  │
                                                  ▼
                                           ACTUAL ACTION

The Adapter uses:
- Position (0-15) → Maps to Mahajana domain
- Quarter (genesis/dharma/karma/moksha) → Maps to action type
- Guardian → Maps to specific CLI
- Tags/Keywords from input → Fuzzy matching to CLI commands
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x4e8a7c21"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from vibe_core.protocols.cli import CLIHandler, CLIMeta, CLIRegistry


@dataclass
class AdapterResult:
    """Result from the MahaCLI Adapter."""

    # Resonance data (from mahamantra)
    resonance: Dict

    # Execution data (from CLI)
    executed: bool = False
    cli_command: Optional[str] = None
    cli_result: Optional[int] = None
    cli_output: Optional[str] = None

    # Matching info
    match_score: float = 0.0
    match_reason: str = ""


class MahaCLIAdapter:
    """
    Bridge between Mahamantra Resonance and Domain CLIs.

    The Lotus computes. The Adapter acts.

    FLOW:
        1. Receive input
        2. Get resonance from mahamantra()
        3. Match resonance to a CLI (via position, quarter, keywords)
        4. Execute CLI if match found
        5. Return combined result

    SAFETY:
        - Default mode: OBSERVE (just match, don't execute)
        - Explicit mode: EXECUTE (actually run the CLI)
    """

    # Mapping: Quarter → Action Type
    QUARTER_ACTIONS = {
        "genesis": "create",  # INPUT - creation, spawning
        "dharma": "verify",  # VERIFY - validation, checking
        "karma": "execute",  # EXECUTE - action, transformation
        "moksha": "output",  # OUTPUT - reporting, display
    }

    # Mapping: Position → Domain hint
    POSITION_DOMAINS = {
        0: "genesis",  # vyasa - creation
        1: "genesis",  # brahma - spawning
        2: "info",  # narada - communication
        3: "system",  # shambhu - transformation
        4: "governance",  # prithu - structure
        5: "governance",  # kumaras - purity
        6: "analysis",  # kapila - sankhya analysis
        7: "governance",  # manu - law
        8: "remedies",  # parashurama - correction
        9: "operations",  # prahlada - devotion/operations
        10: "operations",  # janaka - task management
        11: "governance",  # bhishma - rules
        12: "system",  # nrisimha - protection
        13: "knowledge",  # bali - surrender/knowledge
        14: "knowledge",  # shuka - pure knowledge
        15: "audit",  # yamaraja - judgment/audit
    }

    def __init__(self) -> None:
        self._clis_loaded = False
        self._cli_cache: Dict[str, CLIHandler] = {}

    def _ensure_clis_loaded(self) -> None:
        """Lazy-load all CLIs into registry."""
        if self._clis_loaded:
            return

        # Import all CLI modules to trigger @register_cli
        try:
            from vibe_core.cli import (
                audit_cli,
                genesis_cli,
                governance_cli,
                kirtan_cli,
                knowledge_cli,
                lotus_cli,
                naga_cli,
                prakriti_cli,
                run_cli,
            )
        except ImportError:
            pass  # Some CLIs might not exist

        self._clis_loaded = True

    def execute(
        self,
        input_text: str,
        *,
        mode: str = "observe",  # "observe" or "execute"
        verbose: bool = False,
    ) -> AdapterResult:
        """
        Main entry point - translate input to action.

        Args:
            input_text: Natural language input
            mode: "observe" (match only) or "execute" (run CLI)
            verbose: Include detailed matching info

        Returns:
            AdapterResult with resonance + execution data
        """
        # 1. Get resonance from Mahamantra (the Lotus)
        from vibe_core.mahamantra import mahamantra

        resonance = mahamantra(input_text)

        # 2. Find matching CLI
        self._ensure_clis_loaded()
        cli, score, reason = self._find_cli(resonance, input_text)

        result = AdapterResult(
            resonance=resonance,
            match_score=score,
            match_reason=reason,
        )

        if cli:
            result.cli_command = cli.meta.command

            # 3. Execute if requested
            if mode == "execute":
                args = self._parse_args(input_text, cli)
                result.cli_result = cli.run(args)
                result.executed = True

        return result

    def _find_cli(
        self,
        resonance: Dict,
        input_text: str,
    ) -> Tuple[Optional[CLIHandler], float, str]:
        """
        Find the best matching CLI for this resonance.

        Matching strategy (weighted):
        1. Exact command keyword in input (weight: 1.0)
        2. Position → Domain match (weight: 0.5)
        3. Quarter → Action type match (weight: 0.3)
        4. Tag matching (weight: 0.2)

        Returns:
            (cli_handler, match_score, match_reason)
        """
        position = resonance.get("position", 0)
        quarter = resonance.get("quarter", "genesis")
        input_lower = input_text.lower()

        best_cli = None
        best_score = 0.0
        best_reason = ""

        for cli in CLIRegistry.all():
            meta = cli.meta
            score = 0.0
            reasons = []

            # 1. Exact command match (highest weight)
            if meta.command in input_lower:
                score += 1.0
                reasons.append(f"command '{meta.command}' in input")

            # 2. Subcommand match
            for subcmd in meta.subcommands:
                if subcmd in input_lower:
                    score += 0.8
                    reasons.append(f"subcommand '{subcmd}' in input")
                    break

            # 3. Tag match
            for tag in meta.tags:
                if tag in input_lower:
                    score += 0.3
                    reasons.append(f"tag '{tag}' in input")

            # 4. Domain hint from position
            domain_hint = self.POSITION_DOMAINS.get(position, "")
            if domain_hint and domain_hint in meta.domain:
                score += 0.5
                reasons.append(f"position {position} → domain '{domain_hint}'")

            # 5. Quarter → action type match
            action_hint = self.QUARTER_ACTIONS.get(quarter, "")
            if action_hint:
                for subcmd in meta.subcommands:
                    if action_hint in subcmd:
                        score += 0.2
                        reasons.append(f"quarter '{quarter}' → action '{action_hint}'")
                        break

            # 6. Lotus position match (if CLI has it)
            if meta.lotus_position is not None and meta.lotus_position == position:
                score += 0.6
                reasons.append(f"lotus_position {position} exact match")

            if score > best_score:
                best_score = score
                best_cli = cli
                best_reason = "; ".join(reasons)

        return best_cli, best_score, best_reason

    def _parse_args(self, input_text: str, cli: CLIHandler) -> List[str]:
        """
        Parse input text into CLI arguments.

        Simple strategy:
        - Remove the command name
        - Split remaining into args
        """
        meta = cli.meta
        words = input_text.split()

        # Remove command if present
        args = [w for w in words if w.lower() != meta.command]

        # Check for subcommands
        for subcmd in meta.subcommands:
            if subcmd in input_text.lower():
                # Put subcommand first
                args = [subcmd] + [w for w in args if w.lower() != subcmd]
                break

        return args

    def discover(self) -> Dict[str, CLIMeta]:
        """Discover all available CLIs."""
        self._ensure_clis_loaded()
        return CLIRegistry.discover()

    def commands(self) -> List[str]:
        """List all available commands."""
        self._ensure_clis_loaded()
        return CLIRegistry.commands()


# Singleton
_adapter: Optional[MahaCLIAdapter] = None


def get_adapter() -> MahaCLIAdapter:
    """Get the singleton MahaCLI Adapter."""
    global _adapter
    if _adapter is None:
        _adapter = MahaCLIAdapter()
    return _adapter


# Convenience functions
def maha_execute(input_text: str, *, mode: str = "observe") -> AdapterResult:
    """
    Execute input through the MahaCLI Adapter.

    Usage:
        result = maha_execute("audit the databases")
        print(result.cli_command)  # "audit"
        print(result.resonance["position"])  # 15 (yamaraja)

        # To actually run:
        result = maha_execute("audit databases", mode="execute")
    """
    return get_adapter().execute(input_text, mode=mode)


def maha_discover() -> Dict[str, CLIMeta]:
    """Discover all available CLIs."""
    return get_adapter().discover()
