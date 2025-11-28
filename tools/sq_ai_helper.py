"""
StratoQuant AI helper.

Small utility to call the OpenAI API with StratoQuant-specific domain
knowledge loaded from docs/stratoquant-domain-knowledge.md.

Usage (from repo root):

    export OPENAI_API_KEY=sk-...
    python -m tools.sq_ai_helper

or import in other tools:

    from tools.sq_ai_helper import ask_stratoquant
"""

import os
from pathlib import Path
from typing import Optional

from openai import OpenAI


# Read API key from environment variable.
# Do NOT hard-code the key in this file.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Load shared domain knowledge so all calls use the same background context.
DOMAIN_DOC_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "stratoquant-domain-knowledge.md"
)
if DOMAIN_DOC_PATH.exists():
    DOMAIN_KNOWLEDGE = DOMAIN_DOC_PATH.read_text(encoding="utf-8")
else:
    DOMAIN_KNOWLEDGE = (
        "Domain document docs/stratoquant-domain-knowledge.md not found. "
        "Proceeding with minimal built-in knowledge."
    )


def ask_stratoquant(
    question: str,
    extra_context: Optional[str] = None,
    model: str = "gpt-5.1",
) -> str:
    """
    Ask the StratoQuant assistant a question.

    Parameters
    ----------
    question:
        Natural-language question or instruction.
    extra_context:
        Optional extra text (code, logs, data) to include in the prompt.
    model:
        OpenAI model name. For heavier coding tasks you can switch to
        'gpt-5.1-codex' if available.

    Returns
    -------
    str
        The model's main text response.
    """
    if client.api_key is None:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")

    input_messages = [
        {
            "role": "user",
            "content": (
                "You are the StratoQuant assistant. Use the following domain "
                "knowledge as your background context:\n\n"
                f"{DOMAIN_KNOWLEDGE}\n\n"
                "Now answer the user's question."
            ),
        }
    ]

    if extra_context:
        input_messages.append(
            {
                "role": "user",
                "content": f"Additional context:\n\n{extra_context}",
            }
        )

    input_messages.append({"role": "user", "content": question})

    response = client.responses.create(
        model=model,
        instructions=(
            "Be precise and practical. Prefer concrete code, trading logic, and "
            "risk-aware explanations. Assume this is the StratoQuant repository."
        ),
        input=input_messages,
    )

    return response.output_text


def _cli_loop() -> None:
    """Simple REPL for quick experiments."""
    print("StratoQuant AI helper. Empty line to exit.\n")
    while True:
        try:
            q = input("StratoQuant> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not q:
            break

        try:
            answer = ask_stratoquant(q)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {exc}")
            continue

        print()
        print(answer)
        print("-" * 80)


if __name__ == "__main__":
    _cli_loop()
