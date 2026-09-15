"""PlagiSense explainable NLP analysis module."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from backend.nlp.engine import analyze_documents
except ImportError:
    try:
        from .engine import analyze_documents
    except ImportError:
        from engine import analyze_documents  # type: ignore

__all__ = ["analyze_documents"]
