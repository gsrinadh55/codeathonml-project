def calculate_risk_score(semantic: float, lexical: float, concept: float) -> float:
    """
    Calculate multi-signal risk/evidence score.
    This is an engineering heuristic.
    """
    return 0.65 * semantic + 0.20 * lexical + 0.15 * concept

def determine_risk_level(score: float) -> str:
    """
    Determine risk level based on MVP thresholds.
    """
    if score >= 0.70:
        return "HIGH"
    elif score >= 0.40:
        return "MEDIUM"
    return "LOW"

def determine_category(semantic: float, lexical: float, concept: float, paraphrase_gap: float) -> str:
    """
    Determine a similarity pattern category based on the signal values.
    """
    # Exact or close copy
    if semantic >= 0.85 and lexical >= 0.70:
        return "EXACT / CLOSE COPY"
        
    # Heavy paraphrase pattern
    if semantic >= 0.70 and lexical < 0.45 and concept >= 0.40 and paraphrase_gap >= 0.35:
        return "HEAVY PARAPHRASE"
        
    # Fallback to score-based categories
    score = calculate_risk_score(semantic, lexical, concept)
    if score >= 0.70:
        return "HIGH SIMILARITY"
    if score >= 0.40:
        return "MODERATE SIMILARITY"
        
    return "LOW SIMILARITY"

def get_evidence_flags(semantic: float, lexical: float, concept: float, paraphrase_gap: float) -> list:
    """
    Return human-readable bullet points of the strongest evidence signals.
    """
    flags = []
    if semantic >= 0.80:
        flags.append("High semantic similarity")
    
    if lexical >= 0.75:
        flags.append("High lexical overlap")
    elif lexical < 0.40 and semantic >= 0.70:
        flags.append("Low lexical overlap")
        
    if concept >= 0.70:
        flags.append("Strong concept alignment")
        
    if paraphrase_gap >= 0.40:
        flags.append("Large paraphrase gap")
        
    return flags
