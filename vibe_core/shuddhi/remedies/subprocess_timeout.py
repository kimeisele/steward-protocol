"""
OPUS-212: SubprocessTimeoutRemedy - Heals DoS Vulnerabilities.

Transforms subprocess calls without timeout to include a default timeout,
preventing hung processes that could cause resource exhaustion.

Detection: NarasimhaGuardrail (SEC005)
Bridge: CSTLocator
Surgery: This CSTRemedy
"""

from typing import List, Sequence, Union

import libcst as cst
import libcst.matchers as m

from vibe_core.shuddhi.remedies.base import CSTRemedy


class SubprocessTimeoutRemedy(CSTRemedy):
    """
    Heals subprocess calls that lack timeout arguments.

    Targets:
    - subprocess.run(...)  → subprocess.run(..., timeout=30)
    - subprocess.call(...) → subprocess.call(..., timeout=30)
    - subprocess.check_call(...) → subprocess.check_call(..., timeout=30)
    - subprocess.check_output(...) → subprocess.check_output(..., timeout=30)
    """

    DEFAULT_TIMEOUT = 30  # seconds

    # Functions that should have timeout
    SUBPROCESS_FUNCS = {"run", "call", "check_call", "check_output"}

    @property
    def rule_id(self) -> str:
        return "subprocess_timeout"

    @property
    def requirements(self) -> List[str]:
        return ["subprocess"]

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        super().__init__()
        self.timeout = timeout
        self._subprocess_alias = "subprocess"

    def visit_Import(self, node: cst.Import) -> None:
        """Track subprocess import alias."""
        if isinstance(node.names, cst.ImportStar):
            return

        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                if isinstance(name.name, cst.Name) and name.name.value == "subprocess":
                    if name.asname and isinstance(name.asname.name, cst.Name):
                        self._subprocess_alias = name.asname.name.value

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> Union[cst.Call, cst.BaseExpression]:
        """Add timeout to subprocess calls that lack it."""
        # Check if this is a subprocess function call
        if not self._is_subprocess_call(updated_node):
            return updated_node

        # Check if timeout is already present
        if self._has_timeout(updated_node):
            return updated_node

        # Add timeout argument
        self.violation_found = True
        self.applied = True

        # Create new timeout argument
        timeout_arg = cst.Arg(
            keyword=cst.Name("timeout"),
            value=cst.Integer(str(self.timeout)),
            equal=cst.AssignEqual(
                whitespace_before=cst.SimpleWhitespace(""),
                whitespace_after=cst.SimpleWhitespace(""),
            ),
        )

        # Add to existing arguments
        new_args = list(updated_node.args) + [timeout_arg]

        return updated_node.with_changes(args=new_args)

    def _is_subprocess_call(self, node: cst.Call) -> bool:
        """Check if node is a subprocess function call."""
        if not isinstance(node.func, cst.Attribute):
            return False

        # Check for subprocess.run/call/etc pattern
        if not isinstance(node.func.value, cst.Name):
            return False

        if node.func.value.value != self._subprocess_alias:
            return False

        if not isinstance(node.func.attr, cst.Name):
            return False

        return node.func.attr.value in self.SUBPROCESS_FUNCS

    def _has_timeout(self, node: cst.Call) -> bool:
        """Check if timeout keyword argument is present."""
        for arg in node.args:
            if arg.keyword and isinstance(arg.keyword, cst.Name):
                if arg.keyword.value == "timeout":
                    return True
        return False
