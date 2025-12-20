"""
OPUS-159: Genesis Service Tests

Tests for the vibe_core Stadtamt - central infrastructure genesis.

"Feinste Lasagne, vegetarisch, ohne Zwiebeln, beste Bio-Zutaten."
"""

import json
from pathlib import Path

import pytest

from vibe_core.genesis import (
    BuildResult,
    ComplianceBureau,
    ComplianceReport,
    GenesisResult,
    GenesisService,
    InfrastructureBuilder,
    ModuleType,
    TemplateRegistry,
)

# =============================================================================
# SECTION 1: Import and Initialization Tests
# =============================================================================


class TestGenesisImports:
    """Test that all genesis components are importable."""

    def test_import_genesis_service(self):
        """GenesisService should be importable."""
        assert GenesisService is not None

    def test_import_compliance_bureau(self):
        """ComplianceBureau should be importable."""
        assert ComplianceBureau is not None

    def test_import_template_registry(self):
        """TemplateRegistry should be importable."""
        assert TemplateRegistry is not None

    def test_import_infrastructure_builder(self):
        """InfrastructureBuilder should be importable."""
        assert InfrastructureBuilder is not None

    def test_import_types(self):
        """All types should be importable."""
        assert ModuleType is not None
        assert BuildResult is not None
        assert ComplianceReport is not None
        assert GenesisResult is not None


class TestGenesisServiceInit:
    """Test GenesisService initialization."""

    def test_service_initializes(self, tmp_path):
        """GenesisService should initialize with workspace."""
        service = GenesisService(workspace=tmp_path)
        assert service is not None

    def test_singleton_pattern(self, tmp_path):
        """GenesisService should use singleton pattern."""
        GenesisService.reset_instance()
        s1 = GenesisService.get_instance(workspace=tmp_path)
        s2 = GenesisService.get_instance()
        assert s1 is s2
        GenesisService.reset_instance()

    def test_has_components(self, tmp_path):
        """GenesisService should have all components."""
        service = GenesisService(workspace=tmp_path)
        assert service.compliance is not None
        assert service.templates is not None
        assert service.builder is not None


# =============================================================================
# SECTION 2: Module Type Tests
# =============================================================================


class TestModuleType:
    """Tests for ModuleType enum."""

    def test_all_types_exist(self):
        """All expected module types should exist."""
        assert ModuleType.PLUGIN
        assert ModuleType.CARTRIDGE
        assert ModuleType.SECTION
        assert ModuleType.ANALYZER
        assert ModuleType.SENSE
        assert ModuleType.ACTION
        assert ModuleType.UNKNOWN

    def test_from_string(self):
        """from_string should convert string to ModuleType."""
        assert ModuleType.from_string("plugin") == ModuleType.PLUGIN
        assert ModuleType.from_string("CARTRIDGE") == ModuleType.CARTRIDGE
        assert ModuleType.from_string("unknown_xyz") == ModuleType.UNKNOWN


# =============================================================================
# SECTION 3: Path Classification Tests
# =============================================================================


class TestPathClassification:
    """Tests for path classification."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a service for testing."""
        return GenesisService(workspace=tmp_path)

    def test_classify_plugin_path(self, service):
        """Plugin paths should be classified correctly."""
        path = Path("vibe_core/plugins/my_plugin")
        assert service.classify_path(path) == ModuleType.PLUGIN

    def test_classify_cartridge_path(self, service):
        """Cartridge paths should be classified correctly."""
        path = Path("vibe_core/cartridges/system/my_agent")
        assert service.classify_path(path) == ModuleType.CARTRIDGE

    def test_classify_section_path(self, service):
        """Section paths should be classified correctly."""
        path = Path("vibe_core/phoenix/sections/my_section")
        assert service.classify_path(path) == ModuleType.SECTION

    def test_classify_sense_path(self, service):
        """Sense paths should be classified correctly."""
        path = Path("plugins/opus_assistant/manas/cortex/my_sense.py")
        assert service.classify_path(path) == ModuleType.SENSE

    def test_classify_action_path(self, service):
        """Action paths should be classified correctly."""
        path = Path("plugins/opus_assistant/manas/cortex/my_action.py")
        assert service.classify_path(path) == ModuleType.ACTION

    def test_classify_pycache_ignored(self, service):
        """__pycache__ should be classified as UNKNOWN."""
        path = Path("vibe_core/plugins/__pycache__")
        assert service.classify_path(path) == ModuleType.UNKNOWN

    def test_classify_unknown_path(self, service):
        """Unknown paths should be classified as UNKNOWN."""
        path = Path("random/path/here")
        assert service.classify_path(path) == ModuleType.UNKNOWN


# =============================================================================
# SECTION 4: Compliance Bureau Tests
# =============================================================================


class TestComplianceBureau:
    """Tests for ComplianceBureau."""

    @pytest.fixture
    def bureau(self, tmp_path):
        """Create a compliance bureau for testing."""
        return ComplianceBureau(workspace=tmp_path)

    def test_audit_nonexistent_path(self, bureau, tmp_path):
        """Audit of nonexistent path should fail."""
        path = tmp_path / "nonexistent"
        report = bureau.audit(path, ModuleType.PLUGIN)
        assert not report.passed

    def test_audit_empty_plugin(self, bureau, tmp_path):
        """Audit of empty plugin should list missing files."""
        plugin_path = tmp_path / "empty_plugin"
        plugin_path.mkdir()

        report = bureau.audit(plugin_path, ModuleType.PLUGIN)

        assert not report.passed
        assert "__init__.py" in report.missing_files
        assert "manifest.json" in report.missing_files

    def test_audit_complete_plugin(self, bureau, tmp_path):
        """Audit of complete plugin should pass."""
        plugin_path = tmp_path / "complete_plugin"
        plugin_path.mkdir()

        # Create required files
        (plugin_path / "__init__.py").write_text("# init")
        (plugin_path / "plugin_main.py").write_text("class CompletePluginPlugin: pass")
        (plugin_path / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "complete_plugin",
                    "name": "Complete Plugin",
                    "version": "1.0.0",
                }
            )
        )

        report = bureau.audit(plugin_path, ModuleType.PLUGIN)
        assert report.passed

    def test_quick_check_empty(self, bureau, tmp_path):
        """Quick check of empty dir should return False."""
        empty_path = tmp_path / "empty"
        empty_path.mkdir()
        assert not bureau.quick_check(empty_path, ModuleType.PLUGIN)

    def test_get_missing_files(self, bureau, tmp_path):
        """get_missing should return list of missing files."""
        plugin_path = tmp_path / "partial"
        plugin_path.mkdir()
        (plugin_path / "__init__.py").write_text("# init")

        missing = bureau.get_missing(plugin_path, ModuleType.PLUGIN)
        assert "manifest.json" in missing
        assert "plugin_main.py" in missing
        assert "__init__.py" not in missing


# =============================================================================
# SECTION 5: Template Registry Tests
# =============================================================================


class TestTemplateRegistry:
    """Tests for TemplateRegistry."""

    def test_singleton_pattern(self):
        """TemplateRegistry should use singleton pattern."""
        r1 = TemplateRegistry.get_instance()
        r2 = TemplateRegistry.get_instance()
        assert r1 is r2

    def test_has_plugin_templates(self):
        """Registry should have plugin templates."""
        registry = TemplateRegistry.get_instance()
        templates = registry.get_templates(ModuleType.PLUGIN)
        assert "__init__.py" in templates
        assert "manifest.json" in templates
        assert "plugin_main.py" in templates

    def test_has_cartridge_templates(self):
        """Registry should have cartridge templates."""
        registry = TemplateRegistry.get_instance()
        templates = registry.get_templates(ModuleType.CARTRIDGE)
        assert "__init__.py" in templates
        assert "cartridge_main.py" in templates
        assert "cartridge.yaml" in templates

    def test_template_render(self):
        """Templates should render with context."""
        registry = TemplateRegistry.get_instance()
        template = registry.get_template(ModuleType.PLUGIN, "__init__.py")
        assert template is not None

        rendered = template.render(
            {
                "name": "Test Plugin",
                "class_name": "TestPlugin",
            }
        )
        assert "Test Plugin" in rendered
        assert "TestPluginPlugin" in rendered


# =============================================================================
# SECTION 6: Infrastructure Builder Tests
# =============================================================================


class TestInfrastructureBuilder:
    """Tests for InfrastructureBuilder."""

    @pytest.fixture
    def builder(self, tmp_path):
        """Create a builder for testing."""
        return InfrastructureBuilder(workspace=tmp_path)

    def test_build_plugin(self, builder, tmp_path):
        """Builder should create all plugin files."""
        plugin_path = tmp_path / "new_plugin"
        plugin_path.mkdir()

        result = builder.build(plugin_path, ModuleType.PLUGIN)

        assert result.success
        assert result.files_created_count >= 3
        assert (plugin_path / "__init__.py").exists()
        assert (plugin_path / "manifest.json").exists()
        assert (plugin_path / "plugin_main.py").exists()

    def test_build_does_not_overwrite(self, builder, tmp_path):
        """Builder should not overwrite existing files."""
        plugin_path = tmp_path / "existing_plugin"
        plugin_path.mkdir()

        # Create existing file
        init_path = plugin_path / "__init__.py"
        init_path.write_text("# Existing content")

        result = builder.build(plugin_path, ModuleType.PLUGIN)

        assert "__init__.py" in result.skipped_files
        assert init_path.read_text() == "# Existing content"

    def test_repair_missing_only(self, builder, tmp_path):
        """Repair should only create missing files."""
        plugin_path = tmp_path / "partial_plugin"
        plugin_path.mkdir()

        # Create one file
        (plugin_path / "__init__.py").write_text("# Existing")

        result = builder.repair(
            plugin_path,
            ModuleType.PLUGIN,
            missing_files=["manifest.json"],
        )

        assert "manifest.json" in result.created_files
        assert "__init__.py" not in result.created_files

    def test_dry_run_no_files(self, tmp_path):
        """Dry run should not create actual files."""
        builder = InfrastructureBuilder(workspace=tmp_path, dry_run=True)
        plugin_path = tmp_path / "dry_run_plugin"
        plugin_path.mkdir()

        result = builder.build(plugin_path, ModuleType.PLUGIN)

        assert result.files_created_count > 0
        assert not (plugin_path / "__init__.py").exists()


# =============================================================================
# SECTION 7: GenesisService Integration Tests
# =============================================================================


class TestGenesisServiceIntegration:
    """Integration tests for GenesisService."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a service for testing."""
        return GenesisService(workspace=tmp_path)

    def test_ensure_compliance_empty_plugin(self, service, tmp_path):
        """ensure_compliance should create missing files."""
        plugin_path = tmp_path / "vibe_core" / "plugins" / "test_plugin"
        plugin_path.mkdir(parents=True)

        result = service.ensure_compliance(plugin_path, ModuleType.PLUGIN)

        assert result.success
        assert result.files_created
        assert (plugin_path / "__init__.py").exists()
        assert (plugin_path / "manifest.json").exists()

    def test_ensure_compliance_already_compliant(self, service, tmp_path):
        """ensure_compliance should return early if already compliant."""
        plugin_path = tmp_path / "vibe_core" / "plugins" / "compliant_plugin"
        plugin_path.mkdir(parents=True)

        # Create all required files
        (plugin_path / "__init__.py").write_text("# init")
        (plugin_path / "plugin_main.py").write_text("class CompliantPluginPlugin: pass")
        (plugin_path / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "compliant_plugin",
                    "name": "Compliant",
                    "version": "1.0.0",
                }
            )
        )

        result = service.ensure_compliance(plugin_path, ModuleType.PLUGIN)

        assert result.success
        assert len(result.files_created) == 0

    def test_scaffold_new_plugin(self, service, tmp_path):
        """scaffold_new should create complete plugin."""
        plugin_path = tmp_path / "vibe_core" / "plugins" / "scaffolded"
        plugin_path.mkdir(parents=True)

        result = service.scaffold_new(
            plugin_path,
            ModuleType.PLUGIN,
            {"name": "My Scaffolded Plugin", "description": "A test plugin"},
        )

        assert result.success
        assert result.build_result.files_created_count >= 3

        # Check manifest content
        manifest = json.loads((plugin_path / "manifest.json").read_text())
        assert manifest["name"] == "My Scaffolded Plugin"

    def test_quick_check_integration(self, service, tmp_path):
        """quick_check should work with classify_path."""
        plugin_path = tmp_path / "vibe_core" / "plugins" / "quick_test"
        plugin_path.mkdir(parents=True)

        # Empty - should fail
        assert not service.quick_check(plugin_path)

        # Add required files
        (plugin_path / "__init__.py").write_text("# init")
        (plugin_path / "plugin_main.py").write_text("class QuickTestPlugin: pass")
        (plugin_path / "manifest.json").write_text("{}")

        # Now should pass
        assert service.quick_check(plugin_path)


# =============================================================================
# SECTION 8: Cartridge Scaffolding Tests
# =============================================================================


class TestCartridgeScaffolding:
    """Tests for cartridge (agent) scaffolding."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a service for testing."""
        return GenesisService(workspace=tmp_path)

    def test_scaffold_cartridge(self, service, tmp_path):
        """scaffold_new should create complete cartridge."""
        cartridge_path = tmp_path / "vibe_core" / "cartridges" / "system" / "my_agent"
        cartridge_path.mkdir(parents=True)

        result = service.scaffold_new(
            cartridge_path,
            ModuleType.CARTRIDGE,
            {"name": "My Agent", "domain": "testing"},
        )

        assert result.success
        assert (cartridge_path / "__init__.py").exists()
        assert (cartridge_path / "cartridge_main.py").exists()
        assert (cartridge_path / "cartridge.yaml").exists()
        assert (cartridge_path / "steward.json").exists()

    def test_cartridge_has_oath(self, service, tmp_path):
        """Scaffolded cartridge should have OathMixin."""
        cartridge_path = tmp_path / "vibe_core" / "cartridges" / "system" / "oath_agent"
        cartridge_path.mkdir(parents=True)

        service.scaffold_new(cartridge_path, ModuleType.CARTRIDGE)

        main_content = (cartridge_path / "cartridge_main.py").read_text()
        assert "OathMixin" in main_content
        assert "oath_sworn" in main_content
