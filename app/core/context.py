from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DOCUMENTS_DIR = Path("data/documents")
_portfolio_context: str | None = None


def load_portfolio_context() -> str:
    """
    Load all markdown and text files from data/documents into a single string.
    Called once at startup and cached for the lifetime of the process.
    """
    global _portfolio_context
    if _portfolio_context is not None:
        return _portfolio_context

    docs = sorted(DOCUMENTS_DIR.glob("*.md")) + sorted(DOCUMENTS_DIR.glob("*.txt"))
    if not docs:
        logger.warning("No documents found in data/documents — bot will have no portfolio context.")
        _portfolio_context = ""
        return _portfolio_context

    parts = []
    for path in docs:
        if path.name == ".gitkeep":
            continue
        content = path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(f"## {path.stem}\n\n{content}")
            logger.info(f"Loaded: {path.name} ({len(content)} chars)")

    _portfolio_context = "\n\n---\n\n".join(parts)
    logger.info(f"Total portfolio context: {len(_portfolio_context)} chars across {len(parts)} file(s)")
    return _portfolio_context


def reload_context():
    """Force a reload of documents (called after new files are uploaded)."""
    global _portfolio_context
    _portfolio_context = None
