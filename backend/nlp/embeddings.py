import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_model = None

def load_model():
    """Load the SentenceTransformer model if it hasn't been loaded yet."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def encode_passages(passages):
    """
    Encode a list of text passages into embeddings.
    """
    if not passages:
        return np.array([])
    model = load_model()
    embeddings = model.encode(passages, normalize_embeddings=True)
    return embeddings

def semantic_similarity(emb_a, emb_b):
    """
    Calculate the semantic similarity between two single embeddings.
    Since embeddings are normalized, dot product is equivalent to cosine similarity,
    but we use sklearn's cosine_similarity for safety/explicitness.
    emb_a and emb_b should be 1D numpy arrays.
    Returns a float between 0.0 and 1.0.
    """
    # Reshape for sklearn if they are 1D
    if emb_a.ndim == 1:
        emb_a = emb_a.reshape(1, -1)
    if emb_b.ndim == 1:
        emb_b = emb_b.reshape(1, -1)
    
    sim = cosine_similarity(emb_a, emb_b)[0][0]
    return max(0.0, min(1.0, float(sim)))

def batch_semantic_similarity(embeddings_a, embeddings_b):
    """
    Calculate similarities between all pairs of embeddings in A and B.
    Returns a 2D matrix of shape (len(embeddings_a), len(embeddings_b)).
    """
    sim_matrix = cosine_similarity(embeddings_a, embeddings_b)
    # Clip values to ensure they are strictly between 0 and 1
    return np.clip(sim_matrix, 0.0, 1.0)
