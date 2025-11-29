# Getting Started

This guide will help you get StratoQuant Nexus up and running.

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/anderseriksen-beep/STRATOQUANT_NEXUS_PROJECT.git
cd STRATOQUANT_NEXUS_PROJECT

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Using Docker (Coming Soon)

```bash
docker pull stratoquant/nexus
docker run -p 8080:8080 stratoquant/nexus
```

## First Run

### Using the CLI

```bash
# Run the trading engine
stratoquant
```

### Using Python

```python
import asyncio
from stratoquant_nexus import TradingEngine

async def main():
    engine = TradingEngine()
    await engine.start()
    
    # Your trading logic here
    
    await engine.stop()

asyncio.run(main())
```

## Configuration

Create a `.env` file in the project root:

```bash
STRATOQUANT_LOG_LEVEL=INFO
STRATOQUANT_PAPER_TRADING=true
STRATOQUANT_MAX_POSITIONS=5
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/stratoquant_nexus

# Run only unit tests
pytest tests/unit/
```

## Next Steps

- Read the [Architecture Guide](architecture.md)
- Set up [TradingView Integration](tradingview-integration.md)
- Review [Configuration Options](configuration.md)
