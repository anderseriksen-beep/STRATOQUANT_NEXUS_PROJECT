"""Command-line interface for StratoQuant Nexus."""

import asyncio
import sys

import structlog

from stratoquant_nexus import TradingEngine
from stratoquant_nexus.utils import get_settings, setup_logging


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code
    """
    settings = get_settings()
    setup_logging(log_level=settings.log_level)
    logger = structlog.get_logger()

    logger.info(
        "Starting StratoQuant Nexus",
        version="0.1.0",
        paper_trading=settings.paper_trading,
    )

    try:
        engine = TradingEngine()
        asyncio.run(_run_engine(engine))
        return 0
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        return 0
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        return 1


async def _run_engine(engine: TradingEngine) -> None:
    """Run the trading engine.

    Args:
        engine: Trading engine instance
    """
    logger = structlog.get_logger()

    await engine.start()
    logger.info("Engine started, press Ctrl+C to stop")

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await engine.stop()


if __name__ == "__main__":
    sys.exit(main())
