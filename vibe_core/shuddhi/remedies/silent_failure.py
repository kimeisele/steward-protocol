"""
OPUS-308: SilentFailureRemedy - Heals except:pass anti-pattern.

Transforms silent exception handlers to logged handlers.
"""

from typing import Union

import libcst as cst
import libcst.matchers as m

from vibe_core.shuddhi.remedies.base import CSTRemedy


class SilentFailureRemedy(CSTRemedy):
    """
    Heals violations where exceptions are silently swallowed.

    Matches:
        except Exception:
            pass

        except:
            pass

    Transforms to:
        except Exception as e:
            logger.warning(f"Suppressed error: {e}")
    """

    @property
    def rule_id(self) -> str:
        return "silent_failure"

    @property
    def requirements(self) -> list[str]:
        return ["logger"]  # Needs logger import in scope

    def __init__(self):
        super().__init__()
        self._needs_logger_import = False

    def leave_ExceptHandler(
        self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        """
        Match except handlers with only 'pass' in body.
        """
        # Check if body is just 'pass'
        if not self._is_pass_only(updated_node.body):
            return updated_node

        # This is a silent failure - transform it
        self.applied = True
        self._needs_logger_import = True

        # Get exception type (default to Exception if bare except)
        exc_type = updated_node.type
        if exc_type is None:
            exc_type = cst.Name("Exception")

        # Create: except Exception as e:
        #             logger.warning(f"Suppressed error: {e}")
        return updated_node.with_changes(
            type=exc_type,
            name=cst.AsName(name=cst.Name("e")),
            body=cst.IndentedBlock(
                body=[
                    cst.SimpleStatementLine(
                        body=[
                            cst.Expr(
                                value=cst.Call(
                                    func=cst.Attribute(
                                        value=cst.Name("logger"),
                                        attr=cst.Name("warning"),
                                    ),
                                    args=[
                                        cst.Arg(
                                            value=cst.FormattedString(
                                                parts=[
                                                    cst.FormattedStringText("Suppressed error: "),
                                                    cst.FormattedStringExpression(expression=cst.Name("e")),
                                                ]
                                            )
                                        )
                                    ],
                                )
                            )
                        ]
                    )
                ]
            ),
        )

    def _is_pass_only(self, body: cst.BaseSuite) -> bool:
        """Check if body contains only 'pass'."""
        if isinstance(body, cst.IndentedBlock):
            if len(body.body) != 1:
                return False
            stmt = body.body[0]
            if isinstance(stmt, cst.SimpleStatementLine):
                if len(stmt.body) == 1 and isinstance(stmt.body[0], cst.Pass):
                    return True
        return False
