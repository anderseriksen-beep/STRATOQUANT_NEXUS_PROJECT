"""StratoQuant Nexus - Institutional-grade crypto trading engine.

Multi-layer architecture from data → signals → risk → execution.
"""

__version__ = "0.1.0"

from stratoquant_nexus.engine import TradingEngine

__all__ = ["TradingEngine", "__version__"]
