This repository is StratoQuant, an intraday crypto trading system.

When suggesting code or explanations, assume:

- We trade crypto perpetual futures intraday.
- Risk management and robust execution are more important than maximum leverage.
- Code should be clean, modular Python or Pine Script v6, aligned with the existing layer/architecture.
- For Pine v6, always separate:
  - inputs
  - signal logic
  - risk management (SL/TP, position sizing)

Avoid:

- Martingale or doubling down after losses.
- Unrealistic assumptions about fills or zero slippage.
- Mixing many concerns in a single huge script.
