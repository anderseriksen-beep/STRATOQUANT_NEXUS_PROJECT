# StratoQuant Domain Knowledge

StratoQuant is a modular, intraday crypto trading engine for perpetual futures
(e.g. BTCUSDT, ETHUSDT) on centralized exchanges.

## Markets and Timeframes

- Instruments: crypto perpetual futures (USDT-margined).
- Main timeframes: 1s, 1m, 3m, 5m, 15m, 1h.
- We care about:
  - Exchange fees, funding, tick size, min order size.
  - Latency and realistic fill assumptions (no magic zero-slippage fills).

## Regimes and Volatility

- The system classifies regimes, e.g.:
  - Calm / range-bound.
  - Trending (up / down).
  - Volatile / chaotic.
- Regime is used to:
  - Adjust position sizing.
  - Enable/disable certain strategies.
  - Tighten or loosen risk parameters (stops, daily loss caps).

## Microstructure and Order Book

- Important concepts:
  - Best bid/ask, spread, depth, order book imbalance.
  - Liquidity voids / air pockets.
  - Sweep activity and spoofing / fake liquidity.
- Execution rules:
  - Prefer limit / post-only where possible.
  - Avoid trading into obvious illiquidity or during extreme sweeps.
  - Always assume non-zero slippage and partial fills.

## Trend / Kinematics

- Multi-timeframe structure:
  - Short-term (1m–5m) drives entries and trade management.
  - Higher TF (15m–1h) defines bias and filters trades.
- We avoid:
  - Single-candle fake breakouts without follow-through.
  - Overfitting to one timeframe or one set of parameters.

## Risk Management

- Hard limits:
  - Max risk per trade.
  - Max risk per day / session.
  - Max concurrent exposure per instrument and overall.
- Every strategy must:
  - Use explicit stop-loss logic.
  - Use position sizing tied to volatility and liquidity.
  - Avoid martingale / uncontrolled averaging down.
- Evaluation:
  - Focus on risk-adjusted performance (drawdowns, volatility of equity),
    not only absolute PnL.

## Architecture Overview

- Python backend:
  - `core/` holds engine components:
    - L0: data feed / ingestion.
    - L3: signal fusion.
    - L4: risk manager.
    - L5: execution bridge.
  - FastAPI app (`core/app.py`) for APIs / services.
- Pine Script v6:
  - Used for TradingView charting and prototyping.
  - Strategies should be portable back to Python logic.

## Coding Standards

- Python:
  - Clear modules with single responsibility (data, features, signals, risk,
    execution).
  - Type hints where practical.
  - Tests under `tests/` for risk-critical and core logic.
- Pine Script v6:
  - Separate:
    1. Inputs and parameters.
    2. Signal logic.
    3. Risk block (SL/TP, position sizing, filters).
  - Expose major risk parameters as inputs for easy experimentation.

## Design Principles

- Capital preservation first, edge second, optimization last.
- Prefer few robust strategies over many fragile ones.
- Make all assumptions about liquidity, fills, and latency explicit in code and docs.
