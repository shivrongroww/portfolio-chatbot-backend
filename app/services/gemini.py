import google.generativeai as genai
from app.core.config import get_settings
from app.models.chat import ChatMessage
from typing import Generator

settings = get_settings()

SYSTEM_PROMPT = """You are a helpful portfolio assistant representing Shivang Rai, a \
Product Designer with 2 years of experience. Your job is to answer questions about his \
work, experience, projects, and background in a conversational, engaging, and honest way.

Use ONLY the context provided to answer questions. If the context doesn't contain \
enough information to answer a question, say so honestly — don't make things up.

Keep answers concise but complete. When relevant, mention specific project names, \
roles, or outcomes from the context. Speak in first person on behalf of Shivang.

If someone asks something completely unrelated to the portfolio (e.g., general coding \
help, weather, etc.), politely redirect them to ask about his work."""


def _build_history(history: list[ChatMessage]) -> list[dict]:
    """Convert message history to Gemini's expected format."""
    gemini_history = []
    for msg in history:
        role = "user" if msg.role == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg.content]})
    return gemini_history


def stream_chat(
    message: str,
    history: list[ChatMessage],
    context: str,
) -> Generator[str, None, None]:
    """Yields streamed text chunks from Gemini."""
    genai.configure(api_key=settings.google_api_key)

    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=SYSTEM_PROMPT,
    )

    chat = model.start_chat(history=_build_history(history))

    user_content = message
    if context:
        user_content = (
            f"Relevant context from my portfolio:\n\n{context}\n\n"
            f"---\n\nUser question: {message}"
        )

    response = chat.send_message(user_content, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text
