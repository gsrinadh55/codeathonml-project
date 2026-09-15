"""Lexical similarity calculation for PlagiSense."""

import re
from typing import Set


def tokenize(text: str) -> Set[str]:
    """Normalize and tokenize text into a set of words."""
    if not text:
        return set()
    text = str(text).lower()
    tokens = re.findall(r'\b\w+\b', text)
    return set(tokens)


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Calculate Jaccard similarity between two texts based on word overlap."""
    set_a = tokenize(text_a)
    set_b = tokenize(text_b)
    
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
        
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    
    return float(len(intersection)) / len(union) if union else 0.0


def lexical_similarity(text_a: str, text_b: str) -> float:
    """Calculate lexical similarity using Jaccard similarity."""
    return jaccard_similarity(text_a, text_b)
