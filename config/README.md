# StratoQuant Nexus Project - Configuration

This directory contains configuration files for the trading engine.

## Configuration Files

- `default.yaml` - Default configuration settings
- `development.yaml` - Development environment overrides
- `production.yaml` - Production environment settings

## Environment Variables

Configuration can also be set via environment variables with the `STRATOQUANT_` prefix:

```bash
export STRATOQUANT_LOG_LEVEL=DEBUG
export STRATOQUANT_PAPER_TRADING=true
export STRATOQUANT_MAX_POSITIONS=5
```

## Configuration Priority

1. Environment variables (highest priority)
2. Environment-specific config files
3. Default config file (lowest priority)
