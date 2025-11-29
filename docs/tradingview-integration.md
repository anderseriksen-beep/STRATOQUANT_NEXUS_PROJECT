# TradingView Integration

StratoQuant Nexus includes a Pine Script executor for receiving and processing TradingView alerts.

## Overview

The Pine Executor allows you to:
- Receive webhook alerts from TradingView
- Parse and validate alerts
- Convert alerts to trading signals
- Execute through the trading engine

## Setup

### 1. Configure Webhook Server

The webhook server receives alerts from TradingView:

```python
from stratoquant_nexus.pine_executor import WebhookServer
from stratoquant_nexus.pine_executor.webhook import WebhookConfig

config = WebhookConfig(
    host="0.0.0.0",
    port=8080,
    secret_key="your-secret-key",  # Optional
    path="/webhook"
)

server = WebhookServer(config)
await server.start()
```

### 2. Register Strategies

Register your Pine Script strategies:

```python
from stratoquant_nexus.pine_executor import PineExecutor, PineStrategy

executor = PineExecutor()

strategy = PineStrategy(
    name="MyRSIStrategy",
    description="RSI-based entry and exit",
    symbols=["BTC/USD", "ETH/USD"],
    timeframes=["1h", "4h"],
    risk_multiplier=1.0,
    max_positions=5,
)

executor.register_strategy(strategy)
```

### 3. Configure TradingView Alerts

In TradingView, set up alerts with JSON webhooks:

```json
{
    "action": "{{strategy.order.action}}",
    "symbol": "{{ticker}}",
    "price": {{close}},
    "strategy": "MyRSIStrategy",
    "timeframe": "{{interval}}",
    "message": "{{strategy.order.comment}}"
}
```

Point the webhook URL to: `http://your-server:8080/webhook`

## Alert Types

Supported alert types:

| TradingView Action | Alert Type |
|-------------------|------------|
| `buy`, `long` | LONG_ENTRY |
| `sell`, `short` | SHORT_ENTRY |
| `close_long` | LONG_EXIT |
| `close_short` | SHORT_EXIT |
| `stop_loss` | STOP_LOSS |
| `take_profit` | TAKE_PROFIT |

## Example Pine Script

```pine
//@version=5
strategy("StratoQuant Signal", overlay=true)

// RSI-based strategy
rsiValue = ta.rsi(close, 14)

longCondition = rsiValue < 30
shortCondition = rsiValue > 70

if (longCondition)
    strategy.entry("Long", strategy.long)

if (shortCondition)
    strategy.close("Long")
```

## Webhook Payload Format

Expected webhook payload:

```json
{
    "alert_id": "optional-unique-id",
    "action": "buy|sell|long|short|close_long|close_short",
    "symbol": "BTC/USD",
    "exchange": "binance",
    "price": 42000.50,
    "strategy": "MyStrategy",
    "timeframe": "1h",
    "message": "Optional message"
}
```

## Security

### Signature Validation

Enable HMAC signature validation:

```python
config = WebhookConfig(
    secret_key="your-shared-secret"
)
```

TradingView will send a signature header that the server validates.

### Rate Limiting

Consider implementing rate limiting in production:

```python
# Example using a reverse proxy (nginx)
limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;
```

## Processing Alerts

Handle incoming alerts:

```python
from stratoquant_nexus.pine_executor import PineExecutor, PineAlert

executor = PineExecutor()

async def handle_alert(alert: PineAlert):
    result = await executor.process_alert(alert)
    
    if result.executed:
        print(f"Alert processed: {result.message}")
    else:
        print(f"Alert skipped: {result.message}")

# Register with webhook server
server.on_alert(handle_alert)
```

## Integration with Trading Engine

Connect the Pine executor to the trading engine:

```python
from stratoquant_nexus import TradingEngine
from stratoquant_nexus.pine_executor import PineExecutor, WebhookServer

engine = TradingEngine()
executor = PineExecutor()

async def on_alert(alert):
    result = await executor.process_alert(alert)
    
    if result.executed:
        # Convert to engine format and process
        signals = [executor._alert_to_signal(alert)]
        await engine.process_cycle(signals)

server = WebhookServer()
server.on_alert(on_alert)

await engine.start()
await server.start()
```

## Troubleshooting

### Alert Not Received

1. Check webhook URL is accessible
2. Verify TradingView alert is active
3. Check server logs for errors

### Alert Not Executed

1. Verify strategy is registered and enabled
2. Check symbol matches registered symbols
3. Review risk layer constraints

### Signature Validation Failed

1. Verify secret key matches
2. Check for encoding issues
3. Ensure payload hasn't been modified
