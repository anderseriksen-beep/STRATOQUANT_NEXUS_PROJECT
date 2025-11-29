---
applyTo: "**"
excludeAgent: "code-review"
---

When acting as Copilot coding agent for this repository:

- Always run tests and pre-commit hooks before opening a PR.
- If tests or hooks fail, attempt to fix and re-run once.
- If a task touches execution or risk code (L4/L5):
  - Add or update tests in `tests/test_l4*.py` or `tests/test_l5*.py`.
- Prefer smaller, incremental PRs over huge refactors.
