import re

# A small set of common stop words to exclude from concept extraction
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "be", "been", "being", "it", "this", "that", "these", "those",
    "he", "she", "they", "we", "i", "you", "my", "your", "their", "our", "his", "hers", "its",
    "can", "could", "would", "should", "may", "might", "must", "do", "does", "did",
    "have", "has", "had", "not", "no", "yes", "how", "what", "where", "when", "why", "who", "which",
    "as", "if", "then", "else", "than", "so", "because", "while"
}

# A small deterministic normalization dictionary for related terms
NORMALIZATION_DICT = {
    "exercise": "physical_activity",
    "exercising": "physical_activity",
    "workout": "physical_activity",
    "workouts": "physical_activity",
    "active": "physical_activity",
    "activity": "physical_activity",
    "cardiovascular": "heart_health",
    "cardiac": "heart_health",
    "heart": "heart_health",
    "illness": "disease",
    "sickness": "disease",
    "survival": "survive"
}

def extract_concepts(text: str) -> set:
    """
    Extract concepts from text, ignoring stop words and applying normalization.
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    
    concepts = set()
    for token in tokens:
        if token not in STOP_WORDS:
            # Normalize if present in dict, else keep token as the concept
            concept = NORMALIZATION_DICT.get(token, token)
            concepts.add(concept)
    
    return concepts

def concept_overlap(text_a: str, text_b: str) -> float:
    """
    Calculate the overlap of concepts between two texts using Jaccard similarity
    over the extracted concept sets.
    """
    concepts_a = extract_concepts(text_a)
    concepts_b = extract_concepts(text_b)
    
    if not concepts_a and not concepts_b:
        return 1.0
    if not concepts_a or not concepts_b:
        return 0.0
        
    intersection = concepts_a.intersection(concepts_b)
    union = concepts_a.union(concepts_b)
    
    return float(len(intersection)) / len(union)
