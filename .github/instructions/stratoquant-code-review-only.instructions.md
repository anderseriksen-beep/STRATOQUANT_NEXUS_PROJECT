---
applyTo: "**"
excludeAgent: "coding-agent"
---

When performing a code review for this repository:

- Focus on risk, correctness, and microstructure realism first,
  style second.
- If a change modifies execution or risk:
  - Verify that unit tests for L4/L5 exist or suggest new ones.
  - Check for realistic handling of failures (timeouts, rejects).
- Prefer comments with small, concrete suggested changes the
  developer can apply directly.
