"""L2 Risk Layer - Risk management and position sizing.

This layer handles:
- Position sizing calculations
- Risk-per-trade management
- Portfolio exposure limits
- Stop-loss and take-profit levels
"""

from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from stratoquant_nexus.layers.base import BaseLayer, LayerConfig, LayerLevel
from stratoquant_nexus.layers.l1_signals import SignalType, TradingSignal


class RiskLevel(str, Enum):
    """Risk levels for portfolio management."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class PositionSize(BaseModel):
    """Position sizing calculation result."""

    symbol: str = Field(..., description="Trading symbol")
    units: Decimal = Field(..., description="Number of units to trade")
    notional_value: Decimal = Field(..., description="Total position value")
    risk_amount: Decimal = Field(..., description="Amount at risk")
    stop_loss_price: Decimal = Field(..., description="Stop loss price level")
    take_profit_price: Decimal = Field(..., description="Take profit price level")
    risk_reward_ratio: float = Field(..., description="Risk/reward ratio")


class RiskAssessment(BaseModel):
    """Risk assessment for a trading signal."""

    signal: TradingSignal = Field(..., description="Original trading signal")
    approved: bool = Field(..., description="Whether the trade is approved")
    position_size: PositionSize | None = Field(
        default=None, description="Calculated position size"
    )
    rejection_reason: str | None = Field(
        default=None, description="Reason for rejection if not approved"
    )
    portfolio_exposure_pct: float = Field(
        default=0.0, description="Portfolio exposure percentage"
    )


class RiskLayerConfig(LayerConfig):
    """Configuration for the risk layer."""

    level: LayerLevel = Field(default=LayerLevel.RISK, description="Layer level")
    risk_level: RiskLevel = Field(
        default=RiskLevel.MODERATE, description="Overall risk level"
    )
    max_position_size_pct: float = Field(
        default=0.1, description="Maximum position size as % of portfolio"
    )
    max_portfolio_exposure_pct: float = Field(
        default=0.5, description="Maximum total portfolio exposure"
    )
    default_stop_loss_pct: float = Field(
        default=0.02, description="Default stop loss percentage"
    )
    default_take_profit_pct: float = Field(
        default=0.04, description="Default take profit percentage"
    )
    min_risk_reward_ratio: float = Field(
        default=1.5, description="Minimum required risk/reward ratio"
    )


class RiskLayer(BaseLayer):
    """L2 Risk Layer - Manages risk and position sizing.

    This layer is responsible for:
    1. Calculating optimal position sizes
    2. Setting stop-loss and take-profit levels
    3. Enforcing portfolio exposure limits
    4. Approving or rejecting trades based on risk criteria
    """

    def __init__(self, config: RiskLayerConfig | None = None) -> None:
        """Initialize the risk layer.

        Args:
            config: Risk layer configuration
        """
        if config is None:
            config = RiskLayerConfig(name="RiskLayer")
        super().__init__(config)
        self._portfolio_value = Decimal("100000")  # Default portfolio value
        self._current_exposure = Decimal("0")
        self._active_positions: dict[str, PositionSize] = {}

    async def initialize(self) -> None:
        """Initialize risk layer resources."""
        self._initialized = True

    def set_portfolio_value(self, value: Decimal) -> None:
        """Set the current portfolio value.

        Args:
            value: Portfolio value
        """
        self._portfolio_value = value

    async def process(self, data: Any) -> list[RiskAssessment]:
        """Process trading signals and assess risk.

        Args:
            data: Trading signals to assess

        Returns:
            List of risk assessments
        """
        assessments = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, TradingSignal):
                    assessment = await self._assess_signal(item)
                    assessments.append(assessment)

        return assessments

    async def _assess_signal(self, signal: TradingSignal) -> RiskAssessment:
        """Assess a trading signal for risk.

        Args:
            signal: Trading signal to assess

        Returns:
            Risk assessment
        """
        config: RiskLayerConfig = self.config  # type: ignore

        # Skip HOLD signals
        if signal.signal_type == SignalType.HOLD:
            return RiskAssessment(
                signal=signal,
                approved=False,
                rejection_reason="HOLD signals do not require execution",
            )

        # Check portfolio exposure
        current_exposure_pct = float(self._current_exposure / self._portfolio_value)
        if current_exposure_pct >= config.max_portfolio_exposure_pct:
            return RiskAssessment(
                signal=signal,
                approved=False,
                rejection_reason="Maximum portfolio exposure reached",
                portfolio_exposure_pct=current_exposure_pct * 100,
            )

        # Calculate position size
        position_size = await self._calculate_position_size(signal, config)

        # Validate risk/reward ratio
        if position_size.risk_reward_ratio < config.min_risk_reward_ratio:
            return RiskAssessment(
                signal=signal,
                approved=False,
                position_size=position_size,
                rejection_reason=(
                    f"Risk/reward ratio {position_size.risk_reward_ratio:.2f} "
                    f"below minimum {config.min_risk_reward_ratio}"
                ),
                portfolio_exposure_pct=current_exposure_pct * 100,
            )

        return RiskAssessment(
            signal=signal,
            approved=True,
            position_size=position_size,
            portfolio_exposure_pct=current_exposure_pct * 100,
        )

    async def _calculate_position_size(
        self, signal: TradingSignal, config: RiskLayerConfig
    ) -> PositionSize:
        """Calculate position size for a signal.

        Args:
            signal: Trading signal
            config: Risk layer configuration

        Returns:
            Calculated position size
        """
        price = signal.price
        max_position_value = self._portfolio_value * Decimal(
            str(config.max_position_size_pct)
        )

        # Calculate stop loss and take profit based on signal type
        if signal.signal_type == SignalType.BUY:
            stop_loss = price * Decimal(1 - config.default_stop_loss_pct)
            take_profit = price * Decimal(1 + config.default_take_profit_pct)
        else:  # SELL
            stop_loss = price * Decimal(1 + config.default_stop_loss_pct)
            take_profit = price * Decimal(1 - config.default_take_profit_pct)

        # Calculate risk/reward ratio
        risk = abs(price - stop_loss)
        reward = abs(take_profit - price)
        risk_reward_ratio = float(reward / risk) if risk > 0 else 0.0

        # Calculate units based on risk amount
        risk_amount = self._portfolio_value * Decimal(str(config.default_stop_loss_pct))
        units = max_position_value / price if price > 0 else Decimal("0")

        return PositionSize(
            symbol=signal.symbol,
            units=units.quantize(Decimal("0.00000001")),
            notional_value=max_position_value.quantize(Decimal("0.01")),
            risk_amount=risk_amount.quantize(Decimal("0.01")),
            stop_loss_price=stop_loss.quantize(Decimal("0.01")),
            take_profit_price=take_profit.quantize(Decimal("0.01")),
            risk_reward_ratio=round(risk_reward_ratio, 2),
        )

    async def shutdown(self) -> None:
        """Clean up risk layer resources."""
        self._active_positions.clear()
        self._current_exposure = Decimal("0")
        self._initialized = False
