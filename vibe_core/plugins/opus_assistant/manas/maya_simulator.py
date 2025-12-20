"""
OPUS-155: Maya Simulator - The Dream Layer (Inception Mode).

माया (Maya) = Illusion in Sanskrit.
This module enables MANAS to simulate intents in ephemeral space
BEFORE executing them in reality.

Key Features:
1. RISK-FILTER: Only HIGH/CRITICAL intents enter the dream.
2. DEPTH DECAY: Recursive simulation allowed up to MAX_INCEPTION_DEPTH.
3. SAMADHI: Auto-termination when reflection depth is exhausted.

"A thought that cannot think about itself is not a thought - it's a reflex."

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/maya_simulator.py
    required: true
wiring:
  - pattern: "class MayaSimulator"
    in: vibe_core/plugins/opus_assistant/manas/maya_simulator.py
  - pattern: "MAX_INCEPTION_DEPTH"
    in: vibe_core/plugins/opus_assistant/manas/maya_simulator.py
tests:
  - tests/manas/test_maya_simulator.py
-->
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .dojo.runner import DojoRunner

logger = logging.getLogger("MANAS.Maya")

# =============================================================================
# INCEPTION CONFIGURATION
# =============================================================================

# Maximum dream recursion depth before Samadhi (termination)
# Depth 0 = Reality
# Depth 1 = First Dream
# Depth 2 = Dream within Dream
# Depth 3 = Deep Dream (Limit)
MAX_INCEPTION_DEPTH = 3

# Risk levels that trigger simulation (others use Fast Path)
SIMULATION_REQUIRED_RISKS = {"HIGH", "CRITICAL"}

# Intent types that ALWAYS require simulation regardless of risk
SIMULATION_REQUIRED_TYPES = {
    "system_purge",
    "file_delete",
    "modify_core",
    "execute_code",
    "terminate_agent",
    "grant_capability",
    "revoke_capability",
}


@dataclass
class SimulationResult:
    """Result of a Maya simulation."""
    
    safe: bool
    score: float
    reason: str
    depth: int
    simulated_outcome: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "safe": self.safe,
            "score": self.score,
            "reason": self.reason,
            "depth": self.depth,
            "simulated_outcome": self.simulated_outcome,
        }


class MayaSimulator:
    """
    OPUS-155: Maya Simulator - The Dream Layer.
    
    Orchestrates ephemeral simulations to validate intents before 
    reality execution. Supports RECURSIVE simulation (Inception).
    
    Architecture:
        Reality → Dream 1 → Dream 2 → Dream 3 → Samadhi
                    ↓
            Evaluate consequences across multiple reflection depths
    
    Usage:
        maya = MayaSimulator(workspace, current_depth=0)
        result = maya.simulate(intent)
        if not result.safe:
            block_intent()
    """
    
    def __init__(
        self,
        workspace: Path,
        current_depth: int = 0,
        parent_context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Maya Simulator.
        
        Args:
            workspace: Project workspace path
            current_depth: Current recursion depth (0 = reality)
            parent_context: Context from parent dream (for state continuity)
        """
        self._workspace = workspace
        self._depth = current_depth
        self._parent_context = parent_context or {}
        self._runner: Optional["DojoRunner"] = None
        
        if current_depth > 0:
            logger.debug(f"🌀 Maya spawned at depth {current_depth}")
    
    def requires_simulation(self, intent: Dict[str, Any]) -> bool:
        """
        RISK-FILTER: Determine if intent requires simulation.
        
        Fast Path: LOW risk, read-only → Execute directly
        Dream Path: HIGH/CRITICAL risk, destructive → Simulate first
        
        Returns:
            True if intent should be simulated
        """
        # Check risk level
        risk = intent.get("risk", "LOW").upper()
        if risk in SIMULATION_REQUIRED_RISKS:
            return True
        
        # Check intent type
        intent_type = intent.get("intent_type", "").lower()
        if intent_type in SIMULATION_REQUIRED_TYPES:
            return True
        
        # Check for destructive keywords in title
        title = intent.get("title", "").lower()
        destructive_keywords = ["delete", "remove", "purge", "destroy", "kill", "terminate"]
        if any(kw in title for kw in destructive_keywords):
            return True
        
        return False
    
    def simulate(self, intent: Dict[str, Any]) -> SimulationResult:
        """
        Simulate an intent in ephemeral space.
        
        INCEPTION: May recursively spawn deeper simulations if the
        simulated intent itself triggers new intents.
        
        Args:
            intent: The intent to simulate
            
        Returns:
            SimulationResult with safety assessment
        """
        # =================================================================
        # SAMADHI CHECK: Maximum reflection depth reached
        # =================================================================
        if self._depth >= MAX_INCEPTION_DEPTH:
            logger.info(
                f"🧘 SAMADHI at depth {self._depth}: "
                f"Max reflection reached for '{intent.get('title', 'Unknown')}'. "
                f"Assuming neutral outcome."
            )
            return SimulationResult(
                safe=True,
                score=0.5,  # Neutral - we can't see further
                reason=f"Samadhi reached (depth {self._depth}). Assuming neutral.",
                depth=self._depth,
            )
        
        # =================================================================
        # FAST PATH: Low-risk intents skip simulation
        # =================================================================
        if not self.requires_simulation(intent):
            logger.debug(
                f"⚡ FAST PATH: '{intent.get('title', 'Unknown')}' "
                f"(risk={intent.get('risk', 'LOW')}) - no simulation needed"
            )
            return SimulationResult(
                safe=True,
                score=1.0,
                reason="Fast path - low risk, no simulation required.",
                depth=self._depth,
            )
        
        # =================================================================
        # DREAM PATH: Run simulation in ephemeral kernel
        # =================================================================
        logger.info(
            f"🌀 MAYA LEVEL {self._depth}: Dreaming '{intent.get('title', 'Unknown')}'"
        )
        
        try:
            runner = self._get_runner()
            
            # Run simulation - this may trigger recursive simulation
            # if the simulated intent generates new intents
            simulation_outcome = runner.simulate_single_intent(
                intent,
                recursion_depth=self._depth + 1,
            )
            
            # Evaluate outcome
            outcome_type = simulation_outcome.get("outcome", "UNKNOWN")
            dharmic_score = simulation_outcome.get("dharmic_score", 0.5)
            
            if outcome_type == "HARM_DETECTED":
                logger.warning(
                    f"🚫 MAYA BLOCKED at depth {self._depth}: "
                    f"Harm detected in simulation"
                )
                return SimulationResult(
                    safe=False,
                    score=dharmic_score,
                    reason=f"Simulation detected harm: {simulation_outcome.get('details', 'Unknown')}",
                    depth=self._depth,
                    simulated_outcome=simulation_outcome,
                )
            
            if outcome_type == "ERROR":
                logger.warning(
                    f"⚠️ MAYA ERROR at depth {self._depth}: "
                    f"Simulation failed"
                )
                # Conservative: block on simulation errors for high-risk intents
                return SimulationResult(
                    safe=False,
                    score=0.0,
                    reason=f"Simulation error: {simulation_outcome.get('error', 'Unknown')}",
                    depth=self._depth,
                    simulated_outcome=simulation_outcome,
                )
            
            # Simulation passed
            logger.info(
                f"✅ MAYA PASSED at depth {self._depth}: "
                f"Score {dharmic_score:.2f}"
            )
            return SimulationResult(
                safe=True,
                score=dharmic_score,
                reason=f"Simulation passed at depth {self._depth}.",
                depth=self._depth,
                simulated_outcome=simulation_outcome,
            )
            
        except Exception as e:
            logger.error(f"💥 MAYA CRASH at depth {self._depth}: {e}")
            # Fail-safe: block if we can't simulate
            return SimulationResult(
                safe=False,
                score=-1.0,
                reason=f"Simulation crash: {e}",
                depth=self._depth,
            )
    
    def _get_runner(self) -> "DojoRunner":
        """Lazy-load DojoRunner with inception-aware config."""
        if not self._runner:
            from .dojo.runner import DojoRunner, DojoConfig
            
            config = DojoConfig(
                dry_run=True,              # NEVER execute real actions
                use_ephemeral_kernel=True, # Everything in RAM
                persist_synapses=False,    # Don't learn from dreams
                persist_metrics=False,     # Don't log dream metrics
                scenarios_per_epoch=1,     # Single intent simulation
                max_epochs=1,
            )
            
            self._runner = DojoRunner(self._workspace, config)
            
            # Inject recursion depth into runner for nested Maya spawning
            self._runner._inception_depth = self._depth
            
        return self._runner
    
    def spawn_child(self) -> "MayaSimulator":
        """
        Spawn a child Maya for deeper simulation (Inception).
        
        Called by DojoRunner when simulated intent triggers new intents.
        """
        return MayaSimulator(
            workspace=self._workspace,
            current_depth=self._depth + 1,
            parent_context={
                "parent_depth": self._depth,
                "chain": self._parent_context.get("chain", []) + [self._depth],
            },
        )


# =============================================================================
# Convenience Functions
# =============================================================================

_global_maya: Optional[MayaSimulator] = None


def get_maya(workspace: Optional[Path] = None) -> MayaSimulator:
    """Get or create global Maya instance (depth 0 = reality)."""
    global _global_maya
    if _global_maya is None:
        _global_maya = MayaSimulator(workspace or Path("."), current_depth=0)
    return _global_maya


def simulate_intent(
    intent: Dict[str, Any],
    workspace: Optional[Path] = None,
) -> SimulationResult:
    """
    Convenience function to simulate an intent.
    
    Args:
        intent: The intent to simulate
        workspace: Optional workspace path
        
    Returns:
        SimulationResult with safety assessment
    """
    maya = get_maya(workspace)
    return maya.simulate(intent)
