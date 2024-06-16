import nltk
def extract_info(text, keyword):
    sentencizer = nltk.data.load('tokenizers/punkt/english.pickle')
    """
    Extracts information associated with a keyword from the given text.

    Args:
        text (str): The input text containing relevant information.
        keyword (str): The keyword to search for.

    Returns:
        str: The extracted information related to the keyword.
    """
    # Split the text into sentences
    sentences = sentencizer.tokenize(text)

    # Search for the keyword in each sentence
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            yield sentence



# Example usage
sample_text = """
Mount Everest, also known as Sagarmatha in Nepal, is the highest mountain in the world.
It stands at an elevation of 8,848.86 meters (29,031.7 feet) above sea level.
Many climbers attempt to reach its summit, facing extreme conditions and challenges.
good elevation.
"""

search_keyword = "sagar"
result = [x for x in extract_info(sample_text, search_keyword)]
print(result)
