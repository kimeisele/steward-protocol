"""
SAMSKARA CLI - Wild Protocol Migration
======================================

Integrated with UnifiedCLI via @register_cli.

Usage:
    steward samskara           → Status
    steward samskara discover  → Find wild protocols
    steward samskara judge X   → Yamaraja verdict
    steward samskara migrate X → Move to mahajana folder
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8a3c5f92"

from pathlib import Path
from typing import List

from vibe_core.protocols import register_cli, CLIMeta


@register_cli
class SamskaraCLI:
    """Wild protocol migration via Yamaraja."""

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="samskara",
            description="Wild protocol migration (Yamaraja)",
            domain="governance",
            subcommands=["status", "discover", "judge", "migrate"],
            tags=["migration", "yamaraja", "protocols"],
        )

    def run(self, args: List[str]) -> int:
        """Execute samskara command. Returns exit code."""
        if not args:
            return self._status()

        cmd = args[0]
        rest = args[1:]

        if cmd == "status":
            return self._status()
        elif cmd == "discover":
            return self._discover(rest)
        elif cmd == "judge":
            return self._judge(rest)
        elif cmd == "migrate":
            return self._migrate(rest)
        else:
            print(f"Unknown: {cmd}. Use: status, discover, judge, migrate")
            return 1

    def _status(self) -> int:
        """Show samskara status."""
        from vibe_core.mahamantra.moksha.yamaraja import SamskaraService

        service = SamskaraService()
        state = service.get_state()

        print("SAMSKARA STATUS")
        print("=" * 40)
        print(f"Health:   {state['health']}")
        print(f"Wild:     {state['wild_count']}")
        print(f"Blessed:  {state['blessed_count']}")
        print(f"Mercy:    {state['mercy_count']}")
        print(f"Migrated: {state['total_migrated']}")
        return 0

    def _discover(self, args: List[str]) -> int:
        """Discover wild protocols."""
        from vibe_core.mahamantra.moksha.yamaraja import SamskaraService

        paths = args if args else ["vibe_core/protocols"]
        service = SamskaraService()
        wilds = service.discover_wild(paths)

        print(f"Found {len(wilds)} wild protocols:\n")
        for w in wilds[:20]:
            mark = "✓" if w.get("has_chanting") else "○"
            print(f"  {mark} {w['path']} → {w['target_mahajana']}")

        if len(wilds) > 20:
            print(f"  ... and {len(wilds) - 20} more")

        service.save_manifest()
        return 0

    def _judge(self, args: List[str]) -> int:
        """Judge a protocol."""
        if not args:
            print("Usage: samskara judge <path>")
            return 1

        from vibe_core.mahamantra.moksha.yamaraja import SamskaraService

        path = args[0]
        service = SamskaraService()
        verdict = service.judge(path)

        v = verdict.get("verdict", "?")
        icons = {"allow": "✓", "mercy": "♡", "atone": "~", "deny": "✗"}

        print(f"{icons.get(v, '?')} {v.upper()}: {path}")
        print(f"  Reason: {verdict.get('reason')}")
        print(f"  Target: {verdict.get('target_path')}")

        return 0 if v in ("allow", "mercy") else 1

    def _migrate(self, args: List[str]) -> int:
        """Migrate a protocol."""
        if not args:
            print("Usage: samskara migrate <path>")
            return 1

        from vibe_core.mahamantra.moksha.yamaraja import SamskaraService

        path = args[0]
        service = SamskaraService()

        verdict = service.judge(path)
        v = verdict.get("verdict")

        if v not in ("allow", "mercy"):
            print(f"✗ Cannot migrate: {verdict.get('reason')}")
            return 1

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
