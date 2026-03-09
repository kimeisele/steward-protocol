"""
Tests for OPUS-054: SUTRA (The Thread) - Wiki Documentation Weaver.

Sanskrit: Sutra = Thread, String, Aphorism.

These tests verify:
1. WikiPage and WikiContext data models
2. SutraWeaver page generation
3. WikiSync git operations
4. SutraOrchestrator workflow
5. VEDA intent routing
6. JNANA handler integration
"""

import tempfile
from pathlib import Path
import tempfile
from pathlib import Path
from typing import List, Optional, Union
import pytest
from vibe_core.protocols.system_shell import ShellProtocol, ShellResult


@pytest.fixture(autouse=True)
def _fast_sutra_context(monkeypatch):
    """Keep SUTRA tests deterministic and fast by stubbing heavyweight scanners."""
    from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver

    def fake_gather_mandala(self, ctx):
        if not self._workspace.exists():
            return
        ctx.agents.extend(
            [
                {"id": "analyst", "name": "Analyst", "domain": "RESEARCH", "version": "1.0.0", "capabilities": ["git_analysis"], "tier": "system"},
                {"id": "builder", "name": "Builder", "domain": "OPERATIONS", "version": "1.0.0", "capabilities": ["delivery", "verification"], "tier": "system"},
            ]
        )
        ctx.domains.update({"RESEARCH": ["analyst"], "OPERATIONS": ["builder"]})
        ctx.capabilities.update({"analyst": ["git_analysis"], "builder": ["delivery", "verification"]})

    def fake_gather_akasha(self, ctx):
        if not self._workspace.exists():
            return
        ctx.node_count = 12
        ctx.edge_count = 21
        ctx.constraint_count = 3
        ctx.knowledge_summary = "RESEARCH -> OPERATIONS -> DELIVERY"

    def fake_gather_module(self, ctx):
        if not self._workspace.exists():
            return
        ctx.modules.extend(
            [
                {"name": "governance", "files": 4, "path": "vibe_core/governance"},
                {"name": "protocols", "files": 7, "path": "vibe_core/protocols"},
            ]
        )
        ctx.repo_python_files = 11
        ctx.repo_markdown_files = 8
        ctx.node_manifest_count = 2
        ctx.repo_areas = [{"name": "governance", "python_files": 4}, {"name": "protocols", "python_files": 7}]
        ctx.cartridge_families = [{"name": "system", "agents": 2}]

    monkeypatch.setattr(SutraWeaver, "_gather_mandala_context", fake_gather_mandala)
    monkeypatch.setattr(SutraWeaver, "_gather_akasha_context", fake_gather_akasha)
    monkeypatch.setattr(SutraWeaver, "_gather_module_context", fake_gather_module)

# =============================================================================
# SECTION 1: DATA MODEL TESTS
# =============================================================================


class TestWikiPageType:
    """Tests for WikiPageType enum."""

    def test_all_page_types_exist(self):
        """Verify all expected page types are defined."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPageType

        assert WikiPageType.HOME.value == "Home"
        assert WikiPageType.START_HERE.value == "Start-Here"
        assert WikiPageType.INDEX.value == "Index"
        assert WikiPageType.CONSTITUTION.value == "Constitution"
        assert WikiPageType.GOVERNANCE_INDEX.value == "Governance-Index"
        assert WikiPageType.GOVERNANCE_ATLAS.value == "Governance-Atlas"
        assert WikiPageType.AGI_MANIFESTO.value == "AGI-Manifesto"
        assert WikiPageType.STEWARDSHIP.value == "Stewardship"
        assert WikiPageType.PROTOCOLS.value == "Protocols"
        assert WikiPageType.ARCHITECTURE.value == "Architecture"
        assert WikiPageType.KERNEL.value == "Kernel"
        assert WikiPageType.CANONICAL_ATLAS.value == "Canonical-Atlas"
        assert WikiPageType.PROTOCOL_ATLAS.value == "Protocol-Atlas"
        assert WikiPageType.FEDERATION_REGISTRY.value == "Federation-Registry"
        assert WikiPageType.PANTHEON == WikiPageType.FEDERATION_REGISTRY
        assert WikiPageType.LAW == WikiPageType.CONSTITUTION
        assert WikiPageType.MAP.value == "Map"
        assert WikiPageType.SIDEBAR.value == "_Sidebar"
        assert WikiPageType.FOOTER.value == "_Footer"

    def test_page_types_are_valid_filenames(self):
        """Verify page type values are valid for filenames."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPageType

        for pt in WikiPageType:
            # Should not contain invalid characters
            assert "/" not in pt.value
            assert "\\" not in pt.value
            assert ":" not in pt.value


class TestWikiPage:
    """Tests for WikiPage dataclass."""

    def test_create_wiki_page(self):
        """Test creating a WikiPage."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPage, WikiPageType

        page = WikiPage(
            page_type=WikiPageType.HOME,
            title="Home",
            content="# Welcome",
        )

        assert page.page_type == WikiPageType.HOME
        assert page.title == "Home"
        assert page.content == "# Welcome"
        assert page.generated_at is not None

    def test_filename_property(self):
        """Test filename property returns correct .md file."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPage, WikiPageType

        page = WikiPage(
            page_type=WikiPageType.FEDERATION_REGISTRY,
            title="Test",
            content="content",
        )

        assert page.filename == "Federation-Registry.md"

    def test_filename_uses_declared_wiki_name_when_present(self):
        """Test filename honors a declared wiki_name override."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPage, WikiPageType

        page = WikiPage(page_type=WikiPageType.MAP, title="System Map", wiki_name="System-Map", content="content")

        assert page.filename == "System-Map.md"

    def test_filename_for_sidebar(self):
        """Test sidebar has underscore prefix."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPage, WikiPageType

        page = WikiPage(
            page_type=WikiPageType.SIDEBAR,
            title="Sidebar",
            content="nav",
        )

        assert page.filename == "_Sidebar.md"


class TestWikiContext:
    """Tests for WikiContext dataclass."""

    def test_create_wiki_context_defaults(self):
        """Test creating WikiContext with defaults."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiContext

        ctx = WikiContext()

        assert ctx.system_name == "STEWARD Protocol"
        assert ctx.version == "1.0.0"
        assert ctx.agents == []
        assert ctx.capabilities == {}
        assert ctx.domains == {}
        assert ctx.node_count == 0

    def test_wiki_context_with_data(self):
        """Test WikiContext with populated data."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiContext

        ctx = WikiContext(
            agents=[{"id": "test", "name": "Test Agent"}],
            node_count=42,
            modules=[{"name": "core", "files": 10}],
        )

        assert len(ctx.agents) == 1
        assert ctx.node_count == 42
        assert len(ctx.modules) == 1


class TestSutraResult:
    """Tests for SutraResult dataclass."""

    def test_create_success_result(self):
        """Test creating a successful result."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraResult, WikiPage, WikiPageType

        pages = [
            WikiPage(page_type=WikiPageType.HOME, title="Home", content="# Home"),
        ]

        result = SutraResult(
            success=True,
            pages_generated=pages,
            pages_synced=["Home.md"],
            wiki_url="https://github.com/test/wiki",
        )

        assert result.success is True
        assert len(result.pages_generated) == 1
        assert len(result.pages_synced) == 1
        assert result.wiki_url is not None

    def test_create_failure_result(self):
        """Test creating a failure result."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraResult

        result = SutraResult(
            success=False,
            errors=["Clone failed", "Permission denied"],
        )

        assert result.success is False
        assert len(result.errors) == 2

    def test_to_chat_response_success(self):
        """Test formatting successful result for chat."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraResult, WikiPage, WikiPageType

        pages = [
            WikiPage(page_type=WikiPageType.HOME, title="Home", content="# Home content"),
        ]

        result = SutraResult(success=True, pages_generated=pages)
        response = result.to_chat_response()

        assert "SUTRA" in response
        assert "Home.md" in response
        assert "1" in response  # Pages generated count

    def test_to_chat_response_failure(self):
        """Test formatting failure result for chat."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraResult

        result = SutraResult(success=False, errors=["Test error"])
        response = result.to_chat_response()

        assert "failed" in response.lower()
        assert "Test error" in response


# =============================================================================
# SECTION 2: SUTRA WEAVER TESTS
# =============================================================================


class TestSutraWeaver:
    """Tests for SutraWeaver class."""

    def test_weaver_initialization(self):
        """Test weaver initializes with workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver

        weaver = SutraWeaver()
        assert weaver._workspace is not None

    def test_weaver_with_custom_workspace(self):
        """Test weaver with custom workspace path."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver

        custom_path = Path("/tmp/test_workspace")
        weaver = SutraWeaver(workspace=custom_path)
        assert weaver._workspace == custom_path

    def test_gather_context_returns_context(self):
        """Test gather_context returns WikiContext."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext

        weaver = SutraWeaver()
        ctx = weaver.gather_context()

        assert isinstance(ctx, WikiContext)
        assert ctx.timestamp != ""

    def test_weave_home_page(self):
        """Test weaving Home page."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        ctx = WikiContext(
            system_name="Test System",
            version="2.0.0",
            agents=[{"id": "a1", "name": "Agent1"}],
            node_count=10,
        )

        page = weaver.weave_page(WikiPageType.HOME, ctx)

        assert page.page_type == WikiPageType.HOME
        assert "Test System" in page.content
        assert "2.0.0" in page.content
        assert "Home" in page.title

    def test_weave_federation_registry_page(self):
        """Test weaving federation registry page."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        ctx = WikiContext(
            agents=[
                {"id": "analyst", "name": "Analyst", "capabilities": ["git_analysis"]},
            ],
            domains={"RESEARCH": ["analyst"]},
            capabilities={"analyst": ["git_analysis"]},
        )

        page = weaver.weave_page(WikiPageType.FEDERATION_REGISTRY, ctx)

        assert page.page_type == WikiPageType.FEDERATION_REGISTRY
        assert "Agent Registry" in page.content
        assert "agent" in page.content.lower() or "Agent" in page.content

    def test_weave_constitution_page(self):
        """Test weaving canonical Constitution page."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        ctx = WikiContext()

        page = weaver.weave_page(WikiPageType.CONSTITUTION, ctx)

        assert page.page_type == WikiPageType.CONSTITUTION
        assert "Source: `CONSTITUTION.md`" in page.content
        assert "CONSTITUTION" in page.content or "Constitution" in page.content

    def test_weave_index_page_rewrites_bound_links(self):
        """Test bound markdown rewrites links to the declared surface when possible."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        page = weaver.weave_page(WikiPageType.INDEX, WikiContext())

        assert page.page_type == WikiPageType.INDEX
        assert "[README.md](Start-Here)" in page.content
        assert "[CONSTITUTION.md](Constitution)" in page.content
        assert "[docs/architecture/ARCHITECTURE.md](Architecture)" in page.content

    def test_weave_canonical_atlas_page(self):
        """Test weaving an automated atlas page from registry metadata."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        page = weaver.weave_page(WikiPageType.CANONICAL_ATLAS, WikiContext())

        assert page.page_type == WikiPageType.CANONICAL_ATLAS
        assert "Published Surface Coverage" in page.content
        assert "[Steward Model](Stewardship)" in page.content
        assert "docs/steward" in page.content

    def test_weave_governance_index_page(self):
        """Test weaving governance index page."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        page = weaver.weave_page(WikiPageType.GOVERNANCE_INDEX, WikiContext())

        assert page.page_type == WikiPageType.GOVERNANCE_INDEX
        assert "[[Constitution]]" in page.content
        assert "Governance Overview" in page.content
        assert "contracts.py" in page.content
        assert "__init__.py" not in page.content

    def test_weave_map_page(self):
        """Test weaving Map (architecture) page."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        ctx = WikiContext(
            node_count=50,
            edge_count=100,
            constraint_count=10,
            modules=[{"name": "core", "files": 5, "path": "vibe_core/core"}],
            repo_python_files=25,
            repo_markdown_files=9,
            node_manifest_count=3,
            repo_areas=[{"name": "core", "python_files": 25}],
            cartridge_families=[{"name": "system", "agents": 3}],
        )

        page = weaver.weave_page(WikiPageType.MAP, ctx)

        assert page.page_type == WikiPageType.MAP
        assert "50" in page.content  # node_count
        assert "System Map" in page.content
        assert "Repository Snapshot" in page.content

    def test_weave_sidebar(self):
        """Test weaving sidebar."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        ctx = WikiContext()

        page = weaver.weave_page(WikiPageType.SIDEBAR, ctx)

        assert page.page_type == WikiPageType.SIDEBAR
        assert "[[Home]]" in page.content
        assert "[[Constitution]]" in page.content
        assert "[[Governance-Index|Governance Overview]]" in page.content
        assert "[[Federation-Registry|Agent Registry]]" in page.content
        assert "### Runtime Surface" in page.content

    def test_weave_footer(self):
        """Test weaving footer."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiContext, WikiPageType

        weaver = SutraWeaver()
        ctx = WikiContext(timestamp="2024-01-01 00:00 UTC")

        page = weaver.weave_page(WikiPageType.FOOTER, ctx)

        assert page.page_type == WikiPageType.FOOTER
        assert "SUTRA" in page.content

    def test_weave_all_pages(self):
        """Test weaving all pages at once."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver, WikiPageType

        weaver = SutraWeaver()
        pages = weaver.weave_all()

        # Should have all page types
        page_types = {p.page_type for p in pages}
        for pt in WikiPageType:
            assert pt in page_types


# =============================================================================
# SECTION 3: WIKI SYNC TESTS
# =============================================================================


# =============================================================================
# SECTION 3: WIKI SYNC TESTS (PROTOCOL COMPLIANT)
# =============================================================================


class StubShell:
    """
    YAMARAJA COMPLIANT: Stub implementation of ShellProtocol.
    """

    def __init__(self):
        self.commands: List[List[str]] = []
        self.responses: dict = {}  # map command[0] or full command string to ShellResult
        self.default_response = ShellResult(stdout="", stderr="", returncode=0)

    def run(
        self,
        command: List[str],
        cwd: Optional[Union[str, Path]] = None,
        check: bool = False,
        env: Optional[dict] = None,
    ) -> ShellResult:
        self.commands.append(command)

        # Simple matching for tests
        cmd_str = " ".join(command)
        if command[:3] == ["git", "remote", "get-url"] and "git remote get-url" in self.responses:
            res = self.responses["git remote get-url"]
        elif cmd_str in self.responses:
            res = self.responses[cmd_str]
        elif command[0] in self.responses:  # match by executable/verb logic?
            # Specific logic for git remote get-url
            if command[:3] == ["git", "remote", "get-url"]:
                res = self.responses.get("git remote get-url", self.default_response)
            else:
                res = self.responses.get(command[0], self.default_response)
        else:
            res = self.default_response

        if check and not res.success:
            raise SystemError(f"StubShell: Command failed: {cmd_str}")

        return res


class TestWikiSync:
    """Tests for WikiSync class using StubShell."""

    def test_sync_initialization(self):
        """Test WikiSync initializes."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiSync

        sync = WikiSync()
        assert sync._workspace is not None
        assert sync._wiki_dir is None

    def test_get_wiki_url(self):
        """Test getting wiki URL from git remote."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiSync

        stub = StubShell()
        stub.responses["git remote get-url"] = ShellResult(
            stdout="https://github.com/user/repo.git\n", stderr="", returncode=0
        )

        sync = WikiSync(shell_executor=stub)
        url = sync.get_wiki_url()

        assert url == "https://github.com/user/repo.wiki.git"

    def test_get_wiki_url_without_git_extension(self):
        """Test getting wiki URL when origin doesn't have .git."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiSync

        stub = StubShell()
        stub.responses["git remote get-url"] = ShellResult(
            stdout="https://github.com/user/repo\n", stderr="", returncode=0
        )

        sync = WikiSync(shell_executor=stub)
        url = sync.get_wiki_url()

        assert url == "https://github.com/user/repo.wiki.git"

    def test_write_pages(self):
        """Test writing pages to wiki directory (FileSystem test)."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPage, WikiPageType, WikiSync

        with tempfile.TemporaryDirectory() as tmpdir:
            stub = StubShell()
            sync = WikiSync(shell_executor=stub)
            pages = [
                WikiPage(page_type=WikiPageType.HOME, title="Home", content="# Test Home"),
            ]

            written = sync.write_pages(pages, Path(tmpdir))

            assert written == 1
            assert (Path(tmpdir) / "Home.md").exists()
            assert "# Test Home" in (Path(tmpdir) / "Home.md").read_text()

    def test_write_pages_creates_all_files(self):
        """Test writing multiple pages."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPage, WikiPageType, WikiSync

        with tempfile.TemporaryDirectory() as tmpdir:
            stub = StubShell()
            sync = WikiSync(shell_executor=stub)
            pages = [
                WikiPage(page_type=WikiPageType.HOME, title="Home", content="Home content"),
                WikiPage(page_type=WikiPageType.FEDERATION_REGISTRY, title="Registry", content="Registry content"),
                WikiPage(page_type=WikiPageType.SIDEBAR, title="Sidebar", content="Sidebar"),
            ]

            written = sync.write_pages(pages, Path(tmpdir))

            assert written == 3
            assert (Path(tmpdir) / "Home.md").exists()
            assert (Path(tmpdir) / "Federation-Registry.md").exists()
            assert (Path(tmpdir) / "_Sidebar.md").exists()


# =============================================================================
# SECTION 4: SUTRA ORCHESTRATOR TESTS
# =============================================================================


class TestSutraOrchestrator:
    """Tests for SutraOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator

        orch = SutraOrchestrator()
        assert orch._weaver is not None
        assert orch._sync is not None

    def test_generate_all_pages(self):
        """Test generating all wiki pages."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator, WikiPageType

        orch = SutraOrchestrator()
        pages = orch.generate()

        assert len(pages) == len(WikiPageType)

    def test_export_surface_metadata(self):
        """Test machine-readable surface metadata export."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator

        orch = SutraOrchestrator()
        payload = orch.export_surface_metadata()

        assert payload["kind"] == "wiki_surface_registry"
        assert payload["page_count"] >= 1
        assert any(page["wiki_name"] == "Home" for page in payload["pages"])
        assert payload["system_metrics"]["repo_python_files"] == 11

    def test_generate_specific_pages(self):
        """Test generating specific page types."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator, WikiPageType

        orch = SutraOrchestrator()
        pages = orch.generate(page_types=[WikiPageType.HOME, WikiPageType.MAP])

        assert len(pages) == 2
        page_types = {p.page_type for p in pages}
        assert WikiPageType.HOME in page_types
        assert WikiPageType.MAP in page_types

    def test_preview_home_page(self):
        """Test previewing home page."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator, WikiPageType

        orch = SutraOrchestrator()
        content = orch.preview(WikiPageType.HOME)

        assert isinstance(content, str)
        assert len(content) > 0
        assert "STEWARD" in content or "Home" in content


# =============================================================================
# SECTION 5: VEDA INTEGRATION TESTS
# =============================================================================


class TestVedaSutraIntegration:
    """Tests for VEDA pipeline integration with SUTRA."""

    def test_sutra_intent_exists(self):
        """Test SUTRA intent is defined in VedaIntent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        assert VedaIntent.SUTRA.value == "sutra"
        assert VedaIntent.WIKI.value == "wiki"

    def test_sutra_keywords_defined(self):
        """Test SUTRA keywords are in INTENT_KEYWORDS."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, VedaIntent

        keywords = Artha.INTENT_KEYWORDS.get(VedaIntent.SUTRA, set())
        assert "sutra" in keywords
        assert "wiki" in keywords

    def test_sutra_route_defined(self):
        """Test SUTRA route is in INTENT_ROUTES."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, VedaIntent

        route = Artha.INTENT_ROUTES.get(VedaIntent.SUTRA)
        assert route == "_handle_sutra"

    def test_wiki_route_defined(self):
        """Test WIKI route is in INTENT_ROUTES."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, VedaIntent

        route = Artha.INTENT_ROUTES.get(VedaIntent.WIKI)
        assert route == "_handle_sutra"

    def test_shabda_extracts_wiki_keywords(self):
        """Test Shabda extracts wiki-related keywords."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Shabda

        shabda = Shabda()
        result = shabda.process("update wiki documentation")

        assert "update" in result.keywords or "wiki" in result.keywords
        assert "documentation" in result.keywords or "wiki" in result.keywords

    def test_artha_routes_to_sutra(self):
        """Test Artha routes wiki requests to SUTRA handler."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, Shabda, VedaIntent

        shabda = Shabda()
        artha = Artha()

        shabda_result = shabda.process("update wiki")
        artha_result = artha.process(shabda_result)

        assert artha_result.primary_intent in {VedaIntent.SUTRA, VedaIntent.WIKI}
        assert artha_result.handler_route == "_handle_sutra"

    def test_artha_adds_sutra_context_hint(self):
        """Test Artha adds sutra_context_needed hint for wiki requests."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, Shabda

        shabda = Shabda()
        artha = Artha()

        shabda_result = shabda.process("generate wiki documentation")
        artha_result = artha.process(shabda_result)

        assert "sutra_context_needed" in artha_result.context_hints


# =============================================================================
# SECTION 6: JNANA INTEGRATION TESTS
# =============================================================================


class TestJnanaSutraIntegration:
    """Tests for JNANA handler integration with SUTRA."""

    def test_handle_sutra_query_info(self):
        """Test handling wiki info query."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import handle_sutra_query

        result = handle_sutra_query("wiki info")

        assert "SUTRA" in result
        assert "Wiki" in result or "wiki" in result

    def test_handle_sutra_query_preview(self):
        """Test handling preview request."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import handle_sutra_query

        result = handle_sutra_query("preview wiki")

        assert "Preview" in result or "Home" in result

    def test_handle_sutra_query_pantheon_preview(self):
        """Test handling legacy pantheon preview request."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import handle_sutra_query

        result = handle_sutra_query("preview pantheon")

        assert "Agent Registry" in result

    def test_handle_sutra_query_generate_dry_run(self):
        """Test handling generate (dry run) request."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import handle_sutra_query

        result = handle_sutra_query("generate wiki")

        assert "SUTRA" in result
        assert "Home.md" in result or "generate" in result.lower()

    def test_get_sutra_for_chat(self):
        """Test getting SUTRA status for chat."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import get_sutra_for_chat

        result = get_sutra_for_chat()

        assert "SUTRA" in result
        assert "Wiki" in result or "wiki" in result
        assert "Commands" in result or "preview" in result.lower()

    def test_sutra_keyword_triggers_handler(self):
        """Test that wiki keyword triggers SUTRA handler via VEDA."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, Shabda

        shabda = Shabda()
        artha = Artha()

        result = shabda.process("query wiki documentation")
        artha_result = artha.process(result)

        assert "_handle_sutra" in artha_result.handler_route


# =============================================================================
# SECTION 7: TEMPLATE TESTS
# =============================================================================


class TestWikiTemplates:
    """Tests for wiki page templates."""

    def test_home_template_structure(self):
        """Test Home template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_HOME

        assert "{system_name}" in TEMPLATE_HOME
        assert "{version}" in TEMPLATE_HOME
        assert "{agent_count}" in TEMPLATE_HOME
        assert "{node_count}" in TEMPLATE_HOME
        assert "{quick_links}" in TEMPLATE_HOME

    def test_pantheon_template_structure(self):
        """Test Pantheon template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_PANTHEON

        assert "{title}" in TEMPLATE_PANTHEON
        assert "{intro}" in TEMPLATE_PANTHEON
        assert "{agent_count}" in TEMPLATE_PANTHEON
        assert "{domain_count}" in TEMPLATE_PANTHEON
        assert "{capability_count}" in TEMPLATE_PANTHEON
        assert "{domain_sections}" in TEMPLATE_PANTHEON
        assert "{capability_matrix}" in TEMPLATE_PANTHEON

    def test_atlas_template_structure(self):
        """Test Atlas template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_ATLAS

        assert "{title}" in TEMPLATE_ATLAS
        assert "{intro}" in TEMPLATE_ATLAS
        assert "{surface_rows}" in TEMPLATE_ATLAS
        assert "{source_section}" in TEMPLATE_ATLAS

    def test_governance_index_template_structure(self):
        """Test governance index template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_GOVERNANCE_INDEX

        assert "{canonical_pages}" in TEMPLATE_GOVERNANCE_INDEX
        assert "{constitution_section}" in TEMPLATE_GOVERNANCE_INDEX
        assert "{governance_section}" in TEMPLATE_GOVERNANCE_INDEX
        assert "{title}" in TEMPLATE_GOVERNANCE_INDEX
        assert "Change policy" in TEMPLATE_GOVERNANCE_INDEX

    def test_map_template_structure(self):
        """Test Map template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_MAP

        assert "{node_count}" in TEMPLATE_MAP
        assert "{edge_count}" in TEMPLATE_MAP
        assert "{constraint_count}" in TEMPLATE_MAP
        assert "{repo_python_files}" in TEMPLATE_MAP
        assert "{runtime_section}" in TEMPLATE_MAP
        assert "{module_section}" in TEMPLATE_MAP
        assert "Repository Snapshot" in TEMPLATE_MAP

    def test_sidebar_template_structure(self):
        """Test Sidebar template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_SIDEBAR

        assert "{navigation_sections}" in TEMPLATE_SIDEBAR
        assert "{version}" in TEMPLATE_SIDEBAR

    def test_footer_template_structure(self):
        """Test Footer template has correct structure."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import TEMPLATE_FOOTER

        assert "{timestamp}" in TEMPLATE_FOOTER
        assert "SUTRA" in TEMPLATE_FOOTER


# =============================================================================
# SECTION 8: SINGLETON TESTS
# =============================================================================


class TestSutraSingleton:
    """Tests for singleton access pattern."""

    def test_get_sutra_orchestrator(self):
        """Test get_sutra_orchestrator returns instance."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import get_sutra_orchestrator

        orch = get_sutra_orchestrator()
        assert orch is not None

    def test_get_sutra_orchestrator_same_instance(self):
        """Test singleton returns same instance."""
        from vibe_core.plugins.opus_assistant.manas.cortex import sutra

        # Reset singleton
        sutra._sutra_orchestrator = None

        orch1 = sutra.get_sutra_orchestrator()
        orch2 = sutra.get_sutra_orchestrator()

        assert orch1 is orch2


# =============================================================================
# SECTION 9: ERROR HANDLING TESTS
# =============================================================================


class TestSutraErrorHandling:
    """Tests for error handling in SUTRA."""

    def test_weaver_handles_missing_workspace(self):
        """Test weaver handles non-existent workspace gracefully."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver

        weaver = SutraWeaver(workspace=Path("/nonexistent/path"))
        ctx = weaver.gather_context()

        # Should not crash, should return empty/default context
        assert ctx is not None
        assert ctx.agents == []

    def test_sync_handles_no_git_remote(self):
        """Test WikiSync handles missing git remote."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiSync

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temp dir without git
            sync = WikiSync(workspace=Path(tmpdir))
            url = sync.get_wiki_url()

            # Should return None, not crash
            assert url is None

    def test_result_with_errors_formats_correctly(self):
        """Test error result formats for chat display."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraResult

        result = SutraResult(
            success=False,
            errors=[
                "Network timeout",
                "Authentication failed",
            ],
        )

        response = result.to_chat_response()

        assert "failed" in response.lower()
        assert "Network timeout" in response
        assert "Authentication failed" in response


# =============================================================================
# SECTION 10: INTEGRATION WORKFLOW TESTS
# =============================================================================


class TestSutraWorkflow:
    """Tests for full SUTRA workflow."""

    def test_full_generate_workflow(self):
        """Test complete generate workflow."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator

        orch = SutraOrchestrator()
        pages = orch.generate()

        # Should generate the full declared surface
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiPageType

        assert len(pages) == len(WikiPageType)

        # Each page should have content
        for page in pages:
            assert page.content
            assert page.title
            assert page.filename.endswith(".md")

    def test_preview_all_page_types(self):
        """Test previewing each page type."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator, WikiPageType

        orch = SutraOrchestrator()

        for page_type in [
            WikiPageType.HOME,
            WikiPageType.START_HERE,
            WikiPageType.INDEX,
            WikiPageType.CONSTITUTION,
            WikiPageType.FEDERATION_REGISTRY,
            WikiPageType.CANONICAL_ATLAS,
            WikiPageType.MAP,
        ]:
            content = orch.preview(page_type)
            assert isinstance(content, str)
            assert len(content) > 0

    def test_chat_query_routing(self):
        """Test various chat queries route to SUTRA correctly."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import handle_sutra_query

        # Info query
        result1 = handle_sutra_query("sutra status")
        assert "SUTRA" in result1

        # Preview query
        result2 = handle_sutra_query("show wiki preview")
        assert "Preview" in result2 or "Home" in result2

        # Generate query
        result3 = handle_sutra_query("generate wiki pages")
        assert "SUTRA" in result3
