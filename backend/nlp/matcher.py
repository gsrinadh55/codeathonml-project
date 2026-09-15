"""Passage extraction and semantic matching layer for PlagiSense."""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from backend.nlp.embeddings import encode_passages, batch_semantic_similarity
except ImportError:
    try:
        from .embeddings import encode_passages, batch_semantic_similarity
    except ImportError:
        from embeddings import encode_passages, batch_semantic_similarity  # type: ignore


def split_into_passages(text: str) -> List[str]:
    """Split text into sentences/passages."""
    if not text:
        return []
        
    passages = re.split(r'(?<=[.!?])\s+', str(text).strip())
    clean_passages: List[str] = []
    for p in passages:
        sub_p = [s.strip() for s in p.split('\n') if s.strip()]
        for s in sub_p:
            if len(s) > 2:
                clean_passages.append(s)
                
    return clean_passages


def find_best_matches(source_text: str, submission_text: str) -> List[Dict[str, Any]]:
    """1. Split documents into passages.
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
    
    matches: List[Dict[str, Any]] = []
    for i, sub_passage in enumerate(sub_passages):
        if i >= len(sim_matrix):
            break
        row = sim_matrix[i]
        if hasattr(row, 'tolist'):
            row = row.tolist()
        if not row:
            continue
        best_source_idx = max(range(len(row)), key=lambda k: row[k])
        if best_source_idx < len(source_passages):
            best_score = float(row[best_source_idx])
            matches.append({
                "submission": sub_passage,
                "source": source_passages[best_source_idx],
                "semantic_similarity": best_score
            })
        
    return matches
