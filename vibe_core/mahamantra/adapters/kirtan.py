"""
KIRTAN ADAPTER — VMCapability that injects rendered output into VM results
==========================================================================

Registers a KIRTAN_RENDER custom op in the CycleCompiler (gate=4/SYNC,
priority=1 → runs AFTER ATMA_NIVEDANAM which builds ctx["_result"]).

Every mahamantra(input) call now automatically gets a "kirtan" key
in the result dict containing the human-readable rendering.

ARCHITECTURE:
    VM 9 Steps → ATMA_NIVEDANAM builds _result → KIRTAN_RENDER adds "kirtan"

    Future CycleCompiler ops (MANAS, Language Engine) add their keys
    BEFORE this op. The renderer discovers and uses them automatically.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from vibe_core.mahamantra.protocols._navabhakti import (
    VMCapabilityProtocol,
    VMOpDeclaration,
)
from vibe_core.mahamantra.render import render

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0xa7c1e2f0"


def _kirtan_render_handler(lotus: object, ctx: dict) -> None:
    """CycleCompiler handler: render the VM result dict into human-readable text."""
    result = ctx.get("_result")
    if result is not None and isinstance(result, dict):
        result["kirtan"] = render(result)


class KirtanCapability:
    """VMCapabilityProtocol implementation for the Kirtan Renderer.

    Discovered and registered by lotus_core.bootstrap() alongside
    other VMCapability implementations (e.g. MahaComposition).
    """

    def vm_ops(self) -> List[VMOpDeclaration]:
        return [
            VMOpDeclaration(
                name="KIRTAN_RENDER",
                gate=4,  # SYNC — same gate as ATMA_NIVEDANAM
                handler=_kirtan_render_handler,
                priority=1,  # After ATMA_NIVEDANAM (priority 0)
            ),
        ]


# Singleton
_INSTANCE: Optional[KirtanCapability] = None


def get_kirtan() -> KirtanCapability:
    """Get the KirtanCapability singleton."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = KirtanCapability()
    return _INSTANCE
