"""
YAMARAJA - Position 15
=======================

Quarter: MOKSHA
OpCode: AUDIT_SEAL
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 592 (% 37 == 0 -> CONNECTED)

CLI AUTO INTEGRATION:
    cli_auto discovers NullYamaraja methods.
    Methods delegate to SamskaraService.
    steward samskara → cli_auto → NullYamaraja.samskara_* → SamskaraService
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8fd1e5e1"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Final, List, Protocol, TypedDict, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 15
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "AUDIT_SEAL"
PARAMPARA_VECTOR: Final[int] = 592


# =============================================================================
# CLI AUTO RETURN TYPES (TypedDict for introspection)
# =============================================================================


class SamskaraStatusResult(TypedDict):
    """Status result for cli_auto."""

    health: str
    wild_count: int
    blessed_count: int
    mercy_count: int
    migrated: int


class SamskaraDiscoverResult(TypedDict):
    """Discover result for cli_auto."""

    count: int
    protocols: List[Dict[str, str]]  # [{path, target, has_chanting}]


class SamskaraJudgeResult(TypedDict):
    """Judge result for cli_auto."""

    verdict: str
    reason: str
    target_path: str


class SamskaraMigrateResult(TypedDict):
    """Migrate result for cli_auto."""

    success: bool
    message: str
    from_path: str
    to_path: str


# =============================================================================
# YAMARAJA PROTOCOL - With Samskara Methods
# =============================================================================


@runtime_checkable
class YamarajaProtocol(Protocol):
    """
    Protocol for Yamaraja (AUDIT_SEAL).

    Position 15 in the Mahamantra.

    SAMSKARA METHODS (for cli_auto discovery):
        samskara_status()   - Show migration status
        samskara_discover() - Find wild protocols
        samskara_judge()    - Verdict on protocol
        samskara_migrate()  - Execute migration
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...

    def samskara_status(self) -> SamskaraStatusResult:
        """Get samskara migration status."""
        ...

    def samskara_discover(self, path: str = "vibe_core") -> SamskaraDiscoverResult:
        """Discover wild protocols."""
        ...

    def samskara_judge(self, path: str) -> SamskaraJudgeResult:
        """Judge a protocol for migration."""
        ...

    def samskara_migrate(self, path: str) -> SamskaraMigrateResult:
        """Migrate a protocol to its mahajana folder."""
        ...


class YamarajaBase(WorkerProtocol):
    """
    Base class for Yamaraja implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 15  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 15


class NullYamaraja(YamarajaBase):
    """
    Null implementation that delegates to SamskaraService.

    cli_auto discovers this class and calls its methods.
    Methods delegate to the real SamskaraService.
    """

    def __init__(self) -> None:
        self._service = None

    def _get_service(self):
        """Lazy load SamskaraService."""
        if self._service is None:
            from vibe_core.mahamantra.moksha.yamaraja.samskara_service import SamskaraService

            self._service = SamskaraService()
        return self._service

    def samskara_status(self) -> SamskaraStatusResult:
        """Get samskara migration status."""
        service = self._get_service()
        state = service.get_state()
        return SamskaraStatusResult(
            health=state["health"],
            wild_count=state["wild_count"],
            blessed_count=state["blessed_count"],
            mercy_count=state["mercy_count"],
            migrated=state["total_migrated"],
        )

    def samskara_discover(self, path: str = "vibe_core") -> SamskaraDiscoverResult:
        """Discover wild protocols."""
        service = self._get_service()
        wilds = service.discover_wild([path])
        service.save_manifest()
        return SamskaraDiscoverResult(
            count=len(wilds),
            protocols=[
                {
                    "path": w.path,
                    "target": w.target_mahajana,
                    "has_chanting": "yes" if w.has_chanting else "no",
                }
                for w in wilds[:50]  # Limit for CLI output
            ],
        )

    def samskara_judge(self, path: str) -> SamskaraJudgeResult:
        """Judge a protocol for migration."""
        service = self._get_service()
        verdict = service.judge(path)
        return SamskaraJudgeResult(
            verdict=verdict.get("verdict", "unknown"),
            reason=verdict.get("reason", ""),
            target_path=verdict.get("target_path", ""),
        )

    def samskara_migrate(self, path: str) -> SamskaraMigrateResult:
        """Migrate a protocol to its mahajana folder."""
        from pathlib import Path as P

        service = self._get_service()

        # First judge
        verdict = service.judge(path)
        v = verdict.get("verdict")

        if v not in ("allow", "mercy"):
            return SamskaraMigrateResult(
                success=False,
                message=f"Cannot migrate: {verdict.get('reason')}",
                from_path=path,
                to_path="",
            )

        # Get target
        mahajana = service.identify_mahajana(path)
        if not mahajana:
            return SamskaraMigrateResult(
                success=False,
                message="Cannot identify mahajana",
                from_path=path,
                to_path="",
            )

        name = P(path).stem
        target = verdict.get("target_path", "")

        if service.migrate(path, mahajana, name):
            return SamskaraMigrateResult(
                success=True,
                message="Migration complete",
                from_path=path,
                to_path=target,
            )
        else:
            return SamskaraMigrateResult(
                success=False,
                message="Migration failed",
                from_path=path,
                to_path=target,
            )


def execute(input_text: str, context: dict = None) -> dict:
    """YAMARAJA EXECUTION - Audit Seal (Position 15)"""
    return {
        "success": True,
        "action": "audit_seal",
        "verdict": "HEARD",
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "message": f"Yamaraja [{OPCODE}]: '{input_text}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Explicit exports + protocol re-exports + fractal discovery."""
    if name == "YamarajaService":
        from vibe_core.services.yamaraja_service import YamarajaService

        return YamarajaService

    if name == "SamskaraService":
        from vibe_core.mahamantra.moksha.yamaraja.samskara_service import SamskaraService

        return SamskaraService

    # Lazy protocol re-export (samskara types, etc.)
    try:
        from vibe_core.protocols.mahajanas import yamaraja as _proto

        _val = getattr(_proto, name, _MISSING)
        if _val is not _MISSING:
            return _val
    except ImportError:
        pass

    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
