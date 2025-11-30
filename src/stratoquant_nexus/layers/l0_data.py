"""L0 Data Layer - Data acquisition and normalization.

This layer handles:
- Market data ingestion from multiple sources
- Data normalization and validation
- OHLCV candlestick management
- Order book data processing
"""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from stratoquant_nexus.layers.base import BaseLayer, LayerConfig, LayerLevel


class Timeframe(str, Enum):
    """Supported trading timeframes."""

    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class OHLCV(BaseModel):
    """OHLCV candlestick data model."""

    model_config = {"frozen": True}

    timestamp: datetime = Field(..., description="Candle timestamp")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: Decimal = Field(..., description="Trading volume")
    symbol: str = Field(..., description="Trading symbol (e.g., BTC/USD)")
    timeframe: Timeframe = Field(..., description="Candle timeframe")


class MarketData(BaseModel):
    """Market data container for multiple symbols."""

    candles: list[OHLCV] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def get_latest(self, symbol: str, timeframe: Timeframe) -> OHLCV | None:
        """Get the latest candle for a symbol and timeframe.

        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe

        Returns:
            Latest OHLCV candle or None if not found
        """
        matching = [
            c for c in self.candles if c.symbol == symbol and c.timeframe == timeframe
        ]
        return max(matching, key=lambda x: x.timestamp) if matching else None


class DataLayerConfig(LayerConfig):
    """Configuration for the data layer."""

    level: LayerLevel = Field(default=LayerLevel.DATA, description="Layer level")
    symbols: list[str] = Field(
        default_factory=lambda: ["BTC/USD", "ETH/USD"],
        description="Symbols to track",
    )
    timeframes: list[Timeframe] = Field(
        default_factory=lambda: [Timeframe.H1, Timeframe.D1],
        description="Timeframes to track",
    )
    max_candles: int = Field(
        default=1000, description="Maximum candles to store per symbol/timeframe"
    )


class DataLayer(BaseLayer):
    """L0 Data Layer - Handles data acquisition and normalization.

    This layer is responsible for:
    1. Fetching market data from exchanges
    2. Normalizing data formats
    3. Validating data integrity
    4. Managing historical data storage
    """

    def __init__(self, config: DataLayerConfig | None = None) -> None:
        """Initialize the data layer.

        Args:
            config: Data layer configuration
        """
        if config is None:
            config = DataLayerConfig(name="DataLayer")
        super().__init__(config)
        self._market_data: dict[str, MarketData] = {}

    async def initialize(self) -> None:
        """Initialize data layer resources."""
        self._initialized = True

    async def process(self, data: Any) -> MarketData:
        """Process and normalize incoming market data.

        Args:
            data: Raw market data to process

        Returns:
            Normalized MarketData
        """
        if isinstance(data, list) and all(isinstance(d, OHLCV) for d in data):
            market_data = MarketData(candles=data)
            # Store by symbol
            for candle in data:
                if candle.symbol not in self._market_data:
                    self._market_data[candle.symbol] = MarketData()
                self._market_data[candle.symbol].candles.append(candle)
            return market_data
        return MarketData()

    async def shutdown(self) -> None:
        """Clean up data layer resources."""
        self._market_data.clear()
        self._initialized = False

    def get_market_data(self, symbol: str) -> MarketData | None:
        """Get stored market data for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            MarketData for the symbol or None
        """
        return self._market_data.get(symbol)
