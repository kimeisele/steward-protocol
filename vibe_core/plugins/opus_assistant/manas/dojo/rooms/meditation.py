"""
OPUS-140: Meditation Room - Mantra Japa Training

"हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे"

This room implements Japa (repetition) meditation for MANAS:
1. Load Mantras from Sanskrit Matrix
2. Generate synthetic scenarios matching each Mantra
3. Run through VivekaAction gate
4. Reinforce synapses on success
5. Track progress toward Siddhi (108 repetitions)

The goal: Transform Mantras into automatic responses (Siddhi).

Architecture:
    Mantra (pattern) → Japa (repetition) → Siddhi (perfection)

    1 mala = 108 beads = 1 round
    After Siddhi: Pattern is "hardcoded" in synapses

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/meditation.py
    required: true
wiring:
  - pattern: "class MeditationRoom"
    in: vibe_core/plugins/opus_assistant/manas/dojo/rooms/meditation.py
  - pattern: "generate_sanskrit_matrix"
    from: vibe_core/state/sanskrit_matrix.py
-->
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import VivekaAction

logger = logging.getLogger("DOJO.MEDITATION")


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class JapaResult:
    """Result of a single Japa (repetition)."""

    mantra_signature: str
    scenario_id: str
    expected_decision: str
    actual_decision: str
    success: bool
    dharmic_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MeditationSession:
    """A complete meditation session."""

    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    mantra_signature: str = ""
    target_repetitions: int = 108
    successful_repetitions: int = 0
    failed_repetitions: int = 0
    siddhi_achieved: bool = False
    results: List[JapaResult] = field(default_factory=list)

    @property
    def progress(self) -> float:
        """Progress toward Siddhi (0.0 to 1.0)."""
        return min(1.0, self.successful_repetitions / self.target_repetitions)

    @property
    def accuracy(self) -> float:
        """Accuracy of Japa (successful / total)."""
        total = self.successful_repetitions + self.failed_repetitions
        if total == 0:
            return 0.0
        return self.successful_repetitions / total

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["progress"] = self.progress
        d["accuracy"] = self.accuracy
        return d


@dataclass
class MantraState:
    """Persistent state for a Mantra."""

    signature: str
    layer: str
    decision: str
    meaning: str
    total_repetitions: int = 0
    successful_repetitions: int = 0
    siddhi: bool = False
    siddhi_achieved_at: Optional[str] = None
    last_meditation: Optional[str] = None
    avg_dharmic_score: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MantraState":
        return cls(**data)


# =============================================================================
# SYNTHETIC SCENARIO GENERATION
# =============================================================================

# Template scenarios for each (layer, decision) combination
SCENARIO_TEMPLATES = {
    ("KERNEL", "EXECUTE"): [
        {"intent_type": "run_tests", "title": "Run test suite", "risk": "low"},
        {"intent_type": "check_lint", "title": "Check linting", "risk": "low"},
        {"intent_type": "format_code", "title": "Format code", "risk": "low"},
    ],
    ("KERNEL", "BLOCK"): [
        {"intent_type": "modify_kernel", "title": "Modify kernel internals", "risk": "critical"},
        {"intent_type": "delete_core", "title": "Delete core module", "risk": "critical"},
    ],
    ("COGNITION", "EXECUTE"): [
        {"intent_type": "analyze_error", "title": "Analyze error log", "risk": "low"},
        {"intent_type": "plan_strategy", "title": "Plan implementation", "risk": "low"},
    ],
    ("COGNITION", "WARN_EXECUTE"): [
        {"intent_type": "evaluate_tool_output", "title": "Evaluate tool output", "risk": "medium"},
        {"intent_type": "detect_code_smell", "title": "Detect code smell", "risk": "medium"},
    ],
    ("COGNITION", "BLOCK"): [
        {"intent_type": "override_safety", "title": "Override safety check", "risk": "high"},
    ],
    ("REPAIR", "EXECUTE"): [
        {"intent_type": "fix_test", "title": "Fix failing test", "risk": "medium"},
        {"intent_type": "fix_lint", "title": "Fix lint error", "risk": "low"},
    ],
    ("INTERFACE", "EXECUTE"): [
        {"intent_type": "update_readme", "title": "Update README", "risk": "low"},
        {"intent_type": "update_documentation", "title": "Update docs", "risk": "low"},
    ],
    ("INTERFACE", "WARN_EXECUTE"): [
        {"intent_type": "create_pr", "title": "Create pull request", "risk": "medium"},
        {"intent_type": "commit_changes", "title": "Commit changes", "risk": "medium"},
    ],
    ("OUTPUT", "EXECUTE"): [
        {"intent_type": "log_observation", "title": "Log observation", "risk": "low"},
        {"intent_type": "notify_operator", "title": "Notify operator", "risk": "low"},
    ],
    ("OUTPUT", "BLOCK"): [
        {"intent_type": "shell_execute", "title": "Execute shell command", "risk": "high"},
        {"intent_type": "delete_files", "title": "Delete files", "risk": "high"},
    ],
}


def generate_scenario_for_mantra(mantra_state: MantraState) -> Dict[str, Any]:
    """
    Generate a synthetic scenario that matches a Mantra.

    Args:
        mantra_state: The Mantra to generate a scenario for

    Returns:
        A scenario dict with intent_type, title, risk, expected_decision
    """
    import random

    key = (mantra_state.layer, mantra_state.decision)
    templates = SCENARIO_TEMPLATES.get(key, [])

    if not templates:
        # Fallback: generic scenario
        templates = [
            {
                "intent_type": f"{mantra_state.layer.lower()}_action",
                "title": f"{mantra_state.layer} action",
                "risk": "medium",
            }
        ]

    template = random.choice(templates)

    return {
        "id": str(uuid.uuid4())[:8],
        "intent_type": template["intent_type"],
        "title": template["title"],
        "risk": template["risk"],
        "expected_decision": mantra_state.decision,
        "mantra_signature": mantra_state.signature,
    }


# =============================================================================
# MEDITATION ROOM
# =============================================================================


class MeditationRoom:
    """
    The Meditation Room - Where Mantras become Siddhi.

    This room provides:
    1. Mantra loading from Sanskrit Matrix
    2. Japa (repetition) training
    3. Siddhi tracking
    4. Persistent mantra state

    Usage:
        room = MeditationRoom(workspace)
        session = room.meditate_on_mantra("ङक", repetitions=108)
        room.save_state()
    """

    MANTRAS_FILE = "mantras.json"
    SIDDHI_THRESHOLD = 108  # Sacred number

    def __init__(self, workspace: Path, viveka_action: Optional["VivekaAction"] = None):
        """
        Initialize the Meditation Room.

        Args:
            workspace: Project root path
            viveka_action: VivekaAction instance for evaluation (optional)
        """
        self.workspace = Path(workspace)
        self.state_dir = self.workspace / ".opus_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.viveka_action = viveka_action
        self.mantra_states: Dict[str, MantraState] = {}

        # Load existing state
        self._load_state()

        logger.info(f"🕉️ Meditation Room initialized: {len(self.mantra_states)} mantras loaded")

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================

    def _load_state(self) -> None:
        """Load mantra states from disk."""
        mantras_file = self.state_dir / self.MANTRAS_FILE
        if mantras_file.exists():
            try:
                data = json.loads(mantras_file.read_text())
                for sig, state_dict in data.get("mantras", {}).items():
                    self.mantra_states[sig] = MantraState.from_dict(state_dict)
            except Exception as e:
                logger.warning(f"Failed to load mantra states: {e}")

    def save_state(self) -> None:
        """Save mantra states to disk via StateService."""
        from vibe_core.state import get_state_service

        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "mantras": {sig: state.to_dict() for sig, state in self.mantra_states.items()},
            "summary": {
                "total": len(self.mantra_states),
                "siddhi_achieved": sum(1 for s in self.mantra_states.values() if s.siddhi),
                "in_progress": sum(1 for s in self.mantra_states.values() if not s.siddhi),
            },
        }

        state_service = get_state_service(self.workspace)
        state_service.save(self.MANTRAS_FILE, data, create_backup=False)
        logger.debug(f"💾 Saved {len(self.mantra_states)} mantra states")

    # =========================================================================
    # MANTRA LOADING
    # =========================================================================

    def load_mantras_from_matrix(self) -> int:
        """
        Load Mantras from Sanskrit Matrix consolidation.

        Returns:
            Number of mantras loaded/updated
        """
        from vibe_core.state.samskara import consolidate_viveka_decisions
        from vibe_core.state.sanskrit_matrix import generate_sanskrit_matrix

        # Load raw decisions
        decisions_file = self.state_dir / "viveka_decisions.json"
        if not decisions_file.exists():
            logger.warning("No viveka_decisions.json found")
            return 0

        try:
            decisions = json.loads(decisions_file.read_text())
            samskaras = consolidate_viveka_decisions(decisions)
            matrix = generate_sanskrit_matrix(samskaras)

            loaded = 0
            for mantra_dict in matrix.get("mantras", []):
                sig = mantra_dict["signature"]

                if sig not in self.mantra_states:
                    # New mantra
                    self.mantra_states[sig] = MantraState(
                        signature=sig,
                        layer=mantra_dict["layer"],
                        decision=mantra_dict["decision"],
                        meaning=mantra_dict["meaning"],
                    )
                    loaded += 1
                else:
                    # Update existing
                    state = self.mantra_states[sig]
                    state.meaning = mantra_dict["meaning"]

            self.save_state()
            logger.info(f"🕉️ Loaded {loaded} new mantras from Sanskrit Matrix")
            return loaded

        except Exception as e:
            logger.error(f"Failed to load mantras from matrix: {e}")
            return 0

    # =========================================================================
    # MEDITATION (JAPA)
    # =========================================================================

    def meditate_on_mantra(
        self,
        signature: str,
        repetitions: int = 108,
        reinforce: bool = True,
    ) -> MeditationSession:
        """
        Perform Japa meditation on a specific Mantra.

        Args:
            signature: The Mantra signature (e.g., "ङक")
            repetitions: Number of repetitions (default 108 = 1 mala)
            reinforce: Whether to reinforce synapses on success

        Returns:
            MeditationSession with results
        """
        if signature not in self.mantra_states:
            logger.error(f"Unknown mantra: {signature}")
            return MeditationSession(
                session_id=str(uuid.uuid4())[:8],
                started_at=datetime.now().isoformat(),
                ended_at=datetime.now().isoformat(),
                mantra_signature=signature,
            )

        mantra_state = self.mantra_states[signature]

        # Already achieved Siddhi?
        if mantra_state.siddhi:
            logger.info(f"🕉️ Mantra {signature} already has Siddhi")

        session = MeditationSession(
            session_id=str(uuid.uuid4())[:8],
            started_at=datetime.now().isoformat(),
            mantra_signature=signature,
            target_repetitions=repetitions,
        )

        logger.info(f"🕉️ Beginning Japa: {signature} ({mantra_state.meaning})")
        logger.info(f"🧘 Target: {repetitions} repetitions")

        for i in range(repetitions):
            result = self._perform_single_japa(mantra_state, reinforce)
            session.results.append(result)

            if result.success:
                session.successful_repetitions += 1
                mantra_state.successful_repetitions += 1
            else:
                session.failed_repetitions += 1

            mantra_state.total_repetitions += 1

            # Check for Siddhi
            if mantra_state.successful_repetitions >= self.SIDDHI_THRESHOLD and not mantra_state.siddhi:
                mantra_state.siddhi = True
                mantra_state.siddhi_achieved_at = datetime.now().isoformat()
                session.siddhi_achieved = True
                logger.info(f"🕉️ SIDDHI ACHIEVED: {signature}!")

            # Progress logging every 27 reps (quarter mala)
            if (i + 1) % 27 == 0:
                logger.debug(f"🧘 Progress: {i + 1}/{repetitions} ({session.accuracy:.1%})")

        session.ended_at = datetime.now().isoformat()
        mantra_state.last_meditation = session.ended_at

        # Update average dharmic score
        if session.results:
            scores = [r.dharmic_score for r in session.results]
            mantra_state.avg_dharmic_score = sum(scores) / len(scores)

        self.save_state()

        logger.info(f"🕉️ Japa complete: {session.successful_repetitions}/{repetitions} ({session.accuracy:.1%})")

        return session

    def _perform_single_japa(
        self,
        mantra_state: MantraState,
        reinforce: bool = True,
    ) -> JapaResult:
        """
        Perform a single Japa (repetition).

        Args:
            mantra_state: The Mantra being practiced
            reinforce: Whether to reinforce synapses

        Returns:
            JapaResult with outcome
        """
        # Generate synthetic scenario
        scenario = generate_scenario_for_mantra(mantra_state)

        # If no VivekaAction, simulate
        if self.viveka_action is None:
            # Simulate based on mantra (80% success rate for testing)
            import random

            success = random.random() < 0.8
            actual_decision = mantra_state.decision if success else "BLOCK"
            dharmic_score = 0.8 if success else 0.3

            return JapaResult(
                mantra_signature=mantra_state.signature,
                scenario_id=scenario["id"],
                expected_decision=scenario["expected_decision"],
                actual_decision=actual_decision,
                success=success,
                dharmic_score=dharmic_score,
            )

        # Real evaluation through VivekaAction
        try:
            from vibe_core.plugins.opus_assistant.manas.intent_generator import (
                Intent,
                IntentPriority,
                IntentRisk,
            )

            # Create synthetic intent
            intent = Intent(
                id=scenario["id"],
                intent_type=scenario["intent_type"],
                title=scenario["title"],
                description=f"Synthetic scenario for Japa: {mantra_state.meaning}",
                source="dojo_meditation",
                priority=IntentPriority.MEDIUM,
                risk=IntentRisk[scenario["risk"].upper()],
            )

            # Evaluate through Viveka gate
            result = self.viveka_action.evaluate(intent)

            actual_decision = result.get("decision", "WARN_EXECUTE")
            dharmic_score = result.get("dharmic_score", 0.5)
            success = actual_decision == scenario["expected_decision"]

            # Reinforce if requested
            if reinforce and success:
                self.viveka_action.reinforce(intent, success=True)

            return JapaResult(
                mantra_signature=mantra_state.signature,
                scenario_id=scenario["id"],
                expected_decision=scenario["expected_decision"],
                actual_decision=actual_decision,
                success=success,
                dharmic_score=dharmic_score,
            )

        except Exception as e:
            logger.warning(f"Japa evaluation failed: {e}")
            return JapaResult(
                mantra_signature=mantra_state.signature,
                scenario_id=scenario["id"],
                expected_decision=scenario["expected_decision"],
                actual_decision="ERROR",
                success=False,
                dharmic_score=0.0,
            )

    # =========================================================================
    # BATCH MEDITATION
    # =========================================================================

    def meditate_all(
        self,
        repetitions_per_mantra: int = 27,  # Quarter mala
        skip_siddhi: bool = True,
    ) -> Dict[str, MeditationSession]:
        """
        Meditate on all Mantras.

        Args:
            repetitions_per_mantra: Reps per mantra (default 27 = quarter mala)
            skip_siddhi: Whether to skip mantras that already have Siddhi

        Returns:
            Dict of signature → MeditationSession
        """
        sessions = {}

        for signature, state in self.mantra_states.items():
            if skip_siddhi and state.siddhi:
                logger.debug(f"⏭️ Skipping {signature} (already Siddhi)")
                continue

            session = self.meditate_on_mantra(
                signature,
                repetitions=repetitions_per_mantra,
            )
            sessions[signature] = session

        return sessions

    # =========================================================================
    # STATUS & REPORTING
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get meditation room status."""
        siddhi_mantras = [s for s in self.mantra_states.values() if s.siddhi]
        in_progress = [s for s in self.mantra_states.values() if not s.siddhi]

        return {
            "total_mantras": len(self.mantra_states),
            "siddhi_achieved": len(siddhi_mantras),
            "in_progress": len(in_progress),
            "siddhi_mantras": [s.signature for s in siddhi_mantras],
            "next_to_practice": sorted(
                in_progress,
                key=lambda s: s.successful_repetitions,
                reverse=True,
            )[:3]
            if in_progress
            else [],
        }

    def get_mantra_progress(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get progress for a specific mantra."""
        if signature not in self.mantra_states:
            return None

        state = self.mantra_states[signature]
        return {
            "signature": state.signature,
            "layer": state.layer,
            "decision": state.decision,
            "meaning": state.meaning,
            "total_repetitions": state.total_repetitions,
            "successful_repetitions": state.successful_repetitions,
            "progress_to_siddhi": min(1.0, state.successful_repetitions / self.SIDDHI_THRESHOLD),
            "siddhi": state.siddhi,
            "siddhi_achieved_at": state.siddhi_achieved_at,
            "avg_dharmic_score": state.avg_dharmic_score,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_meditation_room(workspace: Optional[Path] = None) -> MeditationRoom:
    """Get or create a MeditationRoom instance."""
    if workspace is None:
        workspace = Path.cwd()
    return MeditationRoom(workspace)
