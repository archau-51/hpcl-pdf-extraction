import nltk
from nltk.tokenize import sent_tokenize

# NLTK's recommended sentence tokenizer (PunktSentenceTokenizer) loads its
# model data from the "punkt_tab" resource on modern NLTK releases (the
# older "punkt" pickle files are no longer what sent_tokenize() reads from).
# Only hit the network/download if the data isn't already available locally.
_PUNKT_RESOURCE = "tokenizers/punkt_tab"


def _ensure_punkt_tab():
    try:
        nltk.data.find(_PUNKT_RESOURCE)
    except LookupError:
        try:
            nltk.download("punkt_tab")
        except Exception as e:
            # No network access, or some other download hiccup - don't crash
            # at import time. sent_tokenize() will raise a clear LookupError
            # later if the data really is missing when it's needed.
            print(f"Warning: could not download NLTK 'punkt_tab' data: {e}")


_ensure_punkt_tab()


def extract_info(text=str, keyword=str):
    """
    Extracts information associated with a keyword from the given text.

    Args:
        text (str): The input text containing relevant information.
        keyword (str): The keyword to search for.

    Returns:
        str: The extracted information related to the keyword.
    """
    # Split the text into sentences
    sentences = sent_tokenize(text)
    l = []
    # Search for the keyword in each sentence
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            l.append(sentence)
    if len(l) == 0:
        l.append(" ")
    return l
