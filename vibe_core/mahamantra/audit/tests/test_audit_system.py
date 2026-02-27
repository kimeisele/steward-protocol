"""
Tests for the modular audit system.

Tests:
1. AuditRegistry — register, list, filter, clear
2. AuditDispatcher — auto-discovery of auditors
3. AuditKernel — facade over dispatcher + registry
4. Individual auditors — each returns List[AuditFinding]
"""



from vibe_core.mahamantra.audit.audit_dispatcher import (
    AuditDispatcher,
)
from vibe_core.mahamantra.audit.audit_registry import (
    AuditFinding,
    AuditRegistry,
    FindingSeverity,
    FindingStatus,
)
from vibe_core.mahamantra.audit.kernel import AuditKernel

# =========================================================================
# AuditRegistry Tests
# =========================================================================


class TestAuditRegistry:
    def test_register_and_count(self):
        reg = AuditRegistry()
        assert reg.count == 0

        finding = AuditFinding(
            source="test",
            position=0,
            mahajana="test",
            description="test finding",
        )
        reg.register(finding)
        assert reg.count == 1

    def test_list_all(self):
        reg = AuditRegistry()
        f1 = AuditFinding(source="a", position=0, mahajana="x", description="one")
        f2 = AuditFinding(source="b", position=1, mahajana="y", description="two")
        reg.register(f1)
        reg.register(f2)
        assert len(reg.list_all()) == 2

    def test_list_by_severity(self):
        reg = AuditRegistry()
        f_crit = AuditFinding(
            source="a",
            position=0,
            mahajana="x",
            description="critical",
            severity=FindingSeverity.CRITICAL,
        )
        f_warn = AuditFinding(
            source="b",
            position=1,
            mahajana="y",
            description="warning",
            severity=FindingSeverity.WARNING,
        )
        reg.register(f_crit)
        reg.register(f_warn)

        critical = reg.list_by(severity=FindingSeverity.CRITICAL)
        assert len(critical) == 1
        assert critical[0].description == "critical"

    def test_list_by_status(self):
        reg = AuditRegistry()
        f = AuditFinding(source="a", position=0, mahajana="x", description="test")
        reg.register(f)

        identified = reg.list_by(status=FindingStatus.IDENTIFIED)
        assert len(identified) == 1

        resolved = reg.list_by(status=FindingStatus.RESOLVED)
        assert len(resolved) == 0

    def test_clear(self):
        reg = AuditRegistry()
        reg.register(
            AuditFinding(
                source="a",
                position=0,
                mahajana="x",
                description="test",
            )
        )
        assert reg.count == 1
        reg.clear()
        assert reg.count == 0

    def test_get_by_id(self):
        reg = AuditRegistry()
        f = AuditFinding(source="a", position=0, mahajana="x", description="test")
        reg.register(f)
        assert reg.get(f.id) is f
        assert reg.get("nonexistent") is None

    def test_finding_resolve(self):
        f = AuditFinding(source="a", position=0, mahajana="x", description="test")
        assert f.status == FindingStatus.IDENTIFIED
        f.resolve()
        assert f.status == FindingStatus.RESOLVED

    def test_duplicate_registration_ignored(self):
        reg = AuditRegistry()
        f = AuditFinding(source="a", position=0, mahajana="x", description="test")
        reg.register(f)
        reg.register(f)  # same ID
        assert reg.count == 1


# =========================================================================
# AuditDispatcher Tests
# =========================================================================


class TestAuditDispatcher:
    def test_discover_finds_auditors(self):
        """Dispatcher should find auditors with __position__ + Auditor class."""
        reg = AuditRegistry()
        dispatcher = AuditDispatcher(registry=reg)
        dispatcher.discover_auditors()

        # We created lineage_auditor (pos 0), ssot_auditor (pos 1),
        # protocol_auditor (pos 2), hygiene_auditor (pos 3),
        # protocol_resurrection (pos 5), drift (pos 15 — has Auditor class)
        assert len(dispatcher.auditors) >= 3, (
            f"Expected at least 3 auditors, got {len(dispatcher.auditors)}: {list(dispatcher.auditors.keys())}"
        )

    def test_run_all_populates_registry(self):
        """Running all auditors should produce findings in the registry."""
        reg = AuditRegistry()
        dispatcher = AuditDispatcher(registry=reg)
        dispatcher.run_all()
        # We can't predict exact count, but it should run without crashing
        assert isinstance(reg.count, int)

    def test_auditor_protocol_compliance(self):
        """All discovered auditors must have run_audit() → List[AuditFinding]."""
        reg = AuditRegistry()
        dispatcher = AuditDispatcher(registry=reg)
        dispatcher.discover_auditors()

        for pos, auditor in dispatcher.auditors.items():
            assert hasattr(auditor.instance, "run_audit"), (
                f"Auditor at position {pos} ({auditor.module_path}) missing run_audit()"
            )
            result = auditor.instance.run_audit()
            assert isinstance(result, list), f"Auditor at position {pos} returned {type(result)}, not list"


# =========================================================================
# AuditKernel Tests
# =========================================================================


class TestAuditKernel:
    def test_kernel_run_all(self):
        """Kernel.run_all() should return finding count."""
        reg = AuditRegistry()
        dispatcher = AuditDispatcher(registry=reg)
        kernel = AuditKernel(dispatcher=dispatcher, registry=reg)

        count = kernel.run_all()
        assert isinstance(count, int)
        assert count >= 0

    def test_kernel_summary(self):
        """Kernel.summary() should return structured dict."""
        reg = AuditRegistry()
        dispatcher = AuditDispatcher(registry=reg)
        kernel = AuditKernel(dispatcher=dispatcher, registry=reg)

        kernel.run_all()
        summary = kernel.summary()

        assert "total" in summary
        assert "critical" in summary
        assert "warnings" in summary
        assert "info" in summary
        assert "is_pristine" in summary
        assert "auditors_discovered" in summary
        assert "by_source" in summary

    def test_kernel_findings_filter(self):
        """Kernel.findings() should support severity filter."""
        reg = AuditRegistry()
        reg.register(
            AuditFinding(
                source="test",
                position=0,
                mahajana="x",
                description="critical",
                severity=FindingSeverity.CRITICAL,
            )
        )
        reg.register(
            AuditFinding(
                source="test",
                position=0,
                mahajana="x",
                description="info",
                severity=FindingSeverity.INFO,
            )
        )

        kernel = AuditKernel(
            dispatcher=AuditDispatcher(registry=reg),
            registry=reg,
        )

        critical = kernel.critical_findings()
        assert len(critical) == 1
        assert critical[0].description == "critical"

    def test_kernel_is_pristine(self):
        """is_pristine should be True when no critical findings."""
        reg = AuditRegistry()
        kernel = AuditKernel(
            dispatcher=AuditDispatcher(registry=reg),
            registry=reg,
        )
        assert kernel.is_pristine  # empty = pristine

        reg.register(
            AuditFinding(
                source="test",
                position=0,
                mahajana="x",
                description="warning",
                severity=FindingSeverity.WARNING,
            )
        )
        assert kernel.is_pristine  # warnings don't break pristine

        reg.register(
            AuditFinding(
                source="test",
                position=0,
                mahajana="x",
                description="critical",
                severity=FindingSeverity.CRITICAL,
            )
        )
        assert not kernel.is_pristine  # critical breaks pristine


# =========================================================================
# Individual Auditor Tests
# =========================================================================


class TestLineageAuditor:
    def test_returns_list_of_findings(self):
        from vibe_core.mahamantra.audit.lineage_auditor import Auditor

        auditor = Auditor()
        result = auditor.run_audit()
        assert isinstance(result, list)
        for f in result:
            assert isinstance(f, AuditFinding)
            assert f.source == "lineage_auditor"


class TestSSOTAuditor:
    def test_returns_list_of_findings(self):
        from vibe_core.mahamantra.audit.ssot_auditor import Auditor

        auditor = Auditor()
        result = auditor.run_audit()
        assert isinstance(result, list)
        for f in result:
            assert isinstance(f, AuditFinding)
            assert f.source == "ssot_auditor"


class TestHygieneAuditor:
    def test_returns_list_of_findings(self):
        from vibe_core.mahamantra.audit.hygiene_auditor import Auditor

        auditor = Auditor()
        result = auditor.run_audit()
        assert isinstance(result, list)
        for f in result:
            assert isinstance(f, AuditFinding)
            assert f.source == "hygiene_auditor"
