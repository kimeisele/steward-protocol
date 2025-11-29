#!/usr/bin/env python3
"""
LAZY QUEUE WORKER - The Nightly Samadhi

This script processes the Milk Ocean queue of lazy requests.
Can be run as:
1. Cronjob: 0 2 * * * python /path/to/lazy_queue_worker.py
2. Systemd timer (systemd service file)
3. Supervisor daemon
4. Manual: python scripts/lazy_queue_worker.py --daemon

The script:
1. Connects to the Milk Ocean queue
2. Fetches pending requests (batched)
3. Processes each via the kernel
4. Marks complete/failed in queue
5. Logs all operations for audit trail

This ensures:
✅ Non-critical requests are processed asynchronously
✅ Expensive AI models (Pro) are used during off-peak hours
✅ Queue survives crashes (SQLite persistence)
✅ Full audit trail of all processing
"""

import argparse
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("data/logs/lazy_queue_worker.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("LAZY_QUEUE_WORKER")


class LazyQueueWorker:
    """
    Background worker for processing lazy queue requests
    """

    def __init__(self):
        self.running = True
        self.stats = {
            "batches_processed": 0,
            "requests_processed": 0,
            "requests_failed": 0,
            "start_time": datetime.now(timezone.utc).isoformat(),
        }

    def signal_handler(self, sig, frame):
        """Handle SIGTERM/SIGINT gracefully"""
        logger.info("🛑 Shutdown signal received. Finishing current batch...")
        self.running = False

    def run_batch(self, batch_size: int = 10):
        """
        Process one batch of requests from the queue

        Args:
            batch_size: Number of requests to process per batch
        """
        try:
            from envoy.tools.milk_ocean import LazyQueue

            from provider.universal_provider import UniversalProvider
            from vibe_core.kernel_impl import RealVibeKernel

            queue = LazyQueue()
            kernel = RealVibeKernel(ledger_path="data/vibe_ledger.db")
            kernel.boot()
            provider = UniversalProvider(kernel)

            logger.info("🌙 Fetching batch from Milk Ocean...")
            batch = queue.pop_batch(limit=batch_size)

            if not batch:
                logger.debug("💤 No pending requests in queue.")
                return 0

            logger.info(f"🎯 Processing batch of {len(batch)} requests...")
            self.stats["batches_processed"] += 1

            for request in batch:
                request_id = request["request_id"]
                user_input = request["user_input"]
                agent_id = request["agent_id"]

                try:
                    queue.mark_processing(request_id)
                    logger.info(f"⏳ [{request_id}] Processing: {user_input[:60]}...")

                    # Execute the request via the kernel/provider
                    result = provider.route_and_execute(user_input)

                    # Mark as completed
                    queue.mark_completed(request_id, result)
                    self.stats["requests_processed"] += 1

                    logger.info(f"✅ [{request_id}] Completed successfully")

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"❌ [{request_id}] Failed: {error_msg}")
                    queue.mark_failed(request_id, error_msg)
                    self.stats["requests_failed"] += 1

            logger.info(
                f"🏁 Batch complete. "
                f"Processed: {len(batch)}, "
                f"Failed: {sum(1 for r in batch if queue._get_status(r['request_id']) == 'failed')}"
            )

            return len(batch)

        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}", exc_info=True)
            return 0

    def run_daemon(self, interval: int = 300):
        """
        Run as a daemon, continuously processing queue

        Args:
            interval: Seconds to sleep between batches (default 5 minutes)
        """
        logger.info(f"🌙 Lazy Queue Worker started (checking every {interval}s)")

        # Register signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        while self.running:
            try:
                batch_size = self.run_batch(batch_size=10)

                if batch_size == 0:
                    logger.debug(f"💤 Sleeping for {interval}s...")
                    time.sleep(interval)
                else:
                    # If there are more requests, don't sleep - keep processing
                    logger.info("▶️  Processing next batch...")

            except Exception as e:
                logger.error(f"❌ Daemon error: {e}", exc_info=True)
                time.sleep(interval)

        logger.info("🌙 Lazy Queue Worker shutting down...")
        self._print_stats()

    def run_once(self):
        """
        Run a single batch (for cron jobs)
        """
        logger.info("🌙 Lazy Queue Worker (single batch mode)")
        self.run_batch(batch_size=10)
        self._print_stats()

    def _print_stats(self):
        """Print worker statistics"""
        logger.info("=" * 50)
        logger.info("📊 WORKER STATISTICS:")
        logger.info(f"   Start Time:       {self.stats['start_time']}")
        logger.info(f"   Batches:          {self.stats['batches_processed']}")
        logger.info(f"   Requests OK:      {self.stats['requests_processed']}")
        logger.info(f"   Requests FAILED:  {self.stats['requests_failed']}")
        logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Lazy Queue Worker - Process queued requests from Milk Ocean")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (continuous processing)")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between batches in daemon mode (seconds, default 300)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process single batch and exit (default for cron)",
    )

    args = parser.parse_args()

    worker = LazyQueueWorker()

    if args.daemon:
        worker.run_daemon(interval=args.interval)
    else:
        # Default: single batch (cron mode)
        worker.run_once()


if __name__ == "__main__":
    main()
