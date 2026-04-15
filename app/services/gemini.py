import google.generativeai as genai
from app.core.config import get_settings
from app.core.context import load_portfolio_context
from app.models.chat import ChatMessage
from typing import Generator

settings = get_settings()

BASE_SYSTEM_PROMPT = """You are a portfolio assistant representing Shivang Rai, a Product Designer \
with 2 years of experience. Answer questions about his work, experience, projects, and background \
in a conversational, engaging, and honest way.

Use ONLY the information in the portfolio context below to answer questions. If something isn't \
covered, say so honestly — don't make things up. Speak in first person on behalf of Shivang.

If someone asks something unrelated to the portfolio, politely redirect them.

---

PORTFOLIO CONTEXT:

{context}"""


def _build_system_prompt() -> str:
    context = load_portfolio_context()
    if not context:
        return BASE_SYSTEM_PROMPT.replace("{context}", "No portfolio documents loaded yet.")
    return BASE_SYSTEM_PROMPT.format(context=context)


def _build_history(history: list[ChatMessage]) -> list[dict]:
    return [
        {"role": "user" if m.role == "user" else "model", "parts": [m.content]}
        for m in history
    ]


def stream_chat(
    message: str,
    history: list[ChatMessage],
) -> Generator[str, None, None]:
    """Yields streamed text chunks from Gemini."""
    genai.configure(api_key=settings.google_api_key)

    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=_build_system_prompt(),
    )

    chat = model.start_chat(history=_build_history(history))
    response = chat.send_message(message, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text
