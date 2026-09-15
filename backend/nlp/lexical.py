import re

def tokenize(text: str) -> set:
    """
    Normalize and tokenize text into a set of words.
    """
    text = text.lower()
    # Extract alphanumeric words
    tokens = re.findall(r'\b\w+\b', text)
    return set(tokens)

def jaccard_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate Jaccard similarity between two texts based on word overlap.
    """
    set_a = tokenize(text_a)
    set_b = tokenize(text_b)
    
    if not set_a and not set_b:
        # Both are empty
        return 1.0
    if not set_a or not set_b:
        # One is empty
        return 0.0
        
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    
    return float(len(intersection)) / len(union)

def lexical_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate lexical similarity. For MVP, we use Jaccard similarity.
    """
    return jaccard_similarity(text_a, text_b)
