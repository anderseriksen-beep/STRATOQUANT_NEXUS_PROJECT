"""L1 Signal Layer - Signal generation and technical indicators.

This layer handles:
- Technical indicator calculations (RSI, MACD, Bollinger Bands, etc.)
- Signal generation from indicators
- Signal aggregation and scoring
"""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from stratoquant_nexus.layers.base import BaseLayer, LayerConfig, LayerLevel
from stratoquant_nexus.layers.l0_data import OHLCV, MarketData


class SignalType(str, Enum):
    """Types of trading signals."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class SignalStrength(str, Enum):
    """Signal strength levels."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class TradingSignal(BaseModel):
    """Trading signal model."""

    symbol: str = Field(..., description="Trading symbol")
    signal_type: SignalType = Field(..., description="Type of signal")
    strength: SignalStrength = Field(..., description="Signal strength")
    price: Decimal = Field(..., description="Price at signal generation")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    indicators: dict[str, float | str] = Field(
        default_factory=dict, description="Indicator values used"
    )
    confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Confidence score"
    )


class IndicatorResult(BaseModel):
    """Result from indicator calculation."""

    name: str = Field(..., description="Indicator name")
    value: float = Field(..., description="Indicator value")
    signal: SignalType = Field(
        default=SignalType.HOLD, description="Signal from indicator"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SignalLayerConfig(LayerConfig):
    """Configuration for the signal layer."""

    level: LayerLevel = Field(default=LayerLevel.SIGNALS, description="Layer level")
    rsi_period: int = Field(default=14, description="RSI calculation period")
    rsi_overbought: float = Field(default=70.0, description="RSI overbought threshold")
    rsi_oversold: float = Field(default=30.0, description="RSI oversold threshold")
    sma_short_period: int = Field(default=20, description="Short SMA period")
    sma_long_period: int = Field(default=50, description="Long SMA period")


class SignalLayer(BaseLayer):
    """L1 Signal Layer - Generates trading signals from market data.

    This layer is responsible for:
    1. Calculating technical indicators
    2. Generating trading signals
    3. Aggregating multiple signal sources
    4. Providing signal confidence scores
    """

    def __init__(self, config: SignalLayerConfig | None = None) -> None:
        """Initialize the signal layer.

        Args:
            config: Signal layer configuration
        """
        if config is None:
            config = SignalLayerConfig(name="SignalLayer")
        super().__init__(config)
        self._signals: list[TradingSignal] = []

    async def initialize(self) -> None:
        """Initialize signal layer resources."""
        self._initialized = True

    async def process(self, data: Any) -> list[TradingSignal]:
        """Process market data and generate signals.

        Args:
            data: Market data to analyze

        Returns:
            List of generated trading signals
        """
        signals = []

        if isinstance(data, MarketData) and data.candles:
            # Group candles by symbol
            symbols = {c.symbol for c in data.candles}
            for symbol in symbols:
                candles = [c for c in data.candles if c.symbol == symbol]
                if len(candles) >= 2:
                    signal = await self._generate_signal(symbol, candles)
                    if signal:
                        signals.append(signal)
                        self._signals.append(signal)

        return signals

    async def _generate_signal(
        self, symbol: str, candles: list[OHLCV]
    ) -> TradingSignal | None:
        """Generate a signal from candle data.

        Args:
            symbol: Trading symbol
            candles: List of OHLCV candles

        Returns:
            Generated signal or None
        """
        if len(candles) < 2:
            return None

        # Simple momentum-based signal generation
        latest = candles[-1]
        prev = candles[-2]

        # Calculate price change
        price_change = float(latest.close - prev.close) / float(prev.close)

        # Determine signal type
        if price_change > 0.01:
            signal_type = SignalType.BUY
            strength = (
                SignalStrength.STRONG
                if price_change > 0.03
                else SignalStrength.MODERATE
            )
        elif price_change < -0.01:
            signal_type = SignalType.SELL
            strength = (
                SignalStrength.STRONG
                if price_change < -0.03
                else SignalStrength.MODERATE
            )
        else:
            signal_type = SignalType.HOLD
            strength = SignalStrength.WEAK

        # Calculate RSI (simplified)
        rsi = await self._calculate_rsi(candles)

        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            price=latest.close,
            indicators={"rsi": rsi, "price_change_pct": price_change * 100},
            confidence=min(abs(price_change) * 10, 1.0),
        )

    async def _calculate_rsi(self, candles: list[OHLCV], period: int = 14) -> float:
        """Calculate RSI indicator.

        Args:
            candles: List of OHLCV candles
            period: RSI period

        Returns:
            RSI value (0-100)
        """
        if len(candles) < period + 1:
            return 50.0  # Neutral default

        # Calculate price changes
        changes = [
            float(candles[i].close - candles[i - 1].close)
            for i in range(1, len(candles))
        ]

        # Separate gains and losses
        gains = [c if c > 0 else 0 for c in changes[-period:]]
        losses = [-c if c < 0 else 0 for c in changes[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    async def shutdown(self) -> None:
        """Clean up signal layer resources."""
        self._signals.clear()
        self._initialized = False

    def get_latest_signal(self, symbol: str) -> TradingSignal | None:
        """Get the latest signal for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Latest signal or None
        """
        matching = [s for s in self._signals if s.symbol == symbol]
        return max(matching, key=lambda x: x.timestamp) if matching else None
