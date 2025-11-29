"""Trading Engine - Main orchestrator for the multi-layer architecture."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

from stratoquant_nexus.layers import (
    DataLayer,
    ExecutionLayer,
    RiskLayer,
    SignalLayer,
)
from stratoquant_nexus.layers.l0_data import DataLayerConfig
from stratoquant_nexus.layers.l1_signals import SignalLayerConfig
from stratoquant_nexus.layers.l2_risk import RiskLayerConfig
from stratoquant_nexus.layers.l3_execution import ExecutionLayerConfig

logger = structlog.get_logger()


class EngineConfig(BaseModel):
    """Configuration for the trading engine."""

    name: str = Field(default="StratoQuant Nexus", description="Engine name")
    enable_data_layer: bool = Field(default=True, description="Enable data layer")
    enable_signal_layer: bool = Field(default=True, description="Enable signal layer")
    enable_risk_layer: bool = Field(default=True, description="Enable risk layer")
    enable_execution_layer: bool = Field(
        default=True, description="Enable execution layer"
    )
    data_config: DataLayerConfig | None = None
    signal_config: SignalLayerConfig | None = None
    risk_config: RiskLayerConfig | None = None
    execution_config: ExecutionLayerConfig | None = None


class EngineStatus(BaseModel):
    """Current status of the trading engine."""

    running: bool = Field(default=False, description="Whether engine is running")
    layers_initialized: int = Field(
        default=0, description="Number of initialized layers"
    )
    total_layers: int = Field(default=4, description="Total number of layers")
    last_cycle_at: datetime | None = Field(
        default=None, description="Last processing cycle timestamp"
    )
    signals_generated: int = Field(default=0, description="Total signals generated")
    orders_executed: int = Field(default=0, description="Total orders executed")


class TradingEngine:
    """Main trading engine orchestrating all layers.

    The TradingEngine coordinates the multi-layer architecture:
    - L0 Data Layer: Data acquisition & normalization
    - L1 Signal Layer: Signal generation & indicators
    - L2 Risk Layer: Risk management & position sizing
    - L3 Execution Layer: Order execution & management

    Example:
        >>> engine = TradingEngine()
        >>> await engine.start()
        >>> results = await engine.process_cycle(market_data)
        >>> await engine.stop()
    """

    def __init__(self, config: EngineConfig | None = None) -> None:
        """Initialize the trading engine.

        Args:
            config: Engine configuration
        """
        self.config = config or EngineConfig()
        self._running = False
        self._status = EngineStatus()

        # Initialize layers
        self._data_layer = DataLayer(
            self.config.data_config or DataLayerConfig(name="DataLayer")
        )
        self._signal_layer = SignalLayer(
            self.config.signal_config or SignalLayerConfig(name="SignalLayer")
        )
        self._risk_layer = RiskLayer(
            self.config.risk_config or RiskLayerConfig(name="RiskLayer")
        )
        self._execution_layer = ExecutionLayer(
            self.config.execution_config or ExecutionLayerConfig(name="ExecutionLayer")
        )

    @property
    def status(self) -> EngineStatus:
        """Get current engine status."""
        return self._status

    @property
    def is_running(self) -> bool:
        """Check if engine is running."""
        return self._running

    async def start(self) -> None:
        """Start the trading engine and initialize all layers."""
        logger.info("Starting trading engine", name=self.config.name)

        layers_initialized = 0

        if self.config.enable_data_layer:
            await self._data_layer.initialize()
            layers_initialized += 1
            logger.info("Data layer initialized")

        if self.config.enable_signal_layer:
            await self._signal_layer.initialize()
            layers_initialized += 1
            logger.info("Signal layer initialized")

        if self.config.enable_risk_layer:
            await self._risk_layer.initialize()
            layers_initialized += 1
            logger.info("Risk layer initialized")

        if self.config.enable_execution_layer:
            await self._execution_layer.initialize()
            layers_initialized += 1
            logger.info("Execution layer initialized")

        self._running = True
        self._status.running = True
        self._status.layers_initialized = layers_initialized

        logger.info(
            "Trading engine started",
            layers_initialized=layers_initialized,
        )

    async def stop(self) -> None:
        """Stop the trading engine and shutdown all layers."""
        logger.info("Stopping trading engine")

        await asyncio.gather(
            self._data_layer.shutdown(),
            self._signal_layer.shutdown(),
            self._risk_layer.shutdown(),
            self._execution_layer.shutdown(),
        )

        self._running = False
        self._status.running = False
        logger.info("Trading engine stopped")

    async def process_cycle(self, raw_data: Any) -> dict[str, list[Any]]:
        """Run a complete processing cycle through all layers.

        Args:
            raw_data: Raw market data to process

        Returns:
            Dictionary containing results from each layer
        """
        if not self._running:
            raise RuntimeError("Engine is not running. Call start() first.")

        results: dict[str, list[Any]] = {
            "market_data": [],
            "signals": [],
            "risk_assessments": [],
            "execution_reports": [],
        }

        # L0: Process raw data
        if self.config.enable_data_layer:
            market_data = await self._data_layer.process(raw_data)
            results["market_data"] = [market_data]
        else:
            market_data = raw_data

        # L1: Generate signals
        if self.config.enable_signal_layer:
            signals = await self._signal_layer.process(market_data)
            results["signals"] = signals
            self._status.signals_generated += len(signals)
        else:
            signals = []

        # L2: Assess risk
        if self.config.enable_risk_layer:
            risk_assessments = await self._risk_layer.process(signals)
            results["risk_assessments"] = risk_assessments
        else:
            risk_assessments = []

        # L3: Execute orders
        if self.config.enable_execution_layer:
            execution_reports = await self._execution_layer.process(risk_assessments)
            results["execution_reports"] = execution_reports
            self._status.orders_executed += len(
                [r for r in execution_reports if r.success]
            )

        self._status.last_cycle_at = datetime.now(UTC)
        return results

    async def health_check(self) -> dict[str, bool]:
        """Check health of all layers.

        Returns:
            Dictionary of layer health statuses
        """
        return {
            "data_layer": await self._data_layer.health_check(),
            "signal_layer": await self._signal_layer.health_check(),
            "risk_layer": await self._risk_layer.health_check(),
            "execution_layer": await self._execution_layer.health_check(),
        }

    # Layer accessors
    @property
    def data_layer(self) -> DataLayer:
        """Get the data layer."""
        return self._data_layer

    @property
    def signal_layer(self) -> SignalLayer:
        """Get the signal layer."""
        return self._signal_layer

    @property
    def risk_layer(self) -> RiskLayer:
        """Get the risk layer."""
        return self._risk_layer

    @property
    def execution_layer(self) -> ExecutionLayer:
        """Get the execution layer."""
        return self._execution_layer
