"""Pine Script executor - processes TradingView alerts."""

import time

import structlog

from stratoquant_nexus.layers.l1_signals import (
    SignalStrength,
    SignalType,
    TradingSignal,
)
from stratoquant_nexus.pine_executor.models import (
    AlertType,
    ExecutionResult,
    PineAlert,
    PineStrategy,
)

logger = structlog.get_logger()


class PineExecutor:
    """Executor for TradingView Pine Script alerts.

    This class processes incoming alerts from TradingView webhooks
    and converts them into trading signals for the engine.

    Example:
        >>> executor = PineExecutor()
        >>> executor.register_strategy(strategy)
        >>> signal = await executor.process_alert(alert)
    """

    def __init__(self) -> None:
        """Initialize the Pine executor."""
        self._strategies: dict[str, PineStrategy] = {}
        self._processed_alerts: list[PineAlert] = []

    def register_strategy(self, strategy: PineStrategy) -> None:
        """Register a Pine Script strategy.

        Args:
            strategy: Strategy to register
        """
        self._strategies[strategy.name] = strategy
        logger.info("Strategy registered", strategy_name=strategy.name)

    def unregister_strategy(self, strategy_name: str) -> None:
        """Unregister a Pine Script strategy.

        Args:
            strategy_name: Name of strategy to unregister
        """
        if strategy_name in self._strategies:
            del self._strategies[strategy_name]
            logger.info("Strategy unregistered", strategy_name=strategy_name)

    def get_strategy(self, strategy_name: str) -> PineStrategy | None:
        """Get a registered strategy by name.

        Args:
            strategy_name: Strategy name

        Returns:
            Strategy or None if not found
        """
        return self._strategies.get(strategy_name)

    async def process_alert(self, alert: PineAlert) -> ExecutionResult:
        """Process an incoming Pine Script alert.

        Args:
            alert: Alert to process

        Returns:
            Execution result
        """
        start_time = time.time()

        # Validate strategy
        strategy = self._strategies.get(alert.strategy_name)
        if strategy and not strategy.enabled:
            return ExecutionResult(
                alert=alert,
                executed=False,
                message=f"Strategy {alert.strategy_name} is disabled",
            )

        # Convert alert to trading signal
        signal = self._alert_to_signal(alert)

        self._processed_alerts.append(alert)
        execution_time = (time.time() - start_time) * 1000

        logger.info(
            "Alert processed",
            alert_id=alert.alert_id,
            alert_type=alert.alert_type,
            symbol=alert.symbol,
        )

        return ExecutionResult(
            alert=alert,
            executed=True,
            message=f"Alert converted to {signal.signal_type} signal",
            execution_time_ms=round(execution_time, 2),
        )

    def _alert_to_signal(self, alert: PineAlert) -> TradingSignal:
        """Convert a Pine alert to a trading signal.

        Args:
            alert: Pine alert to convert

        Returns:
            Trading signal
        """
        # Map alert types to signal types
        signal_type_map = {
            AlertType.LONG_ENTRY: SignalType.BUY,
            AlertType.SHORT_EXIT: SignalType.BUY,
            AlertType.SHORT_ENTRY: SignalType.SELL,
            AlertType.LONG_EXIT: SignalType.SELL,
            AlertType.STOP_LOSS: SignalType.SELL,
            AlertType.TAKE_PROFIT: SignalType.SELL,
            AlertType.CUSTOM: SignalType.HOLD,
        }

        signal_type = signal_type_map.get(alert.alert_type, SignalType.HOLD)

        return TradingSignal(
            symbol=alert.symbol,
            signal_type=signal_type,
            strength=SignalStrength.MODERATE,
            price=alert.price,
            timestamp=alert.timestamp,
            indicators={"source": "pine_script", "strategy": alert.strategy_name},
            confidence=0.7,  # Pine signals default confidence
        )

    def get_processed_alerts(self) -> list[PineAlert]:
        """Get list of processed alerts.

        Returns:
            List of processed alerts
        """
        return self._processed_alerts.copy()

    def clear_processed_alerts(self) -> None:
        """Clear the processed alerts list."""
        self._processed_alerts.clear()
