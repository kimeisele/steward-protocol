"""
SAMSKARA CLI - Wild Protocol Migration
======================================

Usage:
    python -m vibe_core.mahamantra.cli.samskara discover
    python -m vibe_core.mahamantra.cli.samskara judge <path>
    python -m vibe_core.mahamantra.cli.samskara migrate <path>
    python -m vibe_core.mahamantra.cli.samskara status
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xb48d8a78"  # GenesisByte: parampara % 37 == 0

import sys
from pathlib import Path

from vibe_core.mahamantra.moksha.yamaraja import SamskaraService
from vibe_core.mahamantra import Mahajana


def _get_samskara_service() -> SamskaraService:
    """Get SamskaraService via consistent pattern (mahamantra = force)."""
    from vibe_core.di import ServiceRegistry
    service = ServiceRegistry.get(SamskaraService)
    if service is None:
        service = SamskaraService()
        ServiceRegistry.register(SamskaraService, service)
    return service


def main() -> int:
    """CLI entry point."""
    args = sys.argv[1:]

    if not args:
        return _cmd_status()

    cmd = args[0]

    if cmd == "discover":
        return _cmd_discover(args[1:])
    elif cmd == "judge":
        return _cmd_judge(args[1:])
    elif cmd == "migrate":
        return _cmd_migrate(args[1:])
    elif cmd == "status":
        return _cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: discover, judge, migrate, status")
        return 1


def _cmd_discover(args: list[str]) -> int:
    """Discover wild protocols."""
    paths = args if args else ["vibe_core"]

    service = _get_samskara_service()
    wilds = service.discover_wild(paths)

    print(f"Found {len(wilds)} wild protocols:\n")

    for w in wilds:
        status = "✓" if w.get("has_chanting") else "○"
        print(f"  {status} {w['path']}")
        print(f"    → {w['target_mahajana']} (GAD: {w['gad_score']:.0%})")

    service.save_manifest()
    return 0


def _cmd_judge(args: list[str]) -> int:
    """Judge a protocol."""
    if not args:
        print("Usage: samskara judge <path>")
        return 1

    path = args[0]
    service = _get_samskara_service()

    verdict = service.judge(path)

    v = verdict.get("verdict", "?")
    icon = {"allow": "✓", "mercy": "♡", "atone": "~", "deny": "✗"}.get(v, "?")

    print(f"{icon} {v.upper()}: {path}")
    print(f"  Reason: {verdict.get('reason')}")
    print(f"  Target: {verdict.get('target_path')}")

    if verdict.get("required_samskaras"):
        print(f"  Required: {', '.join(verdict['required_samskaras'])}")

    return 0 if v in ("allow", "mercy") else 1


def _cmd_migrate(args: list[str]) -> int:
    """Migrate a protocol."""
    if not args:
        print("Usage: samskara migrate <path>")
        return 1

    path = args[0]
    service = _get_samskara_service()

    # First judge
    verdict = service.judge(path)
    v = verdict.get("verdict")

    if v not in ("allow", "mercy"):
        print(f"✗ Cannot migrate: {verdict.get('reason')}")
        return 1

    # Get target mahajana
    mahajana = service.identify_mahajana(path)
    if not mahajana:
        print("✗ Cannot identify mahajana")
        return 1

    name = Path(path).stem

    if service.migrate(path, mahajana, name):
        print(f"✓ Migrated to {verdict.get('target_path')}")
        return 0
    else:
        print("✗ Migration failed")
        return 1


def _cmd_status() -> int:
    """Show status."""
    service = _get_samskara_service()
    state = service.get_state()

    print("SAMSKARA STATUS")
    print("=" * 40)
    print(f"Health: {state['health']}")
    print(f"Wild:     {state['wild_count']}")
    print(f"Judging:  {state['judging_count']}")
    print(f"Blessed:  {state['blessed_count']}")
    print(f"Mercy:    {state['mercy_count']}")
    print(f"Rejected: {state['rejected_count']}")
    print(f"Migrated: {state['total_migrated']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
