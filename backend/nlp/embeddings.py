import math
import re

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_ML = True
except ImportError:
    _HAS_ML = False

_model = None


def load_model():
    """Load the SentenceTransformer model if available."""
    global _model
    if not _HAS_ML:
        return None
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def encode_passages(passages):
    """Encode a list of text passages into embeddings."""
    if not passages:
        return np.array([]) if _HAS_ML else []
        
    if _HAS_ML:
        model = load_model()
        if model is not None:
            return model.encode(passages, normalize_embeddings=True)
            
    # Fallback to passage text directly
    return list(passages)


def semantic_similarity(emb_a, emb_b) -> float:
    """Calculate the semantic similarity between two passages or embeddings."""
    if _HAS_ML and hasattr(emb_a, 'ndim'):
        if emb_a.ndim == 1:
            emb_a = emb_a.reshape(1, -1)
        if emb_b.ndim == 1:
            emb_b = emb_b.reshape(1, -1)
        sim = cosine_similarity(emb_a, emb_b)[0][0]
        return max(0.0, min(1.0, float(sim)))

    # Fallback pure-Python semantic calculation
    if isinstance(emb_a, str) and isinstance(emb_b, str):
        from .lexical import jaccard_similarity
        from .concepts import extract_concepts
        
        lex = jaccard_similarity(emb_a, emb_b)
        if lex > 0.90:
            return 1.0
            
        c_a = extract_concepts(emb_a)
        c_b = extract_concepts(emb_b)
        if not c_a or not c_b:
            return 0.0
            
        shared = c_a.intersection(c_b)
        if not shared:
            return 0.0
            
        overlap_a = len(shared) / len(c_a)
        overlap_b = len(shared) / len(c_b)
        jaccard = len(shared) / len(c_a.union(c_b))
        
        # High concept alignment indicates strong paraphrase / semantic similarity
        sem = 0.50 * jaccard + 0.35 * max(overlap_a, overlap_b) + 0.15 * min(overlap_a, overlap_b)
        return max(0.0, min(1.0, float(sem)))

    return 0.0


def batch_semantic_similarity(embeddings_a, embeddings_b):
    """Calculate similarities between all pairs of embeddings in A and B."""
    if _HAS_ML and hasattr(embeddings_a, 'ndim') and len(embeddings_a) > 0 and hasattr(embeddings_b, 'ndim') and len(embeddings_b) > 0:
        sim_matrix = cosine_similarity(embeddings_a, embeddings_b)
        return np.clip(sim_matrix, 0.0, 1.0)

    # Fallback 2D matrix
    matrix = []
    for a in embeddings_a:
        row = [semantic_similarity(a, b) for b in embeddings_b]
        matrix.append(row)
    return matrix
