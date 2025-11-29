"""Unit tests for the Pine Script executor."""

from decimal import Decimal

import pytest

from stratoquant_nexus.pine_executor import (
    PineAlert,
    PineExecutor,
    PineStrategy,
    WebhookServer,
)
from stratoquant_nexus.pine_executor.models import AlertType, ExecutionResult
from stratoquant_nexus.pine_executor.webhook import WebhookConfig


class TestPineExecutor:
    """Tests for the PineExecutor class."""

    @pytest.fixture
    def executor(self) -> PineExecutor:
        """Create a Pine executor for testing."""
        return PineExecutor()

    @pytest.fixture
    def sample_strategy(self) -> PineStrategy:
        """Create a sample strategy."""
        return PineStrategy(
            name="TestStrategy",
            description="A test strategy",
            symbols=["BTC/USD", "ETH/USD"],
            timeframes=["1h", "4h"],
        )

    @pytest.fixture
    def sample_alert(self) -> PineAlert:
        """Create a sample alert."""
        return PineAlert(
            alert_id="test-alert-001",
            alert_type=AlertType.LONG_ENTRY,
            symbol="BTC/USD",
            price=Decimal("42000"),
            strategy_name="TestStrategy",
        )

    def test_register_strategy(
        self, executor: PineExecutor, sample_strategy: PineStrategy
    ) -> None:
        """Test strategy registration."""
        executor.register_strategy(sample_strategy)

        assert executor.get_strategy("TestStrategy") is not None
        assert executor.get_strategy("TestStrategy") == sample_strategy

    def test_unregister_strategy(
        self, executor: PineExecutor, sample_strategy: PineStrategy
    ) -> None:
        """Test strategy unregistration."""
        executor.register_strategy(sample_strategy)
        executor.unregister_strategy("TestStrategy")

        assert executor.get_strategy("TestStrategy") is None

    @pytest.mark.asyncio
    async def test_process_alert(
        self, executor: PineExecutor, sample_alert: PineAlert
    ) -> None:
        """Test processing an alert."""
        result = await executor.process_alert(sample_alert)

        assert isinstance(result, ExecutionResult)
        assert result.alert == sample_alert
        assert result.executed

    @pytest.mark.asyncio
    async def test_disabled_strategy_not_executed(
        self, executor: PineExecutor, sample_alert: PineAlert
    ) -> None:
        """Test that disabled strategies don't execute."""
        strategy = PineStrategy(
            name="TestStrategy",
            enabled=False,
        )
        executor.register_strategy(strategy)

        result = await executor.process_alert(sample_alert)

        assert not result.executed
        assert "disabled" in result.message

    def test_get_processed_alerts(self, executor: PineExecutor) -> None:
        """Test getting processed alerts."""
        alerts = executor.get_processed_alerts()

        assert isinstance(alerts, list)

    def test_clear_processed_alerts(self, executor: PineExecutor) -> None:
        """Test clearing processed alerts."""
        executor.clear_processed_alerts()

        assert len(executor.get_processed_alerts()) == 0


class TestPineAlert:
    """Tests for the PineAlert model."""

    def test_alert_creation(self) -> None:
        """Test alert creation."""
        alert = PineAlert(
            alert_id="test-001",
            alert_type=AlertType.LONG_ENTRY,
            symbol="BTC/USD",
            price=Decimal("42000"),
        )

        assert alert.alert_id == "test-001"
        assert alert.alert_type == AlertType.LONG_ENTRY
        assert alert.symbol == "BTC/USD"

    def test_alert_with_metadata(self) -> None:
        """Test alert with metadata."""
        alert = PineAlert(
            alert_id="test-002",
            alert_type=AlertType.SHORT_ENTRY,
            symbol="ETH/USD",
            price=Decimal("2500"),
            metadata={"source": "pine_v5", "indicator": "RSI"},
        )

        assert alert.metadata["source"] == "pine_v5"
        assert alert.metadata["indicator"] == "RSI"


class TestWebhookServer:
    """Tests for the WebhookServer class."""

    @pytest.fixture
    def webhook_server(self) -> WebhookServer:
        """Create a webhook server for testing."""
        return WebhookServer()

    def test_server_creation(self, webhook_server: WebhookServer) -> None:
        """Test webhook server creation."""
        assert webhook_server.config.port == 8080
        assert not webhook_server.is_running

    def test_custom_config(self) -> None:
        """Test webhook server with custom config."""
        config = WebhookConfig(
            host="127.0.0.1",
            port=9000,
            secret_key="test-secret",
        )
        server = WebhookServer(config)

        assert server.config.port == 9000
        assert server.config.secret_key == "test-secret"

    def test_parse_alert(self, webhook_server: WebhookServer) -> None:
        """Test parsing webhook data into alert."""
        data = {
            "action": "buy",
            "symbol": "BTC/USD",
            "price": "42000.50",
            "strategy": "MyStrategy",
        }

        alert = webhook_server.parse_alert(data)

        assert alert.symbol == "BTC/USD"
        assert alert.alert_type == AlertType.LONG_ENTRY
        assert alert.price == Decimal("42000.50")

    def test_validate_signature_no_secret(self, webhook_server: WebhookServer) -> None:
        """Test signature validation without secret."""
        is_valid = webhook_server.validate_signature(b"test", "any")

        assert is_valid  # No validation when no secret

    @pytest.mark.asyncio
    async def test_handle_webhook(self, webhook_server: WebhookServer) -> None:
        """Test handling webhook request."""
        data = {
            "action": "sell",
            "symbol": "ETH/USD",
            "price": "2500",
        }

        alert = await webhook_server.handle_webhook(data)

        assert alert.symbol == "ETH/USD"
        assert alert.alert_type == AlertType.SHORT_ENTRY

    @pytest.mark.asyncio
    async def test_server_start_stop(self, webhook_server: WebhookServer) -> None:
        """Test server start and stop."""
        await webhook_server.start()
        assert webhook_server.is_running

        await webhook_server.stop()
        assert not webhook_server.is_running
