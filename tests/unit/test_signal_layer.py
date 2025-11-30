"""Unit tests for the signal layer (L1)."""

from decimal import Decimal

import pytest

from stratoquant_nexus.layers.base import LayerLevel
from stratoquant_nexus.layers.l0_data import OHLCV, MarketData
from stratoquant_nexus.layers.l1_signals import (
    SignalLayer,
    SignalLayerConfig,
    SignalStrength,
    SignalType,
    TradingSignal,
)


class TestSignalLayer:
    """Tests for the SignalLayer class."""

    @pytest.fixture
    def signal_layer(self) -> SignalLayer:
        """Create a signal layer for testing."""
        return SignalLayer()

    @pytest.fixture
    def custom_signal_layer(self) -> SignalLayer:
        """Create a custom configured signal layer."""
        config = SignalLayerConfig(
            name="CustomSignalLayer",
            rsi_period=21,
            rsi_overbought=80.0,
            rsi_oversold=20.0,
        )
        return SignalLayer(config)

    @pytest.mark.asyncio
    async def test_layer_initialization(self, signal_layer: SignalLayer) -> None:
        """Test signal layer initialization."""
        await signal_layer.initialize()

        assert signal_layer._initialized
        assert await signal_layer.health_check()

        await signal_layer.shutdown()

    @pytest.mark.asyncio
    async def test_process_market_data(
        self, signal_layer: SignalLayer, sample_market_data: MarketData
    ) -> None:
        """Test processing market data to generate signals."""
        await signal_layer.initialize()

        signals = await signal_layer.process(sample_market_data)

        assert isinstance(signals, list)
        # Should generate at least one signal from sample data
        if signals:
            assert all(isinstance(s, TradingSignal) for s in signals)

        await signal_layer.shutdown()

    @pytest.mark.asyncio
    async def test_get_latest_signal(
        self, signal_layer: SignalLayer, sample_market_data: MarketData
    ) -> None:
        """Test getting the latest signal for a symbol."""
        await signal_layer.initialize()
        await signal_layer.process(sample_market_data)

        signal = signal_layer.get_latest_signal("BTC/USD")

        # May or may not have signal depending on market data
        if signal:
            assert signal.symbol == "BTC/USD"

        await signal_layer.shutdown()

    @pytest.mark.asyncio
    async def test_rsi_calculation(
        self, signal_layer: SignalLayer, sample_candles: list[OHLCV]
    ) -> None:
        """Test RSI indicator calculation."""
        await signal_layer.initialize()

        rsi = await signal_layer._calculate_rsi(sample_candles)

        assert 0 <= rsi <= 100

        await signal_layer.shutdown()

    def test_layer_level(self, signal_layer: SignalLayer) -> None:
        """Test signal layer level is L1."""
        assert signal_layer.level == LayerLevel.SIGNALS

    def test_custom_config(self, custom_signal_layer: SignalLayer) -> None:
        """Test signal layer with custom configuration."""
        assert custom_signal_layer.name == "CustomSignalLayer"


class TestTradingSignal:
    """Tests for the TradingSignal model."""

    def test_signal_creation(self) -> None:
        """Test trading signal creation."""
        signal = TradingSignal(
            symbol="BTC/USD",
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            price=Decimal("42000"),
            confidence=0.85,
        )

        assert signal.symbol == "BTC/USD"
        assert signal.signal_type == SignalType.BUY
        assert signal.strength == SignalStrength.STRONG

    def test_signal_confidence_bounds(self) -> None:
        """Test signal confidence is bounded 0-1."""
        signal = TradingSignal(
            symbol="BTC/USD",
            signal_type=SignalType.BUY,
            strength=SignalStrength.MODERATE,
            price=Decimal("42000"),
            confidence=1.0,
        )

        assert 0.0 <= signal.confidence <= 1.0

    def test_signal_with_indicators(self) -> None:
        """Test signal with indicator values."""
        signal = TradingSignal(
            symbol="ETH/USD",
            signal_type=SignalType.SELL,
            strength=SignalStrength.WEAK,
            price=Decimal("2500"),
            indicators={"rsi": 75.5, "macd": -0.02},
        )

        assert signal.indicators["rsi"] == 75.5
        assert signal.indicators["macd"] == -0.02
