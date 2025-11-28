---
# apply to all files in the repo
applyTo: "**"
---

This repository is **StratoQuant**, a modular intraday crypto trading engine
for crypto perpetual futures.

When generating or reviewing code for this repo:

- Assume the main code lives under `core/`, with layers for:
  - L0 data feed
  - L3 signal fusion
  - L4 risk manager
  - L5 execution bridge
- Always keep risk management and realistic execution higher priority than PnL.

Domain knowledge:

- Before making design decisions about trading, risk, or microstructure,
  consult: `docs/stratoquant-domain-knowledge.md`.

Build & test:

- To install dependencies, run:

  `pip install -r requirements.txt -r requirements-dev.txt`

- To run tests and checks, run:

  `make test` (or `pytest`)
  `pre-commit run --all-files`

General rules:

- Never store secrets (API keys, credentials) in the repo. Use `.env.local`.
- Avoid martingale / averaging-down strategies and unrealistic zero-slippage assumptions.
- Prefer small, well-focused modules and clear tests in `tests/`.
