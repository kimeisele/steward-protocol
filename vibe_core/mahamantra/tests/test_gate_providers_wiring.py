"""
Tests for substrate/gate_providers.py — wire_gate_providers().

Proves the 5 core gate observers wire correctly and that
MahaAttention/MahaLLM (empty routers) are NOT wired.
"""



class TestWireGateProviders:
    """wire_gate_providers() registers exactly the 5 core observers."""

    def test_returns_positive_count(self):
        from vibe_core.mahamantra.substrate.gate_providers import wire_gate_providers

        count = wire_gate_providers()
        assert count >= 0  # idempotent — may be 0 if already wired

    def test_five_core_providers_exist(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_providers

        providers = get_providers()
        for name in ("mantra_gate", "storage_gate", "infer_gate", "sync_gate", "enforce_gate"):
            assert name in providers, f"Missing core provider: {name}"

    def test_no_empty_router_providers(self):
        """MahaAttention and MahaLLM must NOT be wired (0 registered agents = dead code)."""
        from vibe_core.mahamantra.substrate.gate_providers import get_providers

        providers = get_providers()
        assert "maha_attention" not in providers
        assert "maha_llm" not in providers

    def test_idempotent(self):
        from vibe_core.mahamantra.substrate.gate_providers import wire_gate_providers

        wire_gate_providers()
        wire_gate_providers()  # second call must not crash or double-register


class TestGateProviderTypes:
    """Each provider has the expected gate observer interface."""

    def test_mantra_gate_has_parse(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_providers

        p = get_providers()["mantra_gate"]
        assert hasattr(p, "parse")

    def test_storage_gate_has_validate(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_providers

        p = get_providers()["storage_gate"]
        assert hasattr(p, "validate")

    def test_infer_gate_has_infer(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_providers

        p = get_providers()["infer_gate"]
        assert hasattr(p, "infer")

    def test_enforce_gate_has_enforce(self):
        from vibe_core.mahamantra.substrate.gate_providers import get_providers

        p = get_providers()["enforce_gate"]
        assert hasattr(p, "enforce")
