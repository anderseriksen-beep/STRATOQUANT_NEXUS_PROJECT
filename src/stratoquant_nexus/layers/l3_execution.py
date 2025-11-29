"""L3 Execution Layer - Order execution and management.

This layer handles:
- Order creation and submission
- Order status tracking
- Fill management
- Execution reporting
"""

import time
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from stratoquant_nexus.layers.base import BaseLayer, LayerConfig, LayerLevel
from stratoquant_nexus.layers.l1_signals import SignalType
from stratoquant_nexus.layers.l2_risk import RiskAssessment


class OrderType(str, Enum):
    """Order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    """Order side."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status."""

    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order(BaseModel):
    """Trading order model."""

    order_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique order ID"
    )
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Order side")
    order_type: OrderType = Field(default=OrderType.MARKET, description="Order type")
    quantity: Decimal = Field(..., description="Order quantity")
    price: Decimal | None = Field(default=None, description="Limit price")
    stop_price: Decimal | None = Field(default=None, description="Stop price")
    stop_loss: Decimal | None = Field(default=None, description="Stop loss price")
    take_profit: Decimal | None = Field(default=None, description="Take profit price")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    filled_quantity: Decimal = Field(
        default=Decimal("0"), description="Filled quantity"
    )
    average_price: Decimal | None = Field(
        default=None, description="Average fill price"
    )


class ExecutionReport(BaseModel):
    """Execution report for processed orders."""

    order: Order = Field(..., description="The order")
    success: bool = Field(..., description="Whether execution was successful")
    message: str = Field(..., description="Execution message")
    execution_time_ms: float = Field(default=0.0, description="Execution time in ms")
    fees: Decimal = Field(default=Decimal("0"), description="Execution fees")


class ExecutionLayerConfig(LayerConfig):
    """Configuration for the execution layer."""

    level: LayerLevel = Field(default=LayerLevel.EXECUTION, description="Layer level")
    default_order_type: OrderType = Field(
        default=OrderType.MARKET, description="Default order type"
    )
    simulate_execution: bool = Field(
        default=True, description="Whether to simulate execution (paper trading)"
    )
    default_slippage_pct: float = Field(
        default=0.001, description="Default slippage percentage"
    )
    fee_rate: float = Field(default=0.001, description="Trading fee rate")


class ExecutionLayer(BaseLayer):
    """L3 Execution Layer - Handles order execution.

    This layer is responsible for:
    1. Creating orders from risk-assessed signals
    2. Submitting orders to exchanges
    3. Managing order lifecycle
    4. Tracking fills and execution quality
    """

    def __init__(self, config: ExecutionLayerConfig | None = None) -> None:
        """Initialize the execution layer.

        Args:
            config: Execution layer configuration
        """
        if config is None:
            config = ExecutionLayerConfig(name="ExecutionLayer")
        super().__init__(config)
        self._orders: dict[str, Order] = {}
        self._execution_reports: list[ExecutionReport] = []

    async def initialize(self) -> None:
        """Initialize execution layer resources."""
        self._initialized = True

    async def process(self, data: Any) -> list[ExecutionReport]:
        """Process risk assessments and execute orders.

        Args:
            data: Risk assessments to execute

        Returns:
            List of execution reports
        """
        reports = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, RiskAssessment) and item.approved:
                    report = await self._execute_order(item)
                    reports.append(report)
                    self._execution_reports.append(report)

        return reports

    async def _execute_order(self, assessment: RiskAssessment) -> ExecutionReport:
        """Execute an order from a risk assessment.

        Args:
            assessment: Approved risk assessment

        Returns:
            Execution report
        """
        config: ExecutionLayerConfig = self.config  # type: ignore
        signal = assessment.signal
        position_size = assessment.position_size

        if position_size is None:
            return ExecutionReport(
                order=Order(
                    symbol=signal.symbol,
                    side=OrderSide.BUY,
                    quantity=Decimal("0"),
                    status=OrderStatus.REJECTED,
                ),
                success=False,
                message="No position size calculated",
            )

        # Determine order side
        side = OrderSide.BUY if signal.signal_type == SignalType.BUY else OrderSide.SELL

        # Create order
        order = Order(
            symbol=signal.symbol,
            side=side,
            order_type=config.default_order_type,
            quantity=position_size.units,
            price=(
                signal.price if config.default_order_type == OrderType.LIMIT else None
            ),
            stop_loss=position_size.stop_loss_price,
            take_profit=position_size.take_profit_price,
        )

        # Store order
        self._orders[order.order_id] = order

        # Simulate or execute
        if config.simulate_execution:
            return await self._simulate_execution(order, config)
        else:
            # In production, this would connect to an exchange
            return await self._simulate_execution(order, config)

    async def _simulate_execution(
        self, order: Order, config: ExecutionLayerConfig
    ) -> ExecutionReport:
        """Simulate order execution.

        Args:
            order: Order to execute
            config: Execution configuration

        Returns:
            Execution report
        """
        start_time = time.time()

        # Simulate slippage
        if order.price:
            slippage = order.price * Decimal(str(config.default_slippage_pct))
            fill_price = (
                order.price + slippage
                if order.side == OrderSide.BUY
                else order.price - slippage
            )
        else:
            fill_price = order.stop_price or Decimal("0")

        # Calculate fees
        notional = order.quantity * fill_price
        fees = notional * Decimal(str(config.fee_rate))

        # Update order status
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_price = fill_price
        order.updated_at = datetime.now(UTC)

        execution_time = (time.time() - start_time) * 1000

        return ExecutionReport(
            order=order,
            success=True,
            message=f"Order filled at {fill_price} (simulated)",
            execution_time_ms=round(execution_time, 2),
            fees=fees.quantize(Decimal("0.01")),
        )

    async def shutdown(self) -> None:
        """Clean up execution layer resources."""
        self._orders.clear()
        self._execution_reports.clear()
        self._initialized = False

    def get_order(self, order_id: str) -> Order | None:
        """Get an order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order or None
        """
        return self._orders.get(order_id)

    def get_open_orders(self, symbol: str | None = None) -> list[Order]:
        """Get all open orders.

        Args:
            symbol: Filter by symbol (optional)

        Returns:
            List of open orders
        """
        open_statuses = {
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIAL,
        }
        orders = [o for o in self._orders.values() if o.status in open_statuses]
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders
