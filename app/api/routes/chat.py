from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.chat import ChatRequest
from app.services.embeddings import retrieve_context
from app.services.gemini import stream_chat
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/chat")
@limiter.limit("8/minute")
@limiter.limit("100/day")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint. Retrieves relevant context via RAG, then streams
    a Gemini response back to the client as Server-Sent Events.
    """
    try:
        context = retrieve_context(body.message)
    except Exception as e:
        logger.warning(f"RAG retrieval failed, proceeding without context: {e}")
        context = ""

    def generate():
        try:
            for chunk in stream_chat(
                message=body.message,
                history=body.history,
                context=context,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: [ERROR] Something went wrong.\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
