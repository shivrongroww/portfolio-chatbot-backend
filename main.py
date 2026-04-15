from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api import router
from app.core.config import get_settings
from app.core.context import load_portfolio_context
import logging

logging.basicConfig(level=logging.INFO)
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Portfolio Chatbot API",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    load_portfolio_context()


@app.get("/health")
async def health():
    return {"status": "ok"}
