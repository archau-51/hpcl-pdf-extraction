from transformers import pipeline

# Lazily-built, module-level cache for the QA pipeline. Building it loads a
# full transformer model from disk/hub, which is slow, so we only want to do
# it once per process instead of once per keyword per request.
_qa_pipeline = None


def _get_pipeline():
    global _qa_pipeline
    if _qa_pipeline is None:
        _qa_pipeline = pipeline("question-answering")
    return _qa_pipeline


def adv_extract(text, keyword):
    """
    Uses a cached HuggingFace question-answering pipeline to find the answer
    to "What is the <keyword>?" within the given text.

    Args:
        text (str): The context to search within.
        keyword (str): The keyword to ask about.

    Returns:
        dict: The pipeline's answer (includes "answer", "score", etc.).
    """
    question_answering = _get_pipeline()
    answers = question_answering({
        'question': f'What is the {keyword}?',
        'context': text
    })
    return answers
