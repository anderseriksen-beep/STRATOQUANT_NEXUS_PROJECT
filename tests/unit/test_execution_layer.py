"""Unit tests for the execution layer (L3)."""

from decimal import Decimal

import pytest

from stratoquant_nexus.layers.base import LayerLevel
from stratoquant_nexus.layers.l1_signals import (
    SignalStrength,
    SignalType,
    TradingSignal,
)
from stratoquant_nexus.layers.l2_risk import PositionSize, RiskAssessment
from stratoquant_nexus.layers.l3_execution import (
    ExecutionLayer,
    ExecutionReport,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
)


class TestExecutionLayer:
    """Tests for the ExecutionLayer class."""

    @pytest.fixture
    def execution_layer(self) -> ExecutionLayer:
        """Create an execution layer for testing."""
        return ExecutionLayer()

    @pytest.fixture
    def approved_assessment(self) -> RiskAssessment:
        """Create an approved risk assessment."""
        signal = TradingSignal(
            symbol="BTC/USD",
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            price=Decimal("42000"),
            confidence=0.8,
        )
        position = PositionSize(
            symbol="BTC/USD",
            units=Decimal("0.5"),
            notional_value=Decimal("21000"),
            risk_amount=Decimal("420"),
            stop_loss_price=Decimal("41000"),
            take_profit_price=Decimal("43000"),
            risk_reward_ratio=2.0,
        )
        return RiskAssessment(
            signal=signal,
            approved=True,
            position_size=position,
        )

    @pytest.mark.asyncio
    async def test_layer_initialization(self, execution_layer: ExecutionLayer) -> None:
        """Test execution layer initialization."""
        await execution_layer.initialize()

        assert execution_layer._initialized
        assert await execution_layer.health_check()

        await execution_layer.shutdown()

    @pytest.mark.asyncio
    async def test_execute_approved_assessment(
        self, execution_layer: ExecutionLayer, approved_assessment: RiskAssessment
    ) -> None:
        """Test executing an approved risk assessment."""
        await execution_layer.initialize()

        reports = await execution_layer.process([approved_assessment])

        assert len(reports) == 1
        report = reports[0]
        assert isinstance(report, ExecutionReport)
        assert report.success
        assert report.order.status == OrderStatus.FILLED

        await execution_layer.shutdown()

    @pytest.mark.asyncio
    async def test_rejected_assessment_not_executed(
        self, execution_layer: ExecutionLayer
    ) -> None:
        """Test that rejected assessments are not executed."""
        await execution_layer.initialize()

        signal = TradingSignal(
            symbol="BTC/USD",
            signal_type=SignalType.BUY,
            strength=SignalStrength.WEAK,
            price=Decimal("42000"),
        )
        rejected = RiskAssessment(
            signal=signal,
            approved=False,
            rejection_reason="Risk too high",
        )

        reports = await execution_layer.process([rejected])

        assert len(reports) == 0

        await execution_layer.shutdown()

    @pytest.mark.asyncio
    async def test_get_order(
        self, execution_layer: ExecutionLayer, approved_assessment: RiskAssessment
    ) -> None:
        """Test retrieving an order by ID."""
        await execution_layer.initialize()

        reports = await execution_layer.process([approved_assessment])
        order_id = reports[0].order.order_id

        order = execution_layer.get_order(order_id)

        assert order is not None
        assert order.order_id == order_id

        await execution_layer.shutdown()

    @pytest.mark.asyncio
    async def test_get_open_orders(self, execution_layer: ExecutionLayer) -> None:
        """Test getting open orders."""
        await execution_layer.initialize()

        open_orders = execution_layer.get_open_orders()

        assert isinstance(open_orders, list)

        await execution_layer.shutdown()

    def test_layer_level(self, execution_layer: ExecutionLayer) -> None:
        """Test execution layer level is L3."""
        assert execution_layer.level == LayerLevel.EXECUTION


class TestOrder:
    """Tests for the Order model."""

    def test_order_creation(self) -> None:
        """Test order creation."""
        order = Order(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.5"),
        )

        assert order.symbol == "BTC/USD"
        assert order.side == OrderSide.BUY
        assert order.status == OrderStatus.PENDING
        assert order.order_id is not None

    def test_limit_order(self) -> None:
        """Test limit order creation."""
        order = Order(
            symbol="ETH/USD",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=Decimal("2.0"),
            price=Decimal("2500"),
        )

        assert order.order_type == OrderType.LIMIT
        assert order.price == Decimal("2500")


class TestExecutionReport:
    """Tests for the ExecutionReport model."""

    def test_execution_report_creation(self) -> None:
        """Test execution report creation."""
        order = Order(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            quantity=Decimal("0.5"),
        )
        report = ExecutionReport(
            order=order,
            success=True,
            message="Order filled",
            execution_time_ms=15.5,
            fees=Decimal("21.00"),
        )

        assert report.success
        assert report.execution_time_ms == 15.5
        assert report.fees == Decimal("21.00")
