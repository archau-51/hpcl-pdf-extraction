import nltk
nltk.download('punkt')
def extract_info(text=str, keyword=str):
    """
    Extracts information associated with a keyword from the given text.

    Args:
        text (str): The input text containing relevant information.
        keyword (str): The keyword to search for.

    Returns:
        str: The extracted information related to the keyword.
    """
    sentencizer = nltk.data.load('tokenizers/punkt/english.pickle')
    # Split the text into sentences
    sentences = sentencizer.tokenize(text)

    # Search for the keyword in each sentence
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            yield sentence


