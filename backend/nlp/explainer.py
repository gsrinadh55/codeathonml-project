def generate_explanation(category: str) -> str:
    """Generate deterministic explanations based on the similarity category.
    Explanations avoid claiming definitive plagiarism.
    """
    if category == "HEAVY PARAPHRASE":
        return "The passages have high semantic similarity despite relatively low wording overlap. Their underlying ideas and important concepts appear strongly related, suggesting possible paraphrasing or AI-assisted rewriting. This is similarity evidence for human review and does not by itself establish plagiarism."
    elif category == "EXACT / CLOSE COPY":
        return "The passages have very high semantic similarity and substantial wording overlap. This indicates strong textual correspondence and should be reviewed by a human."
    elif category == "HIGH SIMILARITY":
        return "The passages demonstrate strong combined evidence of similarity across meaning and phrasing. This should be reviewed by a human."
    elif category == "MODERATE SIMILARITY":
        return "The passages share some semantic or lexical characteristics, but the available evidence is not strong enough to indicate a clear correspondence."
    else:
        return "The passages show limited semantic and lexical correspondence. No strong similarity evidence was detected."
