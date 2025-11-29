# StratoQuant Nexus Project

[![CI](https://github.com/anderseriksen-beep/STRATOQUANT_NEXUS_PROJECT/actions/workflows/ci.yml/badge.svg)](https://github.com/anderseriksen-beep/STRATOQUANT_NEXUS_PROJECT/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An institutional-grade crypto trading engine with multi-layer architecture, TradingView Pine Script integration, and comprehensive risk management.

## Features

- **Multi-Layer Architecture (L0-L100)**
  - L0 Data Layer: Market data acquisition & normalization
  - L1 Signal Layer: Technical indicators & signal generation
  - L2 Risk Layer: Position sizing & portfolio protection
  - L3 Execution Layer: Order management & execution

- **TradingView Integration**
  - Pine Script webhook receiver
  - Alert parsing & validation
  - Automatic signal conversion

- **Risk Management**
  - Position sizing based on risk parameters
  - Stop-loss & take-profit automation
  - Portfolio exposure limits

- **Developer Experience**
  - Pre-commit hooks (black, isort, ruff)
  - Comprehensive pytest suite
  - VS Code devcontainer support
  - GitHub Actions CI/CD

## Quick Start

### Prerequisites

- Python 3.10+
- pip or uv package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/anderseriksen-beep/STRATOQUANT_NEXUS_PROJECT.git
cd STRATOQUANT_NEXUS_PROJECT

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Basic Usage

```python
import asyncio
from stratoquant_nexus import TradingEngine

async def main():
    # Initialize the trading engine
    engine = TradingEngine()
    
    # Start all layers
    await engine.start()
    
    # Process market data through all layers
    results = await engine.process_cycle(market_data)
    
    # Access results
    signals = results["signals"]
    assessments = results["risk_assessments"]
    reports = results["execution_reports"]
    
    # Shutdown
    await engine.stop()

asyncio.run(main())
```

### Running the CLI

```bash
# Start the trading engine
stratoquant
```

## Project Structure

```
STRATOQUANT_NEXUS_PROJECT/
├── src/stratoquant_nexus/
│   ├── layers/                 # Multi-layer architecture
│   │   ├── base.py            # Base layer class
│   │   ├── l0_data.py         # Data acquisition layer
│   │   ├── l1_signals.py      # Signal generation layer
│   │   ├── l2_risk.py         # Risk management layer
│   │   └── l3_execution.py    # Order execution layer
│   ├── pine_executor/         # TradingView integration
│   │   ├── executor.py        # Alert processing
│   │   ├── models.py          # Alert/strategy models
│   │   └── webhook.py         # Webhook server
│   ├── utils/                 # Utilities
│   │   ├── config.py          # Configuration management
│   │   └── logging.py         # Structured logging
│   ├── engine.py              # Main trading engine
│   └── cli.py                 # Command-line interface
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── config/                    # Configuration files
├── docs/                      # Documentation
├── .github/workflows/         # CI/CD workflows
├── .devcontainer/            # VS Code devcontainer
└── pyproject.toml            # Project configuration
```

## Configuration

### Environment Variables

```bash
# .env file
STRATOQUANT_LOG_LEVEL=INFO
STRATOQUANT_PAPER_TRADING=true
STRATOQUANT_MAX_POSITIONS=10
STRATOQUANT_MAX_POSITION_SIZE_PCT=0.10
```

### Configuration Files

See `config/` directory for YAML configuration options.

## Development

### Running Tests

```bash
# All tests with coverage
pytest

# Unit tests only
pytest tests/unit/ -v

# With coverage report
pytest --cov=src/stratoquant_nexus --cov-report=html
```

### Code Formatting

```bash
# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type checking
mypy src/stratoquant_nexus
```

### Pre-commit Hooks

Pre-commit hooks run automatically on commit:
- black (code formatting)
- isort (import sorting)
- ruff (linting)
- mypy (type checking)

```bash
# Manual run
pre-commit run --all-files
```

## TradingView Integration

### Webhook Setup

1. Configure the webhook server in your settings
2. Set up TradingView alerts with JSON format
3. Point alerts to your webhook endpoint

```json
{
    "action": "{{strategy.order.action}}",
    "symbol": "{{ticker}}",
    "price": {{close}},
    "strategy": "MyStrategy"
}
```

See [TradingView Integration docs](docs/tradingview-integration.md) for details.

## Architecture

The engine uses a layered architecture for clean separation of concerns:

```
┌─────────────────────────────────────────────┐
│           Trading Engine                     │
├─────────────────────────────────────────────┤
│ L3: Execution → Orders, fills, reporting     │
├─────────────────────────────────────────────┤
│ L2: Risk → Position sizing, limits           │
├─────────────────────────────────────────────┤
│ L1: Signals → Indicators, buy/sell signals   │
├─────────────────────────────────────────────┤
│ L0: Data → OHLCV, normalization              │
└─────────────────────────────────────────────┘
```

See [Architecture docs](docs/architecture.md) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves significant risk. Use at your own risk.