import re
import numpy as np
from .embeddings import encode_passages, batch_semantic_similarity

def split_into_passages(text: str) -> list:
    """
    Split text into sentences/passages.
    For this MVP, we use a simple regex split by common sentence terminators.
    """
    if not text:
        return []
        
    # Split by . ! ? optionally followed by whitespace
    passages = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty or very short strings that aren't meaningful passages
    # Also handle newlines if they are used as separators instead of punctuation
    clean_passages = []
    for p in passages:
        # Also split by newlines for cases without punctuation
        sub_p = [s.strip() for s in p.split('\n') if s.strip()]
        for s in sub_p:
            if len(s) > 2:
                clean_passages.append(s)
                
    return clean_passages

def find_best_matches(source_text: str, submission_text: str) -> list:
    """
    1. Split documents into passages.
    2. Encode all passages.
    3. For every submission passage, find the best matching source passage based on semantic similarity.
    Returns a list of dictionaries containing the pairs and their semantic similarity.
    """
    source_passages = split_into_passages(source_text)
    sub_passages = split_into_passages(submission_text)
    
    if not source_passages or not sub_passages:
        return []
        
    # Batch encode all passages for efficiency
    source_embeddings = encode_passages(source_passages)
    sub_embeddings = encode_passages(sub_passages)
    
    # Calculate similarity matrix: shape (len(sub_passages), len(source_passages))
    sim_matrix = batch_semantic_similarity(sub_embeddings, source_embeddings)
    
    matches = []
    for i, sub_passage in enumerate(sub_passages):
        best_source_idx = np.argmax(sim_matrix[i])
        best_score = float(sim_matrix[i][best_source_idx])
        
        matches.append({
            "submission": sub_passage,
            "source": source_passages[best_source_idx],
            "semantic_similarity": best_score
        })
        
    return matches
