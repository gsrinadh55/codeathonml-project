"""Embeddings and semantic similarity calculation for PlagiSense."""

import math
import re
import sys
from pathlib import Path
from typing import Any, List, Optional, Union

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Optional ML libraries with graceful fallbacks
np: Any = None
cosine_similarity: Any = None
SentenceTransformer: Any = None

try:
    import numpy as np  # type: ignore
except (ImportError, Exception):
    np = None

try:
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
except (ImportError, Exception):
    cosine_similarity = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except (ImportError, Exception):
    SentenceTransformer = None

_HAS_ML: bool = bool(np is not None and cosine_similarity is not None and SentenceTransformer is not None)

# Safe package imports
try:
    from backend.nlp.lexical import jaccard_similarity
    from backend.nlp.concepts import extract_concepts
except ImportError:
    try:
        from .lexical import jaccard_similarity
        from .concepts import extract_concepts
    except ImportError:
        from lexical import jaccard_similarity  # type: ignore
        from concepts import extract_concepts  # type: ignore

_model: Any = None


def load_model() -> Any:
    """Load the SentenceTransformer model if available with safe fallback."""
    global _model
    if not _HAS_ML or SentenceTransformer is None:
        return None
    if _model is None:
        try:
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            _model = False
    return _model if _model is not False else None


def encode_passages(passages: List[str]) -> Any:
    """Encode a list of text passages into embeddings."""
    if not passages:
        return np.array([]) if (_HAS_ML and np is not None) else []
        
    if _HAS_ML:
        model = load_model()
        if model is not None:
            try:
                return model.encode(passages, normalize_embeddings=True)
            except Exception:
                pass
            
    # Fallback to passage text directly
    return list(passages)


def semantic_similarity(emb_a: Any, emb_b: Any) -> float:
    """Calculate the semantic similarity between two passages or embeddings."""
    if _HAS_ML and cosine_similarity is not None and hasattr(emb_a, 'ndim') and hasattr(emb_b, 'ndim'):
        try:
            arr_a = emb_a
            arr_b = emb_b
            if getattr(arr_a, 'ndim', 0) == 1:
                arr_a = arr_a.reshape(1, -1)
            if getattr(arr_b, 'ndim', 0) == 1:
                arr_b = arr_b.reshape(1, -1)
            sim = cosine_similarity(arr_a, arr_b)[0][0]
            return max(0.0, min(1.0, float(sim)))
        except Exception:
            pass

    # Fallback pure-Python semantic calculation
    if isinstance(emb_a, str) and isinstance(emb_b, str):
        str_a = emb_a.strip()
        str_b = emb_b.strip()
        if not str_a or not str_b:
            return 0.0

        if jaccard_similarity is not None:
            lex = jaccard_similarity(str_a, str_b)
            if lex > 0.90:
                return 1.0
        else:
            lex = 0.0

        if extract_concepts is not None:
            c_a = extract_concepts(str_a)
            c_b = extract_concepts(str_b)
        else:
            c_a = set(re.findall(r'\b\w+\b', str_a.lower()))
            c_b = set(re.findall(r'\b\w+\b', str_b.lower()))

        if not c_a or not c_b:
            return float(lex)

        shared = c_a.intersection(c_b)
        if not shared:
            return float(lex * 0.5)

        overlap_a = len(shared) / len(c_a)
        overlap_b = len(shared) / len(c_b)
        jaccard = len(shared) / len(c_a.union(c_b))

        # High concept alignment indicates strong paraphrase / semantic similarity
        sem = 0.50 * jaccard + 0.35 * max(overlap_a, overlap_b) + 0.15 * min(overlap_a, overlap_b)
        return max(0.0, min(1.0, float(sem)))

    return 0.0


def batch_semantic_similarity(embeddings_a: Any, embeddings_b: Any) -> Any:
    """Calculate similarities between all pairs of embeddings in A and B."""
    if (_HAS_ML and cosine_similarity is not None and np is not None 
            and hasattr(embeddings_a, 'ndim') and len(embeddings_a) > 0 
            and hasattr(embeddings_b, 'ndim') and len(embeddings_b) > 0):
        try:
            sim_matrix = cosine_similarity(embeddings_a, embeddings_b)
            return np.clip(sim_matrix, 0.0, 1.0)
        except Exception:
            pass

    # Fallback 2D matrix
    matrix: List[List[float]] = []
    for a in embeddings_a:
        row = [semantic_similarity(a, b) for b in embeddings_b]
        matrix.append(row)
    return matrix
