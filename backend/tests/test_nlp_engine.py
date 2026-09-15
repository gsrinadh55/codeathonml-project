import pytest
import json
from backend.nlp.engine import analyze_documents

def test_exact_copy():
    source = "Regular exercise improves cardiovascular health."
    submission = "Regular exercise improves cardiovascular health."
    
    result = analyze_documents(source, submission)
    assert len(result["matches"]) == 1
    match = result["matches"][0]
    
    assert match["semantic_similarity"] > 0.95
    assert match["lexical_similarity"] > 0.95
    assert match["paraphrase_gap"] < 0.10
    assert match["category"] == "EXACT / CLOSE COPY"

def test_heavy_paraphrase():
    source = "Regular exercise improves cardiovascular health."
    submission = "Frequent physical activity helps maintain a healthy heart."
    
    result = analyze_documents(source, submission)
    assert len(result["matches"]) >= 1
    match = result["matches"][0]
    
    assert match["semantic_similarity"] > 0.70
    assert match["lexical_similarity"] < 0.50
    assert match["paraphrase_gap"] > 0.30
    assert match["category"] in ["HEAVY PARAPHRASE", "HIGH SIMILARITY", "MODERATE SIMILARITY"]

def test_unrelated():
    source = "Regular exercise improves cardiovascular health."
    submission = "The university library closes at eight in the evening."
    
    result = analyze_documents(source, submission)
    # The matches should be empty because they don't meet the SEMANTIC_THRESHOLD
    assert len(result["matches"]) == 0

def test_multi_sentence():
    source = "Regular exercise improves cardiovascular health. It can reduce the risk of chronic disease. Physical activity may also improve concentration."
    submission = "Frequent workouts help maintain a healthy heart. Staying active can lower the chance of long-term illness. Students who remain physically active may concentrate better."
    
    result = analyze_documents(source, submission)
    # Depending on sentence boundaries, should find exactly 3 good matches
    assert len(result["matches"]) >= 2
    for match in result["matches"]:
        assert match["semantic_similarity"] > 0.60

def test_common_fact():
    source = "Water is essential for human survival."
    submission = "Humans need water to survive."
    
    result = analyze_documents(source, submission)
    assert len(result["matches"]) == 1
    match = result["matches"][0]
    
    assert match["semantic_similarity"] > 0.80
    assert "human" in match["explanation"] or "plagiarism" in match["explanation"] or "not strong enough" in match["explanation"]

def test_empty_input():
    result = analyze_documents("", "")
    assert result["overall"]["risk_score"] == 0.0
    assert len(result["matches"]) == 0
    
def test_short_passages():
    # Very short sentences may get filtered out, testing that it doesn't crash
    result = analyze_documents("Hi.", "Hi.")
    assert isinstance(result, dict)

def test_json_serializable():
    source = "Regular exercise improves cardiovascular health."
    submission = "Frequent physical activity helps maintain a healthy heart."
    result = analyze_documents(source, submission)
    # Will throw exception if not serializable
    json_str = json.dumps(result)
    assert isinstance(json_str, str)
