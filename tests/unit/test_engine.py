"""Unit tests for the trading engine."""


import pytest

from stratoquant_nexus import TradingEngine
from stratoquant_nexus.engine import EngineConfig
from stratoquant_nexus.layers.l0_data import OHLCV


class TestTradingEngine:
    """Tests for the TradingEngine class."""

    @pytest.fixture
    def engine(self) -> TradingEngine:
        """Create a trading engine for testing."""
        return TradingEngine()

    @pytest.fixture
    def custom_engine(self) -> TradingEngine:
        """Create a custom configured engine for testing."""
        config = EngineConfig(
            name="Test Engine",
            enable_data_layer=True,
            enable_signal_layer=True,
            enable_risk_layer=True,
            enable_execution_layer=True,
        )
        return TradingEngine(config)

    @pytest.mark.asyncio
    async def test_engine_start(self, engine: TradingEngine) -> None:
        """Test engine start initializes all layers."""
        await engine.start()

        assert engine.is_running
        assert engine.status.running
        assert engine.status.layers_initialized == 4

        await engine.stop()

    @pytest.mark.asyncio
    async def test_engine_stop(self, engine: TradingEngine) -> None:
        """Test engine stop shuts down all layers."""
        await engine.start()
        await engine.stop()

        assert not engine.is_running
        assert not engine.status.running

    @pytest.mark.asyncio
    async def test_engine_health_check(self, engine: TradingEngine) -> None:
        """Test engine health check."""
        await engine.start()

        health = await engine.health_check()

        assert health["data_layer"]
        assert health["signal_layer"]
        assert health["risk_layer"]
        assert health["execution_layer"]

        await engine.stop()

    @pytest.mark.asyncio
    async def test_process_cycle_not_running(self, engine: TradingEngine) -> None:
        """Test process cycle raises error when not running."""
        with pytest.raises(RuntimeError, match="Engine is not running"):
            await engine.process_cycle([])

    @pytest.mark.asyncio
    async def test_process_cycle(
        self, engine: TradingEngine, sample_candles: list[OHLCV]
    ) -> None:
        """Test complete processing cycle."""
        await engine.start()

        results = await engine.process_cycle(sample_candles)

        assert "market_data" in results
        assert "signals" in results
        assert "risk_assessments" in results
        assert "execution_reports" in results

        await engine.stop()

    @pytest.mark.asyncio
    async def test_engine_status_updates(
        self, engine: TradingEngine, sample_candles: list[OHLCV]
    ) -> None:
        """Test engine status updates after processing."""
        await engine.start()

        initial_signals = engine.status.signals_generated

        await engine.process_cycle(sample_candles)

        assert engine.status.last_cycle_at is not None
        assert engine.status.signals_generated >= initial_signals

        await engine.stop()

    def test_engine_layer_accessors(self, engine: TradingEngine) -> None:
        """Test layer accessor properties."""
        assert engine.data_layer is not None
        assert engine.signal_layer is not None
        assert engine.risk_layer is not None
        assert engine.execution_layer is not None

    def test_custom_config(self, custom_engine: TradingEngine) -> None:
        """Test engine with custom configuration."""
        assert custom_engine.config.name == "Test Engine"
