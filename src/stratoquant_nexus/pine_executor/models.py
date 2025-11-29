"""Pine Script executor models."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """TradingView alert types."""

    LONG_ENTRY = "long_entry"
    LONG_EXIT = "long_exit"
    SHORT_ENTRY = "short_entry"
    SHORT_EXIT = "short_exit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    CUSTOM = "custom"


class PineAlert(BaseModel):
    """Model for incoming TradingView Pine Script alerts."""

    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: AlertType = Field(..., description="Type of alert")
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(default="", description="Exchange name")
    price: Decimal = Field(..., description="Price at alert")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    strategy_name: str = Field(default="", description="Name of the strategy")
    timeframe: str = Field(default="", description="Timeframe of the alert")
    message: str = Field(default="", description="Custom alert message")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional metadata"
    )


class PineStrategy(BaseModel):
    """Pine Script strategy configuration."""

    name: str = Field(..., description="Strategy name")
    version: str = Field(default="1.0.0", description="Strategy version")
    description: str = Field(default="", description="Strategy description")
    symbols: list[str] = Field(default_factory=list, description="Symbols to trade")
    timeframes: list[str] = Field(default_factory=list, description="Timeframes")
    enabled: bool = Field(default=True, description="Whether strategy is enabled")
    risk_multiplier: float = Field(
        default=1.0, ge=0.1, le=3.0, description="Risk multiplier"
    )
    max_positions: int = Field(default=5, description="Maximum concurrent positions")


class ExecutionResult(BaseModel):
    """Result of alert execution."""

    alert: PineAlert = Field(..., description="Original alert")
    executed: bool = Field(..., description="Whether alert was executed")
    order_id: str | None = Field(default=None, description="Order ID if executed")
    message: str = Field(default="", description="Result message")
    execution_time_ms: float = Field(default=0.0, description="Execution time in ms")
