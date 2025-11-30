import os
from pathlib import Path
from openai import OpenAI

# Read API key from environment variable
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Load the shared domain knowledge so all tools use the same brain
DOMAIN_DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "stratoquant-domain-knowledge.md"
DOMAIN_KNOWLEDGE = DOMAIN_DOC_PATH.read_text(encoding="utf-8")


def ask_stratoquant(question: str, extra_context: str | None = None, model: str = "gpt-5.1") -> str:
    """
    Ask the StratoQuant assistant a question.

    - `question`: your natural language question.
    - `extra_context`: optional code, logs, or data to include.
    - `model`: default is gpt-5.1 for reasoning; you can switch to
      'gpt-5.1-codex' for heavy coding tasks.
    """
    input_messages = [
        {
            "role": "user",
            "content": (
                "You are the StratoQuant assistant. Use the following domain knowledge "
                "as your background context:\n\n"
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
        instructions="Be precise and practical. Prefer concrete code and trading logic.",
        input=input_messages,
    )

    return response.output_text  # main text answer


if __name__ == "__main__":
    # Simple CLI usage: python tools/sq_ai_helper.py
    while True:
        q = input("StratoQuant> ").strip()
        if not q:
            break
        answer = ask_stratoquant(q)
        print()
        print(answer)
        print("-" * 80)
