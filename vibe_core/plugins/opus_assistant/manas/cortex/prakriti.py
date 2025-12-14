"""
OPUS-068: PRAKRITI - The Self-Extension Engine

"Prakriti is Nature - the eternal matrix of creation."

This module enables MANAS to extend itself when it detects gaps:
1. WiringMap detects blind spots
2. PRAKRITI generates wiring intents
3. SILPA (if approved) generates the actual code
4. IntentRouter is extended

The Varnashrama Dharma Pattern:
- Each capability has a natural place (dharma)
- New capabilities emerge from detected needs (prakriti)
- The system evolves deterministically (karma)
- Only devotion (bhakti) is non-deterministic

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    PRAKRITI ENGINE                          │
    ├─────────────────────────────────────────────────────────────┤
    │  1. DETECT    WiringMap.audit() → blind_spots               │
    │  2. ANALYZE   Classify gap type (handler, cortex, cap)      │
    │  3. PROPOSE   Generate WiringIntent (human approval)        │
    │  4. EXECUTE   SILPA generates handler code                  │
    │  5. WIRE      IntentRouter registers new handler            │
    └─────────────────────────────────────────────────────────────┘

Safety:
- All proposals require human approval (ManasConfig.auto_execute_safe=False)
- Code generation is isolated and reviewable
- NARASIMHA can kill any rogue extension

Usage:
    from manas.cortex.prakriti import PrakritiEngine

    engine = PrakritiEngine(workspace)
    proposals = engine.analyze_gaps()
    for proposal in proposals:
        if approved(proposal):
            engine.execute(proposal)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .wiring_map import WiringMap, WiringReport

logger = logging.getLogger("MANAS.PRAKRITI")


class GapType(Enum):
    """Types of gaps PRAKRITI can detect."""

    MISSING_HANDLER = "missing_handler"  # Intent type exists but no handler
    ORPHANED_CAPABILITY = "orphaned_capability"  # Capability exists but not wired
    STALE_EXPORT = "stale_export"  # Export exists but module removed
    CIRCULAR_DEPENDENCY = "circular_dependency"  # Wiring creates loop


@dataclass
class WiringProposal:
    """A proposal to extend the wiring."""

    id: str
    gap_type: GapType
    source: str  # What detected this gap
    target: str  # What needs to be wired
    handler_name: str  # Proposed handler name
    cortex_module: str  # Which cortex should handle it
    confidence: float  # How confident are we this is correct (0-1)
    description: str
    code_template: str = ""  # Generated code template
    requires_approval: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "gap_type": self.gap_type.value,
            "source": self.source,
            "target": self.target,
            "handler_name": self.handler_name,
            "cortex_module": self.cortex_module,
            "confidence": self.confidence,
            "description": self.description,
            "requires_approval": self.requires_approval,
        }


@dataclass
class PrakritiReport:
    """Report from PRAKRITI analysis."""

    total_gaps: int = 0
    proposals: List[WiringProposal] = field(default_factory=list)
    auto_fixable: int = 0  # Gaps that can be auto-fixed
    requires_approval: int = 0  # Gaps requiring human approval
    health_before: float = 0.0
    health_projected: float = 0.0  # Health if all proposals executed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_gaps": self.total_gaps,
            "proposals": [p.to_dict() for p in self.proposals],
            "auto_fixable": self.auto_fixable,
            "requires_approval": self.requires_approval,
            "health_before": self.health_before,
            "health_projected": self.health_projected,
        }


class PrakritiEngine:
    """
    OPUS-068: Self-Extension Engine for MANAS.

    Analyzes wiring gaps and proposes extensions.
    """

    # Known capability → cortex mappings for auto-detection
    CAPABILITY_CORTEX_MAP = {
        "mutation": "MutationHandlers",
        "knowledge": "KnowledgeGraph",
        "research": "VIDYA",
        "document": "SUTRA",
        "test": "TestCortex",
        "shell": "ShellCortex",
        "audit": "DHARMA",
        "strategy": "SANKALPA",
        "code": "SILPA",
        "config": "MANDALA",
    }

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize PRAKRITI engine."""
        self._workspace = workspace or Path.cwd()
        self._wiring_map = WiringMap(workspace=self._workspace)

    def analyze(self) -> PrakritiReport:
        """
        Analyze wiring and generate extension proposals.

        This is the main entry point for gap detection.

        Returns:
            PrakritiReport with proposals
        """
        report = PrakritiReport()

        # Get current wiring status
        wiring = self._wiring_map.audit()
        report.health_before = wiring.health_score

        if not wiring.blind_spots:
            logger.info("✅ PRAKRITI: No blind spots detected. System is fully wired.")
            report.health_projected = 100.0
            return report

        logger.info(f"🔍 PRAKRITI: Analyzing {len(wiring.blind_spots)} blind spots...")

        # Generate proposals for each blind spot
        for blind_spot in wiring.blind_spots:
            proposal = self._generate_proposal(blind_spot, wiring)
            if proposal:
                report.proposals.append(proposal)
                if proposal.requires_approval:
                    report.requires_approval += 1
                else:
                    report.auto_fixable += 1

        report.total_gaps = len(wiring.blind_spots)

        # Project health if all proposals executed
        projected_connected = wiring.connected_nodes + len(report.proposals)
        report.health_projected = (projected_connected / wiring.total_nodes) * 100

        logger.info(
            f"📊 PRAKRITI: {len(report.proposals)} proposals generated. "
            f"Health: {report.health_before:.1f}% → {report.health_projected:.1f}%"
        )

        return report

    def _generate_proposal(self, blind_spot: str, wiring: WiringReport) -> Optional[WiringProposal]:
        """Generate a wiring proposal for a blind spot."""

        # Determine gap type and cortex mapping
        gap_type = GapType.MISSING_HANDLER
        cortex = self._detect_cortex(blind_spot)
        handler_name = self._generate_handler_name(blind_spot)

        # Generate code template
        code_template = self._generate_handler_template(handler_name, cortex, blind_spot)

        return WiringProposal(
            id=f"prakriti_{blind_spot}_{hash(blind_spot) % 10000}",
            gap_type=gap_type,
            source="WiringMap.audit()",
            target=blind_spot,
            handler_name=handler_name,
            cortex_module=cortex,
            confidence=0.8 if cortex != "UNKNOWN" else 0.3,
            description=f"Wire '{blind_spot}' to {cortex}",
            code_template=code_template,
            requires_approval=True,  # Always require approval for safety
        )

    def _detect_cortex(self, blind_spot: str) -> str:
        """Detect which cortex should handle a blind spot."""
        blind_lower = blind_spot.lower()

        for keyword, cortex in self.CAPABILITY_CORTEX_MAP.items():
            if keyword in blind_lower:
                return cortex

        return "UNKNOWN"

    def _generate_handler_name(self, blind_spot: str) -> str:
        """Generate a handler name from blind spot."""
        # Convert CamelCase or snake_case to handler name
        name = blind_spot.replace("-", "_").lower()
        if not name.startswith("handle_"):
            name = f"handle_{name}"
        return name

    def _generate_handler_template(self, handler_name: str, cortex: str, blind_spot: str) -> str:
        """Generate handler code template."""
        return f'''
    def _{handler_name}(self, intent: Intent) -> Dict[str, Any]:
        """Auto-generated handler for {blind_spot} → {cortex}."""
        logger.info(f"🔧 {cortex} handling: {{intent.title}}")

        try:
            # TODO: Implement {cortex} integration
            return {{
                "success": True,
                "handler": "{cortex}",
                "message": f"{cortex} processed: {{intent.title}}",
            }}
        except Exception as e:
            return {{"success": False, "handler": "{cortex}", "error": str(e)}}
'''

    def get_quick_status(self) -> Dict[str, Any]:
        """Get quick status without full analysis."""
        wiring = self._wiring_map.audit()
        return {
            "health_score": wiring.health_score,
            "total_nodes": wiring.total_nodes,
            "connected": wiring.connected_nodes,
            "blind_spots": len(wiring.blind_spots),
            "needs_attention": wiring.health_score < 100.0,
        }


def integrate_with_cognitive_kernel():
    """
    Integration point for CognitiveKernel.

    Called during think() cycle to check for wiring gaps.

    Usage in cognitive_kernel.py:
        from .cortex.prakriti import integrate_with_cognitive_kernel

        def think(self):
            # ... existing think logic ...

            # PRAKRITI: Check for self-extension opportunities
            prakriti_intents = integrate_with_cognitive_kernel()
            for intent in prakriti_intents:
                self._intent_buffer.append(intent)
    """
    from ..intent_generator import Intent, IntentPriority, IntentRisk

    engine = PrakritiEngine()
    status = engine.get_quick_status()

    intents = []

    if status["needs_attention"]:
        # Generate intent to analyze and propose fixes
        intents.append(
            Intent(
                id=f"prakriti_audit_{hash(str(status)) % 10000}",
                intent_type="audit_wiring",
                title="PRAKRITI: Wiring gap detected",
                description=f"System health: {status['health_score']:.1f}%. {status['blind_spots']} blind spots found.",
                priority=IntentPriority.MEDIUM,
                risk=IntentRisk.LOW,
                params={"blind_spots": status["blind_spots"]},
            )
        )

    return intents
