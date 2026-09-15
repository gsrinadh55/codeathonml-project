import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from backend.nlp.matcher import find_best_matches
    from backend.nlp.lexical import lexical_similarity
    from backend.nlp.concepts import concept_overlap
    from backend.nlp.scorer import calculate_risk_score, determine_risk_level, determine_category, get_evidence_flags
    from backend.nlp.explainer import generate_explanation
except ImportError:
    try:
        from .matcher import find_best_matches
        from .lexical import lexical_similarity
        from .concepts import concept_overlap
        from .scorer import calculate_risk_score, determine_risk_level, determine_category, get_evidence_flags
        from .explainer import generate_explanation
    except ImportError:
        from matcher import find_best_matches
        from lexical import lexical_similarity
        from concepts import concept_overlap
        from scorer import calculate_risk_score, determine_risk_level, determine_category, get_evidence_flags
        from explainer import generate_explanation


def analyze_documents(source_text: str, submission_text: str) -> dict:
    """Main public API for analyzing documents.
    Returns a dictionary with overall risk and passage-level evidence.
    """
    # Base cases for empty or near-empty inputs
    if not source_text or not submission_text or not str(source_text).strip() or not str(submission_text).strip():
        return _empty_result()
        
    # Passage matching
    candidate_matches = find_best_matches(source_text, submission_text)
    if not candidate_matches:
        return _empty_result()
        
    # Analyze matches
    analyzed_matches = []
    
    # Configurable semantic threshold to filter out noise
    SEMANTIC_THRESHOLD = 0.50
    
    for match in candidate_matches:
        sub_p = match["submission"]
        src_p = match["source"]
        sem_sim = match["semantic_similarity"]
        
        # Calculate lexical and concept
        lex_sim = lexical_similarity(src_p, sub_p)
        con_sim = concept_overlap(src_p, sub_p)
        
        # Derived metrics
        gap = sem_sim - lex_sim
        score = calculate_risk_score(sem_sim, lex_sim, con_sim)
        cat = determine_category(sem_sim, lex_sim, con_sim, gap)
        flags = get_evidence_flags(sem_sim, lex_sim, con_sim, gap)
        expl = generate_explanation(cat)
        
        match_result = {
            "source": src_p,
            "submission": sub_p,
            "semantic_similarity": round(sem_sim, 4),
            "lexical_similarity": round(lex_sim, 4),
            "concept_overlap": round(con_sim, 4),
            "paraphrase_gap": round(gap, 4),
            "risk_score": round(score, 4),
            "category": cat,
            "evidence": flags,
            "explanation": expl
        }
        
        # Keep only meaningful matches
        if sem_sim >= SEMANTIC_THRESHOLD:
            analyzed_matches.append(match_result)
            
    # Overall score computation
    if not analyzed_matches:
        return _empty_result()
        
    # Find the top matches to calculate overall document risk
    strongest_match = max(analyzed_matches, key=lambda x: x["risk_score"])
    overall_score = strongest_match["risk_score"]
    overall_level = determine_risk_level(overall_score)
    
    # Average signals of suspicious matches
    avg_sem = sum(m["semantic_similarity"] for m in analyzed_matches) / len(analyzed_matches)
    avg_lex = sum(m["lexical_similarity"] for m in analyzed_matches) / len(analyzed_matches)
    avg_con = sum(m["concept_overlap"] for m in analyzed_matches) / len(analyzed_matches)
    
    return {
        "overall": {
            "risk_score": round(overall_score, 4),
            "risk_level": overall_level,
            "semantic_similarity": round(avg_sem, 4),
            "lexical_similarity": round(avg_lex, 4),
            "concept_overlap": round(avg_con, 4)
        },
        "matches": sorted(analyzed_matches, key=lambda x: x["risk_score"], reverse=True)
    }


def _empty_result() -> dict:
    return {
        "overall": {
            "risk_score": 0.0,
            "risk_level": "LOW",
            "semantic_similarity": 0.0,
            "lexical_similarity": 0.0,
            "concept_overlap": 0.0
        },
        "matches": []
    }


if __name__ == "__main__":
    src = "Regular exercise improves cardiovascular health."
    sub = "Frequent physical activity helps maintain a healthy heart."
    res = analyze_documents(src, sub)
    import json
    print("NLP Analysis Test Result:")
    print(json.dumps(res, indent=2))
