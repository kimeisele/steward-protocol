"""
PRAHLAD Coverage Intelligence - Mixin for coverage analysis.

Extracted to reduce service.py below 800 lines.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from vibe_core.naga.services.prahlad.types import (
    CoverageIntelligence,
    KernelLike,
    NagaCoverageData,
    RegistryLike,
    ShuddhiHealResult,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger("PRAHLAD")


class CoverageIntelligenceMixin:
    """
    Mixin for Prahlad coverage intelligence capabilities.

    Provides:
    - get_coverage_intelligence(): Coverage report from TestableRegistry
    - request_shuddhi_heal(): Request healing from Shuddhi
    - list_available_remedies(): List Shuddhi remedies
    """

    # These attributes are expected from PrahladService
    _tests_generated: int
    _chaos_probes: int
    _dharma_audits: int
    _hardening_suite: list

    def get_coverage_intelligence(self, kernel: Optional[KernelLike] = None) -> CoverageIntelligence:
        """
        Get coverage intelligence from TestableRegistry.

        This is NAGA's EYES - visibility into what we actually protect.

        Args:
            kernel: Optional kernel for discovery.

        Returns:
            Coverage report with testables, tests, and NAGA-specific coverage
        """
        try:
            from vibe_core.protocols.testable_registry import (
                get_global_registry,
            )

            registry = get_global_registry()

            if kernel:
                discovery_counts = registry.discover_from_kernel(kernel)
                logger.info(f"PRAHLAD: Discovered {sum(discovery_counts.values())} components")

            summary = registry.get_summary()
            naga_coverage = self._calculate_naga_coverage(registry)

            return {
                "timestamp": datetime.now().isoformat(),
                "source": "prahlad.get_coverage_intelligence",
                "total_testables": summary["total_testables"],
                "total_tests": summary["total_tests"],
                "by_type": summary["by_type"],
                "tests_by_type": summary["tests_by_type"],
                "naga_coverage": naga_coverage,
                "prahlad_stats": {
                    "tests_generated": self._tests_generated,
                    "chaos_probes": self._chaos_probes,
                    "dharma_audits": self._dharma_audits,
                    "hardening_suite_size": len(self._hardening_suite),
                },
            }

        except ImportError as e:
            logger.warning(f"PRAHLAD: TestableRegistry not available: {e}")
            return {
                "error": "TestableRegistry not available",
                "prahlad_stats": {
                    "tests_generated": self._tests_generated,
                    "chaos_probes": self._chaos_probes,
                    "dharma_audits": self._dharma_audits,
                },
            }

    def _calculate_naga_coverage(self, registry: RegistryLike) -> NagaCoverageData:
        """Calculate what NAGA specifically covers."""
        try:
            naga_testables = []
            for testable in registry.testables:
                testable_id = testable.testable_id.lower()
                if any(kw in testable_id for kw in ["naga", "sesha", "vasuki", "takshaka", "prahlad", "cortex"]):
                    naga_testables.append(testable)

            naga_tests = 0
            for testable in naga_testables:
                try:
                    naga_tests += len(testable.get_test_cases())
                except Exception:
                    pass

            return {
                "testables_covered": len(naga_testables),
                "tests_available": naga_tests,
                "services": [t.testable_id for t in naga_testables],
            }
        except Exception as e:
            logger.warning(f"PRAHLAD: NAGA coverage calculation failed: {e}")
            return {"error": str(e)}

    def request_shuddhi_heal(
        self,
        file_path: str,
        rule_id: str,
        dry_run: bool = True,
    ) -> ShuddhiHealResult:
        """
        Request healing from Shuddhi Engine.

        NAGA as AGENCY: We use Shuddhi's API, not rebuild.

        Args:
            file_path: File to heal
            rule_id: Which remedy to apply
            dry_run: If True, just show diff without writing

        Returns:
            Shuddhi result
        """
        try:
            from pathlib import Path

            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.shuddhi import ShuddhiProtocol, ShuddhiStatus

            shuddhi = ServiceRegistry.get(ShuddhiProtocol)
            if not shuddhi:
                return {"error": "Shuddhi not available"}

            path = Path(file_path)
            result = shuddhi.purify(path, rule_id)

            response: ShuddhiHealResult = {
                "healed": result.status == ShuddhiStatus.PURIFIED,
                "file_path": str(result.file_path),
                "rule_id": result.rule_id,
                "dry_run": dry_run,
                "message": result.message,
                "changes": [],
            }

            if hasattr(result, "diff") and result.diff:
                response["changes"] = [result.diff]

            if (
                not dry_run
                and result.status == ShuddhiStatus.PURIFIED
                and hasattr(result, "purified_code")
                and result.purified_code
            ):
                path.write_text(result.purified_code)
                logger.info(f"PRAHLAD: Shuddhi healed {file_path} with {rule_id}")

            return response

        except Exception as e:
            logger.error(f"PRAHLAD: Shuddhi request failed: {e}")
            return {"error": str(e)}

    def list_available_remedies(self) -> List[str]:
        """
        List available Shuddhi remedies.

        Returns:
            List of rule_ids that Shuddhi can apply
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.shuddhi import ShuddhiProtocol

            shuddhi = ServiceRegistry.get(ShuddhiProtocol)
            if not shuddhi:
                return []

            return shuddhi.list_remedies()
        except Exception:
            return []


__all__ = ["CoverageIntelligenceMixin"]
