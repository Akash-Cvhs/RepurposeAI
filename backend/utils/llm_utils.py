from __future__ import annotations

from openai import OpenAI

from backend.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
    GROQ_TIMEOUT_SECONDS,
    LLM_PROVIDER,
)


def summarize_text_with_llm(text: str, context: str = "") -> str:
    """Summarize text with Groq (OpenAI-compatible) when configured."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return ""

    if LLM_PROVIDER != "groq" or not GROQ_API_KEY:
        # Signal caller to use deterministic fallback summarization.
        raise RuntimeError("Groq LLM is not configured")

    client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL, timeout=GROQ_TIMEOUT_SECONDS)
    prompt = (
        "You are a pharmaceutical research assistant. "
        "Summarize the internal document into 3-5 concise bullets focused on "
        "repurposing opportunity, efficacy signal, safety/constraints, and evidence quality."
    )

    if context:
        prompt += f" Context: {context}."

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": cleaned[:12000]},
        ],
        temperature=0.2,
        max_tokens=280,
    )

    content = response.choices[0].message.content if response.choices else ""
    return (content or "").strip()
