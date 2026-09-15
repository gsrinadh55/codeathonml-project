"""Concept extraction and semantic concept overlap calculation for PlagiSense."""

import re
import sys
from pathlib import Path
from typing import Dict, Set

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# A small set of common stop words to exclude from concept extraction
STOP_WORDS: Set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "be", "been", "being", "it", "this", "that", "these", "those",
    "he", "she", "they", "we", "i", "you", "my", "your", "their", "our", "his", "hers", "its",
    "can", "could", "would", "should", "may", "might", "must", "do", "does", "did",
    "have", "has", "had", "not", "no", "yes", "how", "what", "where", "when", "why", "who", "which",
    "as", "if", "then", "else", "than", "so", "because", "while", "also", "remain"
}

# A small deterministic normalization dictionary for related terms
NORMALIZATION_DICT: Dict[str, str] = {
    "exercise": "physical_activity",
    "exercising": "physical_activity",
    "workout": "physical_activity",
    "workouts": "physical_activity",
    "active": "physical_activity",
    "activity": "physical_activity",
    "physical": "physical_activity",
    "staying": "physical_activity",
    "cardiovascular": "heart_health",
    "cardiac": "heart_health",
    "heart": "heart_health",
    "illness": "disease",
    "sickness": "disease",
    "chronic": "disease",
    "survival": "survive",
    "survive": "survive",
    "healthy": "health",
    "health": "health",
    "improves": "benefit",
    "improve": "benefit",
    "helps": "benefit",
    "maintain": "benefit",
    "better": "benefit",
    "essential": "need",
    "need": "need",
    "humans": "human",
    "human": "human",
    "lower": "reduce",
    "reduce": "reduce",
    "chance": "risk",
    "risk": "risk",
    "concentrate": "concentration",
    "concentration": "concentration",
    "frequent": "regular",
    "regular": "regular"
}


def extract_concepts(text: str) -> Set[str]:
    """Extract concepts from text, ignoring stop words and applying normalization."""
    if not text:
        return set()
    text = str(text).lower()
    tokens = re.findall(r'\b\w+\b', text)
    
    concepts: Set[str] = set()
    for token in tokens:
        if token not in STOP_WORDS:
            concept = NORMALIZATION_DICT.get(token, token)
            concepts.add(concept)
    
    return concepts


def concept_overlap(text_a: str, text_b: str) -> float:
    """Calculate the overlap of concepts between two texts using Jaccard similarity
    over the extracted concept sets.
    """
    if not text_a and not text_b:
        return 1.0
    if not text_a or not text_b:
        return 0.0

    concepts_a = extract_concepts(text_a)
    concepts_b = extract_concepts(text_b)
    
    if not concepts_a and not concepts_b:
        return 1.0
    if not concepts_a or not concepts_b:
        return 0.0
        
    intersection = concepts_a.intersection(concepts_b)
    union = concepts_a.union(concepts_b)
    
    return float(len(intersection)) / len(union) if union else 0.0
