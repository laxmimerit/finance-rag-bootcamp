"""The finalized pipeline. The notebook and the Chainlit app both use this."""

from pathlib import Path

from dotenv import load_dotenv
from ragwire import RAGWire

ROOT = Path(__file__).resolve().parent.parent


def get_rag():
    """Load .env (LangSmith tracing) and return the configured pipeline."""
    load_dotenv(ROOT / ".env")
    return RAGWire(str(ROOT / "config" / "finance_rag.yaml"))
