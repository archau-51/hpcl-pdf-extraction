import nltk
import spacy
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

nlp = spacy.load('en_core_web_sm')
sentencizer = nltk.data.load('tokenizers/punkt/english.pickle')

# Load the text data
text = """George Kunkel Jr. was born in Baltimore, Maryland on December 29, 1866.[3] He was the son of theatre manager, actor, and singer George Kunkel and his wife Addie Kunkel.[4] His mother was an actress who was known on the stage as Ada Proctor.[5] His sister was the soprano Mamie Kunkel;[6] known on the concert and oratorio stage after her marriage to the composer and choral conductor Edward M. Zimmerman[7] as both Marie Kunkel Zimmerman and Marie Zimmerman."""

# Define the keyword
keyword = "birthplace"

# Preprocess the text data
doc = nlp(text)

# Named Entity Recognition (NER)
entities = [(entity.text, entity.label_) for entity in doc.ents]

# Part-of-Speech (POS) Tagging
# pos_tags = [(token.text, token.pos_) for token in doc]

# Dependency Parsing
# dependencies = [(token.text, token.dep_, token.head.text, token.head.pos_) for token in doc]

# Sentiment Analysis
# sentiment_analysis = pipeline("sentiment-analysis")
# sentiment = sentiment_analysis(text)

# Question Answering
question_answering = pipeline("question-answering")
answers = question_answering({
    'question': f'What is the {keyword}?',
    'context': text
})

# Extract relevant sentences
sentences = sentencizer.tokenize(text)

# Calculate the TF-IDF vector
# vectorizer = TfidfVectorizer(max_features=5000)
# tfidf = vectorizer.fit_transform(sentences)

# Calculate the cosine similarity between the keyword and the sentences
# similarity = cosine_similarity(tfidf)

# Get the most similar sentences
most_similar_sentences = []
for i, sentence in enumerate(sentences):
    if sentence.lower().startswith(keyword.lower()):
        most_similar_sentences.append(sentence)

# Extract relevant information
relevant_info: List[Dict[str, str]] = []
for sentence in most_similar_sentences:
    entities_in_sentence = [(entity.text, entity.label_) for entity in nlp(sentence).ents]
    relevant_info.extend([{"entity": entity, "label": label} for entity, label in entities_in_sentence])

print("Relevant info:")
print(entities)
print(answers)