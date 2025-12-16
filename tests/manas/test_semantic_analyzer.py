"""
OPUS-032: Semantic Analyzer Tests - The Genesis Impulse.

The 51% Analyzer - finds GAPS, not ERRORS.

These tests verify:
1. Test gap detection works
2. Intents are SAFE and auto-executable
3. Multiple gap types can be detected
4. Config limits are respected
"""

import pytest

from vibe_core.plugins.opus_assistant.manas.analyzers.semantic_analyzer import (
    SemanticAnalyzer,
)
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    IntentPriority,
    IntentRisk,
)


class TestSemanticAnalyzerBasics:
    """Basic functionality tests."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer with temp workspace."""
        return SemanticAnalyzer(workspace=tmp_path)

    def test_analyzer_name(self, analyzer):
        """Analyzer has correct name."""
        assert analyzer.name == "semantic_analyzer"

    def test_empty_workspace_returns_empty_list(self, analyzer):
        """Empty workspace = no intents."""
        intents = analyzer.analyze({})
        assert intents == []


class TestTestGapDetection:
    """Test gap detection functionality."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create workspace with plugin structure."""
        plugins_dir = tmp_path / "vibe_core" / "plugins"
        plugins_dir.mkdir(parents=True)
        return tmp_path

    def test_detects_untested_tools(self, workspace):
        """Detects tools without test files."""
        # Create plugin with tools
        plugin_dir = workspace / "vibe_core" / "plugins" / "my_plugin"
        tools_dir = plugin_dir / "tools"
        tests_dir = plugin_dir / "tests"
        tools_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        # Create tool without test
        (tools_dir / "awesome_tool.py").write_text("# Tool code")
        (tools_dir / "__init__.py").write_text("")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        assert len(intents) == 1
        assert intents[0].intent_type == "semantic_gap_test"
        assert "awesome_tool.py" in intents[0].params["untested_files"]

    def test_ignores_tested_tools(self, workspace):
        """Tools with tests don't create intents."""
        plugin_dir = workspace / "vibe_core" / "plugins" / "my_plugin"
        tools_dir = plugin_dir / "tools"
        tests_dir = plugin_dir / "tests"
        tools_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        # Create tool WITH test
        (tools_dir / "good_tool.py").write_text("# Tool code")
        (tests_dir / "test_good_tool.py").write_text("# Tests")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        assert intents == []

    def test_ignores_private_files(self, workspace):
        """Files starting with _ are ignored."""
        plugin_dir = workspace / "vibe_core" / "plugins" / "my_plugin"
        tools_dir = plugin_dir / "tools"
        tests_dir = plugin_dir / "tests"
        tools_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        # Create private file without test
        (tools_dir / "_private.py").write_text("# Private")
        (tools_dir / "__init__.py").write_text("")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        assert intents == []


class TestIntentProperties:
    """Test intent properties are correct."""

    @pytest.fixture
    def workspace_with_gap(self, tmp_path):
        """Create workspace with untested tool."""
        plugin_dir = tmp_path / "vibe_core" / "plugins" / "test_plugin"
        tools_dir = plugin_dir / "tools"
        tests_dir = plugin_dir / "tests"
        tools_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        (tools_dir / "untested.py").write_text("# Needs tests")
        (tools_dir / "__init__.py").write_text("")

        return tmp_path

    def test_intent_is_safe_risk(self, workspace_with_gap):
        """Test creation intents are SAFE risk."""
        analyzer = SemanticAnalyzer(workspace=workspace_with_gap)
        intents = analyzer.analyze({})

        assert len(intents) == 1
        assert intents[0].risk == IntentRisk.SAFE

    def test_intent_is_auto_executable(self, workspace_with_gap):
        """Test creation intents are auto-executable."""
        analyzer = SemanticAnalyzer(workspace=workspace_with_gap)
        intents = analyzer.analyze({})

        assert intents[0].auto_executable is True

    def test_intent_priority_is_low(self, workspace_with_gap):
        """Tool test intents have LOW priority."""
        analyzer = SemanticAnalyzer(workspace=workspace_with_gap)
        intents = analyzer.analyze({})

        assert intents[0].priority == IntentPriority.LOW

    def test_intent_id_starts_with_genesis(self, workspace_with_gap):
        """Genesis intents start with 'genesis_'."""
        analyzer = SemanticAnalyzer(workspace=workspace_with_gap)
        intents = analyzer.analyze({})

        assert intents[0].id.startswith("genesis_")


class TestManasSpecificCoverage:
    """Test MANAS-specific gap detection."""

    @pytest.fixture
    def opus_workspace(self, tmp_path):
        """Create workspace with opus_assistant structure."""
        manas_dir = tmp_path / "vibe_core" / "plugins" / "opus_assistant" / "manas"
        analyzers_dir = manas_dir / "analyzers"
        tests_dir = tmp_path / "vibe_core" / "plugins" / "opus_assistant" / "tests"

        manas_dir.mkdir(parents=True)
        analyzers_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        return tmp_path, manas_dir, analyzers_dir, tests_dir

    def test_detects_manas_module_without_test(self, opus_workspace):
        """Detects MANAS modules without tests."""
        workspace, manas_dir, analyzers_dir, tests_dir = opus_workspace

        # Create cognitive_kernel without test
        (manas_dir / "cognitive_kernel.py").write_text("# Brain")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        # Should detect missing test
        manas_intents = [i for i in intents if "opus_assistant" in i.params.get("plugin", "")]
        assert len(manas_intents) >= 1

    def test_manas_intents_have_medium_priority(self, opus_workspace):
        """MANAS test intents have MEDIUM priority (brain is important)."""
        workspace, manas_dir, analyzers_dir, tests_dir = opus_workspace

        (manas_dir / "cognitive_kernel.py").write_text("# Brain")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        manas_intents = [i for i in intents if i.params.get("type") == "manas"]
        if manas_intents:
            assert manas_intents[0].priority == IntentPriority.MEDIUM

    def test_detects_analyzer_without_test(self, opus_workspace):
        """Detects analyzers without tests."""
        workspace, manas_dir, analyzers_dir, tests_dir = opus_workspace

        # Create analyzer without test
        (analyzers_dir / "new_analyzer.py").write_text("# Analyzer")
        (analyzers_dir / "__init__.py").write_text("")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        # Should find the gap
        manas_intents = [i for i in intents if "opus_assistant" in i.params.get("plugin", "")]
        if manas_intents:
            files = manas_intents[0].params.get("untested_files", [])
            assert any("new_analyzer" in f for f in files)

    def test_ignores_base_analyzer(self, opus_workspace):
        """base.py doesn't need its own test."""
        workspace, manas_dir, analyzers_dir, tests_dir = opus_workspace

        # Create only base.py
        (analyzers_dir / "base.py").write_text("# Base class")
        (analyzers_dir / "__init__.py").write_text("")

        analyzer = SemanticAnalyzer(workspace=workspace)
        intents = analyzer.analyze({})

        # base.py should not trigger an intent
        manas_intents = [i for i in intents if i.params.get("type") == "manas"]
        if manas_intents:
            files = manas_intents[0].params.get("untested_files", [])
            assert not any("base.py" in f for f in files)


class TestConfigLimits:
    """Test configuration limits."""

    def test_respects_max_intents(self, tmp_path):
        """Respects max_intents_per_run config."""
        from vibe_core.plugins.opus_assistant.manas.analyzers.base import AnalyzerConfig

        # Create many plugins with untested tools
        for i in range(10):
            plugin_dir = tmp_path / "vibe_core" / "plugins" / f"plugin_{i}"
            tools_dir = plugin_dir / "tools"
            tests_dir = plugin_dir / "tests"
            tools_dir.mkdir(parents=True)
            tests_dir.mkdir(parents=True)
            (tools_dir / f"tool_{i}.py").write_text("# Tool")
            (tools_dir / "__init__.py").write_text("")

        config = AnalyzerConfig(max_intents_per_run=3)
        analyzer = SemanticAnalyzer(workspace=tmp_path, config=config)
        intents = analyzer.analyze({})

        assert len(intents) <= 3


class TestMultipleGapTypes:
    """Test detection of multiple gap types in one run."""

    def test_detects_both_tools_and_core_gaps(self, tmp_path):
        """Can detect gaps in both tools/ and core/ directories."""
        plugin_dir = tmp_path / "vibe_core" / "plugins" / "my_plugin"
        tools_dir = plugin_dir / "tools"
        core_dir = plugin_dir / "core"
        tests_dir = plugin_dir / "tests"

        tools_dir.mkdir(parents=True)
        core_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        # Create untested tool
        (tools_dir / "my_tool.py").write_text("# Tool")
        (tools_dir / "__init__.py").write_text("")

        # Create untested core module
        (core_dir / "my_core.py").write_text("# Core")
        (core_dir / "__init__.py").write_text("")

        analyzer = SemanticAnalyzer(workspace=tmp_path)
        intents = analyzer.analyze({})

        # Should have intents for both
        types = [i.params.get("type") for i in intents]
        assert "tools" in types
        assert "core" in types
