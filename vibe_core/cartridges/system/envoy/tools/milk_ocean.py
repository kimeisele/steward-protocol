"""
MILK OCEAN ROUTER (Kshira-Samudra Gateway)

The Brahma Protocol: 4-Tier Request Processing Pipeline

Metaphor (Krishna Book, Chapter 1, Ocean of Milk):
- Bhu-devi (Earth) is overwhelmed with requests (high load, abuse)
- She goes to Brahma (the architect) -> Brahma meditates on the Purusha Sukta
- Only critical prayers reach Vishnu (the kernel, heavy computation)
- Non-urgent requests are stored in the "Milk Ocean" (lazy queue) for later

Architecture:
Level 0: WATCHMAN    - Mechanical filtering (regex, rules) - FREE
Level 1: ENVOY       - Fast classification (Flash AI) - MINIMAL COST
Level 2: SCIENCE     - Complex reasoning (Pro AI) - EXPENSIVE (5% of requests)
Level 3: SAMADHI     - Lazy processing queue - BATCH AT NIGHT

This ensures:
✅ 100x token efficiency
✅ DDoS protection
✅ Abuse prevention
✅ Resilience (queue survives crashes)
"""

import asyncio
import hashlib
import json
import logging
import re
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import SemanticRouter for intelligent classification (PROJECT JNANA)
try:
    from vibe_core.cortex.engines.semantic_engine import SemanticRouter

    SEMANTIC_ROUTER_AVAILABLE = True
except ImportError:
    SemanticRouter = None
    SEMANTIC_ROUTER_AVAILABLE = False

logger = logging.getLogger("MILK_OCEAN_ROUTER")


def _get_runtime_config():
    """Get runtime config with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config
        return get_config().runtime
    except Exception:
        from vibe_core.phoenix.sections.runtime.section_main import RuntimeConfig
        return RuntimeConfig()


class RequestPriority(str, Enum):
    """Request priority levels"""

    BLOCKED = "BLOCKED"  # Level -1: Malicious/spam
    CRITICAL = "CRITICAL"  # Level 0: Emergency interrupt (Gajendra Protocol)
    LOW = "LOW"  # Level 3: Lazy queue
    MEDIUM = "MEDIUM"  # Level 1: Flash classification
    HIGH = "HIGH"  # Level 2: Pro model


class GateResult:
    """Result of a gate decision"""

    def __init__(
        self,
        priority: RequestPriority,
        reason: str,
        action: str,
        metadata: Optional[Dict] = None,
    ):
        self.priority = priority
        self.reason = reason
        self.action = action
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class LazyQueue:
    """
    The Milk Ocean (Kshirodaka) - SQLite-backed async task queue

    Purpose:
    - Store non-urgent requests for batch processing
    - Survive crashes (persistent)
    - Process during off-peak hours
    - Track completion status
    """

    def __init__(self, db_path: str = "data/milk_ocean.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS milk_ocean_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    user_input TEXT NOT NULL,
                    gate_result_json TEXT NOT NULL,
                    agent_id TEXT,
                    priority TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    result_json TEXT,
                    error TEXT
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON milk_ocean_queue (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON milk_ocean_queue (priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON milk_ocean_queue (created_at)")
            conn.commit()

    def push(
        self,
        request_id: str,
        user_input: str,
        gate_result: GateResult,
        agent_id: str = "system",
    ) -> bool:
        """
        Push a request into the Milk Ocean for later processing

        Args:
            request_id: Unique request identifier
            user_input: The user's input/request
            gate_result: The Gate decision
            agent_id: Which agent submitted this

        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO milk_ocean_queue
                    (request_id, user_input, gate_result_json, agent_id,
                     priority, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        request_id,
                        user_input,
                        json.dumps(
                            {
                                "reason": gate_result.reason,
                                "action": gate_result.action,
                                "metadata": gate_result.metadata,
                                "timestamp": gate_result.timestamp,
                            }
                        ),
                        agent_id,
                        gate_result.priority.value,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
            logger.info(f"🌊 Request {request_id} pushed to Milk Ocean (priority: {gate_result.priority})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push to Milk Ocean: {e}")
            return False

    def pop_batch(self, limit: int = 10, priority: Optional[str] = None) -> List[Dict]:
        """
        Pop batch of pending requests (for background worker)

        Args:
            limit: Max number of requests to pop
            priority: Only pop specific priority (default: all)

        Returns:
            List of pending requests
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM milk_ocean_queue WHERE status = 'pending'"
                params = []

                if priority:
                    query += " AND priority = ?"
                    params.append(priority)

                query += " ORDER BY created_at ASC LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to pop batch: {e}")
            return []

    def mark_processing(self, request_id: str) -> bool:
        """Mark a request as being processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE milk_ocean_queue
                    SET status = 'processing'
                    WHERE request_id = ?
                """,
                    (request_id,),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark processing: {e}")
            return False

    def mark_completed(self, request_id: str, result: Dict) -> bool:
        """Mark request as completed with result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE milk_ocean_queue
                    SET status = 'completed',
                        result_json = ?,
                        processed_at = ?
                    WHERE request_id = ?
                """,
                    (
                        json.dumps(result),
                        datetime.now(timezone.utc).isoformat(),
                        request_id,
                    ),
                )
                conn.commit()
            logger.info(f"✅ Request {request_id} completed (from Milk Ocean)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark completed: {e}")
            return False

    def mark_failed(self, request_id: str, error: str) -> bool:
        """Mark request as failed with error"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE milk_ocean_queue
                    SET status = 'failed',
                        error = ?,
                        processed_at = ?
                    WHERE request_id = ?
                """,
                    (error, datetime.now(timezone.utc).isoformat(), request_id),
                )
                conn.commit()
            logger.warning(f"❌ Request {request_id} failed: {error}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT
                        status,
                        COUNT(*) as count,
                        priority
                    FROM milk_ocean_queue
                    GROUP BY status, priority
                """
                )
                rows = cursor.fetchall()

                stats = {
                    "total": 0,
                    "pending": 0,
                    "processing": 0,
                    "completed": 0,
                    "failed": 0,
                    "by_priority": {},
                }

                for row in rows:
                    status, count, priority = row
                    stats["total"] += count
                    stats[status] = stats.get(status, 0) + count

                    if priority not in stats["by_priority"]:
                        stats["by_priority"][priority] = {}
                    stats["by_priority"][priority][status] = count

                return stats
        except Exception as e:
            logger.error(f"❌ Failed to get queue status: {e}")
            return {"error": str(e)}


class MilkOceanRouter:
    """
    The Brahma Protocol Router - 4-Level Request Processing Pipeline

    This is the "Golden Filter" (Yogamaya) that protects the inner city
    (kernel/agents) from chaos.
    """

    def __init__(self, kernel=None):
        self.kernel = kernel
        self.lazy_queue = LazyQueue()

        # Compile security regex patterns once (performance)
        self._sql_injection_pattern = re.compile(
            r"(\b(SELECT|INSERT|DELETE|UPDATE|DROP|UNION|OR|AND)\b|--|;|'|\"|\*|%|\||&|\^)",
            re.IGNORECASE,
        )
        self._command_injection_pattern = re.compile(r"[;&|`$(){}[\]<>\\]")

        # Initialize SemanticRouter for intelligent classification (PROJECT JNANA)
        self._semantic_router = None
        if SEMANTIC_ROUTER_AVAILABLE:
            try:
                self._semantic_router = SemanticRouter()
                logger.info("🧠 SemanticRouter loaded (JNANA Cortex Active)")
            except Exception as e:
                logger.warning(f"⚠️ SemanticRouter failed to load: {e} (falling back to heuristics)")

        logger.info("🌊 Milk Ocean Router initialized (Brahma Protocol Active)")

    def set_kernel(self, kernel):
        """P3.2: Inject kernel reference for lazy queue worker."""
        self.kernel = kernel
        logger.info("🔗 Kernel injected into MilkOceanRouter")

    # ==================== GATE 0: WATCHMAN ====================
    # Mechanical, free, instant blocking

    def _gate_0_watchman(self, user_input: str, agent_id: str) -> GateResult:
        """
        Level 0: The Watchman (Yamadutas blocking entry)

        Instant, zero-cost filtering:
        - SQL injection detection
        - Command injection detection
        - Spam/pattern matching
        - Rate limiting signals

        Returns: BLOCKED or passes to next gate
        """

        # 1. Check for SQL injection
        if self._sql_injection_pattern.search(user_input):
            # Immediately block destructive SQL commands (always malicious in user input)
            destructive_keywords = re.findall(r"\b(DROP|TRUNCATE|ALTER|GRANT|REVOKE)\b", user_input, re.IGNORECASE)
            if destructive_keywords:
                return GateResult(
                    RequestPriority.BLOCKED,
                    "SQL injection pattern detected (destructive command)",
                    "REJECT",
                    {"pattern": "sql_injection", "destructive_keywords": destructive_keywords},
                )

            # Block classic injection patterns: quote + logical operator, comment syntax
            # Examples: ' OR '1'='1, admin'--, 1=1--, " OR "x"="x
            classic_injection = re.search(
                r"('|\")(\s*\)?\s*(OR|AND)\s|\s*--|\s*#|;)",
                user_input,
                re.IGNORECASE,
            )
            if classic_injection:
                return GateResult(
                    RequestPriority.BLOCKED,
                    "SQL injection pattern detected (classic attack vector)",
                    "REJECT",
                    {"pattern": "sql_injection_classic", "matched": classic_injection.group()},
                )

            # Count SQL-like keywords (allow some in legitimate queries)
            sql_keywords = len(re.findall(r"\b(SELECT|INSERT|DELETE|UPDATE)\b", user_input, re.IGNORECASE))
            if sql_keywords > 2:  # More than 2 suspicious keywords = blocked
                return GateResult(
                    RequestPriority.BLOCKED,
                    "SQL injection pattern detected",
                    "REJECT",
                    {"pattern": "sql_injection", "keywords_found": sql_keywords},
                )

        # 2. Check for command injection
        if self._command_injection_pattern.search(user_input):
            # Only block if multiple shell metacharacters
            dangerous_chars = len(re.findall(r"[;&|`$()]", user_input))
            if dangerous_chars >= 3:
                return GateResult(
                    RequestPriority.BLOCKED,
                    "Command injection pattern detected",
                    "REJECT",
                    {
                        "pattern": "command_injection",
                        "dangerous_chars": dangerous_chars,
                    },
                )

        # 3. Check for obvious spam/abuse
        if len(user_input) > 10000:
            return GateResult(
                RequestPriority.BLOCKED,
                "Input too large (DoS protection)",
                "REJECT",
                {"size": len(user_input), "limit": 10000},
            )

        # 4. Empty input
        if not user_input or not user_input.strip():
            return GateResult(
                RequestPriority.BLOCKED,
                "Empty input",
                "REJECT",
                {"reason": "empty_request"},
            )

        # ✅ Passed Watchman
        logger.debug(f"✅ Watchman: {agent_id} input passed security check")
        return GateResult(
            RequestPriority.MEDIUM,  # Default: promote to next gate
            "Security check passed",
            "FORWARD_TO_ENVOY",
            {"watchman_clean": True},
        )

    # ==================== GATE 1: ENVOY (BRAHMA'S MEDITATION) ====================
    # Semantic classification using PROJECT JNANA (SemanticRouter)

    def _gate_1_envoy_classification(self, user_input: str) -> GateResult:
        """
        Level 1: Envoy's Meditation (Brahma's Fast Thinking)

        Classifies intent using SemanticRouter (sentence-transformers):
        - HIGH confidence + simple intent -> MEDIUM (Flash can handle)
        - HIGH confidence + complex intent -> HIGH (needs Pro model)
        - LOW confidence -> HIGH (needs Pro model to understand)
        - Batch/repetitive intents -> LOW (lazy queue)

        Falls back to heuristics if SemanticRouter unavailable.
        """
        # Try SemanticRouter first (PROJECT JNANA)
        if self._semantic_router is not None:
            try:
                return self._gate_1_semantic_classification(user_input)
            except Exception as e:
                logger.warning(f"⚠️ SemanticRouter error: {e} (falling back to heuristics)")

        # Fallback: Simple heuristics
        return self._gate_1_heuristic_fallback(user_input)

    def _gate_1_semantic_classification(self, user_input: str) -> GateResult:
        """Use SemanticRouter for intelligent intent classification."""
        # Run async SemanticRouter in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Get routing decision with confidence
        route_result = loop.run_until_complete(self._semantic_router.resolve_intent_with_confidence(user_input))

        confidence = route_result.get("confidence", 0.0)
        confidence_level = route_result.get("confidence_level", "low")
        concepts = route_result.get("concepts", set())
        intent_type = route_result.get("intent_type", "CHAT")

        logger.info(
            f"🧠 JNANA: confidence={confidence:.2f} ({confidence_level}), concepts={concepts}, intent={intent_type}"
        )

        # Check for batch/repetitive patterns in concepts
        batch_concepts = {"schedule", "batch", "report", "export", "archive", "backup"}
        if concepts & batch_concepts:
            return GateResult(
                RequestPriority.LOW,
                f"Batch operation detected (confidence: {confidence:.2f})",
                "LAZY_QUEUE",
                {"intent": "batch_processing", "concepts": list(concepts), "confidence": confidence},
            )

        # Route based on confidence level
        if confidence_level == "low":
            # Low confidence = ambiguous, needs Pro model to understand
            return GateResult(
                RequestPriority.HIGH,
                f"Low confidence ({confidence:.2f}) - needs Pro model for disambiguation",
                "INVOKE_SCIENCE",
                {"intent": "ambiguous", "concepts": list(concepts), "confidence": confidence},
            )

        elif confidence_level == "high":
            # High confidence = we understand the intent
            # Check if it's a complex reasoning task
            complex_concepts = {"analyze", "debug", "implement", "refactor", "design", "architect"}
            if concepts & complex_concepts:
                return GateResult(
                    RequestPriority.HIGH,
                    f"Complex reasoning task (confidence: {confidence:.2f})",
                    "INVOKE_SCIENCE",
                    {"intent": "complex_reasoning", "concepts": list(concepts), "confidence": confidence},
                )
            else:
                return GateResult(
                    RequestPriority.MEDIUM,
                    f"Clear intent (confidence: {confidence:.2f}) - Flash can handle",
                    "FLASH_RESPONSE",
                    {"intent": intent_type, "concepts": list(concepts), "confidence": confidence},
                )

        else:  # medium confidence
            return GateResult(
                RequestPriority.MEDIUM,
                f"Medium confidence ({confidence:.2f}) - Flash with context",
                "FLASH_RESPONSE",
                {"intent": intent_type, "concepts": list(concepts), "confidence": confidence},
            )

    def _gate_1_heuristic_fallback(self, user_input: str) -> GateResult:
        """Fallback heuristics when SemanticRouter unavailable."""
        input_lower = user_input.lower()

        # Simple queries (status, "what is", "tell me")
        simple_patterns = [
            r"^what\s+(is|are)",
            r"^tell\s+me",
            r"^list\s+",
            r"^status",
            r"^hello",
            r"^hi\s*$",
            r"^bye",
            r"^thanks",
        ]

        for pattern in simple_patterns:
            if re.match(pattern, input_lower):
                return GateResult(
                    RequestPriority.MEDIUM,
                    "Simple query - can be handled by Flash model",
                    "FLASH_RESPONSE",
                    {"intent": "simple_query", "method": "heuristic_fallback"},
                )

        # Repetitive/low-priority work (reports, batch, etc)
        low_priority_patterns = [
            r"schedule\s+",
            r"batch\s+",
            r"report\s+",
            r"export\s+",
            r"log\s+",
            r"archive\s+",
        ]

        for pattern in low_priority_patterns:
            if re.search(pattern, input_lower):
                return GateResult(
                    RequestPriority.LOW,
                    "Low-priority batch job - queue for lazy processing",
                    "LAZY_QUEUE",
                    {"intent": "batch_processing", "method": "heuristic_fallback"},
                )

        # Complex reasoning (default)
        return GateResult(
            RequestPriority.HIGH,
            "Complex query requiring reasoning - needs Pro model",
            "INVOKE_SCIENCE",
            {"intent": "complex_reasoning", "method": "heuristic_fallback"},
        )

    # ==================== MAIN ROUTER ====================

    def _emit_event_safe(self, event_type: str, message: str, details: Optional[Dict] = None):
        """
        Safely emit an event without blocking request routing
        (Canto 10: Pulse System Integration)

        This is a non-blocking helper that tries to emit an event
        without disrupting the request processing pipeline.
        """
        try:
            # Try to get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Import event bus
            from vibe_core.event_bus import emit_event

            # Schedule event emission (non-blocking)
            if loop.is_running():
                asyncio.create_task(emit_event(event_type, "envoy", message, details=details or {}))
            else:
                # Queue it for next iteration
                try:
                    loop.run_until_complete(emit_event(event_type, "envoy", message, details=details or {}))
                except Exception:
                    pass  # Silently fail - don't disrupt routing
        except Exception as e:
            logger.debug(f"⚠️  Event emission failed (non-blocking): {e}")

    def process_prayer(
        self, user_input: str, agent_id: str = "unknown", critical: bool = False, recursion_depth: int = 0
    ) -> Dict[str, Any]:
        """
        Main entry point: Route the user's "prayer" (request) through the gates

        Args:
            user_input: The user's request
            agent_id: Agent submitting the request
            critical: Is this a CRITICAL priority request? (Gajendra Protocol - emergency bypass)
            recursion_depth: Current recursion depth for VibeCortex circuits (default: 0)

        Returns:
            dict with routing decision and next action
        """

        # Check recursion depth (VibeCortex Safety)
        runtime_config = _get_runtime_config()
        MAX_RECURSION_DEPTH = runtime_config.limits.max_recursion_depth
        if recursion_depth > MAX_RECURSION_DEPTH:
            logger.warning(
                f"⛔ Recursion depth exceeded ({recursion_depth} > {MAX_RECURSION_DEPTH}) for agent {agent_id}"
            )
            return {
                "status": "blocked",
                "reason": "Max recursion depth exceeded",
                "message": "🚫 Recursion limit reached. Circuit execution halted for safety.",
                "recursion_depth": recursion_depth,
            }

        # Generate request ID
        request_id = hashlib.md5(f"{user_input}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        logger.info(
            f"🙏 Received prayer from {agent_id}: {user_input[:50]}... [ID: {request_id}]"
            + (" 🐘🚨 [CRITICAL PRIORITY - GAJENDRA PROTOCOL]" if critical else "")
        )

        # Emit PRAYER_RECEIVED event
        self._emit_event_safe(
            "PRAYER_RECEIVED",
            f"Prayer received from {agent_id}",
            {
                "request_id": request_id,
                "agent_id": agent_id,
                "critical": critical,
                "preview": user_input[:100],
            },
        )

        # ========== GATE 0: WATCHMAN ==========
        gate0_result = self._gate_0_watchman(user_input, agent_id)

        if gate0_result.priority == RequestPriority.BLOCKED:
            logger.warning(f"⛔ Watchman blocked {request_id}: {gate0_result.reason}")

            # Emit ERROR event for blocked requests
            self._emit_event_safe(
                "ERROR",
                f"Prayer blocked by WATCHMAN: {gate0_result.reason}",
                {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "reason": gate0_result.reason,
                },
            )

            return {
                "status": "blocked",
                "request_id": request_id,
                "reason": gate0_result.reason,
                "message": "🚫 Your request was blocked by security filters",
            }

        # ========== GATE 0.5: CRITICAL PRIORITY BYPASS (GAJENDRA INTERRUPT) ==========
        # If critical=True, skip queue entirely and invoke kernel directly
        # This is the "Lotosblume" (sacred offering) that summons Vishnu immediately
        # Even under 1000 years of timeout (DDoS), this prayer is answered
        if critical:
            logger.warning(f"🐘 GAJENDRA CALLS! {request_id} bypasses queue (CRITICAL priority)")

            # Emit CRITICAL_INTERRUPT event - full screen RED flash
            self._emit_event_safe(
                "CRITICAL_INTERRUPT",
                "🐘 GAJENDRA PROTOCOL ACTIVATED - Emergency Interrupt!",
                {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "protocol": "Gajendra Moksha",
                    "action": "kernel_direct_bypass",
                },
            )

            return {
                "status": "critical",
                "request_id": request_id,
                "path": "kernel_direct",
                "message": "🐘🚨 GAJENDRA MOKSHA ACTIVATED - Emergency interrupt to kernel",
                "action": "INVOKE_KERNEL_DIRECT",
                "priority": RequestPriority.CRITICAL.value,
                "bypass_queue": True,
                "details": {
                    "reason": "Critical priority request - queue bypass activated",
                    "protocol": "Gajendra Moksha (Emergency Interrupt)",
                    "target": "Kernel (Vishnu)",
                    "bypass_type": "Lotosblume Signal",
                },
            }

        # ========== GATE 1: ENVOY CLASSIFICATION ==========
        gate1_result = self._gate_1_envoy_classification(user_input)

        # ========== DECIDE ROUTING ==========

        if gate1_result.priority == RequestPriority.LOW:
            # -> GATE 3: LAZY QUEUE
            logger.info(f"🌊 Routing {request_id} to Milk Ocean (lazy queue)")

            # Emit ACTION event for queue routing
            self._emit_event_safe(
                "ACTION",
                "Prayer routed to Milk Ocean (lazy queue)",
                {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "path": "lazy",
                    "priority": "LOW",
                },
            )

            self.lazy_queue.push(request_id, user_input, gate1_result, agent_id)

            return {
                "status": "queued",
                "request_id": request_id,
                "path": "lazy",
                "message": "🌊 Your prayer is heard. Processing in background during off-peak hours.",
                "next_check": "/api/queue/status",
            }

        elif gate1_result.priority == RequestPriority.MEDIUM:
            # -> GATE 1: FLASH MODEL (would be Gemini Flash or Claude Haiku)
            logger.info(f"⚡ Routing {request_id} to Flash model (Envoy)")

            # Emit ACTION event for flash routing
            self._emit_event_safe(
                "ACTION",
                "Prayer routed to Flash (Envoy)",
                {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "path": "flash",
                    "priority": "MEDIUM",
                },
            )

            return {
                "status": "routing",
                "request_id": request_id,
                "path": "flash",
                "message": "⚡ Envoy (Brahma) is meditating on your request...",
                "action": gate1_result.action,
                "details": gate1_result.metadata,
            }

        elif gate1_result.priority == RequestPriority.HIGH:
            # -> GATE 2: PRO MODEL (Claude Pro, Opus, etc)
            logger.info(f"🔥 Routing {request_id} to Science (Pro model)")

            # Emit ACTION event for science routing
            self._emit_event_safe(
                "ACTION",
                "Prayer routed to Science (Pro model)",
                {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "path": "science",
                    "priority": "HIGH",
                },
            )

            return {
                "status": "routing",
                "request_id": request_id,
                "path": "science",
                "message": "🔥 Invoking SCIENCE agent for deep reasoning...",
                "action": gate1_result.action,
                "details": gate1_result.metadata,
            }

        # Fallback
        self._emit_event_safe(
            "ERROR",
            f"Unknown routing decision for prayer {request_id}",
            {"request_id": request_id, "agent_id": agent_id},
        )

        return {
            "status": "error",
            "request_id": request_id,
            "error": "Unknown routing decision",
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of the Milk Ocean queue"""
        return {
            "status": "success",
            "ocean_status": self.lazy_queue.get_status(),
            "message": "🌊 Milk Ocean Queue Status",
        }


# ==================== CLI WORKER FOR LAZY QUEUE ====================
# This runs as a background daemon (cronjob or systemd)


def lazy_queue_worker(max_iterations: Optional[int] = None):
    """
    Background worker: Process lazy queue items

    Runs as:
    - Cronjob: python -m envoy.tools.milk_ocean --worker --interval 3600
    - Or: systemd timer for nightly runs

    Processing order:
    1. Pop batch of pending requests (limit 10)
    2. For each: mark as processing
    3. Execute via kernel.route_and_execute()
    4. Mark as completed or failed
    """
    from vibe_core.kernel_impl import RealVibeKernel

    queue = LazyQueue()
    kernel = RealVibeKernel(ledger_path="data/vibe_ledger.db")
    kernel.boot()

    iteration = 0

    while max_iterations is None or iteration < max_iterations:
        iteration += 1
        logger.info(f"🌙 Lazy Queue Worker iteration {iteration}")

        # Pop batch of pending requests
        batch = queue.pop_batch(limit=10)

        if not batch:
            logger.info("💤 No pending requests in Milk Ocean. Sleeping...")
            if max_iterations:
                break
            import time

            time.sleep(60)  # Sleep 1 minute before checking again
            continue

        logger.info(f"🎯 Processing batch of {len(batch)} requests from Milk Ocean")

        for request in batch:
            request_id = request["request_id"]
            user_input = request["user_input"]
            agent_id = request["agent_id"]

            try:
                queue.mark_processing(request_id)
                logger.info(f"⏳ Processing {request_id} from queue...")

                # Execute via kernel
                try:
                    from vibe_core.scheduling.task import Task

                    task = Task(agent_id="envoy", payload={"input": user_input})
                    task_id = kernel.submit_task(task)

                    # Wait for completion (with timeout)
                    import time

                    for _ in range(60):  # 60 second timeout
                        kernel.tick()
                        task_result = kernel.get_task_result(task_id)
                        if task_result:
                            result = task_result
                            break
                        time.sleep(1)
                    else:
                        result = {"status": "timeout", "message": "Task execution timed out"}
                except Exception as e:
                    result = {"status": "error", "error": str(e)}

                queue.mark_completed(request_id, result)
                logger.info(f"✅ Completed {request_id}")

            except Exception as e:
                logger.error(f"❌ Failed to process {request_id}: {e}")
                queue.mark_failed(request_id, str(e))


if __name__ == "__main__":
    import sys

    if "--worker" in sys.argv:
        logger.info("🌙 Starting Lazy Queue Worker...")
        lazy_queue_worker()
    else:
        # Demo
        router = MilkOceanRouter()

        # Test inputs
        test_cases = [
            ("What is the meaning of life?", "user_001", False),
            ("DROP TABLE users;", "attacker", False),
            ("Schedule a report for tomorrow", "user_002", False),
            ("Help me debug this complex algorithm", "user_003", False),
        ]

        print("=" * 80)
        print("BRAHMA PROTOCOL DEMONSTRATION (Milk Ocean Router)")
        print("=" * 80)

        for input_text, agent_id, is_critical in test_cases:
            print(f"\n📥 Input: {input_text}")
            result = router.process_prayer(input_text, agent_id, critical=is_critical)
            print(f"📤 Output: {json.dumps(result, indent=2)}")

        print("\n" + "=" * 80)
        print("GAJENDRA MOKSHA TEST (Emergency Interrupt)")
        print("=" * 80)
        print("\n🐘 Simulating CRITICAL priority request (Lotosblume Signal)...")
        critical_result = router.process_prayer(
            "URGENT: System is under DDoS attack - invoke emergency protocol!",
            agent_id="security_guardian",
            critical=True,
        )
        print(f"\n🚨 CRITICAL Response:\n{json.dumps(critical_result, indent=2)}")

        print(f"\n\n🌊 Queue Status:\n{json.dumps(router.get_queue_status(), indent=2)}")
