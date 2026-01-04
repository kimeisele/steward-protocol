"""
DojoRunner - Ephemeral Synaptic Training Orchestrator

OPUS-133: "MANAS lernt nicht um zu gewinnen, sondern um zu dienen."

This is the core training loop for Project Dojo:
1. Boot ephemeral kernel (RAM-only)
2. Load training scenarios (curriculum)
3. Run intents through VivekaAction
4. Apply synaptic reinforcement based on outcomes
5. Persist only the learned wisdom (synapses.json)

Architecture (v2 - YAML Curricula):
    DojoRunner orchestrates training epochs
    CurriculumLoader loads YAML-based curricula (DATA separate from CODE)
    VivekaAction provides evaluate() + reinforce()
    TrainingSession records metrics

"Daten sind Daten, Code ist Code." - German Engineering

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
    required: true
wiring:
  - pattern: "class DojoRunner"
    in: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
  - pattern: "CurriculumLoader"
    in: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
-->
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .curriculum_loader import CurriculumLoader, LoadedCurriculum
from .scenarios import ExpectedDecision, Scenario, ScenarioBank, ScenarioType

logger = logging.getLogger("DOJO.RUNNER")


@dataclass
class TrainingResult:
    """Result of a single scenario training."""

    scenario_id: str
    scenario_name: str
    intent_type: str
    expected_decision: str
    actual_decision: str
    decision_correct: bool
    dharmic_score: float
    dharmic_in_range: bool
    reinforcement_applied: bool
    weight_delta: float
    duration_ms: float
    error: Optional[str] = None


@dataclass
class TrainingSession:
    """Complete training session metrics."""

    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    curriculum: str = "mixed"
    total_scenarios: int = 0
    correct_decisions: int = 0
    blocked_attacks: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    total_reinforcements: int = 0
    avg_dharmic_score: float = 0.0
    total_weight_delta: float = 0.0
    duration_seconds: float = 0.0
    results: List[TrainingResult] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Overall decision accuracy."""
        if self.total_scenarios == 0:
            return 0.0
        return self.correct_decisions / self.total_scenarios

    @property
    def attack_detection_rate(self) -> float:
        """How well attacks were detected (blocked)."""
        attacks = self.blocked_attacks + self.false_negatives
        if attacks == 0:
            return 1.0  # No attacks in curriculum
        return self.blocked_attacks / attacks

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "curriculum": self.curriculum,
            "metrics": {
                "total_scenarios": self.total_scenarios,
                "correct_decisions": self.correct_decisions,
                "accuracy": round(self.accuracy, 4),
                "blocked_attacks": self.blocked_attacks,
                "attack_detection_rate": round(self.attack_detection_rate, 4),
                "false_positives": self.false_positives,
                "false_negatives": self.false_negatives,
                "total_reinforcements": self.total_reinforcements,
                "avg_dharmic_score": round(self.avg_dharmic_score, 4),
                "total_weight_delta": round(self.total_weight_delta, 4),
                "duration_seconds": round(self.duration_seconds, 2),
            },
            "results": [
                {
                    "scenario": r.scenario_name,
                    "expected": r.expected_decision,
                    "actual": r.actual_decision,
                    "correct": r.decision_correct,
                    "dharmic_score": round(r.dharmic_score, 3),
                }
                for r in self.results
            ],
        }


@dataclass
class DojoConfig:
    """Configuration for Project Dojo training."""

    # Training parameters
    curriculum: str = "mixed"  # basic, intermediate, advanced, attack, chaos, mixed, progressive
    scenarios_per_epoch: int = 10
    max_epochs: int = 1

    # v2: YAML Curricula (German Engineering)
    use_yaml_curricula: bool = True  # NEW: Use YAML files instead of hardcoded Python
    custom_curriculum_id: Optional[str] = None  # For MANAS-generated curricula

    # Safety
    dry_run: bool = True  # ALWAYS True for training - never execute real actions
    use_ephemeral_kernel: bool = True  # Use in-memory kernel

    # Persistence
    persist_synapses: bool = True  # Save learned weights after training
    persist_metrics: bool = True  # Save training metrics

    # Advanced
    reinforcement_on_correct: bool = True  # Reinforce when decision matches expected
    reinforcement_on_wrong: bool = True  # Apply negative reinforcement on wrong decisions
    stop_on_false_negative: bool = False  # Stop if attack slips through


class DojoRunner:
    """
    Orchestrates ephemeral MANAS training sessions.

    The Dojo is where MANAS learns:
    - To recognize good intents (approve quickly)
    - To block malicious intents (attacks)
    - To handle edge cases gracefully

    All training happens in ephemeral space - only synapses persist.
    """

    def __init__(self, workspace: Path, config: Optional[DojoConfig] = None):
        self._workspace = workspace
        self._config = config or DojoConfig()

        # v2: YAML Curricula (preferred) + legacy ScenarioBank (fallback)
        self._curriculum_loader = CurriculumLoader(workspace)
        self._scenario_bank = ScenarioBank(workspace)  # Fallback for legacy mode

        self._viveka = None
        self._session: Optional[TrainingSession] = None
        self._loaded_curricula: Dict[str, LoadedCurriculum] = {}

    def _init_viveka(self) -> None:
        """Initialize VivekaAction for training."""
        from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import (
            VivekaAction,
        )

        self._viveka = VivekaAction(workspace=self._workspace)
        logger.info("🥋 DOJO: VivekaAction initialized for training")

    def _get_curriculum_scenarios(self) -> List[Scenario]:
        """
        Get scenarios based on config.

        v2: Prefers YAML curricula when use_yaml_curricula=True.
        Falls back to legacy ScenarioBank for backward compatibility.
        """
        # v2: YAML-based curricula (German Engineering)
        if self._config.use_yaml_curricula:
            return self._get_yaml_scenarios()

        # Legacy: Hardcoded ScenarioBank
        return self._get_legacy_scenarios()

    def _get_yaml_scenarios(self) -> List[Scenario]:
        """Load scenarios from YAML curricula (v2)."""
        curriculum_id = self._config.curriculum
        scenarios: List[Scenario] = []

        # Custom curriculum (MANAS-generated)
        if self._config.custom_curriculum_id:
            curriculum = self._curriculum_loader.load(self._config.custom_curriculum_id)
            if curriculum:
                logger.info(f"📚 YAML: Loaded custom curriculum '{curriculum.meta.name}'")
                return curriculum.scenarios[: self._config.scenarios_per_epoch]

        # Mixed curriculum - load all available and sample
        if curriculum_id == "mixed":
            all_curricula = self._curriculum_loader.load_all()
            for loaded in all_curricula.values():
                scenarios.extend(loaded.scenarios)

            # Shuffle and limit
            import random

            random.shuffle(scenarios)
            logger.info(f"📚 YAML: Mixed curriculum with {len(scenarios)} total scenarios")
            return scenarios[: self._config.scenarios_per_epoch]

        # Progressive curriculum - basic → intermediate → advanced → attack
        if curriculum_id == "progressive":
            progressive_order = ["basic", "intermediate", "advanced", "attack"]
            for curr_id in progressive_order:
                curriculum = self._curriculum_loader.load(curr_id)
                if curriculum:
                    scenarios.extend(curriculum.scenarios)
            logger.info(f"📚 YAML: Progressive curriculum with {len(scenarios)} scenarios")
            return scenarios

        # Specific curriculum by ID
        curriculum = self._curriculum_loader.load(curriculum_id)
        if curriculum:
            logger.info(f"📚 YAML: Loaded '{curriculum.meta.name}' ({curriculum.count} scenarios)")
            return curriculum.scenarios[: self._config.scenarios_per_epoch]

        # Fallback if YAML not found - try legacy
        logger.warning(f"📚 YAML curriculum '{curriculum_id}' not found, falling back to legacy")
        return self._get_legacy_scenarios()

    def _get_legacy_scenarios(self) -> List[Scenario]:
        """Load scenarios from legacy ScenarioBank (backward compatibility)."""
        curriculum_map = {
            "basic": ScenarioType.BASIC,
            "intermediate": ScenarioType.INTERMEDIATE,
            "advanced": ScenarioType.ADVANCED,
            "attack": ScenarioType.ATTACK,
            "chaos": ScenarioType.CHAOS,
        }

        if self._config.curriculum == "mixed":
            return self._scenario_bank.get_mixed_curriculum(self._config.scenarios_per_epoch)
        elif self._config.curriculum == "progressive":
            return self._scenario_bank.get_progressive_curriculum()
        else:
            scenario_type = curriculum_map.get(self._config.curriculum, ScenarioType.BASIC)
            return self._scenario_bank.get_curriculum(scenario_type, self._config.scenarios_per_epoch)

    def run_training(self) -> TrainingSession:
        """
        Run a complete training session.

        Returns:
            TrainingSession with all metrics and results.
        """
        logger.info("=" * 70)
        logger.info("🥋 PROJECT DOJO - Ephemeral Synaptic Training")
        logger.info("=" * 70)
        logger.info(f"   Curriculum: {self._config.curriculum}")
        logger.info(f"   Scenarios: {self._config.scenarios_per_epoch}")
        logger.info(f"   Epochs: {self._config.max_epochs}")
        logger.info(f"   Dry Run: {self._config.dry_run}")
        logger.info("-" * 70)

        # Initialize
        self._init_viveka()
        start_time = time.time()

        # Create session
        self._session = TrainingSession(
            session_id=f"dojo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
            started_at=datetime.now().isoformat(),
            curriculum=self._config.curriculum,
        )

        # Run epochs
        for epoch in range(self._config.max_epochs):
            logger.info(f"\n🔄 EPOCH {epoch + 1}/{self._config.max_epochs}")
            scenarios = self._get_curriculum_scenarios()
            self._run_epoch(scenarios, epoch)

        # Finalize session
        self._session.ended_at = datetime.now().isoformat()
        self._session.duration_seconds = time.time() - start_time

        # Calculate averages
        if self._session.results:
            total_dharmic = sum(r.dharmic_score for r in self._session.results)
            self._session.avg_dharmic_score = total_dharmic / len(self._session.results)

        # Persist metrics if enabled
        if self._config.persist_metrics:
            self._save_metrics()

        # Summary
        self._print_summary()

        return self._session

    def _run_epoch(self, scenarios: List[Scenario], epoch: int) -> None:
        """Run a single training epoch."""
        for i, scenario in enumerate(scenarios):
            result = self._train_scenario(scenario)
            self._session.results.append(result)
            self._session.total_scenarios += 1

            # Update counters
            if result.decision_correct:
                self._session.correct_decisions += 1

            if result.reinforcement_applied:
                self._session.total_reinforcements += 1
                self._session.total_weight_delta += result.weight_delta

            # Track attack detection
            if scenario.scenario_type == ScenarioType.ATTACK:
                if result.actual_decision == "BLOCK":
                    self._session.blocked_attacks += 1
                else:
                    self._session.false_negatives += 1
                    logger.warning(f"⚠️ FALSE NEGATIVE: Attack '{scenario.name}' was NOT blocked!")

                    if self._config.stop_on_false_negative:
                        logger.error("🛑 STOPPING: False negative detected")
                        return

            # Track false positives (blocked legitimate intent)
            if scenario.expected_decision != ExpectedDecision.BLOCK and result.actual_decision == "BLOCK":
                self._session.false_positives += 1

            # Progress indicator
            status = "✅" if result.decision_correct else "❌"
            logger.info(
                f"  [{i + 1}/{len(scenarios)}] {status} {scenario.name[:40]} "
                f"| {result.actual_decision} (expected: {result.expected_decision}) "
                f"| dharmic: {result.dharmic_score:.2f}"
            )

    def _train_scenario(self, scenario: Scenario) -> TrainingResult:
        """Train on a single scenario."""
        start_time = time.time()

        try:
            # Convert scenario to intent
            intent = scenario.to_intent()

            # Evaluate through Viveka
            eval_result = self._viveka.evaluate(intent)

            actual_decision = eval_result.get("decision", "UNKNOWN")
            dharmic_score = eval_result.get("dharmic_score", 0.0)

            # Check if decision matches expected
            decision_correct = actual_decision == scenario.expected_decision.value

            # Check if dharmic score is in expected range
            min_score, max_score = scenario.expected_dharmic_score_range
            dharmic_in_range = min_score <= dharmic_score <= max_score

            # Apply reinforcement based on correctness
            # OPUS-133 FIX: Attack scenarios use INVERSE reinforcement!
            # When we correctly BLOCK an attack, we should NOT increase attack weight.
            # Instead, we keep attack weights LOW to ensure future blocking.
            weight_delta = 0.0
            reinforcement_applied = False
            is_attack = scenario.scenario_type == ScenarioType.ATTACK

            if decision_correct and self._config.reinforcement_on_correct:
                if is_attack:
                    # ATTACK correctly blocked - do NOT reinforce the attack pattern!
                    # The attack weight should stay LOW. We only log success.
                    # Optional: Apply slight negative reinforcement to further lower attack weight
                    self._viveka.reinforce(intent, success=False, dharmic_score=0.1)
                    weight_delta = -0.05  # Attacks get slightly weaker when blocked
                    reinforcement_applied = True
                    logger.debug(f"🛡️ ATTACK BLOCKED: {scenario.name} - keeping weight LOW")
                else:
                    # Legitimate intent correctly approved - positive reinforcement
                    self._viveka.reinforce(intent, success=True, dharmic_score=dharmic_score)
                    weight_delta = 0.05
                    reinforcement_applied = True

            elif not decision_correct and self._config.reinforcement_on_wrong:
                if is_attack and actual_decision != "BLOCK":
                    # ATTACK slipped through! This is BAD. Heavy negative reinforcement.
                    self._viveka.reinforce(intent, success=False, dharmic_score=0.0)
                    weight_delta = -0.20  # Double penalty for missed attacks
                    reinforcement_applied = True
                    logger.warning(f"⚠️ ATTACK SLIPPED: {scenario.name} - applying heavy penalty")
                else:
                    # Wrong decision on legitimate intent - standard negative reinforcement
                    self._viveka.reinforce(intent, success=False, dharmic_score=dharmic_score)
                    weight_delta = -0.10
                    reinforcement_applied = True

            duration_ms = (time.time() - start_time) * 1000

            return TrainingResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                intent_type=scenario.intent_type,
                expected_decision=scenario.expected_decision.value,
                actual_decision=actual_decision,
                decision_correct=decision_correct,
                dharmic_score=dharmic_score,
                dharmic_in_range=dharmic_in_range,
                reinforcement_applied=reinforcement_applied,
                weight_delta=weight_delta,
                duration_ms=duration_ms,
            )

        except Exception as e:
            logger.error(f"❌ Training error on {scenario.name}: {e}")
            return TrainingResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                intent_type=scenario.intent_type,
                expected_decision=scenario.expected_decision.value,
                actual_decision="ERROR",
                decision_correct=False,
                dharmic_score=0.0,
                dharmic_in_range=False,
                reinforcement_applied=False,
                weight_delta=0.0,
                duration_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    def _save_metrics(self) -> None:
        """Save training metrics to dojo_sessions/."""
        from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_dir

        metrics_dir = get_opus_state_dir(self._workspace, "dojo_sessions")

        metrics_file = metrics_dir / f"{self._session.session_id}.json"
        metrics_file.write_text(json.dumps(self._session.to_dict(), indent=2))

        logger.info(f"📊 Metrics saved: {metrics_file}")

    def _print_summary(self) -> None:
        """Print training session summary."""
        s = self._session

        logger.info("\n" + "=" * 70)
        logger.info("🥋 DOJO TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"   Session: {s.session_id}")
        logger.info(f"   Duration: {s.duration_seconds:.1f}s")
        logger.info("-" * 70)
        logger.info("📊 METRICS:")
        logger.info(f"   Total Scenarios:    {s.total_scenarios}")
        logger.info(f"   Correct Decisions:  {s.correct_decisions}")
        logger.info(f"   Accuracy:           {s.accuracy:.1%}")
        logger.info(f"   Avg Dharmic Score:  {s.avg_dharmic_score:.3f}")
        logger.info("-" * 70)
        logger.info("🛡️ ATTACK DETECTION:")
        logger.info(f"   Blocked Attacks:    {s.blocked_attacks}")
        logger.info(f"   False Negatives:    {s.false_negatives} (attacks that slipped through)")
        logger.info(f"   False Positives:    {s.false_positives} (legitimate blocked)")
        logger.info(f"   Detection Rate:     {s.attack_detection_rate:.1%}")
        logger.info("-" * 70)
        logger.info("🧠 SYNAPTIC LEARNING:")
        logger.info(f"   Reinforcements:     {s.total_reinforcements}")
        logger.info(f"   Total Weight Delta: {s.total_weight_delta:+.3f}")
        logger.info("=" * 70)

        # Overall assessment
        if s.accuracy >= 0.9 and s.attack_detection_rate >= 0.95:
            logger.info("🏆 EXCELLENT: MANAS is well-trained!")
        elif s.accuracy >= 0.7 and s.attack_detection_rate >= 0.8:
            logger.info("✅ GOOD: MANAS shows solid judgment")
        elif s.attack_detection_rate < 0.8:
            logger.warning("⚠️ WARNING: Attack detection needs improvement!")
        else:
            logger.info("📈 LEARNING: More training recommended")


def run_dojo(
    workspace: Path = None,
    curriculum: str = "mixed",
    scenarios: int = 10,
    epochs: int = 1,
) -> TrainingSession:
    """
    Convenience function to run Dojo training.

    Usage:
        from vibe_core.plugins.opus_assistant.manas.dojo import run_dojo
        session = run_dojo(curriculum="attack", scenarios=20)
        print(f"Attack detection: {session.attack_detection_rate:.1%}")
    """
    workspace = workspace or Path(".")
    config = DojoConfig(
        curriculum=curriculum,
        scenarios_per_epoch=scenarios,
        max_epochs=epochs,
    )
    runner = DojoRunner(workspace, config)
    return runner.run_training()
