from fastapi import APIRouter
from app.api.routes import chat, ingest

router = APIRouter()
router.include_router(chat.router, tags=["chat"])
router.include_router(ingest.router, tags=["ingest"])
