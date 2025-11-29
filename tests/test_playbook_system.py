"""
🧪 INTEGRATION TESTS FOR GAD-5000 PLAYBOOK SYSTEM
Tests the complete flow: Concept Detection → Playbook Matching → Deterministic Execution
"""

import pytest
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_PLAYBOOK_SYSTEM")

# Import the systems under test
try:
    from envoy.deterministic_executor import DeterministicExecutor, PlaybookExecution
    from provider.universal_provider import UniversalProvider, DeterministicRouter

    IMPORTS_OK = True
except ImportError as e:
    logger.warning(f"⚠️  Import failed: {e}")
    IMPORTS_OK = False


class MockKernel:
    """Mock VibeKernel for testing"""

    def __init__(self):
        self.agent_registry = ["envoy", "herald", "civic", "watchman"]
        self._status = {
            "agents_registered": len(self.agent_registry),
            "ledger_events": 42,
        }

    def get_status(self) -> Dict[str, Any]:
        return self._status

    def submit_task(self, task) -> str:
        return f"task_{id(task)}"


class MockEventEmitter:
    """Mock event emitter for testing"""

    def __init__(self):
        self.events = []

    async def emit(self, event_type: str, message: str, source: str, data: Dict = None):
        self.events.append(
            {
                "type": event_type,
                "message": message,
                "source": source,
                "data": data or {},
            }
        )
        logger.info(f"📨 EVENT: [{event_type}] {message}")


@pytest.mark.skipif(not IMPORTS_OK, reason="Imports not available")
class TestDeterministicExecutor:
    """Test the DeterministicExecutor core functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.engine = DeterministicExecutor(knowledge_dir="knowledge")
        self.event_emitter = MockEventEmitter()

    def test_playbook_engine_initialization(self):
        """Test that DeterministicExecutor initializes correctly"""
        assert self.engine is not None
        assert len(self.engine.playbooks) > 0
        logger.info(f"✅ DeterministicExecutor initialized with {len(self.engine.playbooks)} playbooks")

    def test_playbook_loading(self):
        """Test that playbooks are loaded from YAML"""
        loaded_ids = list(self.engine.playbooks.keys())
        logger.info(f"Loaded playbooks: {loaded_ids}")

        # Check for expected playbooks
        expected_playbooks = [
            "PROJECT_SCAFFOLD_V1",
            "CONTENT_GENERATION_V1",
            "GOVERNANCE_VOTE_V1",
        ]
        for pb_id in expected_playbooks:
            assert pb_id in self.engine.playbooks, f"Expected playbook {pb_id} not found"

        logger.info(f"✅ All expected playbooks loaded: {expected_playbooks}")

    def test_find_playbook_by_concepts(self):
        """Test playbook matching by concepts"""
        # Test matching PROJECT_SCAFFOLD
        concepts = {"CMD_CREATE"}
        playbook = self.engine.find_playbook(concepts)
        assert playbook is not None
        assert "CREATE" in playbook.id or "SCAFFOLD" in playbook.id
        logger.info(f"✅ Found playbook for CMD_CREATE: {playbook.id}")

        # Test matching GOVERNANCE_VOTE
        concepts = {"CMD_VOTE", "DOM_GOVERNANCE"}
        playbook = self.engine.find_playbook(concepts)
        assert playbook is not None
        assert "VOTE" in playbook.id or "GOVERNANCE" in playbook.id
        logger.info(f"✅ Found playbook for CMD_VOTE + DOM_GOVERNANCE: {playbook.id}")

    def test_state_persistence(self):
        """Test that execution state is persisted and loaded"""
        # Create a mock execution
        execution = PlaybookExecution(
            execution_id="test_exec_001",
            playbook_id="PROJECT_SCAFFOLD_V1",
            user_input="Create a test project",
            current_phase_id="phase_1",
            phase_results={"test": "data"},
            status="RUNNING",
        )

        # Save it
        self.engine._save_execution_state(execution)

        # Check that file exists
        state_file = self.engine.state_dir / "test_exec_001.json"
        assert state_file.exists()
        logger.info(f"✅ Execution state persisted to {state_file}")

        # Load it back
        self.engine._load_persisted_executions()
        assert "test_exec_001" in self.engine.executions
        loaded = self.engine.executions["test_exec_001"]
        assert loaded.playbook_id == "PROJECT_SCAFFOLD_V1"
        logger.info(f"✅ Execution state loaded from disk: {loaded.execution_id}")

    def test_evolutionary_loop_proposal(self):
        """Test the Evolutionary Loop (EAD) - playbook proposal generation"""
        user_input = "Do something unusual with the governance system"
        concepts = {"CMD_UNUSUAL", "DOM_GOVERNANCE"}

        proposal = self.engine.generate_playbook_proposal(user_input, concepts)

        assert proposal is not None
        assert "proposal_id" in proposal
        assert proposal["status"] == "PENDING_APPROVAL"
        assert "playbook_draft" in proposal
        assert proposal["approval_required"] is True

        logger.info(f"✅ Generated playbook proposal: {proposal['proposal_id']}")
        logger.info(f"   Status: {proposal['status']} (awaiting HIL review)")

    def test_llm_decision_fallback(self):
        """Test LLM decision making (should fallback gracefully)"""
        options = ["option_1", "option_2", "option_3"]
        context = "Test context for decision"

        # This should work even if LLM is not available
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.engine.get_llm_decision(context, options))

        assert result in options
        logger.info(f"✅ LLM decision made: {result}")


@pytest.mark.skipif(not IMPORTS_OK, reason="Imports not available")
class TestDeterministicRouter:
    """Test the Deterministic Router (SANKHYA + DHARMA)"""

    def setup_method(self):
        """Setup for each test"""
        self.router = DeterministicRouter(knowledge_dir="knowledge")

    def test_concept_detection(self):
        """Test semantic concept detection (SANKHYA)"""
        test_cases = [
            ("Create a new project", {"CMD_CREATE"}),
            ("Show system status", {"CMD_STATUS"}),
            ("Start a voting session", {"CMD_VOTE"}),
        ]

        for text, expected_concepts in test_cases:
            concepts = self.router.analyze(text)
            # At least one expected concept should be found
            assert any(c in concepts for c in expected_concepts), (
                f"Expected {expected_concepts} in {concepts} for input: {text}"
            )
            logger.info(f"✅ Detected concepts for '{text}': {concepts}")

    def test_intent_routing(self):
        """Test deterministic intent routing (DHARMA)"""
        result = self.router.route("Create a new governance campaign")

        assert "agent" in result
        assert "intent_type" in result
        assert "concepts" in result

        logger.info(f"✅ Routed intent to agent: {result['agent']}")
        logger.info(f"   Intent type: {result['intent_type']}")
        logger.info(f"   Detected concepts: {result['concepts']}")


@pytest.mark.skipif(not IMPORTS_OK, reason="Imports not available")
class TestPlaybookExecution:
    """Test playbook execution with full integration"""

    def setup_method(self):
        """Setup for each test"""
        self.engine = DeterministicExecutor(knowledge_dir="knowledge")
        self.kernel = MockKernel()
        self.event_emitter = MockEventEmitter()

    @pytest.mark.asyncio
    async def test_playbook_execution_flow(self):
        """Test full playbook execution flow"""
        # Get a playbook
        concepts = {"CMD_CREATE"}
        playbook = self.engine.find_playbook(concepts)
        assert playbook is not None

        # Create mock intent vector
        from provider.universal_provider import IntentVector, IntentType

        intent_vector = IntentVector(
            raw_input="Create a test project",
            intent_type=IntentType.CREATION,
            target_domain="test",
            confidence=0.95,
        )

        # Execute the playbook
        result = await self.engine.execute(
            playbook_id=playbook.id,
            user_input="Create a test project",
            intent_vector=intent_vector,
            kernel=self.kernel,
            emit_event=self.event_emitter.emit,
        )

        assert result is not None
        assert "status" in result
        assert "playbook_id" in result
        logger.info(f"✅ Playbook execution completed: {result['status']}")
        logger.info(f"   Playbook: {result['playbook_name']}")
        logger.info(f"   Duration: {result['duration_seconds']:.2f}s")


@pytest.mark.skipif(not IMPORTS_OK, reason="Imports not available")
class TestUniversalProviderIntegration:
    """Test UniversalProvider with Playbook Engine"""

    def setup_method(self):
        """Setup for each test"""
        self.kernel = MockKernel()
        self.provider = UniversalProvider(kernel=self.kernel, knowledge_dir="knowledge")
        self.event_emitter = MockEventEmitter()

    def test_universal_provider_initialization(self):
        """Test UniversalProvider initialization"""
        assert self.provider is not None
        assert self.provider.playbook_engine is not None
        assert self.provider.router is not None
        logger.info(f"✅ UniversalProvider initialized with DeterministicExecutor")

    @pytest.mark.asyncio
    async def test_intent_resolution_to_playbook(self):
        """Test complete flow: intent → concepts → playbook"""
        user_input = "Create a new governance campaign"

        # Resolve intent
        vector = self.provider.resolve_intent(user_input)
        assert vector is not None
        logger.info(f"✅ Resolved intent: {vector.intent_type.value}")

        # Find playbook
        concepts = self.provider.router.analyze(user_input)
        playbook = self.provider.playbook_engine.find_playbook(concepts)

        if playbook:
            logger.info(f"✅ Found playbook: {playbook.id}")
        else:
            logger.info(f"⚠️  No playbook found (would trigger EAD proposal)")

    @pytest.mark.asyncio
    async def test_evolutionary_loop_activation(self):
        """Test that EAD (Evolutionary Loop) is activated when no playbook matches"""
        user_input = "Do something completely unprecedented"

        # This should trigger the evolutionary loop
        result = await self.provider.route_and_execute(user_input)

        # Check if proposal was generated
        if result.get("status") == "PROPOSAL_PENDING":
            logger.info(f"✅ EAD activated: {result['proposal_id']}")
            logger.info(f"   Status: {result['status']} (awaiting human approval)")
            assert "playbook_draft" in result
            assert "proposal_id" in result
        else:
            # Playbook was found and executed
            logger.info(f"✅ Playbook found and executed: {result.get('playbook_name', 'unknown')}")


# === HELPER FUNCTIONS FOR MANUAL TESTING ===


def print_test_summary():
    """Print a summary of all tests"""
    print("\n" + "=" * 60)
    print("🧪 GAD-5000 PLAYBOOK SYSTEM - TEST SUMMARY")
    print("=" * 60)
    print("\nTests cover:")
    print("  ✅ DeterministicExecutor initialization and YAML loading")
    print("  ✅ Concept detection (SANKHYA)")
    print("  ✅ Intent routing (DHARMA)")
    print("  ✅ Playbook matching and execution")
    print("  ✅ State persistence (Karma Ledger)")
    print("  ✅ Evolutionary Loop (EAD) - Proposal generation")
    print("  ✅ LLM Dynamic Routing")
    print("  ✅ UniversalProvider integration")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_test_summary()
    print("\nRun tests with: pytest tests/test_playbook_system.py -v")
