"""
OPUS-042: SAMVADA (The Dialogue) - Real-time Human-MANAS Communication.

Sanskrit: Samvada = Dialogue/Conversation

This module provides bidirectional communication between the CLI (human)
and MANAS (cognitive kernel) via Unix domain sockets.

Architecture:
    ┌─────────────────┐     Unix Socket      ┌─────────────────┐
    │  SamvadaClient  │ ←─────────────────→  │  SamvadaListener │
    │  (The Mouth)    │   ~/.opus/samvada    │   (The Ear)      │
    └─────────────────┘                      └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌─────────────────┐
                                             │  Message Handler │
                                             │  (MANAS Brain)   │
                                             └─────────────────┘

"The dialogue between human and machine must be clear and true."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x54d927f7"  # GenesisByte: parampara % 37 == 0

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from uuid import uuid4

logger = logging.getLogger("MANAS.Cortex.Samvada")


# =============================================================================
# MESSAGE PROTOCOL
# =============================================================================


@dataclass
class SamvadaMessage:
    """
    Message sent from client to listener.

    Protocol:
    - type: Message type (chat, status, command)
    - content: The message content
    - msg_id: Unique message ID for correlation
    """

    msg_type: str
    content: str
    msg_id: str = field(default_factory=lambda: uuid4().hex[:12])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(
            {
                "type": self.msg_type,
                "content": self.content,
                "msg_id": self.msg_id,
                "metadata": self.metadata,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "SamvadaMessage":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            msg_type=data.get("type", "chat"),
            content=data.get("content", ""),
            msg_id=data.get("msg_id", uuid4().hex[:12]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SamvadaResponse:
    """
    Response from listener to client.

    Protocol:
    - success: Whether the request succeeded
    - content: The response content
    - error: Error message if failed
    - msg_id: Correlation ID (from request)
    """

    success: bool
    content: str
    error: Optional[str] = None
    msg_id: Optional[str] = None

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(
            {
                "success": self.success,
                "content": self.content,
                "error": self.error,
                "msg_id": self.msg_id,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "SamvadaResponse":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            success=data.get("success", False),
            content=data.get("content", ""),
            error=data.get("error"),
            msg_id=data.get("msg_id"),
        )


# =============================================================================
# THE EAR - LISTENER
# =============================================================================


class SamvadaListener:
    """
    Unix socket listener for receiving messages from CLI.

    The Ear of MANAS - listens for human commands and dispatches
    them to the message handler (cognitive kernel).

    Usage:
        async def handle_message(msg: SamvadaMessage) -> SamvadaResponse:
            return SamvadaResponse(success=True, content=f"Received: {msg.content}")

        listener = SamvadaListener(handler=handle_message)
        await listener.start()  # Blocks until stopped
    """

    DEFAULT_SOCKET_DIR = ".opus"
    DEFAULT_SOCKET_NAME = "samvada.sock"

    def __init__(
        self,
        socket_path: Optional[str] = None,
        handler: Optional[Callable] = None,
    ):
        """
        Initialize the listener.

        Args:
            socket_path: Path to Unix socket (default: ~/.opus/samvada.sock)
            handler: Async function to handle messages
        """
        if socket_path:
            self.socket_path = socket_path
        else:
            home = os.environ.get("HOME", "/tmp")
            opus_dir = Path(home) / self.DEFAULT_SOCKET_DIR
            self.socket_path = str(opus_dir / self.DEFAULT_SOCKET_NAME)

        self._handler = handler or self._default_handler
        self._server: Optional[asyncio.AbstractServer] = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Check if listener is running."""
        return self._is_running

    async def start(self) -> None:
        """
        Start the listener.

        Creates the Unix socket and begins accepting connections.
        This method blocks until stop() is called.
        """
        # Ensure directory exists
        socket_dir = Path(self.socket_path).parent
        socket_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing socket file
        socket_file = Path(self.socket_path)
        if socket_file.exists():
            socket_file.unlink()

        logger.info(f"🎧 SAMVADA Listener starting on {self.socket_path}")

        self._server = await asyncio.start_unix_server(
            self._handle_client,
            path=self.socket_path,
        )

        self._is_running = True

        async with self._server:
            try:
                await self._server.serve_forever()
            except asyncio.CancelledError:
                logger.info("🔇 SAMVADA Listener cancelled")

    async def stop(self) -> None:
        """Stop the listener."""
        self._is_running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("🔇 SAMVADA Listener stopped")

        # Clean up socket file
        socket_file = Path(self.socket_path)
        if socket_file.exists():
            socket_file.unlink()

    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle a client connection."""
        try:
            # Read message (newline-delimited JSON)
            data = await asyncio.wait_for(
                reader.readline(),
                timeout=30.0,
            )

            if not data:
                return

            json_str = data.decode("utf-8").strip()
            logger.debug(f"📨 Received: {json_str[:100]}...")

            # Parse message
            try:
                msg = SamvadaMessage.from_json(json_str)
            except json.JSONDecodeError as e:
                response = SamvadaResponse(
                    success=False,
                    content="",
                    error=f"Invalid JSON: {e}",
                )
                writer.write((response.to_json() + "\n").encode("utf-8"))
                await writer.drain()
                return

            # Call handler
            try:
                response = await self._handler(msg)
                response.msg_id = msg.msg_id
            except Exception as e:
                logger.error(f"Handler error: {e}")
                response = SamvadaResponse(
                    success=False,
                    content="",
                    error=f"Handler error: {e}",
                    msg_id=msg.msg_id,
                )

            # Send response
            writer.write((response.to_json() + "\n").encode("utf-8"))
            await writer.drain()

        except asyncio.TimeoutError:
            logger.warning("Client timeout")
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _default_handler(self, msg: SamvadaMessage) -> SamvadaResponse:
        """Default handler - echo the message."""
        return SamvadaResponse(
            success=True,
            content=f"Echo: {msg.content}",
            msg_id=msg.msg_id,
        )


# =============================================================================
# THE MOUTH - CLIENT
# =============================================================================


class SamvadaClient:
    """
    Unix socket client for sending messages to MANAS.

    The Mouth of the human - sends commands to MANAS and
    receives responses.

    Usage:
        client = SamvadaClient()
        response = await client.send("Status report")
        print(response.content)
    """

    def __init__(
        self,
        socket_path: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the client.

        Args:
            socket_path: Path to Unix socket (default: ~/.opus/samvada.sock)
            timeout: Connection/read timeout in seconds
        """
        if socket_path:
            self.socket_path = socket_path
        else:
            home = os.environ.get("HOME", "/tmp")
            opus_dir = Path(home) / SamvadaListener.DEFAULT_SOCKET_DIR
            self.socket_path = str(opus_dir / SamvadaListener.DEFAULT_SOCKET_NAME)

        self.timeout = timeout

    async def send(self, content: str, msg_type: str = "chat") -> SamvadaResponse:
        """
        Send a message to MANAS and wait for response.

        Args:
            content: The message content
            msg_type: Message type (default: "chat")

        Returns:
            SamvadaResponse from MANAS
        """
        msg = SamvadaMessage(msg_type=msg_type, content=content)

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_unix_connection(self.socket_path),
                timeout=self.timeout,
            )

            try:
                # Send message
                writer.write((msg.to_json() + "\n").encode("utf-8"))
                await writer.drain()

                # Read response
                data = await asyncio.wait_for(
                    reader.readline(),
                    timeout=self.timeout,
                )

                if not data:
                    return SamvadaResponse(
                        success=False,
                        content="",
                        error="Empty response from server",
                        msg_id=msg.msg_id,
                    )

                json_str = data.decode("utf-8").strip()
                return SamvadaResponse.from_json(json_str)

            finally:
                writer.close()
                await writer.wait_closed()

        except FileNotFoundError:
            return SamvadaResponse(
                success=False,
                content="",
                error=f"MANAS is not running (socket not found: {self.socket_path})",
                msg_id=msg.msg_id,
            )
        except ConnectionRefusedError:
            return SamvadaResponse(
                success=False,
                content="",
                error="Connection refused - MANAS may not be running",
                msg_id=msg.msg_id,
            )
        except asyncio.TimeoutError:
            return SamvadaResponse(
                success=False,
                content="",
                error=f"Timeout after {self.timeout}s",
                msg_id=msg.msg_id,
            )
        except Exception as e:
            return SamvadaResponse(
                success=False,
                content="",
                error=str(e),
                msg_id=msg.msg_id,
            )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


async def chat(content: str) -> SamvadaResponse:
    """
    Quick function to send a chat message to MANAS.

    Usage:
        response = await chat("Status report")
        print(response.content)
    """
    client = SamvadaClient()
    return await client.send(content, msg_type="chat")


def chat_sync(content: str) -> SamvadaResponse:
    """
    Synchronous version of chat() for CLI usage.

    Usage:
        response = chat_sync("Status report")
        print(response.content)
    """
    return asyncio.run(chat(content))
