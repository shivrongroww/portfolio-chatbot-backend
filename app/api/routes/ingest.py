import aiofiles
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.chat import IngestResponse
from app.services.embeddings import ingest_documents, SUPPORTED_EXTENSIONS
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

DOCUMENTS_DIR = Path("data/documents")
MAX_FILE_SIZE_MB = 20


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/hour")
async def ingest(request: Request, files: list[UploadFile] = File(...)):
    """
    Upload one or more documents (PDF, TXT, MD) to be embedded and stored
    in the vector database. Can be called multiple times to add more content.
    """
    saved_paths: list[Path] = []
    skipped: list[str] = []

    for file in files:
        suffix = Path(file.filename).suffix.lower()

        if suffix not in SUPPORTED_EXTENSIONS:
            skipped.append(file.filename)
            continue

        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            skipped.append(f"{file.filename} (exceeds {MAX_FILE_SIZE_MB}MB limit)")
            continue

        dest = DOCUMENTS_DIR / file.filename
        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)
        saved_paths.append(dest)

    if not saved_paths:
        raise HTTPException(
            status_code=422,
            detail=f"No valid files to process. Skipped: {skipped or 'none'}. "
                   f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    try:
        count = await ingest_documents(saved_paths)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    msg = f"Successfully ingested {count} file(s)."
    if skipped:
        msg += f" Skipped: {', '.join(skipped)}."

    return IngestResponse(status="ok", files_processed=count, message=msg)


@router.get("/ingest/status")
async def ingest_status():
    """Returns a list of documents currently stored in the documents folder."""
    files = [
        {"name": f.name, "size_kb": round(f.stat().st_size / 1024, 1)}
        for f in DOCUMENTS_DIR.iterdir()
        if f.is_file() and f.name != ".gitkeep"
    ]
    return {"document_count": len(files), "documents": files}
