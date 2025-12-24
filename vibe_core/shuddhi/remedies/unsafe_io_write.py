"""
OPUS-212: UnsafeIOWriteRemedy - The first CST Healer.

Transforms raw 'open().write()' calls to 'self.system.write_file()'.
"""

from typing import List, Union

import libcst as cst
import libcst.matchers as m

from vibe_core.shuddhi.remedies.base import CSTRemedy, ShuddhiScopeError


class UnsafeIOWriteRemedy(CSTRemedy):
    """
    Heals violations where raw open() is used for writing.
    Only applies if 'self.system' is available in scope.
    """

    @property
    def rule_id(self) -> str:
        return "unsafe_io_write"

    @property
    def requirements(self) -> List[str]:
        return ["self.system"]

    def __init__(self):
        super().__init__()
        self._in_class = False
        self._has_self = False
        self._scope_stack = []

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self._scope_stack.append("class")
        self._in_class = True

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self._scope_stack.pop()
        self._in_class = "class" in self._scope_stack
        return updated_node

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        self._scope_stack.append("func")
        # Check if first parameter is 'self'
        if node.params.params:
            first_param = node.params.params[0].name.value
            if first_param == "self":
                self._has_self = True

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        self._scope_stack.pop()
        self._has_self = False  # Simplification for now
        return updated_node

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> Union[cst.Call, cst.FlattenSentinel[cst.Call], cst.RemovalSentinel]:
        """
        Matches: open(file, 'w')
        Note: This is a simplified matcher for the MVP.
        """
        if m.matches(updated_node, m.Call(func=m.Name("open"))):
            # Check for 'w' or 'wb' in arguments
            is_write = False
            for arg in updated_node.args:
                if m.matches(arg.value, m.SimpleString(value=m.MatchIfTrue(lambda v: "w" in v))):
                    is_write = True
                    break

            if is_write:
                # HEURISTIC CHECK (The Final 1%)
                if not (self._in_class and self._has_self):
                    raise ShuddhiScopeError(
                        "Found unsafe 'open()' but no 'self.system' context available (not in a class with 'self')."
                    )

                self.violation_found = True
                # We don't replace the call directly here because open() is often part of a 'with' statement
                # or followed by .write().
                # For the MVP, we focus on the 'with' statement pattern which is most common.

        return updated_node

    def leave_With(
        self, original_node: cst.With, updated_node: cst.With
    ) -> Union[cst.BaseStatement, cst.FlattenSentinel[cst.BaseStatement], cst.RemovalSentinel]:
        """
        Matches:
        with open(path, 'w') as f:
            f.write(data)

        Transforms to:
        self.system.write_file(path, data)
        """
        # 1. Match 'with open(...) as f'
        if len(updated_node.items) != 1:
            return updated_node

        item = updated_node.items[0]
        if not m.matches(item.item, m.Call(func=m.Name("open"))):
            return updated_node

        # Extract path
        open_call = item.item
        if not open_call.args:
            return updated_node

        path_arg = open_call.args[0].value

        # Check if it's a write mode
        is_write = False
        for arg in open_call.args[1:]:
            if m.matches(arg.value, m.SimpleString(value=m.MatchIfTrue(lambda v: "w" in v))):
                is_write = True
                break

        if not is_write:
            return updated_node

        # Extract file handle name (e.g., 'f' in 'as f')
        if not item.asname or not isinstance(item.asname.name, cst.Name):
            return updated_node

        handle_name = item.asname.name.value

        # 2. Match 'handle.write(data)' inside the body
        # For MVP, we assume the body is a single call to write()
        if len(updated_node.body.body) != 1:
            return updated_node

        stmt = updated_node.body.body[0]
        if not m.matches(
            stmt,
            m.SimpleStatementLine(
                body=[m.Expr(value=m.Call(func=m.Attribute(value=m.Name(handle_name), attr=m.Name("write"))))]
            ),
        ):
            return updated_node

        write_call = stmt.body[0].value
        if not write_call.args:
            return updated_node

        data_arg = write_call.args[0].value

        # HEURISTIC CHECK
        if not (self._in_class and self._has_self):
            raise ShuddhiScopeError("Unsafe write found but out of scope for self.system.")

        # 3. Transform to self.system.write_file(path, data)
        self.applied = True
        return cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.Call(
                        func=cst.Attribute(
                            value=cst.Attribute(value=cst.Name("self"), attr=cst.Name("system")),
                            attr=cst.Name("write_file"),
                        ),
                        args=[cst.Arg(value=path_arg), cst.Arg(value=data_arg)],
                    )
                )
            ]
        )
