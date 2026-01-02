"""
OPUS-212: SilentFailureRemedy - Heals Hidden Failures.

Transforms silent exception handlers (except: pass) to log the error,
ensuring violations don't go undetected.

Detection: Watchman StandardsInspectionTool (rule: silent_failure)
Surgery: This CSTRemedy

Philosophy:
"Satyam Eva Jayate" (Only Truth Prevails) - No silent failures.
"""

from typing import List, Sequence, Union

import libcst as cst
import libcst.matchers as m

from vibe_core.shuddhi.remedies.base import CSTRemedy


class SilentExceptRemedy(CSTRemedy):
    """
    Heals silent exception handlers.

    Transforms:
        except Exception:
            pass

    To:
        except Exception as _exc:
            logger.exception("Unexpected error: %s", _exc)
    """

    @property
    def rule_id(self) -> str:
        return "silent_failure"

    @property
    def requirements(self) -> List[str]:
        return ["logging"]

    def __init__(self):
        super().__init__()
        self._has_logger_import = False
        self._logger_name = "logger"

    def visit_Import(self, node: cst.Import) -> None:
        """Track logging imports."""
        if isinstance(node.names, cst.ImportStar):
            return

        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                if isinstance(name.name, cst.Name) and name.name.value == "logging":
                    self._has_logger_import = True

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Track from logging imports."""
        if isinstance(node.module, cst.Name) and node.module.value == "logging":
            self._has_logger_import = True
        elif isinstance(node.module, cst.Attribute):
            # Handle vibe_core.logging or similar
            pass

    def visit_Assign(self, node: cst.Assign) -> None:
        """Track logger = logging.getLogger(...) assignments."""
        if len(node.targets) != 1:
            return

        target = node.targets[0].target
        if isinstance(target, cst.Name):
            if m.matches(
                node.value,
                m.Call(func=m.Attribute(value=m.Name("logging"), attr=m.Name("getLogger"))),
            ):
                self._logger_name = target.value

    def leave_ExceptHandler(
        self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        """Transform silent except handlers."""
        # Check if body is just 'pass' or '...'
        if not self._is_silent_handler(updated_node):
            return updated_node

        self.violation_found = True
        self.applied = True

        # Create exception variable name if not present
        exc_name = "_exc"
        if updated_node.name and isinstance(updated_node.name.name, cst.Name):
            exc_name = updated_node.name.name.value

        # Handle bare except (no type) - must add Exception type
        new_type = updated_node.type
        new_whitespace = updated_node.whitespace_after_except
        if new_type is None:
            new_type = cst.Name("Exception")
            # CST requires whitespace between 'except' and type
            new_whitespace = cst.SimpleWhitespace(" ")

        # Create new 'as _exc' clause if missing
        new_name = updated_node.name
        if new_name is None:
            new_name = cst.AsName(
                name=cst.Name(exc_name),
                whitespace_before_as=cst.SimpleWhitespace(" "),
                whitespace_after_as=cst.SimpleWhitespace(" "),
            )

        # Create logger.exception(...) call
        log_stmt = cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.Call(
                        func=cst.Attribute(
                            value=cst.Name(self._logger_name),
                            attr=cst.Name("exception"),
                        ),
                        args=[
                            cst.Arg(value=cst.SimpleString('"Unexpected error: %s"')),
                            cst.Arg(value=cst.Name(exc_name)),
                        ],
                    )
                )
            ]
        )

        # Replace body
        new_body = cst.IndentedBlock(body=[log_stmt])

        return updated_node.with_changes(
            type=new_type,
            whitespace_after_except=new_whitespace,
            name=new_name,
            body=new_body,
        )

    def _is_silent_handler(self, node: cst.ExceptHandler) -> bool:
        """Check if handler body is just pass or ellipsis."""
        if not isinstance(node.body, cst.IndentedBlock):
            return False

        body = node.body.body
        if len(body) != 1:
            return False

        stmt = body[0]

        # Check for 'pass'
        if isinstance(stmt, cst.SimpleStatementLine):
            if len(stmt.body) == 1:
                if isinstance(stmt.body[0], cst.Pass):
                    return True
                # Check for '...'
                if isinstance(stmt.body[0], cst.Expr):
                    if isinstance(stmt.body[0].value, cst.Ellipsis):
                        return True

        return False
