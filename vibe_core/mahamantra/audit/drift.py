"""
DRIFT AUDITOR - Implements AuditProtocol (GADADHARA)
====================================================

"dharma-kṣetre kuru-kṣetre samavetā yuyutsavaḥ"
"On the field of dharma, the field of Kuru, gathered to fight..."
— Bhagavad Gita 1.1

The DriftAuditor is the KSETRAJNA (knower) observing the KSETRA (field).
It implements AuditProtocol and is GAD-000 compliant.

GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
Mayavad: CLEAR (signed by yamaraja via parampara)

Usage:
    from vibe_core.mahamantra.audit.drift import DriftAuditor

    auditor = DriftAuditor()
    report = auditor.audit()  # Full AuditReport

    # Or atomic:
    valid, broken, violations = auditor.lineage()
"""

from __future__ import annotations

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity, get_source_cache
from vibe_core.mahamantra.protocols._audit import (
    AuditReport,
    LineageViolation,
    ProtocolViolation,
    SSOTViolation,
)
from vibe_core.mahamantra.protocols._pancha import TattvaDict
from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("DRIFT_AUDITOR")


# =============================================================================
# SACRED CONSTANTS (from _axioms.py)
# =============================================================================

SACRED_CONSTANTS: Dict[str, int] = {
    "PARAMPARA": 37,
    "WORDS": 16,
    "TRINITY": 3,
    "HARE_COUNT": 8,
    "KRISHNA_COUNT": 4,
    "RAMA_COUNT": 4,
    "PANCHA": 5,
    "HALVES": 2,
}
SSOT_FILES: Tuple[str, ...] = ("_axioms.py", "_seed.py")


# =============================================================================
# DRIFT AUDITOR - Implements AuditProtocol
# =============================================================================


class Auditor:  # Renamed from DriftAuditor
    """
    The Drift Auditor - Implements AuditProtocol.

    PANCHA TATTVA:
        CHAITANYA  - Drift detection and healing
        NITYANANDA - vibe_core/mahamantra codebase
        ADVAITA    - AuditProtocol, GADProtocol
        GADADHARA  - AuditReport flows to consumers
        SRIVASA    - PARAMPARA=37 governs all
    """

    def __init__(self, root: Path | None = None) -> None:
        self._root = Path(root or "vibe_core/mahamantra")

    # === PANCHA TATTVA ===

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "DriftAuditor - Ksetrajna observing Ksetra",
            "nityananda": f"Codebase at {self._root}",
            "advaita": "AuditProtocol, GADProtocol, PanchaTattvaProtocol",
            "gadadhara": "AuditReport -> Agent Pipeline -> Self-Healing",
            "srivasa": "PARAMPARA=37 (24+12+1)",
        }

    # === GAD-000 CRITERIA ===

    def discover(self) -> Dict[str, object]:
        """Return machine-readable capability description."""
        return {
            "name": "DriftAuditor",
            "protocol": "AuditProtocol",
            "capabilities": ["lineage", "ssot", "protocols", "audit", "heal"],
            "root": str(self._root),
            "parampara": PARAMPARA,
        }

    def get_state(self) -> Dict[str, object]:
        """Return current audit state."""
        v, b, _ = self.lineage()
        c, viol = self.ssot()
        return {
            "lineage_valid": v,
            "lineage_broken": b,
            "ssot_clean": c,
            "ssot_violations": len(viol),
        }

    @property
    def is_idempotent(self) -> bool:
        """Audit is always idempotent (read-only)."""
        return True

    # === AUDIT METHODS ===

    def lineage(self) -> Tuple[int, int, Tuple[LineageViolation, ...]]:
        """Check lineage (genesis % 37). Returns (valid, broken, violations)."""
        violations: List[LineageViolation] = []
        valid = 0
        cache = get_source_cache(self._root)

        for path, content in cache.scan():
            gen = re.search(r'__genesis__\s*[=:]\s*["\']?(0x[0-9a-fA-F]+)', content)
            if not gen:
                continue

            genesis = int(gen.group(1), 16)
            if genesis % PARAMPARA == 0:
                valid += 1
                continue

            mj = re.search(r'__mahajana__\s*[=:]\s*["\'](\w+)["\']', content)
            pos = re.search(r"__position__\s*[=:]\s*(\d+)", content)

            if mj and pos:
                violations.append(
                    LineageViolation(
                        path=str(path),
                        mahajana=mj.group(1),
                        position=int(pos.group(1)),
                        current_genesis=gen.group(1),
                        correct_genesis=self._compute_genesis(mj.group(1), int(pos.group(1))),
                        remainder=genesis % PARAMPARA,
                    )
                )

        return valid, len(violations), tuple(violations)

    def ssot(self) -> Tuple[int, Tuple[SSOTViolation, ...]]:
        """Check SSOT. Returns (clean, violations)."""
        violations: List[SSOTViolation] = []
        clean = 0
        cache = get_source_cache(self._root)

        for path, content in cache.scan():
            if any(s in str(path) for s in SSOT_FILES):
                continue

            lines = content.split("\n")
            file_clean = True

            for i, line in enumerate(lines, 1):
                if line.strip().startswith("#") or "import" in line:
                    continue
                for const, val in SACRED_CONSTANTS.items():
                    if re.search(rf"\b{const}\s*=\s*{val}\b", line):
                        violations.append(SSOTViolation(str(path), i, const, val))
                        file_clean = False

            if file_clean:
                clean += 1

        return clean, tuple(violations)

    def protocols(self) -> Tuple[int, int, Tuple[ProtocolViolation, ...]]:
        """Check protocols. Returns (alive, dead, violations)."""
        violations: List[ProtocolViolation] = []
        alive = 0
        dead = 0

        # Registry: (module, class, protocol_module, protocol)
        checks = [
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
                "vibe_core.mahamantra.kernel.maha_kernel",
                "MahaKernel",
                "vibe_core.mahamantra.protocols._pancha",
                "PanchaTattvaProtocol",
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
            (
                "vibe_core.mahamantra.substrate.vm.venu_orchestrator",
                "VenuOrchestrator",
                "vibe_core.mahamantra.protocols._pancha",
                "PanchaTattvaProtocol",
            ),
        ]

        import importlib

        for mod_name, cls_name, proto_mod, proto_name in checks:
            try:
                mod = importlib.import_module(mod_name)
                cls = getattr(mod, cls_name)
                proto_m = importlib.import_module(proto_mod)
                proto = getattr(proto_m, proto_name)

                instance = cls.create() if hasattr(cls, "create") else cls()
                if isinstance(instance, proto):
                    alive += 1
                else:
                    dead += 1
                    violations.append(ProtocolViolation(cls_name, mod_name, proto_name, "isinstance=False"))
            except Exception as e:
                dead += 1
                violations.append(ProtocolViolation(cls_name, mod_name, proto_name, str(e)[:100]))

        return alive, dead, tuple(violations)

    def run_audit(self) -> List[AuditFinding]:
        """Run full audit and return findings for the registry."""
        findings: List[AuditFinding] = []

        # 1. Lineage Check
        _, _, lin_violations = self.lineage()
        for v in lin_violations:
            findings.append(
                AuditFinding(
                    source="DriftAuditor.lineage",
                    position=__position__,
                    mahajana=__mahajana__,
                    description=f"Broken lineage. Genesis {v.current_genesis} has remainder {v.remainder}",
                    file_path=v.path,
                    severity=FindingSeverity.CRITICAL,
                )
            )

        # 2. SSOT Check
        _, ssot_violations = self.ssot()
        for v in ssot_violations:
            findings.append(
                AuditFinding(
                    source="DriftAuditor.ssot",
                    position=__position__,
                    mahajana=__mahajana__,
                    description=f"Hardcoded sacred constant: {v.constant}={v.value}",
                    file_path=v.path,
                    line_number=v.line,
                    severity=FindingSeverity.WARNING,
                )
            )

        # 3. Protocol Check
        _, _, proto_violations = self.protocols()
        for v in proto_violations:
            findings.append(
                AuditFinding(
                    source="DriftAuditor.protocols",
                    position=__position__,
                    mahajana=__mahajana__,
                    description=f"Protocol violation for {v.class_name}: {v.error}",
                    file_path=v.module.replace(".", "/") + ".py",
                    severity=FindingSeverity.CRITICAL,
                )
            )

        return findings

    # === HEALING (NOT IDEMPOTENT - Marked) ===
    # NOT IDEMPOTENT - Modifies files

    def heal_lineage(self, dry_run: bool = False) -> List[str]:
        """Fix all broken lineages. Returns list of fixed paths."""
        _, _, violations = self.lineage()
        fixed: List[str] = []

        for v in violations:
            path = Path(v.path)
            content = path.read_text()
            new_content = re.sub(
                r'(__genesis__\s*[=:]\s*["\']?)0x[0-9a-fA-F]+(["\']?)', f"\\g<1>{v.correct_genesis}\\g<2>", content
            )
            if not dry_run:
                path.write_text(new_content)
            fixed.append(v.path)

        return fixed

    # === JAPA LOOP LISTENER (ALIVE AUDIT) ===

    def start_listening(self) -> None:
        """
        Hook into the Mahamantra Heartbeat (Japa Loop).

        This makes the Audit ALIVE. Instead of just scanning files,
        we verify system integrity on every cosmic breath.
        """
        # Lazy import to avoid circular dependency
        from vibe_core.mahamantra import mahamantra

        # Register self as listener
        # mahamantra is the singleton instance of MahamantraLotus
        mahamantra.register_listener(self._on_tick)
        logger.info("👂 DriftAuditor started listening to Mahamantra Heartbeat")

    def _on_tick(self, state: Dict[str, object]) -> None:
        """
        Callback for Mahamantra Heartbeat.

        Args:
            state: Tick state dict from MahamantraLotus.tick()
        """
        tick = state.get("tick", 0)

        # LIVENESS CHECK (Every tick)
        # Just being called proves the heart is beating.

        # MALA CHECK (Every 108 ticks)
        # Run a full audit scan periodically to detect drift.
        # 108 is the sacred number of beads in a Mala.
        if isinstance(tick, int) and tick % 108 == 0:
            logger.info(f"📿 MALA COMPLETE (Tick {tick}). Running periodic drift audit...")
            report = self.audit()
            if not report.is_pristine:
                logger.warning(f"⚠️ DRIFT DETECTED during Japa Loop: {report.protocols_dead} dead protocols")
            else:
                logger.info("✅ SYSTEM PRISTINE")

    # === PRIVATE ===

    @staticmethod
    def _compute_genesis(mahajana: str, position: int) -> str:
        """YOGA MAYA: Pure archetype identity."""
        identity = f"{mahajana}:{position}"
        raw = hashlib.sha256(identity.encode()).hexdigest()[:8]
        base = int(raw, 16)
        return f"0x{base - (base % PARAMPARA):08x}"


__all__ = [
    "Auditor",
    "AuditReport",
    "LineageViolation",
    "SSOTViolation",
    "ProtocolViolation",
]
