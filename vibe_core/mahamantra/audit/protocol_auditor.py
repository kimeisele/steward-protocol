"""
PROTOCOL AUDITOR - Runtime Protocol Compliance
===============================================

Verifies that classes actually implement their declared protocols
via isinstance() checks on live instances.

Implements AuditorProtocol: class Auditor + run_audit() → List[AuditFinding].
Auto-discovered by AuditDispatcher via __position__ + Auditor class.
"""

from __future__ import annotations

__mahajana__ = "yamaraja"
__position__ = 2  # Third auditor to run
__genesis__ = "0x8000000f"

import importlib
import logging
from typing import List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import PARAMPARA
from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("AUDIT.PROTOCOL")

# Registry: (module_path, class_name, protocol_module, protocol_name)
# Each entry declares: "this class MUST be isinstance of this protocol"
PROTOCOL_CHECKS: List[Tuple[str, str, str, str]] = [
    (
        "vibe_core.mahamantra.substrate.algorithm.maha",
        "MahaAlgorithm16",
        "vibe_core.mahamantra.protocols._maha_compute",
        "MahaComputeProtocol",
    ),
    (
        "vibe_core.mahamantra.substrate.algorithm.maha",
        "MahaModularSynth",
        "vibe_core.mahamantra.protocols._maha_compute",
        "MahaComputeProtocol",
    ),
    (
        "vibe_core.mahamantra.analysis.derivation_graph",
        "DerivationGraph",
        "vibe_core.mahamantra.protocols._graph",
        "GraphProtocol",
    ),
    (
        "vibe_core.mahamantra.substrate.chamber",
        "SankirtanChamber",
        "vibe_core.mahamantra.protocols._pancha",
        "PanchaTattvaProtocol",
    ),
    (
        "vibe_core.mahamantra.substrate.resonance.resonator",
        "MahaResonator",
        "vibe_core.mahamantra.protocols._pancha",
        "PanchaTattvaProtocol",
    ),
    (
        "vibe_core.mahamantra.adapters.routing",
        "HolographicRouter",
        "vibe_core.mahamantra.protocols._pancha",
        "PanchaTattvaProtocol",
    ),
]


class Auditor:
    """
    Protocol Auditor — verifies runtime protocol compliance.

    Single responsibility: isinstance checks on live instances.
    Instantiates classes and checks protocol conformance.
    """

    def run_audit(self) -> List[AuditFinding]:
        """AuditorProtocol: check all registered protocol claims."""
        findings: List[AuditFinding] = []

        for mod_name, cls_name, proto_mod, proto_name in PROTOCOL_CHECKS:
            try:
                mod = importlib.import_module(mod_name)
                cls = getattr(mod, cls_name)
                proto_m = importlib.import_module(proto_mod)
                proto = getattr(proto_m, proto_name)

                # Instantiate — use create() factory if available
                instance = cls.create() if hasattr(cls, "create") else cls()

                if not isinstance(instance, proto):
                    findings.append(
                        AuditFinding(
                            source="protocol_auditor",
                            position=__position__,
                            mahajana=__mahajana__,
                            description=(f"{cls_name} does not implement {proto_name}. isinstance() returned False."),
                            file_path=mod_name.replace(".", "/") + ".py",
                            severity=FindingSeverity.CRITICAL,
                        )
                    )
            except Exception as e:
                findings.append(
                    AuditFinding(
                        source="protocol_auditor",
                        position=__position__,
                        mahajana=__mahajana__,
                        description=(
                            f"Cannot verify {cls_name} against {proto_name}: {type(e).__name__}: {str(e)[:120]}"
                        ),
                        file_path=mod_name.replace(".", "/") + ".py",
                        severity=FindingSeverity.WARNING,
                    )
                )

        logger.info(
            "Protocol audit: %d findings, %d checks",
            len(findings),
            len(PROTOCOL_CHECKS),
        )
        return findings


__all__ = ["Auditor"]
