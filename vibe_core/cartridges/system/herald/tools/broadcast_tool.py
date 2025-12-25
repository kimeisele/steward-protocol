"""
HERALD Broadcast Tool - Social media publishing (Twitter, Reddit) (Tool Protocol).

OPUS-307 D.2: Full DI via ServiceRegistry. No legacy fallback.
Dependencies come from TwitterProtocol/RedditProtocol.
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols import RedditProtocol, TwitterProtocol

logger = logging.getLogger("HERALD_BROADCAST")


class BroadcastTool(Tool):
    """
    Multi-platform content distribution via DI.

    OPUS-307 D.2: SSOT - All dependencies from ServiceRegistry.
    - TwitterProtocol: Registered by HeraldCartridge
    - RedditProtocol: Registered by HeraldCartridge

    If protocols not registered, operates in offline/simulation mode.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """
        Initialize broadcast tool via DI.

        Args:
            services: ServiceRegistry for dependency injection
        """
        super().__init__(services)

        # OPUS-307 D.2: Get typed protocols from registry
        self._twitter: Optional["TwitterProtocol"] = None
        self._reddit: Optional["RedditProtocol"] = None

        if self.services:
            from vibe_core.protocols import RedditProtocol, TwitterProtocol

            self._twitter = self.services.get(TwitterProtocol)
            self._reddit = self.services.get(RedditProtocol)

        # Log DI status
        twitter_status = "✅" if self._twitter else "❌"
        reddit_status = "✅" if self._reddit else "❌"
        logger.info(f"BroadcastTool: Twitter {twitter_status}, Reddit {reddit_status}")

    @property
    def name(self) -> str:
        return "herald.broadcast"

    @property
    def description(self) -> str:
        return "Publish content, scan mentions, and reply on social media platforms (Twitter, Reddit)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'publish', 'scan_mentions', 'reply', 'verify_credentials'",
            },
            "content": {
                "type": "string",
                "required": False,
                "description": "Content to publish/reply",
            },
            "platform": {
                "type": "string",
                "required": False,
                "description": "Platform: 'twitter' or 'reddit' (default: twitter)",
            },
            "tweet_id": {
                "type": "string",
                "required": False,
                "description": "Tweet ID for replies",
            },
            "since_id": {
                "type": "string",
                "required": False,
                "description": "Last processed mention ID",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate broadcast parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["publish", "scan_mentions", "reply", "verify_credentials"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        if action == "publish" and "content" not in parameters:
            raise ValueError("publish action requires 'content' parameter")

        if action == "reply":
            if "content" not in parameters:
                raise ValueError("reply action requires 'content' parameter")
            if "tweet_id" not in parameters:
                raise ValueError("reply action requires 'tweet_id' parameter")

        if "platform" in parameters and parameters["platform"] not in ["twitter", "reddit"]:
            raise ValueError("platform must be 'twitter' or 'reddit'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute broadcast operation via injected services."""
        try:
            action = parameters["action"]
            platform = parameters.get("platform", "twitter")

            if action == "publish":
                content = parameters["content"]
                if platform == "twitter":
                    success = self._twitter.publish(content) if self._twitter else self._simulate("publish", content)
                else:
                    success = (
                        self._reddit.post("LocalLLaMA", "Steward Update", content)
                        if self._reddit
                        else self._simulate("post", content)
                    )

                return ToolResult(
                    success=success,
                    output={
                        "published": success,
                        "platform": platform,
                        "content_preview": content[:80] + "..." if len(content) > 80 else content,
                    },
                )

            elif action == "scan_mentions":
                since_id = parameters.get("since_id")
                if self._twitter:
                    mentions = self._twitter.scan_mentions(since_id)
                else:
                    mentions = []
                    logger.info("🎭 SIMULATION: No mentions (offline)")

                return ToolResult(
                    success=True,
                    output={"mentions": mentions, "count": len(mentions), "platform": platform},
                )

            elif action == "reply":
                tweet_id = parameters["tweet_id"]
                content = parameters["content"]
                success = self._twitter.reply(tweet_id, content) if self._twitter else self._simulate("reply", content)

                return ToolResult(
                    success=success,
                    output={"replied": success, "tweet_id": tweet_id},
                )

            elif action == "verify_credentials":
                if platform == "twitter":
                    verified = self._twitter.verify_credentials() if self._twitter else False
                else:
                    verified = self._reddit.verify_credentials() if self._reddit else False

                return ToolResult(
                    success=True,
                    output={
                        "verified": verified,
                        "platform": platform,
                        "status": "authenticated" if verified else "offline",
                    },
                )

            return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"BroadcastTool error: {e}", exc_info=True)
            return ToolResult(success=False, error=str(e))

    def _simulate(self, action: str, content: str) -> bool:
        """Simulation mode when services not available."""
        logger.info(f"🎭 SIMULATION: Would {action}: {content[:50]}...")
        return True
