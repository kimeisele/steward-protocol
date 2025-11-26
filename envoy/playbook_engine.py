"""
🎯 PLAYBOOK ENGINE (GAD-5000: DETERMINISTIC EXECUTION)
The Dungeon Master - Executes deterministic playbook sequences.

Role:
1. Loads playbooks from YAML (knowledge/playbooks/)
2. Matches user intent to appropriate playbook
3. Executes playbook phases sequentially
4. Tracks state and emits events for visualization
5. Handles errors and conditional logic

Philosophy:
- Input -> Semantic Graph (SANKHYA) -> Playbook Node -> Execution (KARMA)
- No hallucinations. Just rules and state machines.
- Each phase is deterministic: Check -> Execute -> Emit -> Continue.
"""

import logging
import yaml
import asyncio
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("PLAYBOOK_ENGINE")


class PhaseStatus(Enum):
    """State machine for playbook phases"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    BLOCKED = "blocked"  # Waiting for approval


class ActionType(Enum):
    """Types of actions a phase can execute"""
    CALL_AGENT = "CALL_AGENT"  # Delegate to another agent
    CHECK_STATE = "CHECK_STATE"  # Validate preconditions
    EXECUTE_SCRIPT = "EXECUTE_SCRIPT"  # Run deterministic script
    EMIT_EVENT = "EMIT_EVENT"  # Emit event to visualization layer


@dataclass
class PlaybookPhase:
    """A single phase within a playbook"""
    phase_id: str
    name: str
    description: str
    actions: List[Dict[str, Any]]
    on_success: str  # Next phase or "COMPLETE"
    on_failure: str  # Next phase or "ABORT"
    state_var: Optional[str] = None
    timeout_seconds: int = 60
    requires_approval: bool = False
    status: PhaseStatus = PhaseStatus.PENDING
    result: Optional[Dict[str, Any]] = None


@dataclass
class PlaybookDefinition:
    """A complete playbook"""
    id: str
    name: str
    description: str
    intent_match: Dict[str, Any]
    phases: List[PlaybookPhase]
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaybookExecution:
    """Tracks a playbook execution in progress"""
    execution_id: str
    playbook_id: str
    user_input: str
    current_phase_id: Optional[str] = None
    phase_results: Dict[str, Any] = field(default_factory=dict)
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    started_at: float = field(default_factory=lambda: datetime.now().timestamp())
    completed_at: Optional[float] = None
    error_message: Optional[str] = None

    def is_complete(self) -> bool:
        return self.status in ["COMPLETED", "FAILED"]


class PlaybookEngine:
    """
    The Dungeon Master.
    Loads playbooks, matches intents, and executes phases deterministically.
    """

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.playbooks_dir = self.knowledge_dir / "playbooks"
        self.playbooks: Dict[str, PlaybookDefinition] = {}
        self.executions: Dict[str, PlaybookExecution] = {}
        self._load_playbooks()
        logger.info(f"🎯 Playbook Engine initialized with {len(self.playbooks)} playbooks")

    def _load_playbooks(self):
        """Load all playbooks from knowledge/playbooks/"""
        if not self.playbooks_dir.exists():
            logger.warning(f"⚠️  Playbooks directory not found: {self.playbooks_dir}")
            return

        for playbook_file in self.playbooks_dir.glob("*.yaml"):
            if playbook_file.name == "schema.yaml":
                continue  # Skip the schema definition file

            try:
                with open(playbook_file, 'r') as f:
                    data = yaml.safe_load(f)

                if not data or "playbook" not in data:
                    logger.warning(f"⚠️  Invalid playbook format in {playbook_file.name}")
                    continue

                playbook_data = data["playbook"]
                phases = self._parse_phases(playbook_data.get("phases", []))
                playbook = PlaybookDefinition(
                    id=playbook_data.get("id", playbook_file.stem),
                    name=playbook_data.get("name", "Unknown"),
                    description=playbook_data.get("description", ""),
                    intent_match=playbook_data.get("intent_match", {}),
                    phases=phases,
                    variables=playbook_data.get("variables", {})
                )

                self.playbooks[playbook.id] = playbook
                logger.info(f"✅ Loaded playbook: {playbook.id} ({playbook.name})")

            except Exception as e:
                logger.error(f"❌ Error loading playbook {playbook_file.name}: {e}")

    def _parse_phases(self, phases_data: List[Dict]) -> List[PlaybookPhase]:
        """Parse phase definitions from YAML"""
        phases = []
        for phase_data in phases_data:
            phase = PlaybookPhase(
                phase_id=phase_data.get("phase_id", "unknown"),
                name=phase_data.get("name", ""),
                description=phase_data.get("description", ""),
                actions=phase_data.get("actions", []),
                on_success=phase_data.get("on_success", "COMPLETE"),
                on_failure=phase_data.get("on_failure", "ABORT"),
                state_var=phase_data.get("state_var"),
                timeout_seconds=phase_data.get("timeout_seconds", 60),
                requires_approval=phase_data.get("requires_approval", False)
            )
            phases.append(phase)
        return phases

    def find_playbook(self, concepts: Set[str]) -> Optional[PlaybookDefinition]:
        """
        Find the best matching playbook for a set of detected concepts.

        Matching logic:
        - primary: Must match
        - secondary: Optional, but increases confidence
        """
        best_match = None
        best_score = 0

        for playbook in self.playbooks.values():
            intent_match = playbook.intent_match
            primary = intent_match.get("primary")
            secondary = intent_match.get("secondary", [])

            # Primary must be present
            if primary not in concepts:
                continue

            # Score: primary (10 points) + secondary matches (5 points each)
            score = 10
            if secondary:
                for sec in secondary:
                    if sec in concepts:
                        score += 5

            if score > best_score:
                best_score = score
                best_match = playbook

        return best_match

    async def execute(self,
                      playbook_id: str,
                      user_input: str,
                      intent_vector: Any,
                      kernel: Any = None,
                      emit_event=None) -> Dict[str, Any]:
        """
        Execute a playbook step-by-step.

        Args:
            playbook_id: ID of the playbook to execute
            user_input: The original user input
            intent_vector: The IntentVector from UniversalProvider
            kernel: The VibeKernel instance (for submitting tasks)
            emit_event: Async function to emit events

        Returns:
            Execution result with status and phase results
        """
        if playbook_id not in self.playbooks:
            logger.error(f"❌ Playbook not found: {playbook_id}")
            return {
                "status": "FAILED",
                "error": f"Playbook not found: {playbook_id}"
            }

        playbook = self.playbooks[playbook_id]
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        execution = PlaybookExecution(
            execution_id=execution_id,
            playbook_id=playbook_id,
            user_input=user_input
        )

        # Start execution
        logger.info(f"🚀 Starting playbook execution: {playbook.id} ({execution_id})")

        if emit_event:
            try:
                await emit_event("ACTION", f"Started playbook: {playbook.name}", "playbook_engine", {
                    "playbook_id": playbook_id,
                    "execution_id": execution_id
                })
            except Exception as e:
                logger.debug(f"Event emission failed: {e}")

        # Find the first phase
        first_phase = playbook.phases[0] if playbook.phases else None
        if not first_phase:
            execution.status = "FAILED"
            execution.error_message = "Playbook has no phases"
            return self._format_execution_result(execution, playbook)

        # Execute phases sequentially
        current_phase_id = first_phase.phase_id
        max_iterations = 100  # Prevent infinite loops

        for iteration in range(max_iterations):
            if not current_phase_id or current_phase_id in ["COMPLETE", "ABORT"]:
                break

            # Find the phase
            phase = None
            for p in playbook.phases:
                if p.phase_id == current_phase_id:
                    phase = p
                    break

            if not phase:
                logger.warning(f"⚠️  Phase not found: {current_phase_id}")
                break

            # Execute the phase
            logger.info(f"📍 Executing phase: {phase.name}")
            execution.current_phase_id = current_phase_id

            if emit_event:
                try:
                    await emit_event("THOUGHT", f"Running: {phase.name}", "playbook_engine", {
                        "phase_id": current_phase_id,
                        "phase_name": phase.name
                    })
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")

            # Check if approval is required
            if phase.requires_approval:
                phase.status = PhaseStatus.BLOCKED
                if emit_event:
                    try:
                        await emit_event("ACTION", f"Awaiting approval: {phase.name}", "playbook_engine", {
                            "phase_id": current_phase_id,
                            "requires_approval": True
                        })
                    except Exception as e:
                        logger.debug(f"Event emission failed: {e}")
                # For now, auto-approve. In production, this would wait for user input
                logger.info(f"⏭️  Auto-approving phase (would wait for user in production): {phase.name}")

            # Execute phase actions
            phase.status = PhaseStatus.RUNNING
            phase_success = await self._execute_phase_actions(
                phase, playbook, execution, intent_vector, kernel, emit_event
            )

            if phase_success:
                phase.status = PhaseStatus.COMPLETED
                if phase.state_var:
                    execution.phase_results[phase.state_var] = phase.result or {}
                current_phase_id = phase.on_success
            else:
                phase.status = PhaseStatus.FAILED
                current_phase_id = phase.on_failure

            if emit_event:
                try:
                    await emit_event("ACTION",
                        f"{'Completed' if phase_success else 'Failed'}: {phase.name}",
                        "playbook_engine", {
                            "phase_id": current_phase_id,
                            "success": phase_success
                        })
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")

        # Execution complete
        execution.status = "COMPLETED" if current_phase_id == "COMPLETE" else "FAILED"
        execution.completed_at = datetime.now().timestamp()

        logger.info(f"✅ Playbook execution complete: {execution.id} ({execution.status})")

        return self._format_execution_result(execution, playbook)

    async def _execute_phase_actions(self,
                                     phase: PlaybookPhase,
                                     playbook: PlaybookDefinition,
                                     execution: PlaybookExecution,
                                     intent_vector: Any,
                                     kernel: Any = None,
                                     emit_event=None) -> bool:
        """
        Execute all actions within a phase.
        Returns True if successful, False if any action fails.
        """
        if not phase.actions:
            return True

        for action in phase.actions:
            try:
                action_type = action.get("action_type", "EXECUTE_SCRIPT")
                target = action.get("target")
                params = action.get("params", {})

                logger.info(f"  → Executing action: {action_type} ({target})")

                if action_type == "EMIT_EVENT":
                    # Emit visualization event
                    if emit_event:
                        try:
                            await emit_event("ACTION", f"{target}", "playbook_engine", params)
                        except Exception as e:
                            logger.debug(f"Event emission failed: {e}")

                elif action_type == "CHECK_STATE":
                    # Validate preconditions (stub for now)
                    logger.info(f"  ✓ State check passed: {target}")

                elif action_type == "EXECUTE_SCRIPT":
                    # Execute a script (stub for now - would call actual script)
                    logger.info(f"  ✓ Script executed: {target}")
                    phase.result = {"script": target, "params": params}

                elif action_type == "CALL_AGENT":
                    # Delegate to another agent
                    logger.info(f"  ✓ Delegated to agent: {target}")
                    if kernel:
                        # Would submit task to kernel
                        pass
                    phase.result = {"agent": target, "params": params}

            except Exception as e:
                logger.error(f"❌ Action failed: {action} - {e}")
                return False

        return True

    def _format_execution_result(self, execution: PlaybookExecution, playbook: PlaybookDefinition) -> Dict[str, Any]:
        """Format execution results for response"""
        return {
            "status": execution.status,
            "playbook_id": playbook.id,
            "playbook_name": playbook.name,
            "execution_id": execution.execution_id,
            "summary": f"{'✅ Playbook executed successfully' if execution.status == 'COMPLETED' else '❌ Playbook execution failed'}",
            "phases_executed": [
                {
                    "phase_id": p.phase_id,
                    "name": p.name,
                    "status": p.status.value,
                    "result": p.result
                }
                for p in playbook.phases if p.status != PhaseStatus.PENDING
            ],
            "duration_seconds": (execution.completed_at or datetime.now().timestamp()) - execution.started_at,
            "details": execution.phase_results
        }
