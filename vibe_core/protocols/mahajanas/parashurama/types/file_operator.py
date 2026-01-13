# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0x06addf0e"  # GenesisByte: parampara % 37 == 0

"\n"

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional

from vibe_core.protocols.operator_protocol import (
    Intent,
    IntentType,
    OperatorType,
    SystemContext,
)

logger = logging.getLogger("FILE_OPERATOR")


def _get_runtime_config():
    """Get runtime config with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config

        return get_config().runtime
    except Exception:
        # Fallback for standalone/testing
        from vibe_core.phoenix.sections.runtime.section_main import RuntimeConfig

        return RuntimeConfig()


# The placeholder text indicating no request is pending.
# This must match what's in the ENVOY.md template.
NO_REQUEST_PLACEHOLDER = "> **Write your request here.**"
NO_REQUEST_IDENTIFIER = "_No pending request. Write your request above this line._"


class FileBasedOperator:
    """
    An operator that reads its intent from a designated text file.

    This allows for simple, programmatic control of the Agent City OS
    by writing a request to a file.
    """

    def __init__(self, file_path: str = "ENVOY.md"):
        """
        Initialize the FileBasedOperator.

        Args:
            file_path: The path to the file to monitor for requests.
        """
        self.file_path = Path(file_path)
        self._last_context: Optional[SystemContext] = None
        self._last_request: str = ""
        self._request_pattern = re.compile(r"> \*\*(.*?)\*\*")

    async def receive_context(self, context: SystemContext) -> None:
        """
        Stores the last known system context. Currently a no-op display-wise.
        """
        self._last_context = context

    async def provide_intent(self) -> Intent:
        """
        Reads the designated file, provides an intent if a new request is found,
        and then clears the request from the file.
        """
        runtime_config = _get_runtime_config()
        await asyncio.sleep(runtime_config.orchestration.file_poll_interval)  # Prevent high-CPU polling

        if not self.file_path.exists():
            logger.warning(f"File not found: {self.file_path}. Waiting.")
            return self._idle_intent()

        try:
            content = self.file_path.read_text()

            # This is a simple way to find the request line.
            # It's brittle but matches the current ENVOY.md format.
            request_section_match = self._request_pattern.search(content)

            if not request_section_match:
                logger.debug("Could not find request section in ENVOY.md")
                return self._idle_intent()

            raw_input = request_section_match.group(1).strip()

            is_placeholder = "Write your request here" in raw_input

            if not raw_input or is_placeholder:
                return self._idle_intent()

            # We have a real request. Process it.
            logger.info(f"New file-based request found: '{raw_input}'")

            # Clear the request in the file to prevent reprocessing
            self._clear_request_in_file(content, raw_input)

            # Return the command intent
            return Intent(
                intent_type=IntentType.COMMAND,
                raw_input=raw_input,
                source_operator=self.get_operator_type(),
            )

        except Exception as e:
            logger.error(f"Error processing file {self.file_path}: {e}")
            return self._idle_intent()

    def _clear_request_in_file(self, content: str, request_text: str):
        """Replaces the processed request with the placeholder text."""
        try:
            placeholder_section = (
                f"{NO_REQUEST_PLACEHOLDER} The kernel will process it on the next tick.\n"
                f"> Requests are routed via PlaybookRouter (pattern matching) and dispatched async.\n\n"
                f"{NO_REQUEST_IDENTIFIER}"
            )

            # Construct the string to be replaced
            string_to_replace = (
                f"> **{request_text}**\n"
                f"_The kernel will process it on the next tick. Requests are routed via PlaybookRouter (pattern matching) and dispatched async._"
            )

            new_content = content.replace(string_to_replace, placeholder_section)

            if content != new_content:
                self.file_path.write_text(new_content)
                logger.info(f"Cleared request '{request_text}' from {self.file_path}")
            else:
                # This can happen if the file format changes or on the first run
                logger.warning("Could not clear request. It might be processed again.")

        except Exception as e:
            logger.error(f"Failed to clear request in {self.file_path}: {e}")

    def _idle_intent(self) -> Intent:
        """Returns a 'do nothing' intent when no request is found."""
        return Intent(
            intent_type=IntentType.REFLEX,
            raw_input="idle",
            source_operator=self.get_operator_type(),
        )

    def is_available(self) -> bool:
        """This operator is always available as long as the file path is set."""
        return True

    def get_operator_type(self) -> OperatorType:
        """Returns the operator type."""
        return OperatorType.FILE_BASED
