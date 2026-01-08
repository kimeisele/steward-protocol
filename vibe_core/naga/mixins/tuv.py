"""
TÜV MIXIN - The Certificate (Badge Protocol)

Injected by Ananta to prove compliance.
"Die Plakette am Nummernschild."

Responsibilities:
- Hold the TÜV Badge (issued_at, expires_at, score)
- Verify badge validity at runtime
- Raise Alert if expired (Self-Policing)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from vibe_core.naga.mixins.base import NagaCapabilityMixin
from vibe_core.protocols.substrate import GeneManifest, create_gene_manifest


@dataclass
class TuvBadge:
    """The TÜV Certificate."""

    entity_id: str
    issued_at: datetime
    expires_at: datetime
    score: float
    signature: str  # Signed by TÜV/Chitragupta


class BadgeExpiredError(Exception):
    """Raised when a component runs with an expired badge."""

    pass


class TuvMixin(NagaCapabilityMixin):
    """
    TÜV Capability - Compliance/Badge.

    Gene Manifest:
        - Provides: compliance, badge, certificate
        - Requires: none
        - Priority: 99 (Check first!)
    """

    _tuv_badge: Optional[TuvBadge] = None

    _gene_manifest: GeneManifest = create_gene_manifest(
        name="tuv",
        capabilities=["compliance", "badge", "certificate"],
        requires=[],
        priority=99,
        optional=True,
    )

    def inject_tuv_badge(self, badge: TuvBadge) -> None:
        """Inject a badge (called by Ananta)."""
        self._tuv_badge = badge

    def check_tuv_badge(self) -> bool:
        """
        Verify the badge is valid.

        Returns:
            True if valid

        Raises:
            BadgeExpiredError if expired
        """
        if not self._tuv_badge:
            # No badge = Uncertified
            # In strict mode, this should raise or return False.
            # For now, return False (caller decides policy)
            return False

        if datetime.now() > self._tuv_badge.expires_at:
            raise BadgeExpiredError(
                f"TÜV Badge for {self._tuv_badge.entity_id} expired at {self._tuv_badge.expires_at}"
            )

        return True

    @property
    def tuv_score(self) -> float:
        """Get the compliance score (0.0 - 1.0)."""
        return self._tuv_badge.score if self._tuv_badge else 0.0
