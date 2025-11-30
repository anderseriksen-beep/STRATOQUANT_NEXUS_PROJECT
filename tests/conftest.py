"""Test configuration and fixtures for pytest."""

from datetime import datetime
from decimal import Decimal

import pytest

from stratoquant_nexus.layers.l0_data import OHLCV, MarketData, Timeframe
from stratoquant_nexus.layers.l1_signals import (
    SignalStrength,
    SignalType,
    TradingSignal,
)


@pytest.fixture
def sample_candles() -> list[OHLCV]:
    """Create sample OHLCV candles for testing."""
    return [
        OHLCV(
            timestamp=datetime(2024, 1, 1, i, 0, 0),
            open=Decimal(str(40000 + i * 100)),
            high=Decimal(str(40100 + i * 100)),
            low=Decimal(str(39900 + i * 100)),
            close=Decimal(str(40050 + i * 100)),
            volume=Decimal(str(1000 + i * 10)),
            symbol="BTC/USD",
            timeframe=Timeframe.H1,
        )
        for i in range(20)
    ]


@pytest.fixture
def sample_market_data(sample_candles: list[OHLCV]) -> MarketData:
    """Create sample market data for testing."""
    return MarketData(candles=sample_candles)


@pytest.fixture
def sample_buy_signal() -> TradingSignal:
    """Create a sample buy signal for testing."""
    return TradingSignal(
        symbol="BTC/USD",
        signal_type=SignalType.BUY,
        strength=SignalStrength.STRONG,
        price=Decimal("42000"),
        confidence=0.8,
        indicators={"rsi": 35.0, "price_change_pct": 2.5},
    )


@pytest.fixture
def sample_sell_signal() -> TradingSignal:
    """Create a sample sell signal for testing."""
    return TradingSignal(
        symbol="BTC/USD",
        signal_type=SignalType.SELL,
        strength=SignalStrength.MODERATE,
        price=Decimal("41000"),
        confidence=0.6,
        indicators={"rsi": 75.0, "price_change_pct": -1.5},
    )
