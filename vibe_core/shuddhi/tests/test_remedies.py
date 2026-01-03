"""
Tests for individual Shuddhi remedies.

OPUS-307: Tests that each remedy correctly transforms code.
"""

import tempfile
from pathlib import Path

import pytest

from vibe_core.protocols.shuddhi import ShuddhiStatus
from vibe_core.shuddhi.engine import ShuddhiEngine


class TestSubprocessTimeoutRemedy:
    """Tests for subprocess_timeout remedy."""

    def test_adds_timeout_to_subprocess_run(self):
        """Should add timeout=30 to subprocess.run()."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
import subprocess
result = subprocess.run(['ls'])
""")
            f.flush()
            result = engine.purify(Path(f.name), "subprocess_timeout")

        assert result.status == ShuddhiStatus.PURIFIED
        assert "timeout=30" in result.purified_code

    def test_adds_timeout_to_subprocess_call(self):
        """Should add timeout to subprocess.call()."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
import subprocess
subprocess.call(['echo', 'hello'])
""")
            f.flush()
            result = engine.purify(Path(f.name), "subprocess_timeout")

        assert result.status == ShuddhiStatus.PURIFIED
        assert "timeout=" in result.purified_code

    def test_skips_if_timeout_exists(self):
        """Should skip if timeout already specified."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
import subprocess
subprocess.run(['ls'], timeout=60)
""")
            f.flush()
            result = engine.purify(Path(f.name), "subprocess_timeout")

        assert result.status == ShuddhiStatus.SKIPPED


class TestSilentFailureRemedy:
    """Tests for silent_failure remedy."""

    def test_transforms_bare_except_pass(self):
        """Should transform bare except:pass to proper logging."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
try:
    do_something()
except:
    pass
""")
            f.flush()
            result = engine.purify(Path(f.name), "silent_failure")

        assert result.status == ShuddhiStatus.PURIFIED
        assert "logger" in result.purified_code or "Exception" in result.purified_code

    def test_skips_proper_exception_handling(self):
        """Should skip if exception is already logged."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
try:
    do_something()
except Exception as e:
    logger.error(f"Failed: {e}")
""")
            f.flush()
            result = engine.purify(Path(f.name), "silent_failure")

        assert result.status == ShuddhiStatus.SKIPPED


class TestGetInstanceAntipatternRemedy:
    """Tests for get_instance_antipattern remedy."""

    def test_transforms_known_singleton(self):
        """Should transform X.get_instance() to ServiceRegistry.get()."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
from vibe_core.genesis import GenesisService
genesis = GenesisService.get_instance()
""")
            f.flush()
            result = engine.purify(Path(f.name), "get_instance_antipattern")

        assert result.status == ShuddhiStatus.PURIFIED
        assert "ServiceRegistry" in result.purified_code

    def test_adds_service_registry_import(self):
        """Should add ServiceRegistry import if needed."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
from vibe_core.genesis import GenesisService
def do_work():
    genesis = GenesisService.get_instance()
""")
            f.flush()
            result = engine.purify(Path(f.name), "get_instance_antipattern")

        assert result.status == ShuddhiStatus.PURIFIED
        assert "from vibe_core.di import ServiceRegistry" in result.purified_code


class TestDirectRegistryInstantiationRemedy:
    """Tests for direct_registry_instantiation remedy."""

    def test_transforms_registry_instantiation(self):
        """Should transform ToolRegistry() to ServiceRegistry.get()."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
registry = ToolRegistry()
""")
            f.flush()
            result = engine.purify(Path(f.name), "direct_registry_instantiation")

        assert result.status == ShuddhiStatus.PURIFIED
        assert "ServiceRegistry.get" in result.purified_code


class TestEngineIntegration:
    """Integration tests for ShuddhiEngine."""

    def test_engine_can_heal_expected_rules(self):
        """Engine should be able to heal all expected rule types."""
        engine = ShuddhiEngine()

        expected_rules = [
            "subprocess_timeout",
            "silent_failure",
            "get_instance_antipattern",
            "direct_registry_instantiation",
            "iterdir_discovery",
            "path_scanning_discovery",
        ]

        for rule_id in expected_rules:
            assert engine.can_heal(rule_id), f"Engine cannot heal {rule_id}"

    def test_engine_list_remedies(self):
        """Engine should list all registered remedies."""
        engine = ShuddhiEngine()
        remedies = engine.list_remedies()

        assert isinstance(remedies, list)
        assert len(remedies) >= 6
        assert "subprocess_timeout" in remedies

    def test_engine_purify_unknown_rule(self):
        """Engine should fail gracefully for unknown rules."""
        engine = ShuddhiEngine()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')")
            f.flush()
            result = engine.purify(Path(f.name), "unknown_rule_xyz")

        assert result.status == ShuddhiStatus.FAILED
        assert "No remedy registered" in result.message

    def test_engine_purify_nonexistent_file(self):
        """Engine should fail gracefully for nonexistent files."""
        engine = ShuddhiEngine()
        result = engine.purify(Path("/nonexistent/file.py"), "subprocess_timeout")

        assert result.status == ShuddhiStatus.FAILED
        assert "not found" in result.message.lower()


class TestRemedyProtocolCompliance:
    """Tests for RemedyProtocol compliance."""

    def test_all_remedies_have_requirements(self):
        """All remedies must define requirements."""
        from vibe_core.shuddhi.remedy_loader import discover_remedies

        remedies = discover_remedies()

        for rule_id, remedy_class in remedies.items():
            instance = remedy_class()
            # requirements can be property or method
            if callable(getattr(instance, "requirements", None)):
                requirements = instance.requirements()
            else:
                requirements = instance.requirements
            assert isinstance(requirements, list), f"Remedy {rule_id} requirements must return a list"

    def test_all_remedies_track_applied_state(self):
        """All remedies must track applied state."""
        from vibe_core.shuddhi.remedy_loader import discover_remedies

        remedies = discover_remedies()

        for rule_id, remedy_class in remedies.items():
            instance = remedy_class()
            assert hasattr(instance, "applied")
            assert instance.applied is False, "Fresh remedy should have applied=False"
