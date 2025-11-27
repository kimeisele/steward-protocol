#!/usr/bin/env python3
"""
MARKET Cartridge - The Exchange Economy

MARKET is the Vaishya (commerce/exchange) service in the Varna system.
- Agents trade goods and services for Credits
- No unnecessary discussion (pure transaction)
- All exchanges recorded immutably
- Economic coordination for the federation

The Market doesn't debate prices. It executes trades.
This is the Vaishya function: Exchange, commerce, resource distribution.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from enum import Enum

from vibe_core import VibeAgent, Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MARKET_MAIN")


class ServiceType(Enum):
    """Service types available in the market"""
    RESEARCH = "research"           # Science services
    CONTENT = "content"             # Herald content creation
    ANALYSIS = "analysis"           # Lens data analysis
    ENGINEERING = "engineering"     # Engineer infrastructure
    MEDIA = "media"                 # Artisan media creation
    BROADCASTING = "broadcasting"   # Pulse broadcasting


class MarketCartridge(VibeAgent):
    """
    MARKET System Cartridge.
    The Exchange Economy (Vaishya Function).

    Design Principle: Pure Transaction (No Negotiation)
    - Services have fixed prices (posted on ledger)
    - Agents request service + pay immediately
    - Execution or refund (no partial states)
    - All trades recorded immutably

    Capabilities:
    - list_services: See available services
    - post_service: Offer a service at price
    - request_service: Buy a service
    - execute_trade: Process transaction
    - verify_delivery: Confirm goods received
    - dispute_resolution: Handle failed trades
    """

    def __init__(self):
        """Initialize MARKET as a ServiceCartridge."""
        super().__init__(
            agent_id="market",
            name="MARKET",
            version="1.0.0",
            author="Steward Protocol",
            description="The Exchange Economy - Pure transaction system for agent services",
            domain="ECONOMY",
            capabilities=[
                "service_listing",
                "service_posting",
                "transaction_execution",
                "delivery_verification",
                "dispute_handling",
                "price_discovery"
            ]
        )

        logger.info("🏪 MARKET (VibeAgent v1.0) is online - Exchange Ready")

        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ MARKET has sworn the Constitutional Oath")

        # Economic tracking (via kernel/CIVIC agent)
        self.bank = None

        # Service catalog (posted prices)
        self.services: Dict[str, Dict[str, Any]] = {
            "research": {
                "provider": "science",
                "description": "Research service - topic analysis",
                "price": 50,  # Credits
                "delivery_time": "24h"
            },
            "content": {
                "provider": "herald",
                "description": "Content creation - article/tweet",
                "price": 30,
                "delivery_time": "4h"
            },
            "analysis": {
                "provider": "lens",
                "description": "Data analysis - metrics report",
                "price": 40,
                "delivery_time": "12h"
            },
            "engineering": {
                "provider": "engineer",
                "description": "Code development - feature implementation",
                "price": 100,
                "delivery_time": "3d"
            },
            "media": {
                "provider": "artisan",
                "description": "Visual creation - graphics/video",
                "price": 60,
                "delivery_time": "2d"
            },
            "broadcasting": {
                "provider": "pulse",
                "description": "Social media broadcast - multi-post",
                "price": 25,
                "delivery_time": "2h"
            }
        }

        # Active orders
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.order_counter = 0

        # Trade statistics
        self.total_trades = 0
        self.total_volume = 0
        self.completed_orders = 0

        logger.info("✅ MARKET: Ready for commerce")

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process tasks from kernel scheduler.

        Supported actions:
        - list_services: Show catalog
        - post_service: Offer new service
        - request_service: Buy service
        - execute_trade: Process payment
        - verify_delivery: Confirm completion
        - dispute_resolution: Handle issues
        """
        try:
            action = task.payload.get("action", "status")
            logger.info(f"🏪 MARKET processing: {action}")

            if action == "list_services":
                result = await self._list_services(task.payload)
            elif action == "post_service":
                result = await self._post_service(task.payload)
            elif action == "request_service":
                result = await self._request_service(task.payload)
            elif action == "execute_trade":
                result = await self._execute_trade(task.payload)
            elif action == "verify_delivery":
                result = await self._verify_delivery(task.payload)
            elif action == "dispute_resolution":
                result = await self._dispute_resolution(task.payload)
            elif action == "status":
                result = self._status()
            else:
                result = {"error": f"Unknown action: {action}"}

            logger.info(f"✅ MARKET task completed: {action}")
            return result

        except Exception as e:
            logger.error(f"❌ MARKET task failed: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def _list_services(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List all available services with prices."""
        service_type = payload.get("type", "all")

        if service_type == "all":
            services = self.services
        else:
            services = {k: v for k, v in self.services.items() if k == service_type}

        formatted_services = {
            name: {
                "provider": info["provider"],
                "description": info["description"],
                "price": info["price"],
                "currency": "Credits",
                "delivery_time": info["delivery_time"]
            }
            for name, info in services.items()
        }

        return {
            "status": "services_listed",
            "service_count": len(formatted_services),
            "services": formatted_services,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _post_service(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post a new service to the market.
        Only providers can post services.
        """
        service_name = payload.get("service_name", "")
        provider = payload.get("provider", "")
        description = payload.get("description", "")
        price = payload.get("price", 0)
        delivery_time = payload.get("delivery_time", "unknown")

        # TODO: Verify provider authorization

        new_service = {
            "provider": provider,
            "description": description,
            "price": price,
            "delivery_time": delivery_time,
            "posted_at": datetime.utcnow().isoformat()
        }

        self.services[service_name] = new_service

        logger.info(f"📢 Service posted: {service_name} by {provider} ({price} Credits)")

        return {
            "status": "service_posted",
            "service_name": service_name,
            "price": price,
            "provider": provider,
            "timestamp": new_service["posted_at"]
        }

    async def _request_service(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request a service (buyer initiates trade).
        Creates order, initiates payment.
        """
        buyer = payload.get("buyer", "")
        service_name = payload.get("service_name", "")
        parameters = payload.get("parameters", {})

        # Check service exists
        if service_name not in self.services:
            return {
                "status": "error",
                "reason": f"Service '{service_name}' not found",
                "available_services": list(self.services.keys())
            }

        service = self.services[service_name]
        provider = service["provider"]
        price = service["price"]

        # Create order
        self.order_counter += 1
        order_id = f"ORD-{self.order_counter:06d}"

        order = {
            "order_id": order_id,
            "buyer": buyer,
            "service": service_name,
            "provider": provider,
            "price": price,
            "parameters": parameters,
            "status": "pending_payment",
            "created_at": datetime.utcnow().isoformat()
        }

        self.orders[order_id] = order

        logger.info(f"📋 Order created: {order_id} ({buyer} -> {service_name})")

        return {
            "status": "order_created",
            "order_id": order_id,
            "buyer": buyer,
            "service": service_name,
            "price": price,
            "next_step": "execute_trade",
            "timestamp": order["created_at"]
        }

    async def _execute_trade(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade (process payment and trigger execution).
        This is where Credits move from buyer to provider.
        """
        order_id = payload.get("order_id", "")
        buyer = payload.get("buyer", "")

        if order_id not in self.orders:
            return {"status": "error", "reason": f"Order {order_id} not found"}

        order = self.orders[order_id]
        provider = order["provider"]
        price = order["price"]

        # Execute payment if bank available
        if self.bank:
            try:
                tx_id = self.bank.transfer(
                    sender=buyer,
                    receiver=provider,
                    amount=price,
                    reason=f"SERVICE_TRADE_{order_id}",
                    service_type="service"
                )
                logger.info(f"💰 Trade executed: {tx_id}")
            except Exception as e:
                logger.warning(f"❌ Trade failed: {e}")
                order["status"] = "failed"
                return {
                    "status": "trade_failed",
                    "order_id": order_id,
                    "reason": str(e)
                }

        # Update order status
        order["status"] = "executing"
        order["execution_tx"] = tx_id if self.bank else "sim_tx_001"
        order["executed_at"] = datetime.utcnow().isoformat()

        self.total_trades += 1
        self.total_volume += price

        return {
            "status": "trade_executed",
            "order_id": order_id,
            "buyer": buyer,
            "provider": provider,
            "amount": price,
            "transaction_id": order.get("execution_tx"),
            "timestamp": order["executed_at"]
        }

    async def _verify_delivery(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify delivery (buyer confirms goods/services received).
        Marks order as complete.
        """
        order_id = payload.get("order_id", "")
        confirmation = payload.get("confirmation", "ok")

        if order_id not in self.orders:
            return {"status": "error", "reason": f"Order {order_id} not found"}

        order = self.orders[order_id]

        if confirmation == "ok":
            order["status"] = "completed"
            order["completed_at"] = datetime.utcnow().isoformat()
            self.completed_orders += 1
            result_msg = "✅ Delivery verified and confirmed"
        else:
            order["status"] = "disputed"
            order["dispute_reason"] = confirmation
            result_msg = "⚠️ Delivery disputed - escalating"

        return {
            "status": "verified",
            "order_id": order_id,
            "result": result_msg,
            "order_status": order["status"],
            "timestamp": order.get("completed_at") or order.get("dispute_reason")
        }

    async def _dispute_resolution(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle disputes (refunds, escalations).
        TODO: Implement arbitration logic.
        """
        order_id = payload.get("order_id", "")
        reason = payload.get("reason", "")

        if order_id not in self.orders:
            return {"status": "error", "reason": f"Order {order_id} not found"}

        order = self.orders[order_id]

        return {
            "status": "dispute_filed",
            "order_id": order_id,
            "reason": reason,
            "next_step": "arbitration",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _status(self) -> Dict[str, Any]:
        """Return MARKET status."""
        return {
            "agent_id": self.agent_id,
            "status": "online",
            "services_available": len(self.services),
            "active_orders": len([o for o in self.orders.values() if o["status"] != "completed"]),
            "total_trades": self.total_trades,
            "total_volume": self.total_volume,
            "completed_orders": self.completed_orders,
            "oath_sworn": getattr(self, 'oath_sworn', False),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        return super().get_manifest()


if __name__ == "__main__":
    cartridge = MarketCartridge()
    print(f"✅ {cartridge.name} system cartridge loaded")
    def report_status(self):
        """Report agent status for kernel health monitoring."""
        return {
            "agent_id": "market",
            "name": "MARKET",
            "status": "healthy",
            "domain": "ECONOMY",
            "capabilities": ['trading', 'commerce']
        }


