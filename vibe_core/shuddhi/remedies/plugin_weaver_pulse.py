"""
OPUS-306: PluginWeaverPulseRemedy - Removes weaver.pulse() from plugins.

Plugins must NOT call weaver.pulse() directly.
State commits are the sole authority of StateService.

Pattern matched:
    weaver.pulse()
    weaver = ServiceRegistry.get(StateSyncWeaverProtocol); weaver.pulse()

Transformed to:
    (removed)
"""

from typing import List, Union

import libcst as cst
import libcst.matchers as m

from vibe_core.shuddhi.remedies.base import CSTRemedy


class PluginWeaverPulseRemedy(CSTRemedy):
    """
    Removes weaver.pulse() calls from plugin code.

    Architectural Rule (OPUS-306):
        Plugins write state via StateService.save() or mark_dirty().
        StateService batches writes and triggers weaver.pulse().
        Only StateService has authority to call weaver.pulse().
    """

    @property
    def rule_id(self) -> str:
        return "plugin_weaver_pulse"

    @property
    def requirements(self) -> List[str]:
        return []  # No requirements - this is a removal remedy

    def __init__(self):
        super().__init__()
        self._weaver_vars: set = set()  # Track variables that hold weaver references

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> Union[cst.Assign, cst.RemovalSentinel]:
        """
        Track: weaver = ServiceRegistry.get(StateSyncWeaverProtocol)
        """
        # Check if RHS is ServiceRegistry.get(StateSyncWeaverProtocol)
        if m.matches(
            updated_node.value,
            m.Call(
                func=m.Attribute(
                    value=m.Name("ServiceRegistry"),
                    attr=m.Name("get"),
                )
            ),
        ):
            # Check if argument is StateSyncWeaverProtocol
            call = updated_node.value
            if call.args:
                arg = call.args[0].value
                if m.matches(arg, m.Name("StateSyncWeaverProtocol")):
                    # Track the variable name
                    for target in updated_node.targets:
                        if isinstance(target.target, cst.Name):
                            self._weaver_vars.add(target.target.value)

        return updated_node

    def leave_Expr(self, original_node: cst.Expr, updated_node: cst.Expr) -> Union[cst.Expr, cst.RemovalSentinel]:
        """
        Remove: weaver.pulse() or res = weaver.pulse()
        """
        if self._is_weaver_pulse_call(updated_node.value):
            self.applied = True
            self.violation_found = True
            return cst.RemovalSentinel.REMOVE

        return updated_node

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> Union[cst.SimpleStatementLine, cst.RemovalSentinel]:
        """
        Remove entire line if it contains weaver.pulse() assignment.
        Pattern: res = weaver.pulse()
        """
        for stmt in updated_node.body:
            if isinstance(stmt, cst.Assign):
                if self._is_weaver_pulse_call(stmt.value):
                    self.applied = True
                    self.violation_found = True
                    return cst.RemovalSentinel.REMOVE

        # Check if all statements were removed
        remaining = [s for s in updated_node.body if not isinstance(s, cst.RemovalSentinel)]
        if not remaining:
            return cst.RemovalSentinel.REMOVE

        return updated_node

    def _is_weaver_pulse_call(self, node: cst.BaseExpression) -> bool:
        """Check if node is a weaver.pulse() call."""
        if not isinstance(node, cst.Call):
            return False

        # Match: weaver.pulse() or any_var.pulse() where var is tracked
        if m.matches(node.func, m.Attribute(attr=m.Name("pulse"))):
            attr = node.func
            if isinstance(attr.value, cst.Name):
                var_name = attr.value.value
                # Match known weaver variable names
                if var_name in self._weaver_vars or var_name == "weaver":
                    return True

        return False

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> Union[cst.FunctionDef, cst.RemovalSentinel]:
        """
        Remove entire weaver_pulse() method if it only calls weaver.pulse().
        """
        func_name = updated_node.name.value

        # Target: weaver_pulse method in WeaverBridge
        if func_name == "weaver_pulse":
            self.applied = True
            self.violation_found = True
            return cst.RemovalSentinel.REMOVE

        return updated_node
