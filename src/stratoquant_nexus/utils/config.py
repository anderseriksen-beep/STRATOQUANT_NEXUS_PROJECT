"""Configuration management using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="STRATOQUANT_",
        case_sensitive=False,
    )

    # Application
    app_name: str = "StratoQuant Nexus"
    debug: bool = False
    log_level: str = "INFO"

    # Trading
    default_exchange: str = "binance"
    paper_trading: bool = True
    max_positions: int = 10

    # Risk Management
    max_position_size_pct: float = 0.1
    max_portfolio_exposure_pct: float = 0.5
    default_stop_loss_pct: float = 0.02
    default_take_profit_pct: float = 0.04

    # Webhook Server
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080
    webhook_secret: str = ""

    # API Keys (should be set via environment variables)
    exchange_api_key: str = ""
    exchange_api_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Application settings instance
    """
    return Settings()
