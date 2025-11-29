# Architecture

StratoQuant Nexus uses a multi-layer architecture designed for institutional-grade trading.

## Layer Overview (L0-L100)

The engine implements a hierarchical layer system where each layer has specific responsibilities:

```
┌─────────────────────────────────────────────────────────┐
│                    Trading Engine                        │
├─────────────────────────────────────────────────────────┤
│ L3: Execution Layer                                      │
│     └── Order creation, submission, fills                │
├─────────────────────────────────────────────────────────┤
│ L2: Risk Layer                                           │
│     └── Position sizing, stop-loss, portfolio limits     │
├─────────────────────────────────────────────────────────┤
│ L1: Signal Layer                                         │
│     └── Technical indicators, signal generation          │
├─────────────────────────────────────────────────────────┤
│ L0: Data Layer                                           │
│     └── Market data acquisition, normalization           │
└─────────────────────────────────────────────────────────┘
```

## L0: Data Layer

**Responsibility**: Data acquisition and normalization

The Data Layer is responsible for:
- Fetching market data from exchanges
- Normalizing data into standard OHLCV format
- Managing historical data storage
- Validating data integrity

### Key Components

- `OHLCV`: Candlestick data model
- `MarketData`: Container for multiple symbols
- `DataLayer`: Processing layer

### Example

```python
from stratoquant_nexus.layers import DataLayer
from stratoquant_nexus.layers.l0_data import OHLCV, Timeframe

layer = DataLayer()
await layer.initialize()

# Process raw candle data
market_data = await layer.process(candles)
```

## L1: Signal Layer

**Responsibility**: Signal generation from technical indicators

The Signal Layer is responsible for:
- Calculating technical indicators (RSI, MACD, etc.)
- Generating buy/sell/hold signals
- Aggregating multiple signal sources
- Providing confidence scores

### Key Components

- `TradingSignal`: Signal model with type, strength, confidence
- `SignalLayer`: Signal generation layer

### Example

```python
from stratoquant_nexus.layers import SignalLayer

layer = SignalLayer()
await layer.initialize()

# Generate signals from market data
signals = await layer.process(market_data)
```

## L2: Risk Layer

**Responsibility**: Risk management and position sizing

The Risk Layer is responsible for:
- Calculating optimal position sizes
- Setting stop-loss and take-profit levels
- Enforcing portfolio exposure limits
- Approving/rejecting trades based on risk

### Key Components

- `RiskAssessment`: Result of risk evaluation
- `PositionSize`: Calculated position parameters
- `RiskLayer`: Risk management layer

### Example

```python
from stratoquant_nexus.layers import RiskLayer

layer = RiskLayer()
await layer.initialize()

# Assess risk for signals
assessments = await layer.process(signals)
```

## L3: Execution Layer

**Responsibility**: Order execution and management

The Execution Layer is responsible for:
- Creating orders from approved assessments
- Submitting orders to exchanges
- Managing order lifecycle
- Tracking fills and execution quality

### Key Components

- `Order`: Trading order model
- `ExecutionReport`: Execution result
- `ExecutionLayer`: Order execution layer

### Example

```python
from stratoquant_nexus.layers import ExecutionLayer

layer = ExecutionLayer()
await layer.initialize()

# Execute approved assessments
reports = await layer.process(assessments)
```

## Trading Engine

The `TradingEngine` class orchestrates all layers:

```python
from stratoquant_nexus import TradingEngine

engine = TradingEngine()
await engine.start()

# Run a complete cycle
results = await engine.process_cycle(raw_data)

# Results contain output from each layer
market_data = results["market_data"]
signals = results["signals"]
assessments = results["risk_assessments"]
reports = results["execution_reports"]

await engine.stop()
```

## Data Flow

```
Raw Data → L0 (Data) → Normalized Data
                           ↓
         → L1 (Signal) → Trading Signals
                           ↓
         → L2 (Risk) → Risk Assessments
                           ↓
         → L3 (Execution) → Execution Reports
```

## Extensibility

The architecture supports extension through:
- Custom layers (L4-L100)
- Custom indicators
- Custom risk models
- Multiple exchange adapters
