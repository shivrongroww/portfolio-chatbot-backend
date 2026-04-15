import aiofiles
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.chat import IngestResponse
from app.core.context import reload_context
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

DOCUMENTS_DIR = Path("data/documents")
SUPPORTED_EXTENSIONS = {".md", ".txt"}
MAX_FILE_SIZE_MB = 5


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/hour")
async def ingest(request: Request, files: list[UploadFile] = File(...)):
    saved, skipped = [], []

    for file in files:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            skipped.append(f"{file.filename} (unsupported type)")
            continue

        content = await file.read()
        if len(content) / (1024 * 1024) > MAX_FILE_SIZE_MB:
            skipped.append(f"{file.filename} (exceeds {MAX_FILE_SIZE_MB}MB)")
            continue

        dest = DOCUMENTS_DIR / file.filename
        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)
        saved.append(file.filename)

    if not saved:
        raise HTTPException(
            status_code=422,
            detail=f"No valid files uploaded. Skipped: {skipped or 'none'}. "
                   f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    reload_context()

    msg = f"Loaded {len(saved)} file(s) into context."
    if skipped:
        msg += f" Skipped: {', '.join(skipped)}."

    return IngestResponse(status="ok", files_processed=len(saved), message=msg)


@router.get("/ingest/status")
async def ingest_status():
    files = [
        {"name": f.name, "size_kb": round(f.stat().st_size / 1024, 1)}
        for f in DOCUMENTS_DIR.iterdir()
        if f.is_file() and f.name != ".gitkeep"
    ]
    return {"document_count": len(files), "documents": files}
