"""Unit tests for the data layer (L0)."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from stratoquant_nexus.layers.base import LayerLevel
from stratoquant_nexus.layers.l0_data import (
    OHLCV,
    DataLayer,
    DataLayerConfig,
    MarketData,
    Timeframe,
)


class TestDataLayer:
    """Tests for the DataLayer class."""

    @pytest.fixture
    def data_layer(self) -> DataLayer:
        """Create a data layer for testing."""
        return DataLayer()

    @pytest.fixture
    def custom_data_layer(self) -> DataLayer:
        """Create a custom configured data layer."""
        config = DataLayerConfig(
            name="CustomDataLayer",
            symbols=["BTC/USD", "ETH/USD", "SOL/USD"],
            timeframes=[Timeframe.M15, Timeframe.H1],
            max_candles=500,
        )
        return DataLayer(config)

    @pytest.mark.asyncio
    async def test_layer_initialization(self, data_layer: DataLayer) -> None:
        """Test data layer initialization."""
        await data_layer.initialize()

        assert data_layer._initialized
        assert await data_layer.health_check()

        await data_layer.shutdown()

    @pytest.mark.asyncio
    async def test_layer_shutdown(self, data_layer: DataLayer) -> None:
        """Test data layer shutdown."""
        await data_layer.initialize()
        await data_layer.shutdown()

        assert not data_layer._initialized

    @pytest.mark.asyncio
    async def test_process_candles(
        self, data_layer: DataLayer, sample_candles: list[OHLCV]
    ) -> None:
        """Test processing OHLCV candles."""
        await data_layer.initialize()

        result = await data_layer.process(sample_candles)

        assert isinstance(result, MarketData)
        assert len(result.candles) == len(sample_candles)

        await data_layer.shutdown()

    @pytest.mark.asyncio
    async def test_get_market_data(
        self, data_layer: DataLayer, sample_candles: list[OHLCV]
    ) -> None:
        """Test retrieving stored market data."""
        await data_layer.initialize()
        await data_layer.process(sample_candles)

        market_data = data_layer.get_market_data("BTC/USD")

        assert market_data is not None
        assert len(market_data.candles) > 0

        await data_layer.shutdown()

    def test_layer_level(self, data_layer: DataLayer) -> None:
        """Test data layer level is L0."""
        assert data_layer.level == LayerLevel.DATA

    def test_custom_config(self, custom_data_layer: DataLayer) -> None:
        """Test data layer with custom configuration."""
        assert custom_data_layer.name == "CustomDataLayer"


class TestOHLCV:
    """Tests for the OHLCV model."""

    def test_ohlcv_creation(self) -> None:
        """Test OHLCV candle creation."""
        candle = OHLCV(
            timestamp=datetime.now(UTC),
            open=Decimal("40000"),
            high=Decimal("40500"),
            low=Decimal("39500"),
            close=Decimal("40200"),
            volume=Decimal("1000"),
            symbol="BTC/USD",
            timeframe=Timeframe.H1,
        )

        assert candle.symbol == "BTC/USD"
        assert candle.timeframe == Timeframe.H1
        assert candle.close == Decimal("40200")

    def test_ohlcv_frozen(self) -> None:
        """Test OHLCV is immutable (frozen)."""
        candle = OHLCV(
            timestamp=datetime.now(UTC),
            open=Decimal("40000"),
            high=Decimal("40500"),
            low=Decimal("39500"),
            close=Decimal("40200"),
            volume=Decimal("1000"),
            symbol="BTC/USD",
            timeframe=Timeframe.H1,
        )

        with pytest.raises(Exception):  # noqa: B017
            candle.close = Decimal("41000")  # type: ignore


class TestMarketData:
    """Tests for the MarketData model."""

    def test_get_latest_candle(self, sample_candles: list[OHLCV]) -> None:
        """Test getting latest candle from market data."""
        market_data = MarketData(candles=sample_candles)

        latest = market_data.get_latest("BTC/USD", Timeframe.H1)

        assert latest is not None
        assert latest.symbol == "BTC/USD"

    def test_get_latest_no_match(self, sample_candles: list[OHLCV]) -> None:
        """Test getting latest when no match exists."""
        market_data = MarketData(candles=sample_candles)

        latest = market_data.get_latest("ETH/USD", Timeframe.H1)

        assert latest is None
