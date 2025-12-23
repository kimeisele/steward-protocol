"""
OPUS-211: ArchitectureSense - Structural Integrity Awareness

This sense monitors the architectural health of the codebase.
It uses the CodeScanner to detect structural smells:
1. Duplicate class definitions (code smell)
2. Circular imports (architectural violation)
3. Layer violations (Varga dissonance)

"Architecture is the skeleton of the system.
 When the skeleton is weak, the mind cannot act with power."
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# OPUS-167: Intent imports for generate_intents()
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)

from .base import BaseSense

logger = logging.getLogger("MANAS.Cortex.ArchitectureSense")


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class ArchitectureAnomaly:
    """A detected architectural anomaly."""

    anomaly_type: str  # "duplicate_class", "circular_import", "layer_violation"
    severity: str  # "critical", "warning", "info"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitecturePerception:
    """Result of ArchitectureSense perception."""

    anomalies: List[ArchitectureAnomaly]
    duplicate_count: int
    circular_count: int
    violation_count: int

    # Health score (0-100)
    health_score: int
    timestamp: str

    def is_healthy(self) -> bool:
        """Check if architecture is healthy."""
        return len([a for a in self.anomalies if a.severity == "critical"]) == 0


# =============================================================================
# ArchitectureSense Implementation
# =============================================================================


class ArchitectureSense(BaseSense):
    """
    Structural Integrity Awareness - The Architect's Eye.

    Uses CodeScanner to perceive the skeleton of the codebase.
    """

    name = "architecture_sense"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)
        self._last_perception: Optional[ArchitecturePerception] = None
        logger.info("[ARCHITECTURE_SENSE] Initialized - Watching the skeleton")

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> ArchitecturePerception:
        """
        Perceive the current architectural health.
        """
        anomalies: List[ArchitectureAnomaly] = []

        # 1. Use CodeScanner to find duplicates and imports
        from vibe_core.knowledge.code_scanner import CodeScanner
        from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

        graph = UnifiedKnowledgeGraph()
        scanner = CodeScanner(graph)

        core_path = self._workspace / "vibe_core"
        if core_path.exists():
            scanner.scan_directory(core_path)

        # 2. Extract duplicates
        duplicates = scanner.get_duplicates()
        for dup in duplicates:
            anomalies.append(
                ArchitectureAnomaly(
                    anomaly_type="duplicate_class",
                    severity="warning",
                    message=f"Duplicate class '{dup['class_name']}' found in {dup['count']} files",
                    details=dup,
                )
            )

        # 3. Detect circular imports
        import_graph = scanner.get_import_graph()
        circles = self._find_circles(import_graph)
        for circle in circles:
            anomalies.append(
                ArchitectureAnomaly(
                    anomaly_type="circular_import",
                    severity="critical",
                    message=f"Circular import detected: {' -> '.join(circle)}",
                    details={"cycle": circle},
                )
            )

        # 4. Check for layer violations (Varga dissonance)
        dissonance = scanner.get_dissonant_imports(threshold=0.3)
        for dis in dissonance:
            anomalies.append(
                ArchitectureAnomaly(
                    anomaly_type="layer_violation",
                    severity="info",
                    message=f"Layer violation: {dis['source']} imports {dis['target']} (resonance={dis['resonance']:.2f})",
                    details=dis,
                )
            )

        # 5. Calculate Health Score
        critical_count = sum(1 for a in anomalies if a.severity == "critical")
        warning_count = sum(1 for a in anomalies if a.severity == "warning")
        info_count = sum(1 for a in anomalies if a.severity == "info")

        health_score = max(0, 100 - (critical_count * 25) - (warning_count * 5))

        perception = ArchitecturePerception(
            anomalies=anomalies,
            duplicate_count=len(duplicates),
            circular_count=len(circles),
            violation_count=info_count,
            health_score=health_score,
            timestamp=datetime.utcnow().isoformat(),
        )

        self._last_perception = perception
        return perception

    def _find_circles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find cycles in the import graph using DFS."""
        cycles = []
        visited = set()
        path = []
        path_set = set()

        def visit(node):
            if node in path_set:
                # Cycle found! Extract the cycle part
                cycle_start_idx = path.index(node)
                cycles.append(path[cycle_start_idx:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)
            path_set.add(node)

            # Targets are module names, but graph keys are module:path
            # We need to map module names back to keys if possible
            for target in graph.get(node, []):
                # Simple heuristic: look for module:target in keys
                target_key = f"module:{target}"
                if target_key in graph:
                    visit(target_key)
                else:
                    # Try to find a key that ends with the target name
                    # (e.g. module:vibe_core/event_bus.py matches target event_bus)
                    found = False
                    for key in graph:
                        if key.endswith(f"/{target}.py") or key == f"module:{target}":
                            visit(key)
                            found = True
                            break

            path_set.remove(node)
            path.pop()

        for node in list(graph.keys()):
            visit(node)

        return cycles

    def generate_intents(self, context: Optional[Dict[str, Any]] = None) -> List[Intent]:
        """Generate intents for architectural repair."""
        intents: List[Intent] = []
        perception = self.perceive(context)

        # Generate intents for circular imports
        for anomaly in perception.anomalies:
            if anomaly.anomaly_type == "circular_import":
                intent = Intent(
                    id=f"arch_fix_circle_{hash(str(anomaly.details['cycle']))}",
                    intent_type="code_refactor",
                    title=f"🔴 Fix Circular Import: {anomaly.details['cycle'][0]}",
                    description=anomaly.message,
                    reasoning="Circular imports break modularity and cause runtime issues.",
                    priority=IntentPriority.CRITICAL,
                    risk=IntentRisk.HIGH,
                    related_files=[c.replace("module:", "") for c in anomaly.details["cycle"]],
                    params={"cycle": anomaly.details["cycle"]},
                )
                intents.append(intent)

        # Generate intent for duplicate classes
        if perception.duplicate_count > 0:
            # Group by class name
            duplicates = [a for a in perception.anomalies if a.anomaly_type == "duplicate_class"]
            for dup in duplicates[:3]:  # Top 3 only
                name = dup.details["class_name"]
                intent = Intent(
                    id=f"arch_consolidate_{name.lower()}",
                    intent_type="code_refactor",
                    title=f"🟡 Consolidate Duplicate Class: {name}",
                    description=dup.message,
                    reasoning="Duplicate classes indicate redundant code and violate DRY principle.",
                    priority=IntentPriority.MEDIUM,
                    risk=IntentRisk.MEDIUM,
                    related_files=[loc["path"] for loc in dup.details["locations"]],
                    params={"class_name": name, "locations": dup.details["locations"]},
                )
                intents.append(intent)

        return intents

    def get_boot_summary(self) -> Dict[str, Any]:
        """Polymorphic Boot Summary."""
        perception = self.perceive()
        emoji = "🏗️"
        if perception.health_score < 50:
            emoji = "🏚️"
        elif perception.health_score < 80:
            emoji = "🏗️"
        else:
            emoji = "🏛️"

        return {
            "message": f"Architecture Health: {perception.health_score}% | {perception.duplicate_count} dups, {perception.circular_count} cycles",
            "data": {
                "health_score": perception.health_score,
                "duplicates": perception.duplicate_count,
                "cycles": perception.circular_count,
            },
            "emoji": emoji,
        }
