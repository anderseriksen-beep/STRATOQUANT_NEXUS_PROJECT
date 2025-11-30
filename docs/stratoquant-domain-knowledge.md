# StratoQuant Domain Knowledge

StratoQuant is an intraday crypto trading system focused on perpetual futures (e.g. BTCUSDT) on centralized exchanges.

## Markets and Instruments

- Trade universe: crypto perpetual futures (BTCUSDT, ETHUSDT, etc.).
- Typical timeframes: 1s, 1m, 3m, 5m, 15m, 1h.
- Exchange microstructure matters: fees, funding, tick size, min size.

## Regime and Volatility

- We classify market regimes (e.g. calm, trending, volatile, chaotic).
- Regime is used to:
  - Adjust position sizing.
  - Enable/disable certain strategies.
  - Tighten or loosen risk limits.

## Microstructure and Order Book

- We care about:
  - Spread, depth, queue position, order book imbalance.
  - Liquidity voids / air pockets and spoofing behavior.
- Execution rules:
  - Prefer limit / post-only where possible.
  - Avoid trading into obvious illiquidity or during aggressive sweeps.
  - Respect latency and realistic fill assumptions.

## Trend / Kinematics

- We use multi-timeframe context:
  - Short-term (1m–5m) momentum for entries.
  - Higher TF (15m–1h) to define bias and filter trades.
- Trend confirmation is required to scale in; we avoid single-candle breakouts without follow-through.

## Risk Management

- Hard caps:
  - Max risk per trade.
  - Max risk per day and per session.
- Use stop-loss and position sizing based on volatility and liquidity.
- No martingale, no uncontrolled averaging down.
- Strategy performance is evaluated by risk-adjusted metrics, not raw PnL.

## Architecture

- Python backend for:
  - Data ingestion and feature building (L0–L20).
  - Signal generation and strategy logic (L40–L60).
  - Execution and brokerage integration (L80+).
- Pine Script v6 for:
  - Visualisation and prototyping on TradingView charts.
  - Strategy prototypes that can be ported to Python.

## Coding Standards

- Python:
  - Clear module boundaries (data, models, strategies, execution, risk).
  - Type hints where practical.
  - Tests for core logic and risk-critical components.
- Pine v6:
  - Separate input section, signal logic, and risk block.
  - Expose key risk parameters (SL, TP, max size) as inputs.
