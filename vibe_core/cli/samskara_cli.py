"""
SAMSKARA CLI - THIN Gateway Delegate
=====================================

ROCKET SOLID: Minimal logic. Gateway routes everything.

    steward samskara status   → gateway → mahamantra → cli_auto → Yamaraja
    steward samskara discover → gateway → mahamantra → cli_auto → Yamaraja
    steward samskara judge    → gateway → mahamantra → cli_auto → Yamaraja
    steward samskara migrate  → gateway → mahamantra → cli_auto → Yamaraja

Flow: CLI → Gateway → Mahamantra → cli_auto → YamarajaProtocol → SamskaraService

NO SPAGHETTI. PROTOCOL FIRST. SSOT.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x65597f7c"

import ast
from typing import Dict, List

from vibe_core.protocols import register_cli, CLIMeta

import logging

logger = logging.getLogger(__name__)


def _format_output(cmd: str, output: str) -> str:
    """Format cli_auto output nicely."""
    try:
        # Parse the dict string
        data = ast.literal_eval(output)
        if not isinstance(data, dict):
            return output

        items = data.get("items", [])
        if not items:
            return output

        # Format based on command
        if cmd == "samskara_status":
            lines = ["SAMSKARA STATUS", "=" * 40]
            for item in items:
                key = item.get("key", "?")
                val = item.get("value", "?")
                lines.append(f"{key.replace('_', ' ').title():12} {val}")
            return "\n".join(lines)

        elif cmd == "samskara_discover":
            count = next((i["value"] for i in items if i["key"] == "count"), 0)
            # cli_auto flattens lists - look for protocols_items string
            protocols_str = next((i["value"] for i in items if i["key"] == "protocols_items"), "")
            lines = [f"Found {count} wild protocols:\n"]
            if protocols_str:
                # Parse the flattened list string
                import re

                for m in re.finditer(
                    r"\{'path': '([^']+)', 'target': '([^']+)', 'has_chanting': '([^']+)'\}", protocols_str
                ):
                    path, target, chant = m.groups()
                    mark = "✓" if chant == "yes" else "○"
                    lines.append(f"  {mark} {path} → {target}")
                    if len(lines) > 22:
                        lines.append(f"  ... and more")
                        break
            return "\n".join(lines)

        elif cmd == "samskara_judge":
            verdict = next((i["value"] for i in items if i["key"] == "verdict"), "?")
            reason = next((i["value"] for i in items if i["key"] == "reason"), "")
            target = next((i["value"] for i in items if i["key"] == "target_path"), "")
            icons = {"allow": "✓", "mercy": "♡", "atone": "~", "deny": "✗"}
            return f"{icons.get(verdict, '?')} {verdict.upper()}\n  Reason: {reason}\n  Target: {target}"

        elif cmd == "samskara_migrate":
            success = next((i["value"] for i in items if i["key"] == "success"), False)
            msg = next((i["value"] for i in items if i["key"] == "message"), "")
            to_path = next((i["value"] for i in items if i["key"] == "to_path"), "")
            icon = "✓" if success else "✗"
            return f"{icon} {msg}\n  Destination: {to_path}" if to_path else f"{icon} {msg}"

    except Exception as _exc:
        logger.exception("Unexpected error: %s", _exc)

    return output


@register_cli
class SamskaraCLI:
    """
    THIN CLI - Delegates to Gateway.

    Formats cli_auto output for human readability.
    """

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
        """Route to gateway, format output."""
        from vibe_core.gateway import execute

        if not args:
            args = ["status"]

        cmd = args[0]
        rest = args[1:]

        # Map subcommand to gateway command
        cmd_map = {
            "status": "samskara_status",
            "discover": "samskara_discover",
            "judge": "samskara_judge",
            "migrate": "samskara_migrate",
        }

        gateway_cmd = cmd_map.get(cmd)
        if not gateway_cmd:
            print(f"Unknown: {cmd}. Use: status, discover, judge, migrate")
            return 1

        # Execute via gateway
        result = execute(gateway_cmd, rest)

        # Format and print output
        if result["output"]:
            formatted = _format_output(gateway_cmd, result["output"])
            print(formatted)

        return result["exit_code"]
