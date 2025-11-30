---
applyTo: "core/**"
---

When editing code in `core/`:

- Preserve the L0/L3/L4/L5 separation.
- Keep FastAPI (`core/app.py`) thin; push heavy logic into layer modules.
- Before changing risk or execution logic, explicitly consider:
  - position sizing
  - slippage and partial fills
  - failure modes (exchange errors, timeouts)
