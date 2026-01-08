from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import pytest


# --- MOCKING THE BADGE (Protocol First) ---
@dataclass
class TuvBadge:
    entity_id: str
    issued_at: datetime
    expires_at: datetime
    score: float
    signature: str


class BadgeExpiredError(Exception):
    pass


# --- THE MIXIN (The Gene) ---
# This mirrors what we will build in vibe_core/naga/mixins/tuv.py
class TuvBadgeMixin:
    _tuv_badge: Optional[TuvBadge] = None

    def inject_badge(self, badge: TuvBadge) -> None:
        self._tuv_badge = badge

    def check_badge(self) -> bool:
        if not self._tuv_badge:
            # No badge = Uncertified (Allow in dev, Block in prod?)
            # For strict mode, we might return False
            return False

        if datetime.now() > self._tuv_badge.expires_at:
            raise BadgeExpiredError(f"TÜV Badge expired at {self._tuv_badge.expires_at}")

        return True


# --- THE TEST ---
class TestTuvBadge:
    def test_valid_badge(self):
        service = TuvBadgeMixin()
        badge = TuvBadge(
            entity_id="test_service",
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            score=1.0,
            signature="sig",
        )
        service.inject_badge(badge)
        assert service.check_badge() is True

    def test_expired_badge(self):
        service = TuvBadgeMixin()
        badge = TuvBadge(
            entity_id="test_service",
            issued_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),  # Expired
            score=1.0,
            signature="sig",
        )
        service.inject_badge(badge)

        with pytest.raises(BadgeExpiredError):
            service.check_badge()

    def test_missing_badge(self):
        service = TuvBadgeMixin()
        assert service.check_badge() is False
