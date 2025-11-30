# StratoQuant_Nexus – GitHub Copilot Project Instructions

You are the coding assistant for **StratoQuant_Nexus_Project**.

Your job is to generate **production-grade code, tests and docs** that strictly follow this project’s architecture, specs and templates.

---

## 1. Ground truth & mindset

Always treat these as **canonical**:

- `Specification_StratoQuant_Project.txt`
- `Full_Blueprints_v2.txt`
- `Layer_Inventory_Implementation_Status_v2.txt`
- `Domain-Level_Gap_Analysis_Progress_v2.txt`
- `TCN-10000 Priority TODO List & Implementation_Roadmap_v2.txt`
- `MACHINE_SPEC_*` YAMLs
- `core/system/wiring_master.yaml`
- Templates and legal:
  - `assets/templates/template_python.txt`
  - `assets/templates/template_pine.txt`
  - `assets/templates/template_markdown.txt`
  - `assets/templates/template_txt.txt`
  - `assets/legal/legal_header.txt`
  - `assets/license.md`

**If code conflicts with these specs, the specs win.** Adapt the code, not the design.

Your mindset:

- You are building an **institutional-grade, TCN-10000** engine.
- Optimize for **Trust, Confidence, Noise control, and Auditability**, not quick hacks.
- Every change should either:
  - improve robustness / monitoring / explainability, or
  - bring a layer/domain closer to its spec.

---

## 2. Architecture & layers (L0–L100)

The engine is layered. Common domains:

- **Data (L0)** – ingestion, normalization, feature building.
- **Regime (L1, L64)** – volatility regimes, macro regime shifts.
- **Kinematics (L2, L11–25)** – deep momentum, trend, mean reversion, volatility cycle, continuation/reversal.
- **Pattern (L26–L50)** – candle patterns, continuation/exhaustion structures.
- **Fusion/Expectancy (L3, L51–60, L66–68)** – ensemble models, expectancy, uncertainty.
- **Risk & Tail (L4, L74, L81, L86–87)** – TP/SL, sizing, tail risk, account health.
- **Microstructure (L8–10, L59, L61–63)** – orderbook, spreads, slippage, liquidity regimes, micro-risk.
- **Execution / Bridge (L5, L69–73, L100)** – Python→Pine bridge, failsafes, governance.
- **Feedback/RL/Meta (L6, L7, L65, L82, L88+)** – logging, drift, retraining, RL, self-healing.

When implementing or editing code:

- **Always identify the layer(s) you are touching.**
- Respect the **LAYER CONTRACT**:
  - Inputs (names, shapes, semantics).
  - Outputs (names, shapes, semantics).
  - Failure modes (what happens when data is missing, delayed, corrupt).
  - Metrics hooks (what is logged to `runtime/layer_metrics/`).

Never “smuggle” cross-layer logic. Keep responsibilities local and use wiring.

---

## 3. File & folder conventions

Use and respect existing structure (examples; adjust if the repo differs):

- `core/system/`
  - `wiring_master.yaml` – global wiring graph, **single source of truth**.
  - `domain_apply.py` – applies `MACHINE_SPEC` YAMLs, updates wiring and docs.
  - health / ops / config helpers.
- `core/<domain>/` – domain modules, e.g.:
  - `core/microstructure/l08_microstructure_engine.py`
  - `core/microstructure/l09_orderbook_depth.py`
  - `core/microstructure/l10_fee_slippage_model.py`
- `config/` – YAML configs per domain/layer, plus global engine config.
- `pine/` – Pine v6 executors and layer mirrors (e.g. `pine/layer_mirrors/...`).
- `docs/` – human design docs per domain:
  - `docs/domains/<DOMAIN_ID>_HUMAN_DESIGN.md`
  - summaries, layer inventory, roadmaps.
- `tests/` – mirror the `core/` tree:
  - e.g. `tests/microstructure/test_l08_microstructure_engine.py`.

**When adding anything new**:

1. Choose the correct domain + layer folder.
2. Use the appropriate template (Python/Pine/Markdown/TXT).
3. Update:
   - Domain `MACHINE_SPEC_*.yaml`.
   - `core/system/wiring_master.yaml` via `domain_apply.py` (do **not** hand-edit unless the code clearly expects it).
4. Add tests under `tests/` with matching structure.

---

## 4. Legal headers & templates

For **every** new `.py`, `.pine`, `.md`, `.txt`:

1. Insert the full legal header from `assets/legal/legal_header.txt`.
2. Use the correct template file as the base:
   - Python → `template_python.txt`
   - Pine → `template_pine.txt`
   - Markdown → `template_markdown.txt`
   - Txt / notes → `template_txt.txt`
3. Only replace the placeholder fields (project, file, author, created, version, etc.). Do **not** change the legal wording.

If you generate code or docs, assume another tool/script may later re-apply these templates. Avoid removing or reflowing template markers or special comments like:

- `# AUTO-GENERATED SECTION - DO NOT EDIT`
- `# === LAYER CONTRACT START/END ===`

Honor them.

---

## 5. Python coding rules

- Target **Python 3.11+** (or the version defined in the repo).
- Always:
  - Import explicitly, no unused imports.
  - Use **type hints** on all public functions and classes.
  - Add clear docstrings, with sections: `Args`, `Returns`, `Raises`, `Layer Contract`.
  - Use project logging utilities; never print from production code.
- Prefer:
  - Vectorized operations (NumPy/pandas) where appropriate.
  - Config-driven parameters (via YAML or env) instead of hard-coded magic numbers.
  - Small, composable functions with single responsibility.
- For **layer modules**:
  - Expose a single clear entry point (e.g. `run_layer(...)` or `compute_features(...)`) that matches the LAYER CONTRACT.
  - Validate inputs early (shape, NaNs, required fields).
  - Emit metrics to the designated layer metrics sink (e.g. `runtime/layer_metrics/L08_microstructure.json`).
  - Include graceful fallback behavior for degraded data (e.g. missing orderbook → use ATR/volatility proxy).

---

## 6. Pine Script coding rules

- Use **Pine Script v6**.
- Follow the project’s Pine template and structure.
- Keep Pine focused on:
  - Pre-entry / entry / exit logic.
  - Failsafes, local fallbacks, and on-chart diagnostics.
  - Mirroring Python decisions via JSON/inputs where defined.
- Do **not** embed heavy analytics in Pine if they belong in Python (L2/L3/L4 etc.). Use Pine for:
  - Simple proxies (ATR, RSI, BBW, basic pattern flags).
  - Emergency fallback logic if Python is offline (e.g. safe exits, disabling entries).

---

## 7. MACHINE_SPEC & wiring_master

When generating or editing `MACHINE_SPEC_*.yaml`:

- Ensure each `layer` entry has:
  - `id` (e.g. `"L08"`).
  - `name` (concise and spec-consistent).
  - `role` (short summary from spec).
  - `inputs` / `outputs` (matching spec + actual code).
  - `depends_on` (numerical layers and key upstream domains).
  - `files` (all main code + tests).
  - `status` (`conceptual`, `partial`, `implemented`, etc.).

Do **not** invent dependencies or outputs that contradict `Layer_Inventory_Implementation_Status_v2.txt` or `Full_Blueprints_v2.txt`.

When editing `core/system/wiring_master.yaml`:

- Prefer to adjust via `domain_apply.py` / ops scripts.
- Maintain topological order and consistency:
  - No cycles.
  - All referenced layers must exist.
  - Layer IDs consistent across YAML, code, and docs.

---

## 8. Testing & CI

For any non-trivial code you generate:

- Create/update tests under `tests/` mirroring the module path.
- Use `pytest` style:
  - Arrange–Act–Assert.
  - Clear test names (`test_l08_handles_missing_orderbook_gracefully`).
- Cover:
  - Happy path.
  - Edge cases (missing data, extreme values, degraded sources).
  - Layer contract invariants (e.g. output shapes, NaNs, expected ranges).

When adding new logic that would affect CI:

- Assume GitHub Actions is configured to:
  - Run `pytest`.
  - Run linters (e.g. `flake8`, `ruff`, `black --check`).
- Ensure generated code would pass these checks.

---

## 9. How to respond to user requests

When the human asks for help:

1. **Identify domain + layer(s)** involved.
2. Scan relevant spec docs and existing modules before generating code.
3. Respect existing interfaces; avoid breaking changes unless explicitly asked.
4. If the request is ambiguous, prefer:
   - Completing the most likely layer-consistent behavior, and
   - Leaving precise TODO comments referencing the spec (e.g. `# TODO[L10]: refine slippage model per Full_Blueprints_v2 section L10.3`).

If you are unsure about a detail:

- Prefer a conservative implementation and mark with a clear TODO and spec reference.
