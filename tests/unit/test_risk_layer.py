"""Unit tests for the risk layer (L2)."""

from decimal import Decimal

import pytest

from stratoquant_nexus.layers.base import LayerLevel
from stratoquant_nexus.layers.l1_signals import (
    SignalStrength,
    SignalType,
    TradingSignal,
)
from stratoquant_nexus.layers.l2_risk import (
    PositionSize,
    RiskAssessment,
    RiskLayer,
    RiskLayerConfig,
    RiskLevel,
)


class TestRiskLayer:
    """Tests for the RiskLayer class."""

    @pytest.fixture
    def risk_layer(self) -> RiskLayer:
        """Create a risk layer for testing."""
        return RiskLayer()

    @pytest.fixture
    def conservative_risk_layer(self) -> RiskLayer:
        """Create a conservative risk layer."""
        config = RiskLayerConfig(
            name="ConservativeRisk",
            risk_level=RiskLevel.CONSERVATIVE,
            max_position_size_pct=0.05,
            max_portfolio_exposure_pct=0.3,
        )
        return RiskLayer(config)

    @pytest.mark.asyncio
    async def test_layer_initialization(self, risk_layer: RiskLayer) -> None:
        """Test risk layer initialization."""
        await risk_layer.initialize()

        assert risk_layer._initialized
        assert await risk_layer.health_check()

        await risk_layer.shutdown()

    @pytest.mark.asyncio
    async def test_assess_buy_signal(
        self, risk_layer: RiskLayer, sample_buy_signal: TradingSignal
    ) -> None:
        """Test assessing a buy signal."""
        await risk_layer.initialize()

        assessments = await risk_layer.process([sample_buy_signal])

        assert len(assessments) == 1
        assessment = assessments[0]
        assert isinstance(assessment, RiskAssessment)
        assert assessment.signal == sample_buy_signal

        await risk_layer.shutdown()

    @pytest.mark.asyncio
    async def test_assess_sell_signal(
        self, risk_layer: RiskLayer, sample_sell_signal: TradingSignal
    ) -> None:
        """Test assessing a sell signal."""
        await risk_layer.initialize()

        assessments = await risk_layer.process([sample_sell_signal])

        assert len(assessments) == 1
        assessment = assessments[0]
        assert isinstance(assessment, RiskAssessment)

        await risk_layer.shutdown()

    @pytest.mark.asyncio
    async def test_hold_signal_rejected(self, risk_layer: RiskLayer) -> None:
        """Test that HOLD signals are rejected."""
        await risk_layer.initialize()

        hold_signal = TradingSignal(
            symbol="BTC/USD",
            signal_type=SignalType.HOLD,
            strength=SignalStrength.WEAK,
            price=Decimal("42000"),
        )

        assessments = await risk_layer.process([hold_signal])

        assert len(assessments) == 1
        assert not assessments[0].approved
        assert "HOLD" in str(assessments[0].rejection_reason)

        await risk_layer.shutdown()

    @pytest.mark.asyncio
    async def test_position_sizing(
        self, risk_layer: RiskLayer, sample_buy_signal: TradingSignal
    ) -> None:
        """Test position size calculation."""
        await risk_layer.initialize()

        assessments = await risk_layer.process([sample_buy_signal])

        if assessments[0].approved:
            position = assessments[0].position_size
            assert position is not None
            assert position.units > 0
            assert position.stop_loss_price < position.take_profit_price

        await risk_layer.shutdown()

    def test_layer_level(self, risk_layer: RiskLayer) -> None:
        """Test risk layer level is L2."""
        assert risk_layer.level == LayerLevel.RISK

    def test_set_portfolio_value(self, risk_layer: RiskLayer) -> None:
        """Test setting portfolio value."""
        risk_layer.set_portfolio_value(Decimal("500000"))

        assert risk_layer._portfolio_value == Decimal("500000")


class TestPositionSize:
    """Tests for the PositionSize model."""

    def test_position_size_creation(self) -> None:
        """Test position size creation."""
        position = PositionSize(
            symbol="BTC/USD",
            units=Decimal("0.5"),
            notional_value=Decimal("21000"),
            risk_amount=Decimal("420"),
            stop_loss_price=Decimal("41000"),
            take_profit_price=Decimal("43000"),
            risk_reward_ratio=2.0,
        )

        assert position.symbol == "BTC/USD"
        assert position.units == Decimal("0.5")
        assert position.risk_reward_ratio == 2.0
