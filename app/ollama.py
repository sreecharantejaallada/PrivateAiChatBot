# app/ollama.py
import httpx
from .config import settings
from .logger import get_logger

log = get_logger(__name__)

def _build_payload(prompt: str) -> dict:
    return {
        "model": settings.MODEL_NAME,
        "prompt": f"Answer briefly (max {settings.MAX_CHARS} characters):\n{prompt}",
        "stream": False,
        "options": {"num_predict": 150},
    }

async def query_ollama(prompt: str) -> str:
    """Call Ollama asynchronously and truncate to MAX_CHARS."""
    async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
        try:
            resp = await client.post(settings.OLLAMA_URL, json=_build_payload(prompt))
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "")
            return text[: settings.MAX_CHARS]
        except httpx.HTTPError as exc:
            log.error("Ollama request failed", exc_info=exc)
            raise
