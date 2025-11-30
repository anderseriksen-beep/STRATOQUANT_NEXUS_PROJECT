"""Webhook server for receiving TradingView alerts."""

import hashlib
import hmac
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field

from stratoquant_nexus.pine_executor.models import AlertType, PineAlert

logger = structlog.get_logger()


class WebhookConfig(BaseModel):
    """Configuration for the webhook server."""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    secret_key: str = Field(default="", description="Webhook secret for validation")
    path: str = Field(default="/webhook", description="Webhook endpoint path")


class WebhookServer:
    """Webhook server for receiving TradingView alerts.

    This server receives HTTP POST requests from TradingView alerts
    and converts them into PineAlert objects for processing.

    Example:
        >>> server = WebhookServer(config)
        >>> server.on_alert(callback)
        >>> await server.start()
    """

    def __init__(self, config: WebhookConfig | None = None) -> None:
        """Initialize the webhook server.

        Args:
            config: Server configuration
        """
        self.config = config or WebhookConfig()
        self._running = False
        self._callbacks: list[Callable[[PineAlert], Coroutine[Any, Any, None]]] = []

    def on_alert(
        self, callback: Callable[[PineAlert], Coroutine[Any, Any, None]]
    ) -> None:
        """Register a callback for alert processing.

        Args:
            callback: Async callback function to handle alerts
        """
        self._callbacks.append(callback)

    def validate_signature(self, payload: bytes, signature: str) -> bool:
        """Validate webhook signature.

        Args:
            payload: Request payload
            signature: Provided signature

        Returns:
            True if signature is valid
        """
        if not self.config.secret_key:
            return True  # No validation if no secret configured

        expected = hmac.new(
            self.config.secret_key.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def parse_alert(self, data: dict[str, Any]) -> PineAlert:
        """Parse webhook data into a PineAlert.

        Args:
            data: Webhook payload data

        Returns:
            Parsed PineAlert
        """
        # Map common TradingView alert fields
        alert_type_map = {
            "buy": AlertType.LONG_ENTRY,
            "sell": AlertType.SHORT_ENTRY,
            "long": AlertType.LONG_ENTRY,
            "short": AlertType.SHORT_ENTRY,
            "close_long": AlertType.LONG_EXIT,
            "close_short": AlertType.SHORT_EXIT,
            "stop_loss": AlertType.STOP_LOSS,
            "take_profit": AlertType.TAKE_PROFIT,
        }

        raw_type = str(data.get("action", data.get("type", "custom"))).lower()
        alert_type = alert_type_map.get(raw_type, AlertType.CUSTOM)

        return PineAlert(
            alert_id=str(data.get("alert_id", uuid4())),
            alert_type=alert_type,
            symbol=str(data.get("symbol", data.get("ticker", "UNKNOWN"))),
            exchange=str(data.get("exchange", "")),
            price=Decimal(str(data.get("price", data.get("close", 0)))),
            timestamp=datetime.now(UTC),
            strategy_name=str(data.get("strategy", data.get("strategy_name", ""))),
            timeframe=str(data.get("timeframe", data.get("interval", ""))),
            message=str(data.get("message", data.get("comment", ""))),
            metadata={
                k: str(v)
                for k, v in data.items()
                if k not in {"action", "type", "symbol", "ticker", "price", "close"}
            },
        )

    async def handle_webhook(self, data: dict[str, Any]) -> PineAlert:
        """Handle incoming webhook request.

        Args:
            data: Webhook payload

        Returns:
            Parsed alert
        """
        alert = self.parse_alert(data)

        logger.info(
            "Webhook received",
            alert_id=alert.alert_id,
            symbol=alert.symbol,
            alert_type=alert.alert_type,
        )

        # Notify callbacks
        for callback in self._callbacks:
            await callback(alert)

        return alert

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    async def start(self) -> None:
        """Start the webhook server.

        Note: This is a placeholder. In production, this would start
        an actual HTTP server (e.g., using aiohttp or FastAPI).
        """
        self._running = True
        logger.info(
            "Webhook server started",
            host=self.config.host,
            port=self.config.port,
            path=self.config.path,
        )

    async def stop(self) -> None:
        """Stop the webhook server."""
        self._running = False
        logger.info("Webhook server stopped")
