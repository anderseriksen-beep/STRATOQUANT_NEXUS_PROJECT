# StratoQuant Architecture (L0–L100)

This document gives a **practical, implementation-oriented overview** of the
StratoQuant architecture from **L0 to L100**, grouped by domain. It is written
for:

- Developers working in `core/`, `tests/`, and related tooling.
- Copilot (code review + coding agent) to understand how the system fits
  together and where changes belong.

For detailed blueprints and layer-by-layer specs, see:

- `Full_Blueprints_v2.txt`
- `Layer_Inventory_Implementation_Status_v2.txt`
- `Domain-Level_Gap_Analysis_Progress_v2.txt`
- `TCN-10000_Priority_TODO_List_Roadmap_v2.txt`

This document is the **high-level map** that everything else should follow.

---

## 1. System Overview

### 1.1 Roles

- **Python “Master Engine”**
  - Lives in `core/` and surrounding modules.
  - Responsible for data ingestion, signal generation, risk management,
    execution orchestration, monitoring, and persistence.
- **Pine Script v6 “Executor / Mirror”**
  - Lives in separate Pine files (not in this repo) or under `pine/` if added.
  - Used for TradingView visualization and as a failsafe execution & validation
    layer mirroring Python logic.

### 1.2 High-Level Data Flow

1. **L0 Data Feed**
   - Ingests market data from exchanges (REST/WebSocket).
   - Normalizes into unified OHLCV / order book / trades structures.

2. **Feature & Regime Layers (L1–L2, L11–L25)**
   - Build returns, volatility, trend, and state features on multiple horizons.
   - Classify regimes (calm, trending, volatile, chaotic).

3. **Microstructure Layers (L8–L10, L59, L61–L63)**
   - Take order book snapshots and recent trades to derive liquidity,
     spread, imbalance, and tradeability scores.

4. **Kinematics, Patterns, and Fusion (L2, L11–L50, L51–L58, L60, L3, L7)**
   - Trend / momentum logic.
   - Pattern recognition (multi-horizon).
   - Fusion layers combine all domain signals into an **action proposal**.

5. **Risk & Tail Layers (L4, L74–L80, L81, L83–L87, L91–L95)**
   - Apply risk rules, caps, and constraints.
   - Sanity-check proposed actions against exposure, drawdowns, and tails.

6. **Execution & Pine Mirror (L5, L69, L88–L90, L96–L100)**
   - Translate approved actions into orders.
   - Manage order lifecycle and error handling.
   - Mirror critical decisions into Pine for visualization, monitoring, and
     cross-checks.

7. **Meta-Learning & RL (L6, L65, L82)**
   - Monitor performance over time.
   - Adapt hyperparameters and strategy selection.
   - (Later) reinforcement learning for policy adjustments.

---

## 2. Domain Map & Layer Index

Domain → primary layers:

- **Data Domain**:  
  - L0
- **Regime Domain**:  
  - L1, L64
- **Microstructure Domain**:  
  - L8, L9, L10, L59, L61, L62, L63
- **Kinematics Domain**:  
  - L2, L11–L18, L19–L25, L51–L58, L60
- **Pattern Domain**:  
  - L26–L50
- **Expectancy & Fusion Domain**:  
  - L3, L7, L66–68, L70–73, L75
- **Risk & Tail Domain**:  
  - L4, L74, L76–80, L81, L83, L84, L85–87, L91–95
- **Meta-Learning & Adaptation Domain**:  
  - L6, L65
- **Reinforcement Learning Domain**:  
  - L82
- **Pine Mirror & Execution Domain**:  
  - L5, L69, L88–90, L96–100

The rest of this document summarizes each domain in terms of:

- Mission and scope
- Key inputs / outputs
- Typical modules and configs
- Testing priorities

---

## 3. Data Domain (L0)

**Mission:** provide a **single, clean, time-aligned data bedrock** for all
higher layers.

- **Primary layer:** L0 – Data Ingestion & Market Feed.
- **Location:** `core/l0_data_feed.py` (or related modules).
- **Config:** `config/data.yml` (or similar data feed config).

### 3.1 Responsibilities

- Connect to exchanges (e.g. Binance) via REST, WebSocket, or internal adapters.
- Normalize:
  - Trades
  - Order book snapshots
  - OHLCV bars for multiple timeframes
- Handle:
  - Reconnects, rate limits, timeouts.
  - Time alignment and gap-filling (within reason).
  - Simple quality checks (stale feeds, missing symbols, outliers).

### 3.2 Inputs

- Exchange endpoints and credentials.
- Asset universe (list of tradable symbols).
- Timeframe configuration.

### 3.3 Outputs

- Unified data structures, e.g.:
  - Tick stream / trades.
  - Order book snapshots.
  - Multi-timeframe OHLCV.
- Optional cached / persisted formats (Parquet, Feather, etc).

### 3.4 Testing Priorities

- Data integrity and correct resampling.
- Recovery from disconnections.
- Correct timezone / timestamp handling.
- Backtest mode vs live mode consistency.

---

## 4. Regime Domain (L1, L64)

**Mission:** classify **market state** (regime) to steer risk, sizing, and
strategy mix.

- **Layers:** L1, L64.
- **Location (typical):** `core/regime_*.py`.
- **Config:** `config/regime.yml` or part of a global config.

### 4.1 Responsibilities

- Compute volatility and market state features:
  - Rolling returns, realized variance, ATR, volume & spread conditions.
- Map feature space → discrete regimes, for example:
  - CALM / RANGE
  - TREND UP / TREND DOWN
  - HIGH VOL / CHAOTIC
- Provide regime probabilities when possible.

### 4.2 Inputs

- Data from L0 (recent prices, returns, volumes).
- Optional microstructure inputs (spread, depth, etc).

### 4.3 Outputs

- Regime label per instrument and timeframe.
- Regime confidence / probabilities.
- Volatility metrics passed downstream to risk & kinematics layers.

### 4.4 Testing Priorities

- Stability: small data changes should not cause wild regime flips.
- Sensible behaviour in edge cases (flash crashes, extreme gaps).
- Correct integration with risk and sizing.

---

## 5. Microstructure Domain (L8, L9, L10, L59, L61–L63)

**Mission:** translate **order book + recent trade flow** into actionable
microstructure features and tradeability scores.

- **Layers:** L8, L9, L10, L59, L61, L62, L63.
- **Location (typical):** `core/microstructure_*.py`.
- **Config:** `config/microstructure.yml`.

### 5.1 Responsibilities

- Build features from order book snapshots:
  - Spread, mid-price, depth at best N levels.
  - Order book imbalance (bid vs ask).
  - Slippage proxies for different order sizes.
- Analyze recent trade flow:
  - Aggressive vs passive volume.
  - Short-term buying/selling pressure.

- Map these into:
  - **Tradeability scores** (is it safe to trade now?).
  - **Liquidity classes** (thin, normal, deep).
  - Filters for **when to skip trading** entirely.

### 5.2 Inputs

- Order book snapshots and trades from L0.
- Current regimes from L1 (optional, for context).

### 5.3 Outputs

- Microstructure feature vector.
- Tradeability / liquidity score signals.
- Flags for “avoid trading now” conditions.

### 5.4 Testing Priorities

- Correct feature calculations under different depth configurations.
- Sensible slippage estimates given book depth.
- Robustness to data glitches (empty book, partial book, stale snapshots).

---

## 6. Kinematics Domain (L2, L11–L18, L19–L25, L51–L58, L60)

**Mission:** express **trend, momentum, and price dynamics** across multiple
time horizons.

- **Layers:** L2, L11–L18, L19–L25, L51–L58, L60.
- **Location (typical):** `core/kinematics_*.py`.
- **Config:** `config/kinematics.yml`.

### 6.1 Responsibilities

- Compute a hierarchy of trend & momentum features:
  - Short-term: 1m–5m.
  - Medium-term: 15m–1h.
- Use moving averages, regressions, or other filters to detect:
  - Direction (up/down/sideways).
  - Strength / persistence of moves.
  - Pullback vs breakout behaviour.

- Provide:
  - Trend states / scores.
  - Momentum signs.
  - Reversion vs continuation biases.

### 6.2 Inputs

- Time-series features from L0 (and L1 for volatility context).
- Possibly microstructure filters (avoid signals in illiquid conditions).

### 6.3 Outputs

- Multi-timeframe trend / momentum feature set.
- Directional bias indicators for use in pattern / fusion layers.

### 6.4 Testing Priorities

- Correct handling of look-ahead bias (no future data).
- Smooth behaviour during regime transitions.
- Symmetry / consistency across assets and timeframes.

---

## 7. Pattern Domain (L26–L50)

**Mission:** capture **higher-order patterns** (combinations of trends,
volatility, microstructure) that have predictive value.

- **Layers:** L26–L50.
- **Location (typical):** `core/patterns_*.py`.
- **Config:** `config/patterns.yml`.

### 7.1 Responsibilities

- Encode patterns such as:
  - Breakout-with-confirmation.
  - Pullback-in-trend.
  - Volatility compress / expansion.
  - Liquidity traps and mean reversion setups.

- Use:
  - Deterministic pattern logic.
  - Simple statistical models.
  - Later: shallow learning models.

### 7.2 Inputs

- Features from kinematics, microstructure, and regime domains.
- Optionally external alpha sources.

### 7.3 Outputs

- Pattern signals:
  - Pattern IDs.
  - Pattern-specific confidence / quality scores.
  - Side suggestions (long/short/flat).

### 7.4 Testing Priorities

- Backtest stability: patterns shouldn’t vanish with minor parameter changes.
- Clear, interpretable logic (prefer explicit code over opaque magic).
- Avoid overfitting to a single asset or time period.

---

## 8. Expectancy & Fusion Domain (L3, L7, L66–L68, L70–73, L75)

**Mission:** fuse all domain outputs into a **coherent action proposal** with
expected value and confidence.

- **Layers:** L3, L7, L66–L68, L70–73, L75.
- **Location (typical):** `core/fusion_engine.py` (e.g. `l3_fusion_engine.py`).
- **Config:** `config/fusion.yml`.

### 8.1 Responsibilities

- Combine:
  - Regime labels.
  - Trend / momentum features.
  - Pattern signals.
  - Microstructure & tradeability.
- Produce:
  - Direction proposal (long/short/flat).
  - Raw score of expected edge (before risk filters).
  - Time horizon / holding expectations.

### 8.2 Inputs

- All upstream domain features (L0–L2, L8–L10, L26–L50, etc.).
- Risk parameters / constraints for context.

### 8.3 Outputs

- **Action proposal object**, passed to L4 risk:
  - Symbol, side, size suggestion (pre-risk).
  - Expected reward, risk, probability of success (where possible).
  - Confidence or priority ranking vs other signals.

### 8.4 Testing Priorities

- Fusion logic should be robust and monotonic with key features:
  - e.g. stronger trend & good liquidity → not smaller edge.
- Clear mapping from input features to output score.
- Consistency across assets and timeframes.

---

## 9. Risk & Tail Domain (L4, L74, L76–L80, L81, L83–L87, L91–95)

**Mission:** enforce **capital preservation**, tail control, and global
constraints.

- **Layers:** L4, L74, L76–L80, L81, L83–L87, L91–95.
- **Location (typical):** `core/l4_risk_manager.py` and related modules.
- **Config:** `config/risk.yml` or `config/risk_*.yml`.

### 9.1 Responsibilities

- Per-trade risk:
  - Position sizing.
  - Stop-loss levels (price or volatility-based).
  - Take-profit / trailing logic.

- Global risk:
  - Daily/weekly loss limits.
  - Max open risk per instrument and overall.
  - Max leverage / exposure.

- Tail & scenario checks:
  - Stress tests on volatility spikes, gaps, and liquidity dry-ups.
  - Hard “kill switches” when conditions are too extreme.

### 9.2 Inputs

- Action proposals from fusion domain.
- Regime / volatility metrics.
- Current positions & PnL.
- Configured risk parameters and portfolio limits.

### 9.3 Outputs

- **Approved action** with final size & risk parameters, OR:
  - Rejection / downgrade (e.g. smaller size, no trade).
- Updated risk state used by monitoring & meta layers.

### 9.4 Testing Priorities

- No action may bypass the risk manager.
- Enforcement of all hard caps in both backtest and live modes.
- Correct behaviour under extreme input values (e.g. zero liquidity).

---

## 10. Meta-Learning & Adaptation Domain (L6, L65)

**Mission:** adapt strategies, parameters, and weights over time based on
performance.

- **Layers:** L6, L65.
- **Location (typical):** `core/meta_*.py`.
- **Config:** `config/meta.yml`.

### 10.1 Responsibilities

- Monitor:
  - Strategy and layer performance (by domain, symbol, timeframe).
  - Risk-adjusted metrics and stability.
- Adapt:
  - Strategy weights.
  - Regime thresholds.
  - Pattern activation / deactivation.

### 10.2 Inputs

- Trade logs, PnL curves, and risk metrics.
- Diagnostics from execution & risk layers.

### 10.3 Outputs

- Updated configuration snapshots.
- Recommendations / automatic changes to strategy mix or parameters.

---

## 11. Reinforcement Learning Domain (L82)

**Mission:** provide a framework for **learning policies from interaction** with
the environment.

- **Layer:** L82.
- **Location (typical):** `core/rl_*.py`.
- **Config:** `config/rl.yml`.

### 11.1 Responsibilities

- ORCHESTRATION of RL experiments (on top of stable baseline strategies).
- Interaction with a simulated or live environment (carefully risk-limited).
- Learning policy adjustments or reward shaping.

### 11.2 Inputs/Outputs

- Inputs: environment state from other layers.
- Outputs: policy parameters, strategy weights, or decision overrides (subject
  to risk manager approval).

---

## 12. Pine Mirror & Execution Domain (L5, L69, L88–L90, L96–100)

**Mission:** translate approved actions into **realistic order flow**, and
mirror key behaviour into Pine for oversight.

- **Layers:** L5, L69, L88–L90, L96–100.
- **Location (typical):** `core/l5_execution_bridge.py` & Pine files.
- **Config:** `config/execution.yml`, exchange configs.

### 12.1 Responsibilities

- Execution bridging:
  - Convert actions → orders (market, limit, post-only, etc.).
  - Manage order lifecycle (place, modify, cancel, error handling).
  - Respect exchange constraints and rate limits.

- Pine mirror:
  - Output signals and risk state to a JSON schema consumed by Pine.
  - In Pine, reconstruct the strategy view on TradingView for monitoring.

### 12.2 Inputs

- Approved actions from L4.
- Live market data from L0.
- Exchange states and open positions.

### 12.3 Outputs

- Order instructions to broker/exchange clients.
- Execution logs, fills, and error reports.
- Pine-compatible data streams for charts.

### 12.4 Testing Priorities

- Correct mapping of sizes and sides to exchange API.
- Robust handling of partial fills, rejects, and disconnections.
- Consistency between Python and Pine behaviour when given the same signals.

---

## 13. Cross-Cutting Services

### 13.1 Logging & Monitoring

- **Location:** `core/logging_config.py`, monitoring hooks, and `logs/`.
- **Goals:**
  - Structured logs with correlation IDs (e.g. symbol, strategy, layer).
  - Logs for:
    - data anomalies (L0)
    - regime changes (L1)
    - entry/exit decisions (fusion + risk + execution)
  - Easy filtering for debugging and auditing.

### 13.2 Configuration & Wiring

- **Location:** YAML files under `config/`, plus wiring specs such as
  `wiring_master.yaml`.
- **Goals:**
  - Declarative configuration of domains, layers, and data flows.
  - Allow domain-specific MACHINE_SPECs to be applied via scripts such as
    `domain_apply.py`.

### 13.3 Health & Ops

- **Location:** `health_check.py`, `wiring_check.py`, `ops_utils.py`, etc.
- **Goals:**
  - Quick check that:
    - data feeds are configured,
    - wiring is consistent,
    - all critical modules import and run basic smoke tests.
  - Provide CLI utilities for:
    - applying domain specs,
    - regenerating configs,
    - running standardized validation suites.

---

## 14. How to Work With This Architecture

When adding or modifying code:

1. **Identify the domain / layer group**  
   - Data? Regime? Microstructure? Kinematics? Pattern? Fusion? Risk? Execution?

2. **Place the change in the correct module**  
   - Keep L0–L5 core engine modules focused and cohesive.
   - Avoid mixing risk logic into data code, or microstructure into UI code.

3. **Update configs & tests together**  
   - If behaviour changes, configs and tests in `tests/` should be updated.

4. **Think end-to-end**  
   - An edit at L0 affects every downstream layer and ultimately risk & execution.
   - Always consider risk and microstructure implications of changes to signals.

This document should remain the **canonical high-level map** for StratoQuant.
Whenever the engine architecture changes, update this file so humans and tools
(Copilot, AI helpers) stay aligned.
