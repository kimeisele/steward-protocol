"""
TEST: Action Handlers (Hardened)
================================
Verifies GAD-5000 strict validation in action handlers.
"""

from vibe_core.cartridges.system.envoy.action_handlers import ActionContext, CheckStateHandler


class TestCheckStateHandler:
    def setup_method(self):
        self.handler = CheckStateHandler()
        self.context = ActionContext(
            phase_id="test_phase",
            playbook_id="test_playbook",
            execution_id="test_exec",
            user_input="test input",
            phase_results={"existing_field": "value"},
        )

    async def test_validate_input_success(self):
        """Should pass when all required fields are present."""
        params = {"required_fields": ["existing_field"], "constraints": {}}
        result = await self.handler.execute("input_validation", params, self.context)
        assert result.success is True
        assert result.data["validation"] == "passed"

    async def test_validate_input_failure_missing_field(self):
        """Should FAIL when required field is missing (STRICT MODE)."""
        params = {"required_fields": ["missing_field"], "constraints": {}}
        result = await self.handler.execute("input_validation", params, self.context)
        assert result.success is False
        assert "Missing required fields: missing_field" in result.error

    async def test_validate_input_failure_regex(self):
        """Should FAIL when regex pattern does not match."""
        self.context.phase_results["email"] = "invalid-email"
        params = {"required_fields": ["email"], "constraints": {"email_pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"}}
        result = await self.handler.execute("input_validation", params, self.context)
        assert result.success is False
        assert "does not match pattern" in result.error

    async def test_permission_check_failure(self):
        """Should FAIL when user lacks admin role."""
        # Context defaults to role="unknown" (or None)
        params = {"required_permissions": ["admin"]}
        result = await self.handler.execute("permission_check", params, self.context)
        assert result.success is False
        assert "Permission denied" in result.error

    async def test_permission_check_success(self):
        """Should PASS when user has admin role."""
        self.context.user_role = "admin"
        params = {"required_permissions": ["admin"]}
        result = await self.handler.execute("permission_check", params, self.context)
        assert result.success is True
