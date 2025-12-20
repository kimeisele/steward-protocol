"""
OPUS-158: Infrastructure Genesis Tests

Tests for the Stadtamt Service - auto-generates GAD-000 compliant infrastructure.

"Jedes Haus bekommt einen Briefkasten. Jede Straße ein Schild."
"Every house gets a mailbox. Every street a sign."
"""

import json
from pathlib import Path

import pytest

from vibe_core.plugins.opus_assistant.manas.cortex.genesis import (
    InfrastructureClassifier,
    InfrastructureGenerator,
    ModuleType,
)
from vibe_core.plugins.opus_assistant.manas.cortex.genesis.generator import (
    GenerationResult,
)

# =============================================================================
# SECTION 1: Basic Import and Initialization Tests
# =============================================================================


class TestGenesisBasic:
    """Basic genesis tests."""

    def test_imports(self):
        """Genesis components should be importable."""
        assert InfrastructureClassifier is not None
        assert InfrastructureGenerator is not None
        assert ModuleType is not None

    def test_classifier_initializes(self, tmp_path):
        """InfrastructureClassifier should initialize with workspace."""
        classifier = InfrastructureClassifier(workspace=tmp_path)
        assert classifier is not None

    def test_generator_initializes(self, tmp_path):
        """InfrastructureGenerator should initialize with workspace."""
        generator = InfrastructureGenerator(workspace=tmp_path)
        assert generator is not None


# =============================================================================
# SECTION 2: ModuleType Tests
# =============================================================================


class TestModuleType:
    """Tests for ModuleType enum."""

    def test_module_types_exist(self):
        """All expected module types should exist."""
        assert ModuleType.PLUGIN
        assert ModuleType.ANALYZER
        assert ModuleType.SENSE
        assert ModuleType.ACTION
        assert ModuleType.SECTION
        assert ModuleType.UNKNOWN

    def test_unknown_is_default(self):
        """UNKNOWN should be usable as fallback."""
        assert ModuleType.UNKNOWN.name == "UNKNOWN"


# =============================================================================
# SECTION 3: Classifier Tests
# =============================================================================


class TestInfrastructureClassifier:
    """Tests for InfrastructureClassifier."""

    @pytest.fixture
    def classifier(self, tmp_path):
        """Create a classifier for testing."""
        return InfrastructureClassifier(workspace=tmp_path)

    def test_classify_plugin_path(self, classifier):
        """Plugin paths should classify as PLUGIN."""
        path = Path("vibe_core/plugins/my_plugin")
        result = classifier.classify(path, is_directory=True)
        assert result == ModuleType.PLUGIN

    def test_classify_analyzer_path(self, classifier):
        """Analyzer paths should classify as ANALYZER."""
        path = Path("vibe_core/plugins/opus_assistant/manas/analyzers/my_analyzer")
        result = classifier.classify(path, is_directory=True)
        assert result == ModuleType.ANALYZER

    def test_classify_sense_path(self, classifier):
        """Sense files should classify as SENSE."""
        path = Path("vibe_core/plugins/opus_assistant/manas/cortex/my_sense.py")
        result = classifier.classify_file(path)
        assert result == ModuleType.SENSE

    def test_classify_action_path(self, classifier):
        """Action files should classify as ACTION."""
        path = Path("vibe_core/plugins/opus_assistant/manas/cortex/my_action.py")
        result = classifier.classify_file(path)
        assert result == ModuleType.ACTION

    def test_classify_section_path(self, classifier):
        """Phoenix section paths should classify as SECTION."""
        path = Path("vibe_core/phoenix/sections/my_section")
        result = classifier.classify(path, is_directory=True)
        assert result == ModuleType.SECTION

    def test_classify_unknown_path(self, classifier):
        """Unknown paths should classify as UNKNOWN."""
        path = Path("random/unknown/path")
        result = classifier.classify(path, is_directory=True)
        assert result == ModuleType.UNKNOWN

    def test_classify_ignores_pycache(self, classifier):
        """__pycache__ should be ignored."""
        path = Path("vibe_core/plugins/__pycache__")
        result = classifier.classify(path, is_directory=True)
        assert result == ModuleType.UNKNOWN

    def test_classify_ignores_git(self, classifier):
        """.git should be ignored."""
        path = Path(".git/objects")
        result = classifier.classify(path, is_directory=True)
        assert result == ModuleType.UNKNOWN


# =============================================================================
# SECTION 4: Generator Tests
# =============================================================================


class TestInfrastructureGenerator:
    """Tests for InfrastructureGenerator."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator for testing."""
        return InfrastructureGenerator(workspace=tmp_path)

    def test_generate_plugin_creates_init(self, generator, tmp_path):
        """Generate plugin should create __init__.py."""
        plugin_path = tmp_path / "test_plugin"
        plugin_path.mkdir()

        result = generator.generate(plugin_path, ModuleType.PLUGIN)

        assert result.success
        assert "__init__.py" in result.created_files
        assert (plugin_path / "__init__.py").exists()

    def test_generate_plugin_creates_manifest(self, generator, tmp_path):
        """Generate plugin should create manifest.json."""
        plugin_path = tmp_path / "test_plugin"
        plugin_path.mkdir()

        result = generator.generate(plugin_path, ModuleType.PLUGIN)

        assert "manifest.json" in result.created_files
        assert (plugin_path / "manifest.json").exists()

        # Verify manifest content
        manifest = json.loads((plugin_path / "manifest.json").read_text())
        assert manifest["type"] == "plugin"
        assert manifest["id"] == "test_plugin"

    def test_generate_plugin_creates_main(self, generator, tmp_path):
        """Generate plugin should create plugin_main.py."""
        plugin_path = tmp_path / "test_plugin"
        plugin_path.mkdir()

        result = generator.generate(plugin_path, ModuleType.PLUGIN)

        assert "plugin_main.py" in result.created_files
        assert (plugin_path / "plugin_main.py").exists()

    def test_generate_does_not_overwrite(self, generator, tmp_path):
        """Generator should not overwrite existing files."""
        plugin_path = tmp_path / "test_plugin"
        plugin_path.mkdir()

        # Create existing __init__.py
        init_path = plugin_path / "__init__.py"
        init_path.write_text("# Existing content")

        result = generator.generate(plugin_path, ModuleType.PLUGIN)

        # __init__.py should be skipped
        assert "__init__.py" in result.skipped_files
        assert init_path.read_text() == "# Existing content"

    def test_generate_section_creates_manifest(self, generator, tmp_path):
        """Generate section should create manifest.json."""
        section_path = tmp_path / "test_section"
        section_path.mkdir()

        result = generator.generate(section_path, ModuleType.SECTION)

        assert result.success
        assert "manifest.json" in result.created_files

        manifest = json.loads((section_path / "manifest.json").read_text())
        assert manifest["type"] == "phoenix_section"

    def test_generate_unknown_returns_error(self, generator, tmp_path):
        """Generate UNKNOWN should return error."""
        path = tmp_path / "unknown"
        path.mkdir()

        result = generator.generate(path, ModuleType.UNKNOWN)

        assert not result.success
        assert len(result.errors) > 0


# =============================================================================
# SECTION 5: GenerationResult Tests
# =============================================================================


class TestGenerationResult:
    """Tests for GenerationResult dataclass."""

    def test_result_success_when_no_errors(self, tmp_path):
        """Result should be success when no errors."""
        result = GenerationResult(
            path=tmp_path,
            module_type=ModuleType.PLUGIN,
            created_files={"test.py": tmp_path / "test.py"},
        )
        assert result.success is True

    def test_result_failure_when_errors(self, tmp_path):
        """Result should be failure when errors."""
        result = GenerationResult(
            path=tmp_path,
            module_type=ModuleType.PLUGIN,
            errors=["Something went wrong"],
        )
        assert result.success is False

    def test_files_created_count(self, tmp_path):
        """files_created_count should match created_files length."""
        result = GenerationResult(
            path=tmp_path,
            module_type=ModuleType.PLUGIN,
            created_files={
                "a.py": tmp_path / "a.py",
                "b.py": tmp_path / "b.py",
            },
        )
        assert result.files_created_count == 2


# =============================================================================
# SECTION 6: Dry Run Tests
# =============================================================================


class TestDryRun:
    """Tests for dry run mode."""

    def test_dry_run_does_not_create_files(self, tmp_path):
        """Dry run should not create actual files."""
        generator = InfrastructureGenerator(workspace=tmp_path, dry_run=True)

        plugin_path = tmp_path / "test_plugin"
        plugin_path.mkdir()

        result = generator.generate(plugin_path, ModuleType.PLUGIN)

        # Result should report files as created
        assert result.files_created_count > 0

        # But files should not actually exist
        assert not (plugin_path / "__init__.py").exists()
        assert not (plugin_path / "manifest.json").exists()


# =============================================================================
# SECTION 7: Integration Tests
# =============================================================================


class TestGenesisIntegration:
    """Integration tests for the full genesis flow."""

    def test_classify_then_generate(self, tmp_path):
        """Full flow: classify path then generate infrastructure."""
        classifier = InfrastructureClassifier(workspace=tmp_path)
        generator = InfrastructureGenerator(workspace=tmp_path)

        # Create a plugin directory structure
        plugin_path = tmp_path / "vibe_core" / "plugins" / "new_plugin"
        plugin_path.mkdir(parents=True)

        # Classify
        module_type = classifier.classify(Path("vibe_core/plugins/new_plugin"), is_directory=True)
        assert module_type == ModuleType.PLUGIN

        # Generate
        result = generator.generate(plugin_path, module_type)
        assert result.success
        assert result.files_created_count >= 3  # __init__, manifest, plugin_main

    def test_expected_files_for_plugin(self):
        """Classifier should report expected files for plugin type."""
        classifier = InfrastructureClassifier()
        expected = classifier.get_expected_files(ModuleType.PLUGIN)

        assert "__init__.py" in expected
        assert "manifest.json" in expected
        assert "plugin_main.py" in expected
