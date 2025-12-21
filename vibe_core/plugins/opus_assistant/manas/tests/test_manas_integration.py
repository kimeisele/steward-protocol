"""
MANAS Integration Tests - PROOF OF LIFE

OPUS-032: The Cognitive Kernel

These tests verify that MANAS:
1. Initializes correctly
2. Generates intents from system state
3. Manages intent buffer
4. Respects rate limits
5. Remembers past actions
6. Learns from outcomes

"Ungetesteter Code ist nur eine Meinung."
"""

from datetime import datetime
from pathlib import Path


class TestMemoryStore:
    """Tests for MANAS MemoryStore - Learning from the Past."""

    def test_memory_store_initialization(self, tmp_path: Path):
        """Memory store should initialize with empty memories."""
        from vibe_core.plugins.opus_assistant.manas.memory_store import MemoryStore

        store = MemoryStore(workspace=tmp_path)

        assert store._memories == []
        assert store._workspace == tmp_path

    def test_memory_store_remember(self, tmp_path: Path):
        """Memory store should persist memories."""
        from vibe_core.plugins.opus_assistant.manas.memory_store import (
            MemoryEntry,
            MemoryStore,
        )

        store = MemoryStore(workspace=tmp_path)

        entry = MemoryEntry(
            intent_type="test_intent",
            intent_description="Test description",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        store.remember(entry)

        assert len(store._memories) == 1
        assert store._memories[0].intent_type == "test_intent"

    def test_memory_store_success_rate(self, tmp_path: Path):
        """Memory store should calculate success rates."""
        from vibe_core.plugins.opus_assistant.manas.memory_store import (
            MemoryEntry,
            MemoryStore,
        )

        store = MemoryStore(workspace=tmp_path)

        # Add 3 successes, 1 failure
        for i in range(3):
            store.remember(
                MemoryEntry(
                    intent_type="cleanup",
                    intent_description=f"Cleanup {i}",
                    timestamp=datetime.utcnow().isoformat(),
                    outcome="success",
                )
            )

        store.remember(
            MemoryEntry(
                intent_type="cleanup",
                intent_description="Cleanup failed",
                timestamp=datetime.utcnow().isoformat(),
                outcome="failed",
            )
        )

        rate = store.get_success_rate("cleanup")
        assert rate == 0.75  # 3/4

    def test_memory_store_cooldown(self, tmp_path: Path):
        """Memory store should detect cooldown after failure."""
        from vibe_core.plugins.opus_assistant.manas.memory_store import (
            MemoryEntry,
            MemoryStore,
        )

        store = MemoryStore(workspace=tmp_path)

        # Add recent failure
        store.remember(
            MemoryEntry(
                intent_type="risky_action",
                intent_description="Risky action",
                timestamp=datetime.utcnow().isoformat(),
                outcome="failed",
            )
        )

        assert store.is_in_cooldown("risky_action") is True
        assert store.is_in_cooldown("other_action") is False

    def test_memory_store_rejected_detection(self, tmp_path: Path):
        """Memory store should detect recently rejected intents."""
        from vibe_core.plugins.opus_assistant.manas.memory_store import (
            MemoryEntry,
            MemoryStore,
        )

        store = MemoryStore(workspace=tmp_path)

        store.remember(
            MemoryEntry(
                intent_type="unwanted",
                intent_description="User rejected",
                timestamp=datetime.utcnow().isoformat(),
                outcome="rejected",
                feedback="Not needed",
            )
        )

        assert store.was_recently_rejected("unwanted") is True
        assert store.was_recently_rejected("wanted") is False

    def test_memory_store_persistence(self, tmp_path: Path):
        """Memory store should persist and reload."""
        from vibe_core.plugins.opus_assistant.manas.memory_store import (
            MemoryEntry,
            MemoryStore,
        )

        store1 = MemoryStore(workspace=tmp_path)
        store1.remember(
            MemoryEntry(
                intent_type="persistent",
                intent_description="Should survive reload",
                timestamp=datetime.utcnow().isoformat(),
                outcome="success",
            )
        )

        # Create new store (should load from disk)
        store2 = MemoryStore(workspace=tmp_path)

        assert len(store2._memories) == 1
        assert store2._memories[0].intent_type == "persistent"


class TestIntentGenerator:
    """Tests for MANAS IntentGenerator - Proactive Thinking."""

    def test_intent_generator_initialization(self, tmp_path: Path):
        """Intent generator should initialize with analyzers."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            IntentGenerator,
        )

        gen = IntentGenerator(workspace=tmp_path)

        assert gen._workspace == tmp_path
        assert len(gen._analyzers) > 0

    async def test_intent_generation_empty_context(self, tmp_path: Path):
        """Intent generator should handle empty context."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            IntentGenerator,
        )

        gen = IntentGenerator(workspace=tmp_path)

        # With empty context and no git repo, should return empty or minimal intents
        intents = await gen.generate_intents({})

        # Should not crash
        assert isinstance(intents, list)

    def test_intent_priority_enum(self):
        """Intent priorities should have correct values."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            IntentPriority,
        )

        assert IntentPriority.LOW.value == "low"
        assert IntentPriority.MEDIUM.value == "medium"
        assert IntentPriority.HIGH.value == "high"
        assert IntentPriority.CRITICAL.value == "critical"

    def test_intent_risk_enum(self):
        """Intent risks should have correct values."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentRisk

        assert IntentRisk.SAFE.value == "safe"
        assert IntentRisk.LOW.value == "low"
        assert IntentRisk.MEDIUM.value == "medium"
        assert IntentRisk.HIGH.value == "high"

    def test_intent_creation(self):
        """Intents should serialize correctly."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
            IntentPriority,
            IntentRisk,
        )

        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test Intent",
            description="A test intent",
            reasoning="For testing purposes",
            priority=IntentPriority.HIGH,
            risk=IntentRisk.LOW,
            auto_executable=True,
        )

        data = intent.to_dict()

        assert data["id"] == "test_001"
        assert data["title"] == "Test Intent"
        assert data["priority"] == "high"
        assert data["risk"] == "low"
        assert data["auto_executable"] is True


class TestCognitiveKernel:
    """Tests for MANAS CognitiveKernel - The Mind."""

    def test_cognitive_kernel_initialization(self, tmp_path: Path):
        """Cognitive kernel should initialize with all components."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )

        config = ManasConfig(
            thinking_interval_minutes=60,
            idle_threshold_minutes=30,
            auto_execute_safe=False,
        )

        kernel = CognitiveKernel(workspace=tmp_path, config=config)

        assert kernel._memory is not None
        assert kernel._intent_generator is not None
        assert kernel._config == config

    def test_cognitive_kernel_think_first_time(self, tmp_path: Path):
        """First think() should always execute."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )

        config = ManasConfig(thinking_interval_minutes=60)
        kernel = CognitiveKernel(workspace=tmp_path, config=config)

        # First think should execute (no rate limit)
        intents = kernel.think(context={}, force=False)

        # Should have recorded thought time
        assert kernel._last_thought_time is not None
        assert isinstance(intents, list)

    def test_cognitive_kernel_rate_limit(self, tmp_path: Path):
        """Think should respect rate limit."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )

        config = ManasConfig(
            thinking_interval_minutes=60,
            idle_threshold_minutes=1000,  # Very high so we don't trigger idle
        )
        kernel = CognitiveKernel(workspace=tmp_path, config=config)

        # First think
        kernel.think(context={}, force=False)
        first_thought_time = kernel._last_thought_time

        # Second think should be rate limited
        intents = kernel.think(context={}, force=False)

        # Should not have updated thought time
        assert kernel._last_thought_time == first_thought_time
        assert intents == []

    def test_cognitive_kernel_force_think(self, tmp_path: Path):
        """Force=True should bypass rate limit."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )

        config = ManasConfig(thinking_interval_minutes=60)
        kernel = CognitiveKernel(workspace=tmp_path, config=config)

        # First think
        kernel.think(context={}, force=False)
        first_thought_time = kernel._last_thought_time

        # Force second think
        kernel.think(context={}, force=True)

        # Should have updated thought time
        assert kernel._last_thought_time > first_thought_time

    def test_cognitive_kernel_intent_buffer(self, tmp_path: Path):
        """Intent buffer should be accessible."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
        )

        kernel = CognitiveKernel(workspace=tmp_path)

        buffer = kernel.get_intent_buffer_for_opus()

        assert "pending" in buffer
        assert "recent_executed" in buffer
        assert "total_pending" in buffer

    def test_cognitive_kernel_approve_reject(self, tmp_path: Path):
        """Intents should be approvable/rejectable."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            IntentBufferEntry,
        )
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
        )

        kernel = CognitiveKernel(workspace=tmp_path)

        # Manually add an intent
        intent = Intent(
            id="manual_001",
            intent_type="manual_test",
            title="Manual Test",
            description="Manually added for testing",
            reasoning="Test purposes",
        )
        entry = IntentBufferEntry(intent=intent)
        kernel._buffer.add(entry)

        # Reject it
        success = kernel.reject_intent("manual_001", "Testing rejection")

        assert success is True
        assert entry.status == "rejected"

    def test_cognitive_kernel_memory_integration(self, tmp_path: Path):
        """Cognitive kernel should use memory for decisions."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
        )

        kernel = CognitiveKernel(workspace=tmp_path)

        # Record a failed intent type
        kernel._memory.record_intent_outcome(
            intent_type="cleanup_stale_branches",
            description="Test cleanup",
            outcome="failed",
            feedback="Git error",
        )

        # That intent type should now be in cooldown
        assert kernel._memory.is_in_cooldown("cleanup_stale_branches") is True


class TestManasCircuitIntegration:
    """Tests for MANAS circuit integration."""

    def test_manas_awakening_circuit_exists(self):
        """MANAS awakening circuit should exist."""
        from pathlib import Path

        circuit_path = Path(
            "/home/user/steward-protocol/vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml"
        )

        assert circuit_path.exists(), "MANAS awakening circuit not found"

    def test_manas_awakening_circuit_valid_yaml(self):
        """MANAS awakening circuit should be valid YAML."""
        from pathlib import Path

        import yaml

        circuit_path = Path(
            "/home/user/steward-protocol/vibe_core/plugins/opus_assistant/circuits/manas_awakening.yaml"
        )

        with open(circuit_path) as f:
            data = yaml.safe_load(f)

        assert "circuit" in data
        assert data["circuit"]["id"] == "MANAS_AWAKENING"
        assert "triggers" in data["circuit"]
        assert "states" in data["circuit"]


class TestManasKernelTickIntegration:
    """Tests for MANAS integration with kernel_tick.py."""

    def test_manas_import_available(self):
        """MANAS should be importable from kernel_tick module."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import MANAS_AVAILABLE

        # Import should work regardless of whether MANAS is available
        assert isinstance(MANAS_AVAILABLE, bool)

    def test_manas_methods_in_handler(self):
        """Kernel tick handler should have MANAS methods."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        # Check that methods exist
        assert hasattr(KernelTickHandler, "_manas_check_rate_limit")
        assert hasattr(KernelTickHandler, "_manas_generate_intents")
        assert hasattr(KernelTickHandler, "_manas_auto_execute_safe")
        assert hasattr(KernelTickHandler, "_manas_update_buffer")
        assert hasattr(KernelTickHandler, "_manas_approve_intent")
        assert hasattr(KernelTickHandler, "_manas_reject_intent")
        assert hasattr(KernelTickHandler, "_manas_get_buffer")


class TestManasEndToEnd:
    """End-to-end tests for the complete MANAS flow."""

    def test_full_thought_cycle(self, tmp_path: Path):
        """Complete thought cycle should work end-to-end."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            ManasConfig,
        )

        config = ManasConfig(
            thinking_interval_minutes=0,  # No rate limit for test
            idle_threshold_minutes=0,
            auto_execute_safe=False,
        )

        kernel = CognitiveKernel(workspace=tmp_path, config=config)

        # Execute thought cycle
        intents = kernel.think(context={}, force=True)

        # Should have recorded the thought
        assert kernel._last_thought_time is not None

        # Buffer should be accessible
        buffer = kernel.get_intent_buffer_for_opus()
        assert "pending" in buffer

    def test_memory_survives_restart(self, tmp_path: Path):
        """Memory should survive kernel restart."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
        )

        # First kernel records memory
        kernel1 = CognitiveKernel(workspace=tmp_path)
        kernel1._memory.record_intent_outcome(
            intent_type="persistent_test",
            description="Should survive",
            outcome="success",
        )

        # Second kernel should have the memory
        kernel2 = CognitiveKernel(workspace=tmp_path)
        rate = kernel2._memory.get_success_rate("persistent_test")

        assert rate == 1.0  # 100% success (1 out of 1)

    def test_intent_buffer_persistence(self, tmp_path: Path):
        """Intent buffer should persist across restarts."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            IntentBufferEntry,
        )
        from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

        # First kernel adds intent
        kernel1 = CognitiveKernel(workspace=tmp_path)
        intent = Intent(
            id="persist_001",
            intent_type="persistent",
            title="Should Persist",
            description="Test persistence",
            reasoning="Testing",
        )
        kernel1._buffer.add(IntentBufferEntry(intent=intent))
        # IntentBuffer auto-saves on add()

        # Second kernel should have it
        kernel2 = CognitiveKernel(workspace=tmp_path)
        pending = kernel2.get_pending_intents()

        assert len(pending) >= 1
        assert any(i.id == "persist_001" for i in pending)


# Run with: pytest -xvs vibe_core/plugins/opus_assistant/manas/tests/test_manas_integration.py
