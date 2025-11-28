This repository is **StratoQuant**, a modular intraday crypto trading engine.

When suggesting code, explanations, or refactors, assume:

- We trade crypto perpetual futures intraday (e.g. BTCUSDT, ETHUSDT).
- Robust risk management and realistic execution are more important than
  maximizing leverage or raw PnL.
- Core Python code lives primarily under `core/` and is organised by layers:
  data feed, signal fusion, risk, execution, and API.
- Tests live under `tests/` and should be kept in sync with core logic.
- TradingView strategies and indicators are written in **Pine Script v6**.

Guidelines for suggestions:

- Prefer clean, modular Python with clear separation of concerns.
- For Pine v6, always separate:
  - Inputs and configuration.
  - Signal logic.
  - Risk management (SL/TP, sizing, filters).
- Highlight important risk or execution implications when changing strategy
  logic or order handling.
- Avoid strategies that rely on martingale, unlimited averaging down, or
  unrealistic zero-slippage assumptions.
- Never suggest committing secrets (API keys, credentials) to the repository;
  refer to `.env.local` and environment variables instead.
