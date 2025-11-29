"""Base layer class for the multi-tier trading architecture."""

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, Field


class LayerLevel(IntEnum):
    """Layer hierarchy levels (L0-L100 architecture)."""

    DATA = 0  # L0: Data acquisition & normalization
    SIGNALS = 1  # L1: Signal generation & indicators
    RISK = 2  # L2: Risk management & position sizing
    EXECUTION = 3  # L3: Order execution & management
    # Additional layers can be added up to L100 for advanced strategies


class LayerConfig(BaseModel):
    """Base configuration for all layers."""

    enabled: bool = Field(default=True, description="Whether the layer is enabled")
    name: str = Field(..., description="Layer name")
    level: LayerLevel = Field(..., description="Layer hierarchy level")
    log_level: str = Field(default="INFO", description="Logging level")


class BaseLayer(ABC):
    """Abstract base class for all trading engine layers.

    This implements the multi-layer architecture (L0-L100) where each layer
    has a specific responsibility in the trading pipeline.

    Attributes:
        config: Layer configuration
        _initialized: Whether the layer has been initialized
    """

    def __init__(self, config: LayerConfig) -> None:
        """Initialize the base layer.

        Args:
            config: Layer configuration
        """
        self.config = config
        self._initialized = False

    @property
    def name(self) -> str:
        """Get the layer name."""
        return self.config.name

    @property
    def level(self) -> LayerLevel:
        """Get the layer level."""
        return self.config.level

    @property
    def is_enabled(self) -> bool:
        """Check if the layer is enabled."""
        return self.config.enabled

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the layer resources.

        This method should be called before processing data.
        """

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process data through the layer.

        Args:
            data: Input data to process

        Returns:
            Processed output data
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up layer resources.

        This method should be called when shutting down the layer.
        """

    async def health_check(self) -> bool:
        """Check if the layer is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self._initialized and self.is_enabled
