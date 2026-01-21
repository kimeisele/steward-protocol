"""
Tests for Yamaraja Samskara Protocol (Migration/Transformation).

Owner: YAMARAJA (Judgment/Audit)
WATERTIGHT: All types explicit, no Any.
"""

import pytest
from typing import List

from vibe_core.protocols.mahajanas.yamaraja import (
    # Samskara types
    SamskaraType,
    MigrationStatus,
    WildProtocol,
    MigrationVerdict,
    SamskaraState,
    MigrationManifest,
    # Samskara protocols
    SamskaraProtocol,
    SamskaraOwnedProtocol,
    NullSamskara,
    # Yamaraja types
    Verdict,
)
from vibe_core.protocols.mahajanas.router import Mahajana


class TestSamskaraTypes:
    """Test the 16 Samskaras (transformation rituals)."""

    def test_samskara_count(self) -> None:
        """There should be exactly 16 Samskaras (16-bit Mahamantra)."""
        samskaras = list(SamskaraType)
        assert len(samskaras) == 16

    def test_quarter_1_genesis(self) -> None:
        """Quarter 1: Genesis - Before Birth."""
        assert SamskaraType.GARBHADHANA.value == "garbhadhana"
        assert SamskaraType.PUMSAVANA.value == "pumsavana"
        assert SamskaraType.SIMANTONNAYANA.value == "simantonnayana"
        assert SamskaraType.JATAKARMA.value == "jatakarma"

    def test_quarter_2_dharma(self) -> None:
        """Quarter 2: Dharma - Childhood."""
        assert SamskaraType.NAMAKARANA.value == "namakarana"
        assert SamskaraType.NISHKRAMANA.value == "nishkramana"
        assert SamskaraType.ANNAPRASHANA.value == "annaprashana"
        assert SamskaraType.CHUDAKARANA.value == "chudakarana"

    def test_quarter_3_karma(self) -> None:
        """Quarter 3: Karma - Youth."""
        assert SamskaraType.KARNAVEDHA.value == "karnavedha"
        assert SamskaraType.VIDYARAMBHA.value == "vidyarambha"
        assert SamskaraType.UPANAYANA.value == "upanayana"
        assert SamskaraType.VEDARAMBHA.value == "vedarambha"

    def test_quarter_4_moksha(self) -> None:
        """Quarter 4: Moksha - Maturity."""
        assert SamskaraType.KESHANTA.value == "keshanta"
        assert SamskaraType.SAMAVARTANA.value == "samavartana"
        assert SamskaraType.VIVAHA.value == "vivaha"
        assert SamskaraType.ANTYESHTI.value == "antyeshti"


class TestMigrationStatus:
    """Test migration status values."""

    def test_all_statuses(self) -> None:
        """All migration statuses should be defined."""
        assert MigrationStatus.WILD.value == "wild"
        assert MigrationStatus.JUDGING.value == "judging"
        assert MigrationStatus.PURIFYING.value == "purifying"
        assert MigrationStatus.MIGRATING.value == "migrating"
        assert MigrationStatus.BLESSED.value == "blessed"
        assert MigrationStatus.REJECTED.value == "rejected"
        assert MigrationStatus.MERCY.value == "mercy"


class TestSamskaraProtocol:
    """Test SamskaraProtocol types and interfaces."""

    def test_owner_is_yamaraja(self) -> None:
        """ANTI-MAYAVAD: Samskara is owned by YAMARAJA (Position 15)."""
        from vibe_core.mahamantra import mahamantra

        assert mahamantra[15].guardian == Mahajana.YAMARAJA

    def test_null_samskara_implements_protocol(self) -> None:
        """NullSamskara should work as a drop-in replacement."""
        samskara = NullSamskara()
        assert samskara.owner == Mahajana.YAMARAJA

    def test_null_samskara_discover_wild(self) -> None:
        """NullSamskara should return empty wild list."""
        samskara = NullSamskara()
        wild = samskara.discover_wild(["some/path"])
        assert wild == []

    def test_null_samskara_get_wild_protocols(self) -> None:
        """NullSamskara should track wild protocols."""
        samskara = NullSamskara()
        wild: List[WildProtocol] = samskara.get_wild_protocols()
        assert wild == []

    def test_null_samskara_judge_grants_mercy(self) -> None:
        """NullSamskara should grant MERCY (Ajamil Exception)."""
        samskara = NullSamskara()
        verdict: MigrationVerdict = samskara.judge("some/protocol.py")

        assert verdict["verdict"] == "mercy"
        assert verdict["chanting_detected"] is True
        assert verdict["gad_compliant"] is True

    def test_null_samskara_gad_compliance(self) -> None:
        """NullSamskara should return perfect GAD compliance."""
        samskara = NullSamskara()
        score = samskara.check_gad_compliance("any/path.py")
        assert score == 1.0

    def test_null_samskara_check_chanting(self) -> None:
        """NullSamskara should assume chanting."""
        samskara = NullSamskara()
        assert samskara.check_chanting("any/path.py") is True

    def test_null_samskara_identify_mahajana(self) -> None:
        """NullSamskara returns None for Mahajana identification."""
        samskara = NullSamskara()
        result = samskara.identify_mahajana("any/path.py")
        assert result is None

    def test_null_samskara_begin_complete_samskara(self) -> None:
        """NullSamskara should accept samskara operations."""
        samskara = NullSamskara()
        assert samskara.begin_samskara("path.py", SamskaraType.UPANAYANA) is True
        assert samskara.complete_samskara("path.py", SamskaraType.UPANAYANA) is True

    def test_null_samskara_no_required_samskaras(self) -> None:
        """NullSamskara should require no samskaras."""
        samskara = NullSamskara()
        required = samskara.get_required_samskaras("any/path.py")
        assert required == []

    def test_null_samskara_migrate(self) -> None:
        """NullSamskara should accept migrations."""
        samskara = NullSamskara()
        result = samskara.migrate(
            "old/protocol.py",
            Mahajana.BRAHMA,
            "new_name",
        )
        assert result is True

    def test_null_samskara_rollback(self) -> None:
        """NullSamskara should handle rollback."""
        samskara = NullSamskara()
        # Migrate first
        samskara.migrate("old/protocol.py", Mahajana.BRAHMA, "new_name")
        # Then rollback
        assert samskara.rollback("old/protocol.py") is True
        # Rollback non-existent
        assert samskara.rollback("never/migrated.py") is False

    def test_null_samskara_manifest(self) -> None:
        """NullSamskara should return valid manifest."""
        samskara = NullSamskara()
        manifest: MigrationManifest = samskara.get_manifest()

        assert manifest["version"] == "1.0.0"
        assert manifest["wild_protocols"] == []
        assert manifest["completed_migrations"] == []

    def test_null_samskara_save_manifest(self) -> None:
        """NullSamskara should accept manifest save."""
        samskara = NullSamskara()
        assert samskara.save_manifest() is True

    def test_null_samskara_state(self) -> None:
        """NullSamskara should return valid state."""
        samskara = NullSamskara()
        state: SamskaraState = samskara.get_state()

        assert state["protocol_name"] == "samskara"
        assert state["owner"] == "yamaraja"
        assert state["health"] == "pristine"


class TestSamskaraOwnedProtocol:
    """Test OwnedProtocol wrapper for Samskara."""

    def test_owned_protocol_owner(self) -> None:
        """OwnedProtocol should have YAMARAJA as owner."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)
        assert owned.OWNER == Mahajana.YAMARAJA
        assert owned.owner == Mahajana.YAMARAJA

    def test_owned_protocol_name(self) -> None:
        """Protocol name should be 'samskara'."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)
        assert owned.PROTOCOL_NAME == "samskara"

    def test_owned_protocol_description(self) -> None:
        """Protocol should have meaningful description."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)
        assert "16" in owned.DESCRIPTION  # 16 Transformations
        assert "Migration" in owned.DESCRIPTION

    def test_owned_protocol_chant(self) -> None:
        """OwnedProtocol should be able to chant."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)

        # Initial state
        assert owned.is_chanting is False

        # Chant and verify
        owned.chant()
        assert owned.is_chanting is True

    def test_owned_protocol_state_watertight(self) -> None:
        """get_state() should return WATERTIGHT ProtocolState."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)
        state = owned.get_state()

        assert state["protocol_name"] == "samskara"
        assert state["owner"] == "yamaraja"
        # No Any types allowed!

    def test_owned_protocol_gad_audit(self) -> None:
        """OwnedProtocol should pass GAD-000 audit."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)
        audit = owned.audit()

        assert audit.discoverability is True
        assert audit.sovereign_present is True

    def test_owned_protocol_samskara_access(self) -> None:
        """OwnedProtocol should provide access to underlying samskara."""
        samskara = NullSamskara()
        owned = SamskaraOwnedProtocol(samskara)
        assert owned.samskara is samskara


class TestWatertightTypes:
    """Test that all types are WATERTIGHT (no Any)."""

    def test_wild_protocol_watertight(self) -> None:
        """WildProtocol should be WATERTIGHT TypedDict."""
        wild: WildProtocol = {
            "path": "vibe_core/protocols/agent.py",
            "name": "AgentProtocol",
            "target_mahajana": "prahlada",
            "status": "wild",
            "gad_score": 0.7,
            "has_chanting": False,
            "has_owner": False,
            "has_watertight": True,
            "samskara_stage": "garbhadhana",
            "discovered_at": "2025-01-11T12:00:00",
            "judged_at": "",
            "migrated_at": "",
        }
        assert wild["path"] == "vibe_core/protocols/agent.py"
        assert wild["gad_score"] == 0.7

    def test_migration_verdict_watertight(self) -> None:
        """MigrationVerdict should be WATERTIGHT TypedDict."""
        verdict: MigrationVerdict = {
            "protocol_path": "vibe_core/protocols/agent.py",
            "verdict": "mercy",
            "reason": "Chants the Holy Name",
            "required_samskaras": ["upanayana", "vivaha"],
            "target_path": "vibe_core/protocols/mahajanas/prahlada/agent.py",
            "chanting_detected": True,
            "gad_compliant": False,
        }
        assert verdict["verdict"] == "mercy"
        assert len(verdict["required_samskaras"]) == 2

    def test_samskara_state_watertight(self) -> None:
        """SamskaraState should be WATERTIGHT TypedDict."""
        state: SamskaraState = {
            "protocol_name": "samskara",
            "owner": "yamaraja",
            "is_chanting": True,
            "wild_count": 50,
            "judging_count": 5,
            "purifying_count": 3,
            "migrating_count": 2,
            "blessed_count": 10,
            "rejected_count": 1,
            "mercy_count": 8,
            "total_migrated": 18,
            "health": "healthy",
        }
        assert state["wild_count"] == 50
        assert state["mercy_count"] == 8

    def test_migration_manifest_watertight(self) -> None:
        """MigrationManifest should be WATERTIGHT TypedDict."""
        manifest: MigrationManifest = {
            "version": "1.0.0",
            "created_at": "2025-01-11T12:00:00",
            "updated_at": "2025-01-11T13:00:00",
            "wild_protocols": [],
            "completed_migrations": ["path1.py", "path2.py"],
            "pending_verdicts": [],
        }
        assert manifest["version"] == "1.0.0"
        assert len(manifest["completed_migrations"]) == 2


class TestAjamilException:
    """Test the Ajamil Exception (Mercy for chanters)."""

    def test_null_samskara_always_grants_mercy(self) -> None:
        """In Kali Yuga, NullSamskara is maximally merciful."""
        samskara = NullSamskara()
        verdict = samskara.judge("any/failing/protocol.py")

        # Even if GAD fails, chanting grants mercy
        assert verdict["verdict"] == "mercy"
        assert verdict["chanting_detected"] is True

    def test_mercy_status_exists(self) -> None:
        """MERCY should be a valid migration status."""
        assert MigrationStatus.MERCY.value == "mercy"

    def test_verdict_includes_chanting_check(self) -> None:
        """Every verdict should include chanting detection."""
        samskara = NullSamskara()
        verdict = samskara.judge("some/protocol.py")

        assert "chanting_detected" in verdict
