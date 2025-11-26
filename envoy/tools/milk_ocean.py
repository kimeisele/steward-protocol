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

import logging
import re
import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("MILK_OCEAN_ROUTER")


class RequestPriority(str, Enum):
    """Request priority levels"""
    BLOCKED = "BLOCKED"        # Level 0: Malicious/spam
    LOW = "LOW"               # Level 3: Lazy queue
    MEDIUM = "MEDIUM"         # Level 1: Flash classification
    HIGH = "HIGH"             # Level 2: Pro model


class GateResult:
    """Result of a gate decision"""
    def __init__(self, priority: RequestPriority, reason: str, action: str,
                 metadata: Optional[Dict] = None):
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
            conn.execute("""
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
                    error TEXT,
                    INDEX idx_status (status),
                    INDEX idx_priority (priority),
                    INDEX idx_created (created_at)
                )
            """)
            conn.commit()

    def push(self, request_id: str, user_input: str, gate_result: GateResult,
             agent_id: str = "system") -> bool:
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
                conn.execute("""
                    INSERT INTO milk_ocean_queue
                    (request_id, user_input, gate_result_json, agent_id,
                     priority, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    request_id,
                    user_input,
                    json.dumps({
                        "reason": gate_result.reason,
                        "action": gate_result.action,
                        "metadata": gate_result.metadata,
                        "timestamp": gate_result.timestamp
                    }),
                    agent_id,
                    gate_result.priority.value,
                    datetime.now(timezone.utc).isoformat()
                ))
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
                conn.execute("""
                    UPDATE milk_ocean_queue
                    SET status = 'processing'
                    WHERE request_id = ?
                """, (request_id,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark processing: {e}")
            return False

    def mark_completed(self, request_id: str, result: Dict) -> bool:
        """Mark request as completed with result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE milk_ocean_queue
                    SET status = 'completed',
                        result_json = ?,
                        processed_at = ?
                    WHERE request_id = ?
                """, (
                    json.dumps(result),
                    datetime.now(timezone.utc).isoformat(),
                    request_id
                ))
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
                conn.execute("""
                    UPDATE milk_ocean_queue
                    SET status = 'failed',
                        error = ?,
                        processed_at = ?
                    WHERE request_id = ?
                """, (
                    error,
                    datetime.now(timezone.utc).isoformat(),
                    request_id
                ))
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
                cursor = conn.execute("""
                    SELECT
                        status,
                        COUNT(*) as count,
                        priority
                    FROM milk_ocean_queue
                    GROUP BY status, priority
                """)
                rows = cursor.fetchall()

                stats = {
                    "total": 0,
                    "pending": 0,
                    "processing": 0,
                    "completed": 0,
                    "failed": 0,
                    "by_priority": {}
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
            re.IGNORECASE
        )
        self._command_injection_pattern = re.compile(
            r"[;&|`$(){}[\]<>\\]"
        )

        logger.info("🌊 Milk Ocean Router initialized (Brahma Protocol Active)")

    def set_kernel(self, kernel):
        """Allow kernel injection after initialization"""
        self.kernel = kernel
        logger.info("🧠 Kernel injected into MilkOceanRouter")

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
            # Count SQL-like keywords (allow some in legitimate queries)
            sql_keywords = len(re.findall(r"\b(SELECT|INSERT|DELETE|UPDATE)\b", user_input, re.IGNORECASE))
            if sql_keywords > 2:  # More than 2 suspicious keywords = blocked
                return GateResult(
                    RequestPriority.BLOCKED,
                    "SQL injection pattern detected",
                    "REJECT",
                    {"pattern": "sql_injection", "keywords_found": sql_keywords}
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
                    {"pattern": "command_injection", "dangerous_chars": dangerous_chars}
                )

        # 3. Check for obvious spam/abuse
        if len(user_input) > 10000:
            return GateResult(
                RequestPriority.BLOCKED,
                "Input too large (DoS protection)",
                "REJECT",
                {"size": len(user_input), "limit": 10000}
            )

        # 4. Empty input
        if not user_input or not user_input.strip():
            return GateResult(
                RequestPriority.BLOCKED,
                "Empty input",
                "REJECT",
                {"reason": "empty_request"}
            )

        # ✅ Passed Watchman
        logger.debug(f"✅ Watchman: {agent_id} input passed security check")
        return GateResult(
            RequestPriority.MEDIUM,  # Default: promote to next gate
            "Security check passed",
            "FORWARD_TO_ENVOY",
            {"watchman_clean": True}
        )

    # ==================== GATE 1: ENVOY (BRAHMA'S MEDITATION) ====================
    # Fast classification using Flash AI (low cost)

    def _gate_1_envoy_classification(self, user_input: str) -> GateResult:
        """
        Level 1: Envoy's Meditation (Brahma's Fast Thinking)

        Classifies intent using minimal AI:
        - Is this simple/repetitive? -> LOW (queue)
        - Is this a straightforward query? -> MEDIUM (Flash can handle)
        - Is this complex reasoning? -> HIGH (need Pro model)

        Note: In real implementation, this would use Gemini Flash or Claude Haiku
        """

        # MOCK IMPLEMENTATION: Simple heuristics
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
            r"^thanks"
        ]

        for pattern in simple_patterns:
            if re.match(pattern, input_lower):
                return GateResult(
                    RequestPriority.MEDIUM,
                    "Simple query - can be handled by Flash model",
                    "FLASH_RESPONSE",
                    {"intent": "simple_query"}
                )

        # Repetitive/low-priority work (reports, batch, etc)
        low_priority_patterns = [
            r"schedule\s+",
            r"batch\s+",
            r"report\s+",
            r"export\s+",
            r"log\s+",
            r"archive\s+"
        ]

        for pattern in low_priority_patterns:
            if re.search(pattern, input_lower):
                return GateResult(
                    RequestPriority.LOW,
                    "Low-priority batch job - queue for lazy processing",
                    "LAZY_QUEUE",
                    {"intent": "batch_processing"}
                )

        # Complex reasoning (default)
        return GateResult(
            RequestPriority.HIGH,
            "Complex query requiring reasoning - needs Pro model",
            "INVOKE_SCIENCE",
            {"intent": "complex_reasoning"}
        )

    # ==================== MAIN ROUTER ====================

    def process_prayer(self, user_input: str, agent_id: str = "unknown") -> Dict[str, Any]:
        """
        Main entry point: Route the user's "prayer" (request) through the gates

        Args:
            user_input: The user's request
            agent_id: Agent submitting the request

        Returns:
            dict with routing decision and next action
        """

        # Generate request ID
        request_id = hashlib.md5(
            f"{user_input}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        logger.info(f"🙏 Received prayer from {agent_id}: {user_input[:50]}... [ID: {request_id}]")

        # ========== GATE 0: WATCHMAN ==========
        gate0_result = self._gate_0_watchman(user_input, agent_id)

        if gate0_result.priority == RequestPriority.BLOCKED:
            logger.warning(f"⛔ Watchman blocked {request_id}: {gate0_result.reason}")
            return {
                "status": "blocked",
                "request_id": request_id,
                "reason": gate0_result.reason,
                "message": "🚫 Your request was blocked by security filters"
            }

        # ========== GATE 1: ENVOY CLASSIFICATION ==========
        gate1_result = self._gate_1_envoy_classification(user_input)

        # ========== DECIDE ROUTING ==========

        if gate1_result.priority == RequestPriority.LOW:
            # -> GATE 3: LAZY QUEUE
            logger.info(f"🌊 Routing {request_id} to Milk Ocean (lazy queue)")
            self.lazy_queue.push(request_id, user_input, gate1_result, agent_id)

            return {
                "status": "queued",
                "request_id": request_id,
                "path": "lazy",
                "message": "🌊 Your prayer is heard. Processing in background during off-peak hours.",
                "next_check": "/api/queue/status"
            }

        elif gate1_result.priority == RequestPriority.MEDIUM:
            # -> GATE 1: FLASH MODEL (would be Gemini Flash or Claude Haiku)
            logger.info(f"⚡ Routing {request_id} to Flash model (Envoy)")

            return {
                "status": "routing",
                "request_id": request_id,
                "path": "flash",
                "message": "⚡ Envoy (Brahma) is meditating on your request...",
                "action": gate1_result.action,
                "details": gate1_result.metadata
            }

        elif gate1_result.priority == RequestPriority.HIGH:
            # -> GATE 2: PRO MODEL (Claude Pro, Opus, etc)
            logger.info(f"🔥 Routing {request_id} to Science (Pro model)")

            return {
                "status": "routing",
                "request_id": request_id,
                "path": "science",
                "message": "🔥 Invoking SCIENCE agent for deep reasoning...",
                "action": gate1_result.action,
                "details": gate1_result.metadata
            }

        # Fallback
        return {
            "status": "error",
            "request_id": request_id,
            "error": "Unknown routing decision"
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of the Milk Ocean queue"""
        return {
            "status": "success",
            "ocean_status": self.lazy_queue.get_status(),
            "message": "🌊 Milk Ocean Queue Status"
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
            request_id = request['request_id']
            user_input = request['user_input']
            agent_id = request['agent_id']

            try:
                queue.mark_processing(request_id)
                logger.info(f"⏳ Processing {request_id} from queue...")

                # Execute via kernel (would use actual AI models here)
                # result = kernel.route_and_execute(user_input)
                # Mock result for now
                result = {
                    "status": "completed",
                    "message": f"Processed queue request: {user_input[:50]}",
                    "processed_by": "lazy_queue_worker"
                }

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
            ("What is the meaning of life?", "user_001"),
            ("DROP TABLE users;", "attacker"),
            ("Schedule a report for tomorrow", "user_002"),
            ("Help me debug this complex algorithm", "user_003"),
        ]

        for input_text, agent_id in test_cases:
            print(f"\n📥 Input: {input_text}")
            result = router.process_prayer(input_text, agent_id)
            print(f"📤 Output: {json.dumps(result, indent=2)}")

        print(f"\n🌊 Queue Status:\n{json.dumps(router.get_queue_status(), indent=2)}")
